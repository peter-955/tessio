"use client";

import {
  DSButtonLink,
  DSCard,
  DSErrorState,
  DSSelect,
  DSStack,
  DSText,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePatchProject } from "../../hooks/mutations/use-patch-project";
import type { DefaultEnvironmentValues } from "../../typing/types/default-environment-values.type";
import { buildProjectPath } from "../../utils/project-path.util";
import { buildDefaultEnvironmentValues } from "../../utils/project-settings.util";
import { LoadingState } from "../loading-state/loading-state";
import { SettingsCardFooter } from "../settings-card-footer/settings-card-footer";

interface Props {
  project: Project;
}

export const DefaultEnvironmentCard: FC<Props> = ({ project }) => {
  const { t } = useTranslation("projects");
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const { mutate: patchProject, isPending: isSaving } = usePatchProject(project.key, {
    isGlobalErrorToastDisabled: true,
  });
  const {
    data: environments,
    isPending: isLoadingEnvironments,
    isError: isEnvironmentsError,
    isFetching: isFetchingEnvironments,
    refetch: refetchEnvironments,
  } = useGetEnvironments(project.key);
  const form = useDSForm<DefaultEnvironmentValues>({
    mode: "controlled",
    initialValues: buildDefaultEnvironmentValues(project),
  });
  const environmentOptions: DSSelectOption<string>[] = (environments ?? []).map((environment) => {
    return { value: environment.id, label: environment.name };
  });

  const handleSaveError = (error: ApiError): void => {
    if (error.code === "UNKNOWN_REFERENCE") {
      form.setFieldError("defaultEnvironmentId", t("settings.defaults.environmentInvalid"));
      void refetchEnvironments();
      return;
    }

    showErrorToast(resolveMessage(error));
  };

  const handleValidSubmit = (values: DefaultEnvironmentValues): void => {
    patchProject(
      { defaultEnvironmentId: values.defaultEnvironmentId },
      {
        onSuccess: (updatedProject) => {
          const savedValues = buildDefaultEnvironmentValues(updatedProject);
          showSuccessToast(t("settings.saved"));
          form.setInitialValues(savedValues);
          form.setValues(savedValues);
          form.resetDirty(savedValues);
        },
        onError: handleSaveError,
      },
    );
  };

  const renderField = (): ReactNode => {
    if (isLoadingEnvironments) {
      return <LoadingState label={t("settings.defaults.loading")} lineCount={1} />;
    }

    if (isEnvironmentsError) {
      return (
        <DSErrorState
          title={t("settings.defaults.loadError")}
          retryLabel={t("errors.retry")}
          isRetrying={isFetchingEnvironments}
          onRetry={() => {
            void refetchEnvironments();
          }}
        />
      );
    }

    if (environmentOptions.length === 0) {
      return (
        <DSStack gap={2} align="start">
          <DSText color="muted">{t("settings.defaults.noEnvironments")}</DSText>
          <DSButtonLink href={buildProjectPath(project.key, "test-data")} icon="environments">
            {t("settings.defaults.manageEnvironments")}
          </DSButtonLink>
        </DSStack>
      );
    }

    return (
      <DSSelect
        label={t("settings.defaults.environment")}
        value={form.values.defaultEnvironmentId}
        options={environmentOptions}
        onChange={(value) => {
          form.setFieldValue("defaultEnvironmentId", value);
        }}
        description={t("settings.defaults.environmentDescription")}
        error={form.errors.defaultEnvironmentId}
        isClearable
      />
    );
  };

  return (
    <DSCard title={t("settings.defaults.title")}>
      <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          {renderField()}
          <SettingsCardFooter isDirty={form.isDirty()} isSaving={isSaving} />
        </DSStack>
      </form>
    </DSCard>
  );
};
