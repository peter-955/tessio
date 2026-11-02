import { describe, expect, it } from "vitest";
import { listReferencedKeys, splitReferences } from "./split-references.util";

describe("splitReferences", () => {
  it("splits text around data and file references", () => {
    expect(splitReferences("Sign in as {{data.user_email}} and upload {{file.invoice}}.")).toEqual([
      { type: "text", text: "Sign in as " },
      { type: "reference", kind: "data", key: "user_email" },
      { type: "text", text: " and upload " },
      { type: "reference", kind: "file", key: "invoice" },
      { type: "text", text: "." },
    ]);
  });

  it("keeps plain text and unknown braces as text", () => {
    expect(splitReferences("Open {{other.key}} and {{data.}}")).toEqual([
      { type: "text", text: "Open {{other.key}} and {{data.}}" },
    ]);
    expect(splitReferences("")).toEqual([]);
  });

  it("returns adjacent references without empty text parts", () => {
    expect(splitReferences("{{data.a}}{{data.b}}")).toEqual([
      { type: "reference", kind: "data", key: "a" },
      { type: "reference", kind: "data", key: "b" },
    ]);
  });
});

describe("listReferencedKeys", () => {
  it("collects each data and file key once from texts and steps", () => {
    expect(
      listReferencedKeys(
        ["Signed in as {{data.user_email}}", null],
        [
          { order: 1, action: "Type {{data.user_email}} and {{data.password}}", expected: null },
          { order: 2, action: "Upload {{file.invoice}}", expected: "{{data.password}} is hidden" },
        ],
      ),
    ).toEqual({ dataKeys: ["user_email", "password"], fileKeys: ["invoice"] });
  });
});
