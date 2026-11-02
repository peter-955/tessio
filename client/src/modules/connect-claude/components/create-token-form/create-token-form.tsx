"use client";

import {
  DSAlert,
  DSButton,
  DSCard,
  DSEmptyState,
  DSErrorState,
  DSInput,
  DSSelect,
  DSSkeleton,
  DSStack,
  hasLength,
  isNotEmpty,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { toFormErrorText } from "@/modules/auth/utils/form-error.util";
import { useGetProjects } from "@/shared/hooks/queries/use-get-projects";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostApiToken } from "../../hooks/mutations/use-post-api-token";
import {
  API_TOKEN_SCOPES,
  DEFAULT_API_TOKEN_SCOPE,
  DEFAULT_TOKEN_LIFETIME,
  MAX_ACTIVE_API_TOKENS,
  MAX_API_TOKEN_NAME_LENGTH,
  TOKEN_LIFETIME_DAYS,
} from "../../typing/constants/api-token.constant";
import type {
  ApiTokenScope,
  CreateApiTokenValues,
  CreatedApiToken,
  TokenLifetime,
} from "../../typing/types/api-token.type";
import { CreatedTokenDialog } from "../created-token-dialog/created-token-dialog";
import styles from "./create-token-form.module.scss";

const PROJECT_SKELETON_LINE_COUNT = 3;

interface Props {
  activeTokenCount: number;
}

export const CreateTokenForm: FC<Props> = ({ activeTokenCount }) => {
  const { t } = useTranslation("connectClaude");
  const resolveMessage = useResolveApiErrorMessage();
  const { data: projects, isPending: isLoadingProjects, isError, refetch } = useGetProjects();
  const [createdToken, setCreatedToken] = useState<CreatedApiToken | null>(null);
  const createToken = usePostApiToken();
  const isNameRequired = isNotEmpty(t("create.nameRequired"));
  const isNameShortEnough = hasLength({ max: MAX_API_TOKEN_NAME_LENGTH }, t("create.nameTooLong"));
  const form = useDSForm<CreateApiTokenValues>({
    mode: "controlled",
    initialValues: {
      name: "",
      projectKey: null,
      lifetimeDays: DEFAULT_TOKEN_LIFETIME,
      scope: DEFAULT_API_TOKEN_SCOPE,
    },
    validate: {
      name: (value) => {
        return isNameRequired(value) ?? isNameShortEnough(value.trim());
      },
      projectKey: isNotEmpty(t("create.projectRequired")),
    },
  });

  const activeProjects = (projects ?? []).filter((project) => {
    return !project.isArchived;
  });
  const projectOptions: DSSelectOption<string>[] = activeProjects.map((project) => {
    return { value: project.key, label: `${project.key} · ${project.name}` };
  });
  const lifetimeOptions: DSSelectOption<TokenLifetime>[] = TOKEN_LIFETIME_DAYS.map((days) => {
    return { value: days, label: t("create.lifetimeOption", { count: Number(days) }) };
  });
  const scopeOptions: DSSelectOption<ApiTokenScope>[] = API_TOKEN_SCOPES.map((scope) => {
    return { value: scope, label: t(`scope.options.${scope}`) };
  });
  const selectedProject = activeProjects.find((project) => {
    return project.key === form.values.projectKey;
  });
  const isLimitReached = activeTokenCount >= MAX_ACTIVE_API_TOKENS;
  const serverError = createToken.error
    ? resolveMessage(createToken.error, {
        PERMISSION_DENIED: t("errors.notMember"),
        NOT_FOUND: t("errors.projectNotFound"),
      })
    : null;

  const handleNameChange = (value: string): void => {
    form.setFieldValue("name", value);
  };

  const handleProjectChange = (value: string | null): void => {
    form.setFieldValue("projectKey", value);
  };

  const handleLifetimeChange = (value: TokenLifetime | null): void => {
    form.setFieldValue("lifetimeDays", value ?? DEFAULT_TOKEN_LIFETIME);
  };

  const handleScopeChange = (value: ApiTokenScope | null): void => {
    form.setFieldValue("scope", value ?? DEFAULT_API_TOKEN_SCOPE);
  };

  const handleValidSubmit = (values: CreateApiTokenValues): void => {
    if (values.projectKey === null) {
      return;
    }

    createToken.mutate(
      {
        name: values.name.trim(),
        projectKey: values.projectKey,
        expiresInDays: Number(values.lifetimeDays),
        scope: values.scope,
      },
      {
        onSuccess: (response) => {
          form.reset();
          setCreatedToken(response);
        },
      },
    );
  };

  const handleRetryProjects = (): void => {
    void refetch();
  };

  const handleCloseCreatedToken = (): void => {
    setCreatedToken(null);
    createToken.reset();
  };

  let content = (
    <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
      <DSStack gap={4}>
        {isLimitReached && <DSAlert color="warning">{t("create.limitReached")}</DSAlert>}
        {serverError !== null && <DSAlert color="danger">{serverError}</DSAlert>}
        <div className={styles.fields}>
          <DSInput
            label={t("create.name")}
            placeholder={t("create.namePlaceholder")}
            value={form.values.name}
            onChange={handleNameChange}
            error={toFormErrorText(form.errors.name)}
            autoComplete="off"
            isRequired
          />
          <DSSelect
            label={t("create.project")}
            placeholder={t("create.projectPlaceholder")}
            value={form.values.projectKey}
            options={projectOptions}
            onChange={handleProjectChange}
            error={form.errors.projectKey}
            nothingFoundLabel={t("create.projectNotFound")}
            isSearchable
            isRequired
          />
          <DSSelect
            label={t("create.lifetime")}
            value={form.values.lifetimeDays}
            options={lifetimeOptions}
            onChange={handleLifetimeChange}
          />
          <DSSelect
            label={t("scope.label")}
            value={form.values.scope}
            options={scopeOptions}
            onChange={handleScopeChange}
            description={t(`scope.descriptions.${form.values.scope}`)}
            isRequired
          />
        </div>
        {selectedProject?.myRole === "viewer" && (
          <DSAlert color="info">
            {form.values.scope === "api" ? t("create.viewerApiHint") : t("create.viewerHint")}
          </DSAlert>
        )}
        <div>
          <DSButton
            type="primary"
            nativeType="submit"
            icon="key"
            isLoading={createToken.isPending}
            isDisabled={isLimitReached}
          >
            {t("create.submit")}
          </DSButton>
        </div>
      </DSStack>
    </form>
  );
  if (isLoadingProjects) {
    content = <DSSkeleton lineCount={PROJECT_SKELETON_LINE_COUNT} />;
  } else if (isError) {
    content = (
      <DSErrorState
        title={t("create.projectsLoadFailed")}
        retryLabel={t("table.retry")}
        onRetry={handleRetryProjects}
      />
    );
  } else if (activeProjects.length === 0) {
    content = <DSEmptyState title={t("create.noProjects")} icon="projects" size="sm" />;
  }

  return (
    <DSCard title={t("create.title")}>
      {content}
      <CreatedTokenDialog createdToken={createdToken} onClose={handleCloseCreatedToken} />
    </DSCard>
  );
};
