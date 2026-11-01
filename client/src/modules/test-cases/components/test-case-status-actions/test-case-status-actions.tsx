"use client";

import {
  DSActionIcon,
  DSButton,
  DSMenu,
  DSTooltip,
  type DSMenuItem,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutTestCaseStatus } from "../../hooks/mutations/use-put-test-case-status";
import type { TestCaseDetail, TestCaseStatus } from "../../typing/types/test-case.type";
import { buildTestCaseStatusActions } from "../../utils/status-actions.util";
import { DeprecateTestCaseModal } from "../deprecate-test-case-modal/deprecate-test-case-modal";
import styles from "./test-case-status-actions.module.scss";

interface Props {
  detail: TestCaseDetail;
  isDirty: boolean;
}

export const TestCaseStatusActions: FC<Props> = ({ detail, isDirty }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const [isDeprecateOpened, setIsDeprecateOpened] = useState(false);
  const changeStatus = usePutTestCaseStatus(project.key, detail.code, {
    onSuccess: (updatedDetail) => {
      setIsDeprecateOpened(false);
      showSuccessToast(
        t("toasts.statusChanged", {
          code: updatedDetail.code,
          status: t(`status.${updatedDetail.status}`),
        }),
      );
    },
    onError: () => {
      setIsDeprecateOpened(false);
    },
  });
  const { primary, secondary } = buildTestCaseStatusActions(detail.status);
  const isDisabled = isDirty || changeStatus.isPending;

  const handleStatus = (status: TestCaseStatus): void => {
    if (status === "deprecated") {
      setIsDeprecateOpened(true);
      return;
    }

    changeStatus.mutate(status);
  };

  const menuItems: DSMenuItem[] = secondary.map((action) => {
    return {
      key: action.status,
      label: t(`actions.${action.label}`),
      isDanger: action.status === "deprecated",
      onClick: () => {
        handleStatus(action.status);
      },
    };
  });

  return (
    <>
      <DSTooltip label={t("form.saveFirst")} isDisabled={!isDirty}>
        <span className={styles.actions}>
          {primary !== null && (
            <DSButton
              type="primary"
              isLoading={changeStatus.isPending && changeStatus.variables === primary.status}
              isDisabled={isDisabled}
              title={isDirty ? t("form.saveFirst") : undefined}
              onClick={() => {
                handleStatus(primary.status);
              }}
            >
              {t(`actions.${primary.label}`)}
            </DSButton>
          )}
          {menuItems.length > 0 && (
            <DSMenu
              items={menuItems}
              target={
                <DSActionIcon
                  icon="dots"
                  type="default"
                  ariaLabel={t("actions.more")}
                  isDisabled={isDisabled}
                />
              }
            />
          )}
        </span>
      </DSTooltip>
      <DeprecateTestCaseModal
        caseCode={detail.code}
        isOpened={isDeprecateOpened}
        isPending={changeStatus.isPending}
        onConfirm={() => {
          changeStatus.mutate("deprecated");
        }}
        onClose={() => {
          setIsDeprecateOpened(false);
        }}
      />
    </>
  );
};
