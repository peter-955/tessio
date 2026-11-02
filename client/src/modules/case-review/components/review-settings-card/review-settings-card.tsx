"use client";

import { DSCard, DSStack, DSSwitch } from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { SettingsCardFooter } from "@/modules/projects/components/settings-card-footer/settings-card-footer";
import { usePatchProject } from "@/modules/projects/hooks/mutations/use-patch-project";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  project: Project;
}

export const ReviewSettingsCard: FC<Props> = ({ project }) => {
  const { t } = useTranslation("caseReview");
  const { showSuccessToast } = useShowToast();
  const [isRequired, setIsRequired] = useState(project.requireSeparateReviewer);
  const [savedValue, setSavedValue] = useState(project.requireSeparateReviewer);
  const { mutate: patchProject, isPending: isSaving } = usePatchProject(project.key);

  if (savedValue !== project.requireSeparateReviewer) {
    setSavedValue(project.requireSeparateReviewer);
    setIsRequired(project.requireSeparateReviewer);
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    patchProject(
      { requireSeparateReviewer: isRequired },
      {
        onSuccess: () => {
          showSuccessToast(t("settings.saved"));
        },
      },
    );
  };

  return (
    <DSCard title={t("settings.title")}>
      <form onSubmit={handleSubmit} noValidate>
        <DSStack gap={4}>
          <DSSwitch
            label={t("settings.separateReviewer")}
            description={t("settings.separateReviewerDescription")}
            isChecked={isRequired}
            onChange={setIsRequired}
          />
          <SettingsCardFooter isDirty={isRequired !== savedValue} isSaving={isSaving} />
        </DSStack>
      </form>
    </DSCard>
  );
};
