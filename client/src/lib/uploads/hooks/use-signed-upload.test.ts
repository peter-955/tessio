import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { renderHookWithProviders } from "@/test/utils/render-hook-with-providers.util";
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createProvidersWrapper } from "../test-utils/create-providers-wrapper.util";
import { FakeXmlHttpRequest } from "../test-utils/fake-xml-http-request.util";
import { AVATAR_UPLOAD_TARGET } from "../typing/constants/avatar-upload-target.constant";
import { MAX_AVATAR_SIZE_IN_BYTES } from "../typing/constants/upload-limits.constant";
import { UploadPhase } from "../typing/enums/upload-phase.enum";
import type { SignedUpload } from "../typing/types/signed-upload.type";
import type { ProjectUploadTarget } from "../typing/types/upload-target.type";
import type { UploadedFile } from "../typing/types/uploaded-file.type";
import { UploadCanceledError } from "../upload-canceled-error";
import { completeSignedUpload } from "../utils/complete-signed-upload.util";
import { requestSignedUpload } from "../utils/request-signed-upload.util";
import { useAvatarUpload } from "./use-avatar-upload";
import { useSignedUpload, type UseSignedUploadResult } from "./use-signed-upload";

const { showErrorToast } = vi.hoisted(() => {
  return { showErrorToast: vi.fn<(title: string, description?: string) => void>() };
});

vi.mock("@/shared/hooks/use-show-toast", () => {
  const toasts = {
    showErrorToast,
    showSuccessToast: vi.fn(),
    showInfoToast: vi.fn(),
    showWarningToast: vi.fn(),
  };

  return {
    useShowToast: () => {
      return toasts;
    },
  };
});

vi.mock("../utils/request-signed-upload.util", () => {
  return { requestSignedUpload: vi.fn() };
});

vi.mock("../utils/complete-signed-upload.util", () => {
  return { completeSignedUpload: vi.fn() };
});

const PROJECT_TARGET: ProjectUploadTarget = {
  kind: "test_file",
  projectKey: "TES",
  allowedFileTypes: ["application/pdf"],
};

const SIGNED_UPLOAD: SignedUpload = {
  fileId: "8c3c3a4e-1f1a-4f63-9b49-5f0f1a2b3c4d",
  url: "http://localhost:3208/tessio",
  fields: { key: "projects/TES/files/8c3c3a4e/report.pdf", policy: "eyJ" },
  objectKey: "projects/TES/files/8c3c3a4e/report.pdf",
};

const UPLOADED_FILE: UploadedFile = {
  id: SIGNED_UPLOAD.fileId,
  kind: "test_file",
  fileName: "report.pdf",
  contentType: "application/pdf",
  size: 4,
  status: "uploaded",
  createdAt: "2026-11-01T10:00:00Z",
};

const createPdfFile = (): File => {
  return new File(["%PDF"], "report.pdf", { type: "application/pdf" });
};

const createFileOfSize = (size: number, name: string, type: string): File => {
  const file = new File(["x"], name, { type });
  Object.defineProperty(file, "size", { value: size });

  return file;
};

const waitForRequest = async (): Promise<FakeXmlHttpRequest> => {
  await waitFor(() => {
    expect(FakeXmlHttpRequest.latest?.isSent).toBe(true);
  });
  const request = FakeXmlHttpRequest.latest;
  if (request === undefined) {
    throw new Error("No request was made.");
  }

  return request;
};

const startUpload = (result: { current: UseSignedUploadResult }, file: File): Promise<unknown> => {
  let upload: Promise<unknown> = Promise.resolve();
  act(() => {
    upload = result.current.upload(file).catch((error: unknown) => {
      return error;
    });
  });

  return upload;
};

