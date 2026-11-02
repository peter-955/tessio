"use client";

import { DSButton, DSCard, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { SuspectedCause } from "@/components/suspected-cause/suspected-cause";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import type { Failure } from "../../typing/types/failure.type";
import { checkCanAssignFailure } from "../../utils/failure-capability.util";
import { ChangeCauseModal } from "./change-cause-modal/change-cause-modal";
import styles from "./failure-cause-card.module.scss";

interface Props {
  failure: Pick<Failure, "id" | "status" | "cause" | "causeReason" | "testCaseCode">;
}

export const FailureCauseCard: FC<Props> = ({ failure }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const [isModalOpened, setIsModalOpened] = useState(false);
  const canChange = checkCanAssignFailure(project, failure);

  return (
    <DSCard title={t("cause.title")}>
      <div className={styles.content}>
        {failure.cause === null ? (
          <DSText color="muted">{t("cause.none")}</DSText>
        ) : (
          <SuspectedCause cause={failure.cause} reason={failure.causeReason} />
        )}
        {canChange && (
          <div>
            <DSButton
              type="outline"
              size="sm"
              icon="edit"
              onClick={() => {
                setIsModalOpened(true);
              }}
            >
              {t("cause.change")}
            </DSButton>
          </div>
        )}
      </div>
      {isModalOpened && (
        <ChangeCauseModal
          failure={failure}
          onClose={() => {
            setIsModalOpened(false);
          }}
        />
      )}
    </DSCard>
  );
};
