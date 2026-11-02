"use client";

import type { FC } from "react";
import type { CaseReferences } from "../typing/types/case-sheet.type";
import { splitReferences } from "../utils/split-references.util";
import { ReferenceChip } from "./reference-chip/reference-chip";
import styles from "./reference-text.module.scss";

interface Props {
  text: string;
  references: CaseReferences;
}

export const ReferenceText: FC<Props> = ({ text, references }) => {
  return (
    <span className={styles.text}>
      {splitReferences(text).map((part, index) => {
        if (part.type === "text") {
          return <span key={index}>{part.text}</span>;
        }

        return (
          <ReferenceChip
            key={index}
            kind={part.kind}
            referenceKey={part.key}
            references={references}
          />
        );
      })}
    </span>
  );
};