describe("useSignedUpload", () => {
  beforeEach(() => {
    FakeXmlHttpRequest.reset();
    vi.stubGlobal("XMLHttpRequest", FakeXmlHttpRequest);
    vi.mocked(requestSignedUpload).mockResolvedValue(SIGNED_UPLOAD);
    vi.mocked(completeSignedUpload).mockResolvedValue(UPLOADED_FILE);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uploads the file and returns the stored file", async () => {
    const onSuccess = vi.fn<(file: UploadedFile) => void>();
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({ target: PROJECT_TARGET, onSuccess });
    });

    expect(result.current.phase).toBe(UploadPhase.IDLE);
    expect(result.current.rules).toEqual({
      maxSizeInBytes: 20971520,
      acceptedTypes: ["application/pdf"],
    });

    const upload = startUpload(result, createPdfFile());
    const request = await waitForRequest();
    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.UPLOADING);
    });
    expect(result.current.isUploading).toBe(true);

    act(() => {
      request.emitProgress(2, 4);
    });
    await waitFor(() => {
      expect(result.current.progress?.percent).toBe(50);
    });

    act(() => {
      request.respond(204);
    });

    await expect(upload).resolves.toEqual(UPLOADED_FILE);
    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.UPLOADED);
    });
    expect(result.current.progress).toEqual({ loadedBytes: 4, totalBytes: 4, percent: 100 });
    expect(result.current.uploadedFile).toEqual(UPLOADED_FILE);
    expect(result.current.isUploading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(onSuccess).toHaveBeenCalledTimes(1);
    expect(onSuccess.mock.calls[0]?.[0]).toEqual(UPLOADED_FILE);
    expect(showErrorToast).not.toHaveBeenCalled();
  });

  it("toasts a too-large file without any request", async () => {
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({ target: PROJECT_TARGET });
    });

    const outcome = await startUpload(
      result,
      createFileOfSize(20971521, "big.pdf", "application/pdf"),
    );

    expect(outcome).toMatchObject({ status: 413, code: "FILE_TOO_LARGE" });
    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.FAILED);
    });
    expect(result.current.error).toMatchObject({ code: "FILE_TOO_LARGE" });
    expect(showErrorToast).toHaveBeenCalledWith(englishErrors.api.FILE_TOO_LARGE);
    expect(requestSignedUpload).not.toHaveBeenCalled();
    expect(FakeXmlHttpRequest.instances).toHaveLength(0);
  });

  it("prefers the caller's message for the error code", async () => {
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({
        target: PROJECT_TARGET,
        apiErrors: { FILE_TYPE_NOT_ALLOWED: "Only PDF files." },
      });
    });

    await startUpload(result, new File(["a"], "a.txt", { type: "text/plain" }));

    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith("Only PDF files.");
    });
  });

  it("toasts a storage failure and never completes", async () => {
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({ target: PROJECT_TARGET });
    });

    const upload = startUpload(result, createPdfFile());
    const request = await waitForRequest();
    act(() => {
      request.failNetwork();
    });

    await expect(upload).resolves.toMatchObject({ status: 0, code: "UPLOAD_NOT_COMPLETED" });
    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.FAILED);
    });
    expect(showErrorToast).toHaveBeenCalledWith(englishErrors.api.UPLOAD_NOT_COMPLETED);
    expect(completeSignedUpload).not.toHaveBeenCalled();
  });

  it("cancels the upload without a toast", async () => {
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({ target: PROJECT_TARGET });
    });

    const upload = startUpload(result, createPdfFile());
    const request = await waitForRequest();
    act(() => {
      result.current.cancel();
    });

    await expect(upload).resolves.toBeInstanceOf(UploadCanceledError);
    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.CANCELED);
    });
    expect(request.isAborted).toBe(true);
    expect(showErrorToast).not.toHaveBeenCalled();
    expect(completeSignedUpload).not.toHaveBeenCalled();
  });

  it("shows no toast when the caller disabled toasts", async () => {
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({ target: PROJECT_TARGET, isGlobalErrorToastDisabled: true });
    });

    await startUpload(result, createFileOfSize(20971521, "big.pdf", "application/pdf"));

    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.FAILED);
    });
    expect(showErrorToast).not.toHaveBeenCalled();
  });

  it("cancels the running upload when a new one starts", async () => {
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({ target: PROJECT_TARGET });
    });

    const firstUpload = startUpload(result, createPdfFile());
    const firstRequest = await waitForRequest();
    const secondUpload = startUpload(result, createPdfFile());

    await expect(firstUpload).resolves.toBeInstanceOf(UploadCanceledError);
    expect(firstRequest.isAborted).toBe(true);
    await waitFor(() => {
      expect(FakeXmlHttpRequest.instances).toHaveLength(2);
    });
    const secondRequest = await waitForRequest();
    act(() => {
      secondRequest.respond(204);
    });

    await expect(secondUpload).resolves.toEqual(UPLOADED_FILE);
    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.UPLOADED);
    });
    expect(showErrorToast).not.toHaveBeenCalled();
  });

  it("clears the state on reset", async () => {
    const { result } = renderHookWithProviders(() => {
      return useSignedUpload({ target: PROJECT_TARGET, isGlobalErrorToastDisabled: true });
    });

    await startUpload(result, createFileOfSize(20971521, "big.pdf", "application/pdf"));
    await waitFor(() => {
      expect(result.current.phase).toBe(UploadPhase.FAILED);
    });

    act(() => {
      result.current.reset();
    });

    await waitFor(() => {
      expect(result.current.error).toBeNull();
    });
    expect(result.current.phase).toBe(UploadPhase.IDLE);
    expect(result.current.progress).toBeNull();
  });

  it("keeps the rules stable for an inline target with the same values", () => {
    const queryClient = createTestQueryClient();
    const { result, rerender } = renderHook(
      ({ allowedFileTypes }: { allowedFileTypes: string[] }) => {
        return useSignedUpload({ target: { kind: "import", projectKey: "TES", allowedFileTypes } });
      },
      {
        initialProps: { allowedFileTypes: ["text/csv"] },
        wrapper: createProvidersWrapper(queryClient),
      },
    );
    const firstRules = result.current.rules;

    rerender({ allowedFileTypes: ["text/csv"] });
    expect(result.current.rules).toBe(firstRules);

    rerender({ allowedFileTypes: ["text/csv", "application/json"] });
    expect(result.current.rules.acceptedTypes).toEqual(["text/csv", "application/json"]);
  });

  it("aborts the upload on unmount", async () => {
    const queryClient = createTestQueryClient();
    const { result, unmount } = renderHook(
      () => {
        return useSignedUpload({ target: PROJECT_TARGET });
      },
      {
        wrapper: createProvidersWrapper(queryClient),
      },
    );

    const upload = startUpload(result, createPdfFile());
    const request = await waitForRequest();
    unmount();

    await expect(upload).resolves.toBeInstanceOf(UploadCanceledError);
    expect(request.isAborted).toBe(true);
    expect(completeSignedUpload).not.toHaveBeenCalled();
    expect(showErrorToast).not.toHaveBeenCalled();
  });
});

