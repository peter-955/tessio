"use client";

import {
  DSActionIcon,
  DSButton,
  DSCard,
  DSErrorState,
  DSMenu,
  DSSkeleton,
  DSStack,
  DSTable,
  DSText,
  type DSMenuItem,
} from "@/components/design-system";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetLabels } from "../../hooks/queries/use-get-labels";
import type { LabelModalState } from "../../typing/types/label-modal-state.type";
import type { Label } from "../../typing/types/label.type";
import { DeleteLabelModal } from "../delete-label-modal/delete-label-modal";
import { LabelChip } from "../label-chip/label-chip";
import { LabelModal } from "../label-modal/label-modal";
import styles from "./label-manager-card.module.scss";

interface Props {
  projectKey: string;
  canManage: boolean;
}

export const LabelManagerCard: FC<Props> = ({ projectKey, canManage }) => {
  const { t } = useTranslation("labels");
  const { data: labels, isPending, isError, isFetching, refetch } = useGetLabels(projectKey);
  const [modalState, setModalState] = useState<LabelModalState>({ mode: "closed" });

  const closeModal = (): void => {
    setModalState({ mode: "closed" });
  };

  const buildMenuItems = (label: Label): DSMenuItem[] => {
    return [
      {
        key: "edit",
        label: t("manager.edit"),
        icon: "edit",
        onClick: () => {
          setModalState({ mode: "edit", label });
        },
      },
      { key: "divider", type: "divider" },
      {
        key: "delete",
        label: t("manager.delete"),
        icon: "trash",
        isDanger: true,
        onClick: () => {
          setModalState({ mode: "delete", label });
        },
      },
    ];
  };

  const renderLabels = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true" aria-label={t("manager.loading")}>
          <DSSkeleton lineCount={3} />
        </div>
      );
    }

    if (isError || labels === undefined) {
      return (
        <DSErrorState
          title={t("manager.loadError")}
          retryLabel={t("manager.retry")}
          isRetrying={isFetching}
          titleOrder={3}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (labels.length === 0) {
      return <DSText color="muted">{t("manager.empty")}</DSText>;
    }

    return (
      <DSTable label={t("manager.tableLabel")}>
        <caption className={styles.caption}>{t("manager.tableLabel")}</caption>
        <thead>
          <tr>
            <th scope="col">{t("manager.name")}</th>
            <th scope="col">{t("manager.usage")}</th>
            {canManage && (
              <th scope="col" className={styles.actionsCell}>
                <span className={styles.visuallyHidden}>{t("manager.actions")}</span>
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {labels.map((label) => {
            return (
              <tr key={label.id}>
                <th scope="row" className={styles.nameCell}>
                  <LabelChip name={label.name} color={label.color} />
                </th>
                <td className={styles.muted}>{t("manager.usedBy", { count: label.caseCount })}</td>
                {canManage && (
                  <td className={styles.actionsCell}>
                    <DSMenu
                      items={buildMenuItems(label)}
                      target={
                        <DSActionIcon
                          icon="dots"
                          ariaLabel={t("manager.actionsFor", { name: label.name })}
                        />
                      }
                    />
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
      </DSTable>
    );
  };

  return (
    <DSCard title={t("manager.title")}>
      <DSStack gap={4}>
        <div className={styles.header}>
          <DSText color="muted">{t("manager.description")}</DSText>
          {canManage && (
            <DSButton
              type="default"
              icon="plus"
              onClick={() => {
                setModalState({ mode: "create" });
              }}
            >
              {t("manager.add")}
            </DSButton>
          )}
        </div>
        {renderLabels()}
      </DSStack>
      {(modalState.mode === "create" || modalState.mode === "edit") && (
        <LabelModal
          projectKey={projectKey}
          label={modalState.mode === "edit" ? modalState.label : null}
          labels={labels ?? []}
          onClose={closeModal}
        />
      )}
      {modalState.mode === "delete" && (
        <DeleteLabelModal projectKey={projectKey} label={modalState.label} onClose={closeModal} />
      )}
    </DSCard>
  );
};
