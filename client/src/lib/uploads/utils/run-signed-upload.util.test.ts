import { ApiError } from "@/lib/api/api-error";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FakeXmlHttpRequest } from "../test-utils/fake-xml-http-request.util";
import { UploadPhase } from "../typing/enums/upload-phase.enum";
import type { SignedUpload } from "../typing/types/signed-upload.type";
import type { UploadProgress } from "../typing/types/upload-progress.type";
import type { ProjectUploadTarget } from "../typing/types/upload-target.type";
import type { UploadedFile } from "../typing/types/uploaded-file.type";
import { UploadCanceledError } from "../upload-canceled-error";
import { completeSignedUpload } from "./complete-signed-upload.util";
import { requestSignedUpload } from "./request-signed-upload.util";
import { runSignedUpload } from "./run-signed-upload.util";

vi.mock("./request-signed-upload.util", () => {
  return { requestSignedUpload: vi.fn() };
});

vi.mock("./complete-signed-upload.util", () => {
  return { completeSignedUpload: vi.fn() };
});

const TARGET: ProjectUploadTarget = {
  kind: "evidence",
  projectKey: "TES",
  allowedFileTypes: ["application/pdf"],
};

const SIGNED_UPLOAD: SignedUpload = {
  fileId: "8c3c3a4e-1f1a-4f63-9b49-5f0f1a2b3c4d",
  url: "http://localhost:3208/tessio",
  fields: { key: "projects/TES/files/8c3c3a4e/proof.png", policy: "eyJ" },
  objectKey: "projects/TES/files/8c3c3a4e/proof.png",
};

const UPLOADED_FILE: UploadedFile = {
  id: SIGNED_UPLOAD.fileId,
  kind: "evidence",
  fileName: "proof.png",
  contentType: "image/png",
  size: 4,
  status: "uploaded",
  createdAt: "2026-11-01T10:00:00Z",
};

const createFile = (): File => {
  return new File(["abcd"], "proof.png", { type: "image/png" });
};

const waitForRequest = async (): Promise<FakeXmlHttpRequest> => {
  await vi.waitFor(() => {
    expect(FakeXmlHttpRequest.latest?.isSent).toBe(true);
  });
  const request = FakeXmlHttpRequest.latest;
  if (request === undefined) {
    throw new Error("No request was made.");
  }

  return request;
};

describe("runSignedUpload", () => {
  beforeEach(() => {
    FakeXmlHttpRequest.reset();
    vi.stubGlobal("XMLHttpRequest", FakeXmlHttpRequest);
    vi.mocked(requestSignedUpload).mockResolvedValue(SIGNED_UPLOAD);
    vi.mocked(completeSignedUpload).mockResolvedValue(UPLOADED_FILE);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("signs, posts and completes the upload in order", async () => {
    const onPhaseChange = vi.fn<(phase: UploadPhase) => void>();
    const onProgress = vi.fn<(progress: UploadProgress) => void>();
    const file = createFile();

    const upload = runSignedUpload({ target: TARGET, file, onPhaseChange, onProgress });
    const request = await waitForRequest();

    expect(requestSignedUpload).toHaveBeenCalledWith(TARGET, file, "image/png");
    expect(completeSignedUpload).not.toHaveBeenCalled();
    expect(request.url).toBe(SIGNED_UPLOAD.url);
    expect(request.body?.get("Content-Type")).toBe("image/png");
    expect(request.body?.get("key")).toBe(SIGNED_UPLOAD.fields.key);

    request.emitProgress(2, 4);
    request.respond(204);

    await expect(upload).resolves.toEqual(UPLOADED_FILE);
    expect(completeSignedUpload).toHaveBeenCalledWith(TARGET, SIGNED_UPLOAD.fileId);
    expect(onPhaseChange.mock.calls.map(([phase]) => phase)).toEqual([
      UploadPhase.SIGNING,
      UploadPhase.UPLOADING,
      UploadPhase.COMPLETING,
    ]);
    expect(onProgress.mock.calls.map(([progress]) => progress.percent)).toEqual([0, 50, 100]);
    expect(onProgress.mock.calls.at(-1)?.[0]).toEqual({
      loadedBytes: 4,
      totalBytes: 4,
      percent: 100,
    });
  });

  it("makes no request when the local check fails", async () => {
    const onPhaseChange = vi.fn<(phase: UploadPhase) => void>();
    const upload = runSignedUpload({
      target: TARGET,
      file: new File(["<html>"], "page.html", { type: "text/html" }),
      onPhaseChange,
    });

    await expect(upload).rejects.toMatchObject({ code: "FILE_TYPE_NOT_ALLOWED" });
    expect(requestSignedUpload).not.toHaveBeenCalled();
    expect(FakeXmlHttpRequest.instances).toHaveLength(0);
    expect(onPhaseChange).not.toHaveBeenCalled();
  });

  it("passes a server error through unchanged", async () => {
    const serverError = new ApiError({
      status: 403,
      code: "PERMISSION_DENIED",
      message: "Permission denied.",
    });
    vi.mocked(requestSignedUpload).mockRejectedValue(serverError);

    await expect(runSignedUpload({ target: TARGET, file: createFile() })).rejects.toBe(serverError);
    expect(FakeXmlHttpRequest.instances).toHaveLength(0);
  });

  it("never completes after a failed storage upload", async () => {
    const upload = runSignedUpload({ target: TARGET, file: createFile() });
    const request = await waitForRequest();

    request.respond(403, "<Error><Code>AccessDenied</Code></Error>", "Forbidden");

    await expect(upload).rejects.toMatchObject({ status: 403, code: "UPLOAD_NOT_COMPLETED" });
    expect(completeSignedUpload).not.toHaveBeenCalled();
  });

  it("stops between steps when the signal is aborted", async () => {
    const abortController = new AbortController();
    vi.mocked(requestSignedUpload).mockImplementation(() => {
      abortController.abort();

      return Promise.resolve(SIGNED_UPLOAD);
    });

    const upload = runSignedUpload({
      target: TARGET,
      file: createFile(),
      signal: abortController.signal,
    });

    await expect(upload).rejects.toBeInstanceOf(UploadCanceledError);
    expect(FakeXmlHttpRequest.instances).toHaveLength(0);
    expect(completeSignedUpload).not.toHaveBeenCalled();
  });

  it("never completes after a canceled storage upload", async () => {
    const abortController = new AbortController();
    const upload = runSignedUpload({
      target: TARGET,
      file: createFile(),
      signal: abortController.signal,
    });
    const request = await waitForRequest();

    abortController.abort();

    await expect(upload).rejects.toBeInstanceOf(UploadCanceledError);
    expect(request.isAborted).toBe(true);
    expect(completeSignedUpload).not.toHaveBeenCalled();
  });
});
