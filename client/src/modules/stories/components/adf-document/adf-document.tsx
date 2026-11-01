"use client";

import { DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { parseAdfDocument, rankAdfHeadingLevels } from "../../utils/adf.util";
import styles from "./adf-document.module.scss";
import { AdfNode } from "./adf-node/adf-node";

interface Props {
  value: unknown;
}

export const AdfDocument: FC<Props> = ({ value }) => {
  const { t } = useTranslation("stories");
  const parsedDocument = parseAdfDocument(value);

  if (parsedDocument === null || parsedDocument.content.length === 0) {
    return <DSText color="muted">{t("description.empty")}</DSText>;
  }

  const document = rankAdfHeadingLevels(parsedDocument);

  return (
    <div className={styles.document}>
      {document.content.map((node, index) => {
        return <AdfNode key={index} node={node} depth={1} />;
      })}
    </div>
  );
};
