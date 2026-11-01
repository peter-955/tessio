import { ApiError } from "@/lib/api/api-error";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AVATAR_UPLOAD_TARGET } from "../typing/constants/avatar-upload-target.constant";
import { completeSignedUpload } from "./complete-signed-upload.util";

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

const FILE_ID = "8c3c3a4e-1f1a-4f63-9b49-5f0f1a2b3c4d";

const STORED_FILE = {
  id: FILE_ID,
  kind: "evidence",
  fileName: "proof.png",
  contentType: "image/png",
  size: 10,
  status: "uploaded",
  createdAt: "2026-11-01T10:00:00Z",
};

describe("completeSignedUpload", () => {
  beforeEach(() => {
    post.mockResolvedValue({ data: STORED_FILE, response: new Response(null, { status: 200 }) });
  });

  it("completes a project upload", async () => {
    const storedFile = await completeSignedUpload(
      { kind: "evidence", projectKey: "TES", allowedFileTypes: [] },
      FILE_ID,
    );

    expect(storedFile).toEqual(STORED_FILE);
    expect(post).toHaveBeenCalledWith("/api/projects/{project_key}/uploads/{file_id}/complete", {
      params: { path: { project_key: "TES", file_id: FILE_ID } },
    });
  });

  it("completes an avatar upload", async () => {
    await completeSignedUpload(AVATAR_UPLOAD_TARGET, FILE_ID);

    expect(post).toHaveBeenCalledWith("/api/me/avatar-upload/{file_id}/complete", {
      params: { path: { file_id: FILE_ID } },
    });
  });

  it("throws an ApiError with the server code", async () => {
    post.mockResolvedValue({
      error: { code: "UPLOAD_NOT_COMPLETED", message: "Upload not completed." },
      response: new Response(null, { status: 409 }),
    });

    const request = completeSignedUpload(AVATAR_UPLOAD_TARGET, FILE_ID);

    await expect(request).rejects.toBeInstanceOf(ApiError);
    await expect(request).rejects.toMatchObject({ status: 409, code: "UPLOAD_NOT_COMPLETED" });
  });
});
