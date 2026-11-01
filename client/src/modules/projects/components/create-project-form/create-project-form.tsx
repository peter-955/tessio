"use client";

import {
  DSAlert,
  DSButton,
  DSCard,
  DSGroup,
  DSInput,
  DSSelect,
  DSStack,
  DSTextarea,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostProject } from "../../hooks/mutations/use-post-project";
import { useGetJiraBoards } from "../../hooks/queries/use-get-jira-boards";
import { CREATE_PROJECT_FIELD_ERROR_CODES } from "../../typing/constants/create-project-error.constant";
import {
  PROJECT_DESCRIPTION_MAX_LENGTH,
  PROJECT_NAME_MAX_LENGTH,
} from "../../typing/constants/project-key.constant";
import type { CreateProjectValues } from "../../typing/types/create-project-values.type";
import type { JiraProject } from "../../typing/types/jira.type";
import { toFormErrorText } from "../../utils/form-error.util";
import {
  checkIsValidProjectKey,
  normalizeProjectKeyInput,
  suggestProjectKey,
} from "../../utils/project-key.util";
import { buildProjectPath } from "../../utils/project-path.util";
import { JiraLoadError } from "../jira-load-error/jira-load-error";
import styles from "./create-project-form.module.scss";

interface Props {
  jiraProjects: JiraProject[];
  onJiraProjectLinked: () => void;
  onJiraNotConfigured: () => void;
}

