import { describe, expect, it } from "vitest";
import { filterSuggestions, findReferenceQuery, insertReference } from "./reference-query.util";
import type { DSReferenceSuggestion } from "./step-editor.type";

const SUGGESTIONS: DSReferenceSuggestion[] = [
  { kind: "data", key: "password" },
  { kind: "data", key: "username" },
  { kind: "data", key: "user_email" },
  { kind: "data", key: "admin_user" },
  { kind: "file", key: "users.csv" },
];

describe("findReferenceQuery", () => {
  it("finds an open data reference before the caret", () => {
    const text = "Log in as {{data.us";

    expect(findReferenceQuery(text, text.length)).toEqual({
      kind: "data",
      prefix: "us",
      start: 10,
    });
  });

  it("allows spaces after the braces and an empty prefix", () => {
    expect(findReferenceQuery("Upload {{ file.", 15)).toEqual({
      kind: "file",
      prefix: "",
      start: 7,
    });
  });

  it("only looks at the text before the caret", () => {
    expect(findReferenceQuery("{{data.user}} and more", 9)).toEqual({
      kind: "data",
      prefix: "us",
      start: 0,
    });
  });

  it.each([
    ["no reference", "Open the page", 13],
    ["a closed reference", "{{data.user}}", 13],
    ["an unknown kind", "{{secret.key", 12],
    ["a space inside the key", "{{data.us er", 12],
  ])("returns null for %s", (_, text, caret) => {
    expect(findReferenceQuery(text, caret)).toBeNull();
  });
});

describe("insertReference", () => {
  it("completes the reference and moves the caret after it", () => {
    const text = "Log in as {{data.us now";
    const query = { kind: "data" as const, prefix: "us", start: 10 };

    expect(insertReference(text, query, "username", 19)).toEqual({
      text: "Log in as {{data.username}} now",
      caret: 27,
    });
  });

  it("reuses closing braces that follow the caret", () => {
    const text = "Upload {{file.}}";
    const query = { kind: "file" as const, prefix: "", start: 7 };

    expect(insertReference(text, query, "avatar.png", 14)).toEqual({
      text: "Upload {{file.avatar.png}}",
      caret: 26,
    });
  });
});

describe("filterSuggestions", () => {
  it("keeps the same kind, prefix matches first, then matches inside the key", () => {
    const query = { kind: "data" as const, prefix: "US", start: 0 };

    expect(filterSuggestions(SUGGESTIONS, query).map((suggestion) => suggestion.key)).toEqual([
      "username",
      "user_email",
      "admin_user",
    ]);
  });

  it("returns at most eight suggestions", () => {
    const suggestions = Array.from({ length: 12 }, (_, index): DSReferenceSuggestion => {
      return { kind: "data", key: `key_${index}` };
    });

    expect(filterSuggestions(suggestions, { kind: "data", prefix: "", start: 0 })).toHaveLength(8);
  });
});
