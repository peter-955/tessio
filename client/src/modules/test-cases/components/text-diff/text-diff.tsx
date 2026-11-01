import { Fragment, type FC, type ReactNode } from "react";
import type { DiffToken, TextDiffLabels } from "../../typing/types/version-diff.type";
import styles from "./text-diff.module.scss";

interface Props {
  tokens: readonly DiffToken[];
  labels: TextDiffLabels;
  separator?: string;
}

export const TextDiff: FC<Props> = ({ tokens, labels, separator = "" }) => {
  const renderToken = (token: DiffToken): ReactNode => {
    if (token.kind === "added") {
      return (
        <ins className={styles.added}>
          <span className={styles.visuallyHidden}>{`${labels.added}: `}</span>
          {token.value}
        </ins>
      );
    }

    if (token.kind === "removed") {
      return (
        <del className={styles.removed}>
          <span className={styles.visuallyHidden}>{`${labels.removed}: `}</span>
          {token.value}
        </del>
      );
    }

    return token.value;
  };

  return (
    <p className={styles.text}>
      {tokens.map((token, index) => {
        return (
          <Fragment key={index}>
            {index > 0 && separator}
            {renderToken(token)}
          </Fragment>
        );
      })}
    </p>
  );
};
