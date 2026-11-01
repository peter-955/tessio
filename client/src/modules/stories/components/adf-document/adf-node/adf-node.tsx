"use client";

import { DSBadge } from "@/components/design-system";
import classNames from "classnames";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import {
  ADF_CARD_TYPES,
  ADF_DEFAULT_HEADING_ELEMENT,
  ADF_DEFAULT_PANEL_TYPE,
  ADF_HEADING_ELEMENTS,
  ADF_LIST_ITEM_TYPES,
  ADF_MEDIA_TYPES,
  ADF_PANEL_TYPES,
  ADF_STATUS_COLORS,
  ADF_TASK_DONE_STATE,
} from "../../../typing/constants/adf.constant";
import type { AdfNode as AdfNodeValue } from "../../../typing/types/adf.type";
import {
  buildSafeHref,
  readAdfPlainText,
  readNumberAttribute,
  readStringAttribute,
} from "../../../utils/adf.util";
import { AdfDate } from "../adf-date/adf-date";
import styles from "../adf-document.module.scss";
import { AdfText } from "../adf-text/adf-text";

interface Props {
  node: AdfNodeValue;
  depth: number;
}

export const AdfNode: FC<Props> = ({ node, depth }) => {
  const { t } = useTranslation("stories");

  const renderChildren = (): ReactNode => {
    return node.content.map((child, index) => {
      return <AdfNode key={index} node={child} depth={depth + 1} />;
    });
  };

  const renderListChildren = (): ReactNode => {
    return node.content.map((child, index) => {
      const element = <AdfNode key={index} node={child} depth={depth + 1} />;

      return ADF_LIST_ITEM_TYPES.includes(child.type) ? element : <li key={index}>{element}</li>;
    });
  };

  const renderCard = (): ReactNode => {
    const url = readStringAttribute(node, "url");
    if (url === null) {
      return null;
    }

    const href = buildSafeHref(url);

    return href === null ? (
      url
    ) : (
      <a href={href} target="_blank" rel="noopener noreferrer">
        {url}
      </a>
    );
  };

  if (ADF_CARD_TYPES.includes(node.type)) {
    return renderCard();
  }

  if (ADF_MEDIA_TYPES.includes(node.type)) {
    return <span className={styles.attachment}>{t("adf.attachment")}</span>;
  }

  switch (node.type) {
    case "text":
      return <AdfText text={node.text ?? ""} marks={node.marks} />;
    case "paragraph":
      return <p>{renderChildren()}</p>;
    case "heading": {
      const HeadingElement =
        ADF_HEADING_ELEMENTS[readNumberAttribute(node, "level") ?? 0] ??
        ADF_DEFAULT_HEADING_ELEMENT;

      return <HeadingElement className={styles.heading}>{renderChildren()}</HeadingElement>;
    }
    case "bulletList":
      return <ul>{renderListChildren()}</ul>;
    case "orderedList":
      return (
        <ol start={readNumberAttribute(node, "order") ?? undefined}>{renderListChildren()}</ol>
      );
    case "taskList":
      return <ul className={styles.taskList}>{renderListChildren()}</ul>;
    case "listItem":
      return <li>{renderChildren()}</li>;
    case "taskItem": {
      const label = readAdfPlainText(node).trim();

      return (
        <li className={styles.taskItem}>
          <input
            type="checkbox"
            checked={readStringAttribute(node, "state") === ADF_TASK_DONE_STATE}
            aria-label={label === "" ? undefined : label}
            aria-hidden={label === "" ? true : undefined}
            disabled
            readOnly
          />
          <span>{renderChildren()}</span>
        </li>
      );
    }
    case "blockquote":
      return <blockquote className={styles.blockquote}>{renderChildren()}</blockquote>;
    case "codeBlock":
      return (
        <pre className={styles.codeBlock}>
          <code data-language={readStringAttribute(node, "language") ?? undefined}>
            {readAdfPlainText(node)}
          </code>
        </pre>
      );
    case "rule":
      return <hr className={styles.rule} />;
    case "hardBreak":
      return <br />;
    case "panel": {
      const panelType = readStringAttribute(node, "panelType") ?? ADF_DEFAULT_PANEL_TYPE;
      const panelClassName = ADF_PANEL_TYPES.includes(panelType)
        ? styles[panelType]
        : styles[ADF_DEFAULT_PANEL_TYPE];

      return (
        <div role="note" className={classNames(styles.panel, panelClassName)}>
          {renderChildren()}
        </div>
      );
    }
    case "expand":
    case "nestedExpand":
      return (
        <details className={styles.expand}>
          <summary>{readStringAttribute(node, "title") ?? ""}</summary>
          {renderChildren()}
        </details>
      );
    case "table":
      return (
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <tbody>{renderChildren()}</tbody>
          </table>
        </div>
      );
    case "tableRow":
      return <tr>{renderChildren()}</tr>;
    case "tableHeader":
      return (
        <th
          colSpan={readNumberAttribute(node, "colspan") ?? undefined}
          rowSpan={readNumberAttribute(node, "rowspan") ?? undefined}
        >
          {renderChildren()}
        </th>
      );
    case "tableCell":
      return (
        <td
          colSpan={readNumberAttribute(node, "colspan") ?? undefined}
          rowSpan={readNumberAttribute(node, "rowspan") ?? undefined}
        >
          {renderChildren()}
        </td>
      );
    case "mention": {
      const name = (readStringAttribute(node, "text") ?? node.text ?? "").replace(/^@/, "");

      return <span className={styles.mention}>{`@${name}`}</span>;
    }
    case "emoji":
      return <>{readStringAttribute(node, "text") ?? readStringAttribute(node, "shortName")}</>;
    case "status":
      return (
        <DSBadge color={ADF_STATUS_COLORS[readStringAttribute(node, "color") ?? ""] ?? "gray"}>
          {readStringAttribute(node, "text") ?? ""}
        </DSBadge>
      );
    case "date":
      return <AdfDate timestamp={readStringAttribute(node, "timestamp")} />;
    default:
      return node.content.length === 0 ? null : <>{renderChildren()}</>;
  }
};
