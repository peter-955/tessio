"use client";

import { DSActionIcon, DSBadge, DSTooltip } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import classNames from "classnames";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ENDPOINT_LINK_PATTERN } from "../../typing/constants/test-data.constant";
import type { DataGridColumn } from "../../typing/types/data-grid-column.type";
import type { DataItemCreatePreset } from "../../typing/types/data-item-modal-state.type";
import type { DataItem, DataItemKind } from "../../typing/types/data-item.type";
import type { RevealedSecrets } from "../../typing/types/revealed-secrets.type";
import { canEditDataItemKinds } from "../../utils/data-item-capability.util";
import { SecretValue } from "../secret-value/secret-value";
import styles from "./data-grid-cell.module.scss";

interface Props {
  dataKey: string;
  rowKind: DataItemKind;
  column: DataGridColumn;
  scopeName: string;
  item: DataItem | undefined;
  projectItem: DataItem | undefined;
  revealedSecrets: RevealedSecrets;
  onCreate: (preset: DataItemCreatePreset) => void;
  onEdit: (item: DataItem) => void;
  onDelete: (item: DataItem) => void;
}

export const DataGridCell: FC<Props> = ({
  dataKey,
  rowKind,
  column,
  scopeName,
  item,
  projectItem,
  revealedSecrets,
  onCreate,
  onEdit,
  onDelete,
}) => {
  const { t } = useTranslation("testData");
  const project = useCurrentProject();
  const canReveal = checkHasProjectCapability(project, "secret.reveal");
  const actionLabels = { key: dataKey, scope: scopeName };

  if (item === undefined) {
    const isInheriting = column.environment !== null && projectItem !== undefined;
    const presetKind = projectItem?.kind ?? rowKind;
    const canCreate = !column.isArchived && canEditDataItemKinds(project, [presetKind]);

    const handleCreate = (): void => {
      onCreate({ key: dataKey, kind: presetKind, scopeId: column.scopeId });
    };

    return (
      <span className={styles.cell}>
        <span className={styles.muted}>
          {isInheriting ? t("grid.inherited") : t("grid.noValue")}
        </span>
        {canCreate && (
          <span className={styles.actions}>
            <DSActionIcon
              icon="plus"
              ariaLabel={
                isInheriting
                  ? t("actions.override", actionLabels)
                  : t("actions.addInScope", actionLabels)
              }
              hasTooltip
              onClick={handleCreate}
            />
          </span>
        )}
      </span>
    );
  }

  const canEdit = !column.isArchived && canEditDataItemKinds(project, [item.kind]);

  const renderValue = (): ReactNode => {
    if (item.kind === "secret") {
      return (
        <SecretValue
          dataKey={dataKey}
          hasValue={item.hasValue}
          revealedValue={revealedSecrets.revealedValueById[item.id]}
          canReveal={canReveal}
          isRevealing={revealedSecrets.isRevealing(item.id)}
          onReveal={() => {
            void revealedSecrets.reveal(item.id);
          }}
          onHide={() => {
            revealedSecrets.hide(item.id);
          }}
        />
      );
    }

    const value = item.value ?? "";
    if (item.kind === "endpoint" && ENDPOINT_LINK_PATTERN.test(value)) {
      return (
        <DSTooltip label={value}>
          <a
            className={classNames(styles.value, styles.link)}
            href={value}
            target="_blank"
            rel="noopener noreferrer"
          >
            {value}
          </a>
        </DSTooltip>
      );
    }

    return (
      <DSTooltip label={value}>
        <span className={styles.value}>{value}</span>
      </DSTooltip>
    );
  };

  return (
    <span className={styles.cell}>
      {renderValue()}
      {item.kind !== rowKind && <DSBadge>{t(`kind.${item.kind}`)}</DSBadge>}
      {canEdit && (
        <span className={styles.actions}>
          <DSActionIcon
            icon="edit"
            ariaLabel={t("actions.edit", actionLabels)}
            hasTooltip
            onClick={() => {
              onEdit(item);
            }}
          />
          <DSActionIcon
            icon="trash"
            ariaLabel={t("actions.deleteItem", actionLabels)}
            hasTooltip
            onClick={() => {
              onDelete(item);
            }}
          />
        </span>
      )}
    </span>
  );
};
