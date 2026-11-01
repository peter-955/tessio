"use client";

import {
  DSAlert,
  DSButton,
  DSButtonLink,
  DSGroup,
  DSInput,
  DSPasswordInput,
  DSStack,
  DSText,
  isEmail,
  isNotEmpty,
  useDSForm,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { toFormErrorText } from "@/modules/projects/utils/form-error.util";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutJiraConnection } from "../../hooks/mutations/use-put-jira-connection";
import {
  JIRA_API_TOKENS_URL,
  JIRA_SITE_URL_PLACEHOLDER,
} from "../../typing/constants/jira-connection.constant";
import type { JiraConnectionValues } from "../../typing/types/jira-connection-values.type";
import type { JiraConnection } from "../../typing/types/jira-connection.type";
import { checkIsSameJiraSite } from "../../utils/jira-site-url.util";

interface Props {
  connection: JiraConnection;
}

export const JiraConnectionForm: FC<Props> = ({ connection }) => {
  const { t } = useTranslation("settings");
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast } = useShowToast();
  const [submitErrorMessage, setSubmitErrorMessage] = useState<string | null>(null);
  const { mutate: saveConnection, isPending: isSaving } = usePutJiraConnection();
  const savedSiteUrl = connection.isConfigured ? connection.siteUrl : null;

  const checkIsTokenRequired = (siteUrl: string): boolean => {
    return !checkIsSameJiraSite(siteUrl, savedSiteUrl);
  };

  const form = useDSForm<JiraConnectionValues>({
    mode: "controlled",
    initialValues: {
      siteUrl: connection.siteUrl ?? "",
      accountEmail: connection.accountEmail ?? "",
      apiToken: "",
    },
    validate: {
      siteUrl: isNotEmpty(t("jira.errors.siteUrlRequired")),
      accountEmail: isEmail(t("jira.errors.emailInvalid")),
      apiToken: (value, values) => {
        return checkIsTokenRequired(values.siteUrl) && value.trim() === ""
          ? t("jira.errors.apiTokenRequired")
          : null;
      },
    },
  });
  const isTokenRequired = checkIsTokenRequired(form.values.siteUrl);

  const resolveSaveErrorMessage = (error: ApiError): string => {
    if (error.code === "JIRA_INVALID_CREDENTIALS") {
      return t("jira.errors.invalidCredentials");
    }
    if (error.code === "JIRA_UNREACHABLE") {
      return t("jira.errors.unreachable");
    }
    if (error.code === "INVALID_REQUEST") {
      return t("jira.errors.invalidRequest");
    }

    return resolveMessage(error);
  };

  const handleSaveError = (error: ApiError): void => {
    if (error.code === "INVALID_REQUEST" && error.fieldErrors.accountEmail !== undefined) {
      form.setFieldError("accountEmail", t("jira.errors.emailInvalid"));
    }
    setSubmitErrorMessage(resolveSaveErrorMessage(error));
  };

  const handleValidSubmit = (values: JiraConnectionValues): void => {
    const apiToken = values.apiToken.trim();
    setSubmitErrorMessage(null);
    saveConnection(
      {
        siteUrl: values.siteUrl.trim(),
        accountEmail: values.accountEmail.trim(),
        apiToken: apiToken === "" ? null : apiToken,
      },
      {
        onSuccess: (savedConnection) => {
          const savedValues: JiraConnectionValues = {
            siteUrl: savedConnection.siteUrl ?? values.siteUrl.trim(),
            accountEmail: savedConnection.accountEmail ?? values.accountEmail.trim(),
            apiToken: "",
          };
          showSuccessToast(
            t("jira.success", {
              name: savedConnection.accountDisplayName ?? savedValues.accountEmail,
            }),
          );
          form.setInitialValues(savedValues);
          form.setValues(savedValues);
          form.resetDirty(savedValues);
        },
        onError: handleSaveError,
      },
    );
  };

  return (
    <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
      <DSStack gap={4}>
        <DSText size="sm" color="muted">
          {t("jira.hint")}
        </DSText>
        {submitErrorMessage && <DSAlert color="danger">{submitErrorMessage}</DSAlert>}
        <DSInput
          label={t("jira.siteUrl")}
          value={form.values.siteUrl}
          onChange={(value) => {
            form.setFieldValue("siteUrl", value);
          }}
          placeholder={JIRA_SITE_URL_PLACEHOLDER}
          error={toFormErrorText(form.errors.siteUrl)}
          autoComplete="url"
          isRequired
        />
        <DSInput
          type="email"
          label={t("jira.accountEmail")}
          value={form.values.accountEmail}
          onChange={(value) => {
            form.setFieldValue("accountEmail", value);
          }}
          error={toFormErrorText(form.errors.accountEmail)}
          autoComplete="email"
          isRequired
        />
        <DSStack gap={1}>
          <DSPasswordInput
            label={t("jira.apiToken")}
            value={form.values.apiToken}
            onChange={(value) => {
              form.setFieldValue("apiToken", value);
            }}
            description={isTokenRequired ? undefined : t("jira.apiTokenKeep")}
            error={form.errors.apiToken}
            autoComplete="new-password"
            isRequired={isTokenRequired}
          />
          <DSGroup>
            <DSButtonLink href={JIRA_API_TOKENS_URL} type="ghost" icon="key" isExternal>
              {t("jira.apiTokenHelp")}
            </DSButtonLink>
          </DSGroup>
        </DSStack>
        <DSGroup justify="end">
          <DSButton type="primary" nativeType="submit" icon="check" isLoading={isSaving}>
            {t("jira.submit")}
          </DSButton>
        </DSGroup>
      </DSStack>
    </form>
  );
};