describe("useAvatarUpload", () => {
  beforeEach(() => {
    FakeXmlHttpRequest.reset();
    vi.stubGlobal("XMLHttpRequest", FakeXmlHttpRequest);
    vi.mocked(requestSignedUpload).mockResolvedValue(SIGNED_UPLOAD);
    vi.mocked(completeSignedUpload).mockResolvedValue({ ...UPLOADED_FILE, kind: "avatar" });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uses the avatar target and the 2 MB image rules", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAvatarUpload();
    });

    expect(result.current.rules).toEqual({
      maxSizeInBytes: MAX_AVATAR_SIZE_IN_BYTES,
      acceptedTypes: ["image/jpeg", "image/png", "image/webp"],
    });

    const file = new File(["png"], "me.png", { type: "image/png" });
    const upload = startUpload(result, file);
    const request = await waitForRequest();
    act(() => {
      request.respond(204);
    });

    await expect(upload).resolves.toMatchObject({ kind: "avatar" });
    expect(requestSignedUpload).toHaveBeenCalledWith(AVATAR_UPLOAD_TARGET, file, "image/png");
    expect(completeSignedUpload).toHaveBeenCalledWith(AVATAR_UPLOAD_TARGET, SIGNED_UPLOAD.fileId);
  });

  it("rejects an avatar over 2 MB before any request", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAvatarUpload({ apiErrors: { FILE_TOO_LARGE: "Avatar must be 2 MB or less." } });
    });

    await startUpload(
      result,
      createFileOfSize(MAX_AVATAR_SIZE_IN_BYTES + 1, "me.png", "image/png"),
    );

    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith("Avatar must be 2 MB or less.");
    });
    expect(requestSignedUpload).not.toHaveBeenCalled();
  });
});
