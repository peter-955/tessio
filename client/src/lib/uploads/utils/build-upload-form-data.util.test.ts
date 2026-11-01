import { describe, expect, it } from "vitest";
import type { SignedUpload } from "../typing/types/signed-upload.type";
import { buildUploadFormData } from "./build-upload-form-data.util";

const createSignedUpload = (fields: Record<string, string>): SignedUpload => {
  return {
    fileId: "8c3c3a4e-1f1a-4f63-9b49-5f0f1a2b3c4d",
    url: "http://localhost:3208/tessio",
    fields,
    objectKey: "projects/TES/files/8c3c3a4e/report.pdf",
  };
};

describe("buildUploadFormData", () => {
  it("appends the fields in order, then the content type, then the file", () => {
    const file = new File(["%PDF"], "report.pdf", { type: "application/pdf" });
    const formData = buildUploadFormData(
      createSignedUpload({
        key: "projects/TES/files/8c3c3a4e/report.pdf",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "tessio/20261101/us-east-1/s3/aws4_request",
        "x-amz-date": "20261101T000000Z",
        policy: "eyJleHBpcmF0aW9uIjoi",
        "x-amz-signature": "abc123",
      }),
      file,
      "application/pdf",
    );
    const entries = [...formData.entries()];

    expect(entries.map(([name]) => name)).toEqual([
      "key",
      "x-amz-algorithm",
      "x-amz-credential",
      "x-amz-date",
      "policy",
      "x-amz-signature",
      "Content-Type",
      "file",
    ]);
    expect(formData.get("key")).toBe("projects/TES/files/8c3c3a4e/report.pdf");
    expect(formData.get("policy")).toBe("eyJleHBpcmF0aW9uIjoi");
    expect(formData.get("Content-Type")).toBe("application/pdf");
    const sentFile = formData.get("file");
    expect(sentFile).toBeInstanceOf(File);
    expect(sentFile instanceof File ? sentFile.name : null).toBe("report.pdf");
  });

  it("does not add a key when the fields lack one", () => {
    const formData = buildUploadFormData(
      createSignedUpload({ policy: "eyJ", "x-amz-signature": "abc" }),
      new File(["a"], "a.png", { type: "image/png" }),
      "image/png",
    );

    expect(formData.has("key")).toBe(false);
    expect([...formData.keys()]).toEqual(["policy", "x-amz-signature", "Content-Type", "file"]);
  });
});