export const CreateProjectForm: FC<Props> = ({
  jiraProjects,
  onJiraProjectLinked,
  onJiraNotConfigured,
}) => {
  const { t } = useTranslation("projects");
  const router = useRouter();
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast } = useShowToast();
  const [isKeyEdited, setIsKeyEdited] = useState(false);
  const [submitError, setSubmitError] = useState<ApiError | null>(null);
  const { mutate: createProject, isPending: isCreating } = usePostProject();
  const form = useDSForm<CreateProjectValues>({
    mode: "controlled",
    initialValues: { jiraProjectKey: null, jiraBoardId: null, name: "", key: "", description: "" },
    validate: {
      jiraProjectKey: (value) => {
        return value === null ? t("errors.jiraProjectRequired") : null;
      },
      jiraBoardId: (value) => {
        return value === null ? t("errors.jiraBoardRequired") : null;
      },
      name: (value) => {
        const trimmedName = value.trim();
        if (trimmedName === "") {
          return t("errors.nameRequired");
        }

        return trimmedName.length > PROJECT_NAME_MAX_LENGTH
          ? t("errors.tooLong", { count: PROJECT_NAME_MAX_LENGTH })
          : null;
      },
      key: (value) => {
        return checkIsValidProjectKey(value) ? null : t("errors.keyInvalid");
      },
      description: (value) => {
        return value.trim().length > PROJECT_DESCRIPTION_MAX_LENGTH
          ? t("errors.tooLong", { count: PROJECT_DESCRIPTION_MAX_LENGTH })
          : null;
      },
    },
  });
  const { jiraProjectKey, jiraBoardId } = form.values;
  const { setFieldValue } = form;
  const {
    data: jiraBoards,
    error: jiraBoardsError,
    isPending: isLoadingBoards,
    isFetching: isFetchingBoards,
    refetch: refetchBoards,
  } = useGetJiraBoards(jiraProjectKey);
  const singleBoardId = jiraBoards?.length === 1 ? String(jiraBoards[0].id) : null;

  useEffect(() => {
    if (singleBoardId !== null && jiraBoardId === null) {
      setFieldValue("jiraBoardId", singleBoardId);
    }
  }, [jiraBoardId, setFieldValue, singleBoardId]);

  const jiraProjectOptions: DSSelectOption<string>[] = jiraProjects.map((jiraProject) => {
    return { value: jiraProject.key, label: `${jiraProject.key} · ${jiraProject.name}` };
  });
  const boardOptions: DSSelectOption<string>[] = (jiraBoards ?? []).map((jiraBoard) => {
    return { value: String(jiraBoard.id), label: `${jiraBoard.name} (${jiraBoard.type})` };
  });
  const isBoardSelectDisabled = jiraProjectKey === null || isLoadingBoards;
  const hasNoBoards = jiraBoards !== undefined && jiraBoards.length === 0;

  const handleJiraProjectChange = (selectedKey: string | null): void => {
    setFieldValue("jiraProjectKey", selectedKey);
    setFieldValue("jiraBoardId", null);
    const jiraProject = jiraProjects.find((candidate) => {
      return candidate.key === selectedKey;
    });
    if (jiraProject === undefined) {
      return;
    }

    if (!isKeyEdited) {
      setFieldValue("key", suggestProjectKey(jiraProject.key, jiraProject.name));
    }
    if (form.values.name.trim() === "") {
      setFieldValue("name", jiraProject.name);
    }
  };

  const handleKeyChange = (value: string): void => {
    const normalizedKey = normalizeProjectKeyInput(value);
    setIsKeyEdited(normalizedKey !== "");
    setFieldValue("key", normalizedKey);
  };

  const handleCreateError = (error: ApiError): void => {
    if (error.code === "PROJECT_KEY_ALREADY_USED") {
      form.setFieldError("key", resolveMessage(error));
    }
    if (error.code === "JIRA_PROJECT_ALREADY_LINKED") {
      form.setFieldError("jiraProjectKey", resolveMessage(error));
      onJiraProjectLinked();
    }
    if (error.code === "JIRA_NOT_CONFIGURED") {
      onJiraNotConfigured();
    }
    setSubmitError(
      error.code !== null && CREATE_PROJECT_FIELD_ERROR_CODES.has(error.code) ? null : error,
    );
  };

  const handleValidSubmit = (values: CreateProjectValues): void => {
    if (values.jiraProjectKey === null || values.jiraBoardId === null) {
      return;
    }

    setSubmitError(null);
    const trimmedDescription = values.description.trim();
    createProject(
      {
        key: values.key,
        name: values.name.trim(),
        description: trimmedDescription === "" ? null : trimmedDescription,
        jiraProjectKey: values.jiraProjectKey,
        jiraBoardId: Number(values.jiraBoardId),
      },
      {
        onSuccess: (project) => {
          showSuccessToast(t("create.success"));
          router.push(buildProjectPath(project.key, "members"));
        },
        onError: handleCreateError,
      },
    );
  };

  return (
    <DSCard>
      <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate className={styles.form}>
        <DSStack gap={4}>
          {submitError && <DSAlert color="danger">{resolveMessage(submitError)}</DSAlert>}
          <DSSelect
            label={t("fields.jiraProject")}
            value={jiraProjectKey}
            options={jiraProjectOptions}
            onChange={handleJiraProjectChange}
            description={
              jiraProjectOptions.length === 0 ? t("hints.allJiraProjectsLinked") : undefined
            }
            error={form.errors.jiraProjectKey}
            nothingFoundLabel={t("hints.noMatch")}
            isDisabled={jiraProjectOptions.length === 0}
            isSearchable
            isRequired
          />
          {jiraBoardsError ? (
            <JiraLoadError
              error={jiraBoardsError}
              isRetrying={isFetchingBoards}
              onRetry={() => {
                void refetchBoards();
              }}
            />
          ) : (
            <DSSelect
              label={t("fields.jiraBoard")}
              value={jiraBoardId}
              options={boardOptions}
              onChange={(value) => {
                setFieldValue("jiraBoardId", value);
              }}
              description={hasNoBoards ? t("hints.noBoards") : undefined}
              error={form.errors.jiraBoardId}
              isDisabled={isBoardSelectDisabled || hasNoBoards}
              isRequired
            />
          )}
          <DSInput
            label={t("fields.name")}
            value={form.values.name}
            onChange={(value) => {
              setFieldValue("name", value);
            }}
            error={toFormErrorText(form.errors.name)}
            isRequired
          />
          <DSInput
            label={t("fields.key")}
            value={form.values.key}
            onChange={handleKeyChange}
            description={t("fields.keyDescription")}
            error={toFormErrorText(form.errors.key)}
            autoComplete="off"
            isRequired
          />
          <DSTextarea
            label={t("fields.description")}
            value={form.values.description}
            onChange={(value) => {
              setFieldValue("description", value);
            }}
            error={form.errors.description}
            maxLength={PROJECT_DESCRIPTION_MAX_LENGTH}
          />
          <DSGroup justify="end">
            <DSButton type="primary" nativeType="submit" icon="plus" isLoading={isCreating}>
              {t("create.submit")}
            </DSButton>
          </DSGroup>
        </DSStack>
      </form>
    </DSCard>
  );
};
