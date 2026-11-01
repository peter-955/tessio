import { describe, expect, it } from "vitest";
import { ADF_MAX_DEPTH } from "../typing/constants/adf.constant";
import type { AdfNode } from "../typing/types/adf.type";
import {
  buildSafeHref,
  parseAdfDocument,
  rankAdfHeadingLevels,
  readAdfPlainText,
  readNumberAttribute,
  readStringAttribute,
} from "./adf.util";

const buildNestedValue = (depth: number): unknown => {
  return Array.from({ length: depth }).reduce<unknown>(
    (child) => {
      return { type: "blockquote", content: [child] };
    },
    { type: "text", text: "deep" },
  );
};

const measureDepth = (node: AdfNode): number => {
  return node.content.reduce((deepest, child) => {
    return Math.max(deepest, measureDepth(child) + 1);
  }, 0);
};

describe("parseAdfDocument", () => {
  it("returns null for values that are not an ADF document", () => {
    expect(parseAdfDocument(null)).toBeNull();
    expect(parseAdfDocument(undefined)).toBeNull();
    expect(parseAdfDocument("text")).toBeNull();
    expect(parseAdfDocument([])).toBeNull();
    expect(parseAdfDocument({ type: "paragraph" })).toBeNull();
    expect(parseAdfDocument({ content: [] })).toBeNull();
  });

  it("normalises nodes and drops children that are not objects", () => {
    const document = parseAdfDocument({
      type: "doc",
      content: [
        "garbage",
        42,
        null,
        { text: "no type" },
        {
          type: "paragraph",
          attrs: "bad",
          marks: [{ type: "strong" }, "bad", { attrs: {} }],
          content: [{ type: "text", text: "Hello", marks: [{ type: "em", attrs: { a: 1 } }] }],
        },
      ],
    });

    expect(document).toEqual({
      type: "doc",
      text: null,
      attrs: {},
      marks: [],
      content: [
        {
          type: "paragraph",
          text: null,
          attrs: {},
          marks: [{ type: "strong", attrs: {} }],
          content: [
            {
              type: "text",
              text: "Hello",
              attrs: {},
              marks: [{ type: "em", attrs: { a: 1 } }],
              content: [],
            },
          ],
        },
      ],
    });
  });

  it("stops below the maximum depth", () => {
    const document = parseAdfDocument({ type: "doc", content: [buildNestedValue(100)] });

    expect(document).not.toBeNull();
    expect(measureDepth(document as AdfNode)).toBe(ADF_MAX_DEPTH);
  });
});

describe("ADF attribute readers", () => {
  const node = { attrs: { level: 2, title: "Notes", broken: Number.NaN, count: "3" } };

  it("reads string attributes only when they are strings", () => {
    expect(readStringAttribute(node, "title")).toBe("Notes");
    expect(readStringAttribute(node, "level")).toBeNull();
    expect(readStringAttribute(node, "missing")).toBeNull();
  });

  it("reads finite number attributes only", () => {
    expect(readNumberAttribute(node, "level")).toBe(2);
    expect(readNumberAttribute(node, "broken")).toBeNull();
    expect(readNumberAttribute(node, "count")).toBeNull();
  });
});

describe("buildSafeHref", () => {
  it("keeps http, https and mailto links", () => {
    expect(buildSafeHref("https://docs.shop.test/a?b=1")).toBe("https://docs.shop.test/a?b=1");
    expect(buildSafeHref("http://shop.test")).toBe("http://shop.test/");
    expect(buildSafeHref("mailto:qa@shop.test")).toBe("mailto:qa@shop.test");
  });

  it("rejects script, data and relative links", () => {
    expect(buildSafeHref("javascript:alert(1)")).toBeNull();
    expect(buildSafeHref(" JavaScript:alert(1)")).toBeNull();
    expect(buildSafeHref("data:text/html;base64,PHNjcmlwdD4=")).toBeNull();
    expect(buildSafeHref("/relative/path")).toBeNull();
    expect(buildSafeHref("")).toBeNull();
  });
});

describe("readAdfPlainText", () => {
  it("joins text and mention names", () => {
    const document = parseAdfDocument({
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [
            { type: "mention", attrs: { text: "@Alice" } },
            { type: "text", text: " approves" },
          ],
        },
      ],
    });

    expect(readAdfPlainText(document as AdfNode)).toBe("@Alice approves");
  });
});

describe("rankAdfHeadingLevels", () => {
  it("maps the distinct heading levels to consecutive ranks", () => {
    const heading = (level: number): unknown => {
      return { type: "heading", attrs: { level, id: level }, content: [] };
    };
    const document = parseAdfDocument({
      type: "doc",
      content: [heading(4), { type: "panel", content: [heading(2)] }, heading(6), heading(2)],
    });

    const ranked = rankAdfHeadingLevels(document as AdfNode);

    expect(ranked.content.map((node) => node.attrs)).toEqual([
      { level: 2, id: 4 },
      {},
      { level: 3, id: 6 },
      { level: 1, id: 2 },
    ]);
    expect(ranked.content[1]?.content[0]?.attrs).toEqual({ level: 1, id: 2 });
  });
});
