"use client";

import {
  DSAlert,
  DSModal,
  DSSelect,
  DSStack,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useRouter } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostRerunFailed } from "../../hooks/mutations/use-post-rerun-failed";
import { useManualRunApiErrors } from "../../hooks/use-manual-run-api-errors";
import { SAME_ENVIRONMENT_OPTION } from "../../typing/constants/manual-run.constant";
import { buildRecordManualRunPath } from "../../utils/manual-run-path.util";

interface Props {
  runId: string;
  rerunCount: number;
  onClose: () => void;
}

export const RerunManualModal: FC<Props> = ({ runId, rerunCount, onClose }) => {
  const { t } = useTranslation("manualRun");
  const router = useRouter();
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useManualRunApiErrors();
  const { showSuccessToast } = useShowToast();
  const [environmentChoice, setEnvironmentChoice] = useState<string>(SAME_ENVIRONMENT_OPTION);
  const { data: environments = [] } = useGetEnvironments(project.key);
  const rerunFailed = usePostRerunFailed(project.key, runId);
  const environmentOptions: DSSelectOption<string>[] = [
    { value: SAME_ENVIRONMENT_OPTION, label: t("rerun.sameEnvironment") },
    ...environments.map((environment): DSSelectOption<string> => {
      return { value: environment.id, label: environment.name };
    }),
  ];

  const handleConfirm = (): void => {
    rerunFailed.mutate(
      { environmentId: environmentChoice === SAME_ENVIRONMENT_OPTION ? null : environmentChoice },
      {
        onSuccess: (createdRun) => {
          showSuccessToast(t("rerun.started"));
          router.push(buildRecordManualRunPath(project.key, createdRun.id));
        },
      },
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("rerun.manualTitle")}
      isCloseDisabled={rerunFailed.isPending}
      action={{
        label: t("rerun.confirm"),
        icon: "refresh",
        isLoading: rerunFailed.isPending,
        onClick: handleConfirm,
      }}
    >
      <DSStack gap={4}>
        <DSText>{t("rerun.manualDescription", { count: rerunCount })}</DSText>
        <DSSelect<string>
          label={t("new.environment")}
          value={environmentChoice}
          options={environmentOptions}
          onChange={(choice) => {
            setEnvironmentChoice(choice ?? SAME_ENVIRONMENT_OPTION);
          }}
          isDisabled={rerunFailed.isPending}
        />
        {rerunFailed.error !== null && (
          <DSAlert color="danger">{resolveMessage(rerunFailed.error, apiErrors)}</DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
