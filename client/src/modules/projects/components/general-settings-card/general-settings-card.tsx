"use client";

import {
  DSAlert,
  DSCard,
  DSInput,
  DSSelect,
  DSStack,
  DSTextarea,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchProject } from "../../hooks/mutations/use-patch-project";
import { useGetJiraBoards } from "../../hooks/queries/use-get-jira-boards";
import {
  PROJECT_DESCRIPTION_MAX_LENGTH,
  PROJECT_NAME_MAX_LENGTH,
} from "../../typing/constants/project-key.constant";
import type { GeneralSettingsValues } from "../../typing/types/general-settings-values.type";
import type { UpdateProjectRequest } from "../../typing/types/project-request.type";
import { toFormErrorText } from "../../utils/form-error.util";
import { buildGeneralSettingsValues } from "../../utils/project-settings.util";
import { ReadOnlyField } from "../read-only-field/read-only-field";
import { SettingsCardFooter } from "../settings-card-footer/settings-card-footer";

interface Props {
  project: Project;
}

export const GeneralSettingsCard: FC<Props> = ({ project }) => {
  const { t } = useTranslation("projects");
  const { showSuccessToast } = useShowToast();
  const { mutate: patchProject, isPending: isSaving } = usePatchProject(project.key);
  const {
    data: jiraBoards,
    isPending: isLoadingBoards,
    isError: isBoardsError,
  } = useGetJiraBoards(project.jiraProjectKey);
  const form = useDSForm<GeneralSettingsValues>({
    mode: "controlled",
    initialValues: buildGeneralSettingsValues(project),
    validate: {
      name: (value) => {
        const trimmedName = value.trim();
        if (trimmedName === "") {
          return t("errors.nameRequired");
        }

        return trimmedName.length > PROJECT_NAME_MAX_LENGTH
          ? t("errors.tooLong", { count: PROJECT_NAME_MAX_LENGTH })
          : null;
      },
      description: (value) => {
        return value.trim().length > PROJECT_DESCRIPTION_MAX_LENGTH
          ? t("errors.tooLong", { count: PROJECT_DESCRIPTION_MAX_LENGTH })
          : null;
      },
    },
  });
  const currentBoardId = String(project.jiraBoardId);
  const boardOptions: DSSelectOption<string>[] = (jiraBoards ?? []).map((jiraBoard) => {
    return { value: String(jiraBoard.id), label: `${jiraBoard.name} (${jiraBoard.type})` };
  });
  const hasCurrentBoardOption = boardOptions.some((option) => {
    return option.value === currentBoardId;
  });
  const listedBoardOptions = hasCurrentBoardOption
    ? boardOptions
    : [{ value: currentBoardId, label: currentBoardId }, ...boardOptions];

  const handleValidSubmit = (values: GeneralSettingsValues): void => {
    const changes: UpdateProjectRequest = {};
    if (form.isDirty("name")) {
      changes.name = values.name.trim();
    }
    if (form.isDirty("description")) {
      changes.description = values.description.trim();
    }
    if (form.isDirty("jiraBoardId") && values.jiraBoardId !== null) {
      changes.jiraBoardId = Number(values.jiraBoardId);
    }

    patchProject(changes, {
      onSuccess: (updatedProject) => {
        const savedValues = buildGeneralSettingsValues(updatedProject);
        showSuccessToast(t("settings.saved"));
        form.setInitialValues(savedValues);
        form.setValues(savedValues);
        form.resetDirty(savedValues);
      },
    });
  };

  return (
    <DSCard title={t("settings.general.title")}>
      <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSInput
            label={t("fields.name")}
            value={form.values.name}
            onChange={(value) => {
              form.setFieldValue("name", value);
            }}
            error={toFormErrorText(form.errors.name)}
            isRequired
          />
          <DSTextarea
            label={t("fields.description")}
            value={form.values.description}
            onChange={(value) => {
              form.setFieldValue("description", value);
            }}
            error={form.errors.description}
            maxLength={PROJECT_DESCRIPTION_MAX_LENGTH}
          />
          <ReadOnlyField label={t("fields.key")} value={project.key} />
          {!project.isLinkedToJira && (
            <ReadOnlyField label={t("fields.stories")} value={t("fields.writtenInTessio")} />
          )}
          {project.isLinkedToJira && project.jiraProjectKey !== null && (
            <ReadOnlyField label={t("fields.jiraProject")} value={project.jiraProjectKey} />
          )}
          {!project.isLinkedToJira ? null : isBoardsError ? (
            <>
              <ReadOnlyField label={t("fields.jiraBoard")} value={currentBoardId} />
              <DSAlert color="warning">{t("settings.general.boardLoadFailed")}</DSAlert>
            </>
          ) : (
            <DSSelect
              label={t("fields.jiraBoard")}
              value={form.values.jiraBoardId}
              options={listedBoardOptions}
              onChange={(value) => {
                if (value !== null) {
                  form.setFieldValue("jiraBoardId", value);
                }
              }}
              description={isLoadingBoards ? t("settings.general.boardLoading") : undefined}
              isDisabled={isLoadingBoards}
            />
          )}
          <SettingsCardFooter isDirty={form.isDirty()} isSaving={isSaving} />
        </DSStack>
      </form>
    </DSCard>
  );
};
