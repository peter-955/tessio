"use client";

import {
  DSAlert,
  DSInput,
  DSModal,
  DSSelect,
  DSStack,
  hasLength,
  matches,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostInviteUser } from "../../hooks/mutations/use-post-invite-user";
import { useUserApiErrors } from "../../hooks/use-user-api-errors";
import {
  ASSIGNABLE_WORKSPACE_ROLES,
  EMAIL_PATTERN,
  INVITE_USER_FORM_ID,
  MAX_EMAIL_LENGTH,
  MAX_USER_NAME_LENGTH,
} from "../../typing/constants/user.constant";
import type { InviteUserValues } from "../../typing/types/invite-user-values.type";
import type {
  AssignableWorkspaceRole,
  WorkspaceUser,
} from "../../typing/types/workspace-user.type";
import { toFormErrorText } from "../../utils/form-error.util";

interface Props {
  isOpened: boolean;
  onClose: () => void;
}

export const InviteUserModal: FC<Props> = ({ isOpened, onClose }) => {
  const { t } = useTranslation("users");
  const currentUser = useCurrentUser();
  const isOwner = currentUser.workspaceRole === "owner";
  const { showSuccessToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useUserApiErrors();
  const form = useDSForm<InviteUserValues>({
    mode: "controlled",
    initialValues: { email: "", name: "", workspaceRole: "member" },
    validate: {
      email: (value) => {
        const trimmedEmail = value.trim();
        if (trimmedEmail.length > MAX_EMAIL_LENGTH) {
          return t("errors.emailInvalid");
        }

        return matches(EMAIL_PATTERN, t("errors.emailInvalid"))(trimmedEmail);
      },
      name: hasLength({ min: 1, max: MAX_USER_NAME_LENGTH }, t("errors.nameRequired")),
    },
  });
  const inviteUser = usePostInviteUser();
  const roleOptions: DSSelectOption<AssignableWorkspaceRole>[] = ASSIGNABLE_WORKSPACE_ROLES.map(
    (role): DSSelectOption<AssignableWorkspaceRole> => {
      return {
        value: role,
        label: t(`workspaceRoles.${role}`),
        isDisabled: role === "admin" && !isOwner,
      };
    },
  );
  const alertError =
    inviteUser.error !== null && inviteUser.error.code !== "EMAIL_ALREADY_USED"
      ? inviteUser.error
      : null;

  const handleClose = (): void => {
    form.reset();
    inviteUser.reset();
    onClose();
  };

  const handleValidSubmit = (values: InviteUserValues): void => {
    inviteUser.mutate(
      {
        email: values.email.trim(),
        name: values.name.trim(),
        workspaceRole: values.workspaceRole,
      },
      {
        onSuccess: (invitedUser: WorkspaceUser) => {
          showSuccessToast(t("invite.success", { email: invitedUser.email }));
          handleClose();
        },
        onError: (error: ApiError) => {
          if (error.code === "EMAIL_ALREADY_USED") {
            form.setFieldError("email", t("errors.emailUsed"));
          }
        },
      },
    );
  };

  const handleEmailChange = (value: string): void => {
    form.setFieldValue("email", value);
  };

  const handleNameChange = (value: string): void => {
    form.setFieldValue("name", value);
  };

  const handleRoleChange = (value: AssignableWorkspaceRole | null): void => {
    if (value !== null) {
      form.setFieldValue("workspaceRole", value);
    }
  };

  return (
    <DSModal
      isOpened={isOpened}
      onClose={handleClose}
      title={t("invite.title")}
      isCloseDisabled={inviteUser.isPending}
      action={{
        label: t("invite.submit"),
        formId: INVITE_USER_FORM_ID,
        isLoading: inviteUser.isPending,
      }}
    >
      <form id={INVITE_USER_FORM_ID} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          {alertError !== null && (
            <DSAlert color="danger">{resolveMessage(alertError, apiErrors)}</DSAlert>
          )}
          <DSInput
            type="email"
            label={t("invite.email")}
            value={form.values.email}
            onChange={handleEmailChange}
            error={toFormErrorText(form.errors.email)}
            autoComplete="off"
            isRequired
            isAutoFocused
          />
          <DSInput
            label={t("invite.name")}
            value={form.values.name}
            onChange={handleNameChange}
            error={toFormErrorText(form.errors.name)}
            autoComplete="off"
            isRequired
          />
          <DSSelect<AssignableWorkspaceRole>
            label={t("invite.role")}
            value={form.values.workspaceRole}
            options={roleOptions}
            onChange={handleRoleChange}
            description={isOwner ? undefined : t("invite.adminOwnerOnly")}
            isRequired
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
