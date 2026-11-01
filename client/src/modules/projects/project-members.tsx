"use client";

import { checkIsWorkspaceAdmin } from "@/components/app-shell/utils/workspace-role.util";
import { DSButton, DSEmptyState, DSErrorState, DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useHasProjectCapability } from "@/components/project-context/hooks/use-has-project-capability";
import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useRouter } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { AddMemberModal } from "./components/add-member-modal/add-member-modal";
import { LoadingState } from "./components/loading-state/loading-state";
import { MembersTable } from "./components/members-table/members-table";
import { RemoveMemberModal } from "./components/remove-member-modal/remove-member-modal";
import { PROJECTS_PATH } from "./typing/constants/project-path.constant";

export const ProjectMembersPage: FC = () => {
  const { t } = useTranslation("projects");
  const router = useRouter();
  const project = useCurrentProject();
  const currentUser = useCurrentUser();
  const canManage = useHasProjectCapability("member.manage");
  const isWorkspaceAdmin = checkIsWorkspaceAdmin(currentUser.workspaceRole);
  const {
    data: members,
    isPending,
    isError,
    isFetching,
    refetch,
  } = useGetProjectMembers(project.key);
  const [isAddModalOpened, setIsAddModalOpened] = useState(false);
  const [memberToRemove, setMemberToRemove] = useState<ProjectMember | null>(null);
  const [isRemoveModalOpened, setIsRemoveModalOpened] = useState(false);

  const handleRemove = (member: ProjectMember): void => {
    setMemberToRemove(member);
    setIsRemoveModalOpened(true);
  };

  const handleRemoved = (member: ProjectMember): void => {
    if (member.userId === currentUser.id && !isWorkspaceAdmin) {
      router.push(PROJECTS_PATH);
    }
  };

  const renderContent = (): ReactNode => {
    if (isPending) {
      return <LoadingState label={t("members.loading")} />;
    }

    if (isError || members === undefined) {
      return (
        <DSErrorState
          title={t("members.loadError")}
          retryLabel={t("errors.retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (members.length === 0) {
      return <DSEmptyState title={t("members.empty")} icon="members" />;
    }

    return (
      <MembersTable
        projectKey={project.key}
        members={members}
        canManage={canManage}
        onRemove={handleRemove}
      />
    );
  };

  return (
    <>
      <DSPageHeader
        title={t("members.title")}
        description={t("members.description")}
        actions={
          canManage && (
            <DSButton
              type="primary"
              icon="plus"
              onClick={() => {
                setIsAddModalOpened(true);
              }}
            >
              {t("members.add")}
            </DSButton>
          )
        }
      />
      {renderContent()}
      {canManage && (
        <>
          <AddMemberModal
            projectKey={project.key}
            isOpened={isAddModalOpened}
            onClose={() => {
              setIsAddModalOpened(false);
            }}
          />
          <RemoveMemberModal
            projectKey={project.key}
            member={memberToRemove}
            isOpened={isRemoveModalOpened}
            isSelf={memberToRemove?.userId === currentUser.id}
            onClose={() => {
              setIsRemoveModalOpened(false);
            }}
            onRemoved={handleRemoved}
          />
        </>
      )}
    </>
  );
};
