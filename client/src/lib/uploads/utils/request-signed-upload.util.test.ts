import { ApiError } from "@/lib/api/api-error";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AVATAR_UPLOAD_TARGET } from "../typing/constants/avatar-upload-target.constant";
import { requestSignedUpload } from "./request-signed-upload.util";

interface PostResult {
  data?: unknown;
  error?: unknown;
  response: Response;
}

const { post } = vi.hoisted(() => {
  return { post: vi.fn<(path: string, init: unknown) => Promise<PostResult>>() };
});

vi.mock("@/lib/api/api-client", () => {
  return { apiClient: { POST: post } };
});

const SIGNED_UPLOAD = {
  fileId: "8c3c3a4e-1f1a-4f63-9b49-5f0f1a2b3c4d",
  url: "http://localhost:3208/tessio",
  fields: { key: "projects/TES/files/8c3c3a4e/report.pdf", policy: "eyJ" },
  objectKey: "projects/TES/files/8c3c3a4e/report.pdf",
};

const file = new File(["%PDF"], "report.pdf", { type: "application/pdf" });

describe("requestSignedUpload", () => {
  beforeEach(() => {
    post.mockResolvedValue({ data: SIGNED_UPLOAD, response: new Response(null, { status: 201 }) });
  });

  it("asks the project endpoint with the kind and the normalized type", async () => {
    const signedUpload = await requestSignedUpload(
      { kind: "test_file", projectKey: "TES", allowedFileTypes: ["application/pdf"] },
      file,
      "Application/PDF; charset=binary",
    );

    expect(signedUpload).toEqual(SIGNED_UPLOAD);
    expect(post).toHaveBeenCalledWith("/api/projects/{project_key}/uploads", {
      params: { path: { project_key: "TES" } },
      body: { kind: "test_file", fileName: "report.pdf", contentType: "application/pdf", size: 4 },
    });
  });

  it("asks the avatar endpoint without a kind", async () => {
    await requestSignedUpload(AVATAR_UPLOAD_TARGET, file, "image/png");

    expect(post).toHaveBeenCalledWith("/api/me/avatar-upload", {
      body: { fileName: "report.pdf", contentType: "image/png", size: 4 },
    });
  });

  it("throws an ApiError with the server code", async () => {
    post.mockResolvedValue({
      error: { code: "PERMISSION_DENIED", message: "Permission denied." },
      response: new Response(null, { status: 403 }),
    });

    const request = requestSignedUpload(
      { kind: "import", projectKey: "TES", allowedFileTypes: ["text/csv"] },
      file,
      "text/csv",
    );

    await expect(request).rejects.toBeInstanceOf(ApiError);
    await expect(request).rejects.toMatchObject({ status: 403, code: "PERMISSION_DENIED" });
  });
});
