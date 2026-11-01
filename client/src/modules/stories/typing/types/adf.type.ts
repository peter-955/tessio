export interface AdfMark {
  type: string;
  attrs: Record<string, unknown>;
}

export interface AdfNode {
  type: string;
  text: string | null;
  attrs: Record<string, unknown>;
  marks: AdfMark[];
  content: AdfNode[];
}

export type AdfHeadingElement = "h3" | "h4" | "h5" | "h6";
