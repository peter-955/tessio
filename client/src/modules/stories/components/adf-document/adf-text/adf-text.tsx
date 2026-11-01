import type { FC, ReactNode } from "react";
import type { AdfMark } from "../../../typing/types/adf.type";
import { buildSafeHref, readStringAttribute } from "../../../utils/adf.util";

interface Props {
  text: string;
  marks: AdfMark[];
}

export const AdfText: FC<Props> = ({ text, marks }) => {
  const applyMark = (content: ReactNode, mark: AdfMark): ReactNode => {
    switch (mark.type) {
      case "strong":
        return <strong>{content}</strong>;
      case "em":
        return <em>{content}</em>;
      case "code":
        return <code>{content}</code>;
      case "strike":
        return <s>{content}</s>;
      case "underline":
        return <u>{content}</u>;
      case "subsup":
        return readStringAttribute(mark, "type") === "sub" ? (
          <sub>{content}</sub>
        ) : (
          <sup>{content}</sup>
        );
      case "link": {
        const href = buildSafeHref(readStringAttribute(mark, "href") ?? "");

        return href === null ? (
          content
        ) : (
          <a href={href} target="_blank" rel="noopener noreferrer">
            {content}
          </a>
        );
      }
      default:
        return content;
    }
  };

  return <>{marks.reduce<ReactNode>(applyMark, text)}</>;
};
