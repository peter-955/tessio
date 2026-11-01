"use client";

import {
  DSInput,
  DSModal,
  DSSelect,
  DSStack,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import type { ProjectRole } from "@/components/project-context/typing/types/project.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutProjectMember } from "../../hooks/mutations/use-put-project-member";
import { useGetMemberCandidates } from "../../hooks/queries/use-get-member-candidates";
import { useDebouncedValue } from "../../hooks/use-debounced-value";
import { MEMBER_SEARCH_DEBOUNCE_IN_MILLISECONDS } from "../../typing/constants/member-search.constant";
import { DEFAULT_MEMBER_ROLE, PROJECT_ROLES } from "../../typing/constants/project-role.constant";
import type { MemberCandidate } from "../../typing/types/member-candidate.type";

interface Props {
  projectKey: string;
  isOpened: boolean;
  onClose: () => void;
}

export const AddMemberModal: FC<Props> = ({ projectKey, isOpened, onClose }) => {
  const { t } = useTranslation("projects");
  const { showSuccessToast } = useShowToast();
  const [search, setSearch] = useState("");
  const [selectedCandidate, setSelectedCandidate] = useState<MemberCandidate | null>(null);
  const [role, setRole] = useState<ProjectRole>(DEFAULT_MEMBER_ROLE);
  const debouncedSearch = useDebouncedValue(search, MEMBER_SEARCH_DEBOUNCE_IN_MILLISECONDS);
  const { data: candidates, isPending: isLoadingCandidates } = useGetMemberCandidates(
    projectKey,
    debouncedSearch,
    isOpened,
  );
  const { mutate: putMember, isPending: isAdding } = usePutProjectMember(projectKey);
  const visibleCandidates = candidates ?? [];
  const isSelectedCandidateListed = visibleCandidates.some((candidate) => {
    return candidate.userId === selectedCandidate?.userId;
  });
  const listedCandidates =
    selectedCandidate === null || isSelectedCandidateListed
      ? visibleCandidates
      : [selectedCandidate, ...visibleCandidates];

  const buildCandidateLabel = (candidate: MemberCandidate): string => {
    const label = `${candidate.name} · ${candidate.email}`;

    return candidate.userStatus === "invited" ? `${label} ${t("addMember.invitedSuffix")}` : label;
  };

  const candidateOptions: DSSelectOption<string>[] = listedCandidates.map((candidate) => {
    return {
      value: candidate.userId,
      label: buildCandidateLabel(candidate),
      isDisabled: candidate.userStatus === "deactivated",
    };
  });
  const roleOptions: DSSelectOption<ProjectRole>[] = PROJECT_ROLES.map((projectRole) => {
    return { value: projectRole, label: t(`roles.${projectRole}`) };
  });
  const hasNoCandidates = !isLoadingCandidates && visibleCandidates.length === 0;

  const handleClose = (): void => {
    setSearch("");
    setSelectedCandidate(null);
    setRole(DEFAULT_MEMBER_ROLE);
    onClose();
  };

  const handleCandidateChange = (userId: string | null): void => {
    setSelectedCandidate(
      listedCandidates.find((candidate) => {
        return candidate.userId === userId;
      }) ?? null,
    );
  };

  const handleRoleChange = (projectRole: ProjectRole | null): void => {
    if (projectRole !== null) {
      setRole(projectRole);
    }
  };

  const handleAdd = (): void => {
    if (selectedCandidate === null) {
      return;
    }

    putMember(
      { userId: selectedCandidate.userId, role },
      {
        onSuccess: () => {
          showSuccessToast(t("members.memberAdded"));
          handleClose();
        },
      },
    );
  };

  return (
    <DSModal
      isOpened={isOpened}
      onClose={handleClose}
      title={t("addMember.title")}
      isCloseDisabled={isAdding}
      action={{
        label: t("addMember.submit"),
        icon: "plus",
        isLoading: isAdding,
        isDisabled: selectedCandidate === null,
        onClick: handleAdd,
      }}
    >
      <DSStack gap={4}>
        <DSInput
          label={t("addMember.search")}
          value={search}
          onChange={setSearch}
          autoComplete="off"
          isAutoFocused
        />
        <DSSelect
          label={t("addMember.user")}
          value={selectedCandidate?.userId ?? null}
          options={candidateOptions}
          onChange={handleCandidateChange}
          nothingFoundLabel={t("addMember.noCandidates")}
          isRequired
        />
        {hasNoCandidates && (
          <DSText size="sm" color="muted">
            {t("addMember.noCandidates")}
          </DSText>
        )}
        <DSSelect<ProjectRole>
          label={t("addMember.role")}
          value={role}
          options={roleOptions}
          onChange={handleRoleChange}
          isRequired
        />
      </DSStack>
    </DSModal>
  );
};
