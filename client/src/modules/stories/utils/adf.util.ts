import { ADF_MAX_DEPTH, ADF_SAFE_PROTOCOLS } from "../typing/constants/adf.constant";
import type { AdfMark, AdfNode } from "../typing/types/adf.type";

const isRecord = (value: unknown): value is Record<string, unknown> => {
  return typeof value === "object" && value !== null && !Array.isArray(value);
};

const normaliseAttributes = (value: unknown): Record<string, unknown> => {
  return isRecord(value) ? value : {};
};

const normaliseMark = (value: unknown): AdfMark | null => {
  if (!isRecord(value) || typeof value.type !== "string") {
    return null;
  }

  return { type: value.type, attrs: normaliseAttributes(value.attrs) };
};

const normaliseMarks = (value: unknown): AdfMark[] => {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map(normaliseMark).filter((mark): mark is AdfMark => {
    return mark !== null;
  });
};

const normaliseNode = (value: unknown, depth: number): AdfNode | null => {
  if (!isRecord(value) || typeof value.type !== "string") {
    return null;
  }

  const children = Array.isArray(value.content) && depth < ADF_MAX_DEPTH ? value.content : [];

  return {
    type: value.type,
    text: typeof value.text === "string" ? value.text : null,
    attrs: normaliseAttributes(value.attrs),
    marks: normaliseMarks(value.marks),
    content: children
      .map((child: unknown) => {
        return normaliseNode(child, depth + 1);
      })
      .filter((child): child is AdfNode => {
        return child !== null;
      }),
  };
};

export const parseAdfDocument = (value: unknown): AdfNode | null => {
  if (!isRecord(value) || value.type !== "doc") {
    return null;
  }

  return normaliseNode(value, 0);
};

export const readStringAttribute = (node: Pick<AdfNode, "attrs">, name: string): string | null => {
  const value = node.attrs[name];

  return typeof value === "string" ? value : null;
};

export const readNumberAttribute = (node: Pick<AdfNode, "attrs">, name: string): number | null => {
  const value = node.attrs[name];

  return typeof value === "number" && Number.isFinite(value) ? value : null;
};

export const buildSafeHref = (url: string): string | null => {
  try {
    const parsedUrl = new URL(url);

    return ADF_SAFE_PROTOCOLS.includes(parsedUrl.protocol) ? parsedUrl.href : null;
  } catch {
    return null;
  }
};

export const readAdfPlainText = (node: AdfNode): string => {
  if (node.text !== null) {
    return node.text;
  }

  const ownText = node.type === "mention" ? (readStringAttribute(node, "text") ?? "") : "";

  return node.content.reduce((text, child) => {
    return `${text}${readAdfPlainText(child)}`;
  }, ownText);
};

const collectHeadingLevels = (node: AdfNode): number[] => {
  const ownLevels = node.type === "heading" ? [readNumberAttribute(node, "level") ?? 0] : [];

  return node.content.reduce((levels, child) => {
    return [...levels, ...collectHeadingLevels(child)];
  }, ownLevels);
};

const applyHeadingRanks = (node: AdfNode, ranks: ReadonlyMap<number, number>): AdfNode => {
  const level = node.type === "heading" ? readNumberAttribute(node, "level") : null;

  return {
    ...node,
    attrs: level === null ? node.attrs : { ...node.attrs, level: ranks.get(level) ?? level },
    content: node.content.map((child) => {
      return applyHeadingRanks(child, ranks);
    }),
  };
};

export const rankAdfHeadingLevels = (document: AdfNode): AdfNode => {
  const levels = [...new Set(collectHeadingLevels(document))].sort((first, second) => {
    return first - second;
  });
  const ranks = new Map(
    levels.map((level, index): [number, number] => {
      return [level, index + 1];
    }),
  );

  return applyHeadingRanks(document, ranks);
};
