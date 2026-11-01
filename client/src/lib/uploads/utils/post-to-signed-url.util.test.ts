import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FakeXmlHttpRequest } from "../test-utils/fake-xml-http-request.util";
import type { UploadProgress } from "../typing/types/upload-progress.type";
import { UploadCanceledError } from "../upload-canceled-error";
import { postToSignedUrl } from "./post-to-signed-url.util";

const SIGNED_URL = "http://localhost:3208/tessio";

const getLatestRequest = (): FakeXmlHttpRequest => {
  const request = FakeXmlHttpRequest.latest;
  if (request === undefined) {
    throw new Error("No request was made.");
  }

  return request;
};

const createFormData = (): FormData => {
  const formData = new FormData();
  formData.append("key", "projects/TES/files/a/report.pdf");

  return formData;
};

const createS3ErrorXml = (code: string): string => {
  return `<?xml version="1.0" encoding="UTF-8"?><Error><Code>${code}</Code><Message>Denied</Message></Error>`;
};

describe("postToSignedUrl", () => {
  beforeEach(() => {
    FakeXmlHttpRequest.reset();
    vi.stubGlobal("XMLHttpRequest", FakeXmlHttpRequest);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("posts the form to the signed url without credentials or extra headers", async () => {
    const formData = createFormData();
    const upload = postToSignedUrl({ url: SIGNED_URL, formData });
    const request = getLatestRequest();

    expect(request.method).toBe("POST");
    expect(request.url).toBe(SIGNED_URL);
    expect(request.withCredentials).toBe(false);
    expect(request.body).toBe(formData);
    expect(request.requestHeaders).toEqual({});

    request.respond(204);
    await expect(upload).resolves.toBeUndefined();
  });

  it("reports the upload progress", async () => {
    const onProgress = vi.fn<(progress: UploadProgress) => void>();
    const upload = postToSignedUrl({ url: SIGNED_URL, formData: createFormData(), onProgress });
    const request = getLatestRequest();

    request.emitProgress(1, 3);
    request.emitProgress(3, 3);
    request.respond(204);
    await upload;

    expect(onProgress.mock.calls.map(([progress]) => progress)).toEqual([
      { loadedBytes: 1, totalBytes: 3, percent: 33 },
      { loadedBytes: 3, totalBytes: 3, percent: 100 },
    ]);
  });

  it("maps EntityTooLarge to FILE_TOO_LARGE", async () => {
    const upload = postToSignedUrl({ url: SIGNED_URL, formData: createFormData() });
    getLatestRequest().respond(400, createS3ErrorXml("EntityTooLarge"), "Bad Request");

    await expect(upload).rejects.toMatchObject({ status: 413, code: "FILE_TOO_LARGE" });
  });

  it("maps EntityTooSmall to INVALID_REQUEST", async () => {
    const upload = postToSignedUrl({ url: SIGNED_URL, formData: createFormData() });
    getLatestRequest().respond(400, createS3ErrorXml("EntityTooSmall"), "Bad Request");

    await expect(upload).rejects.toMatchObject({ status: 422, code: "INVALID_REQUEST" });
  });

  it("maps any other storage error to UPLOAD_NOT_COMPLETED with its status", async () => {
    const upload = postToSignedUrl({ url: SIGNED_URL, formData: createFormData() });
    getLatestRequest().respond(403, createS3ErrorXml("AccessDenied"), "Forbidden");

    await expect(upload).rejects.toMatchObject({
      status: 403,
      code: "UPLOAD_NOT_COMPLETED",
      message: "AccessDenied",
    });
  });

  it("uses the status text when the storage sends no error code", async () => {
    const upload = postToSignedUrl({ url: SIGNED_URL, formData: createFormData() });
    getLatestRequest().respond(502, "<html>Bad gateway</html>", "Bad Gateway");

    await expect(upload).rejects.toMatchObject({
      status: 502,
      code: "UPLOAD_NOT_COMPLETED",
      message: "Bad Gateway",
    });
  });

  it("maps a network error to status 0 and UPLOAD_NOT_COMPLETED", async () => {
    const upload = postToSignedUrl({ url: SIGNED_URL, formData: createFormData() });
    getLatestRequest().failNetwork();

    await expect(upload).rejects.toMatchObject({ status: 0, code: "UPLOAD_NOT_COMPLETED" });
  });

  it("rejects with UploadCanceledError when the signal is already aborted", async () => {
    const abortController = new AbortController();
    abortController.abort();

    const upload = postToSignedUrl({
      url: SIGNED_URL,
      formData: createFormData(),
      signal: abortController.signal,
    });

    await expect(upload).rejects.toBeInstanceOf(UploadCanceledError);
    expect(getLatestRequest().isAborted).toBe(true);
    expect(getLatestRequest().isSent).toBe(false);
  });

  it("aborts the request when the signal fires during the upload", async () => {
    const abortController = new AbortController();
    const upload = postToSignedUrl({
      url: SIGNED_URL,
      formData: createFormData(),
      signal: abortController.signal,
    });
    const request = getLatestRequest();
    request.emitProgress(1, 2);

    abortController.abort();

    await expect(upload).rejects.toBeInstanceOf(UploadCanceledError);
    await expect(upload).rejects.toMatchObject({ status: 0, code: null });
    expect(request.isAborted).toBe(true);
  });

  it("removes the abort listener once the request settles", async () => {
    const abortController = new AbortController();
    const removeEventListener = vi.spyOn(abortController.signal, "removeEventListener");
    const upload = postToSignedUrl({
      url: SIGNED_URL,
      formData: createFormData(),
      signal: abortController.signal,
    });
    const request = getLatestRequest();

    request.respond(204);
    await upload;
    abortController.abort();

    expect(removeEventListener).toHaveBeenCalledWith("abort", expect.any(Function));
    expect(request.isAborted).toBe(false);
  });
});
