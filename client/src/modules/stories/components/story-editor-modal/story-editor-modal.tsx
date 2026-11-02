"use client";

import { DSInput, DSModal, DSStack, DSTextarea, useDSForm } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchStory } from "../../hooks/mutations/use-patch-story";
import { usePostStory } from "../../hooks/mutations/use-post-story";
import {
  MAX_STORY_DESCRIPTION_LENGTH,
  MAX_STORY_TITLE_LENGTH,
} from "../../typing/constants/story-editor.constant";
import type { StoryEditorValues } from "../../typing/types/story-editor.type";
import type { StoryDetail } from "../../typing/types/story.type";
import { buildStoryEditorValues, buildStoryRequest } from "../../utils/story-editor.util";
import { CriteriaEditor } from "../criteria-editor/criteria-editor";

interface Props {
  projectKey: string;
  story: StoryDetail | null;
  onClose: () => void;
  onSaved: (story: StoryDetail) => void;
}

export const StoryEditorModal: FC<Props> = ({ projectKey, story, onClose, onSaved }) => {
  const { t } = useTranslation("stories");
  const formId = useId();
  const { showSuccessToast } = useShowToast();
  const form = useDSForm<StoryEditorValues>({
    mode: "controlled",
    initialValues: buildStoryEditorValues(story),
    validate: {
      title: (value) => {
        const title = value.trim();
        if (title === "") {
          return t("editor.titleRequired");
        }

        return title.length > MAX_STORY_TITLE_LENGTH
          ? t("editor.tooLong", { max: MAX_STORY_TITLE_LENGTH })
          : null;
      },
    },
  });

  const handleSaved = (savedStory: StoryDetail, message: string): void => {
    showSuccessToast(message);
    onSaved(savedStory);
    onClose();
  };

  const createStory = usePostStory(projectKey, {
    onSuccess: (savedStory) => {
      handleSaved(savedStory, t("editor.created", { key: savedStory.jiraKey }));
    },
  });
  const updateStory = usePatchStory(projectKey, story?.jiraKey ?? "", {
    onSuccess: (savedStory) => {
      handleSaved(savedStory, t("editor.updated"));
    },
  });
  const isSaving = createStory.isPending || updateStory.isPending;

  const handleValidSubmit = (values: StoryEditorValues): void => {
    const body = buildStoryRequest(values);
    if (story === null) {
      createStory.mutate(body);
      return;
    }

    updateStory.mutate(body);
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={
        story === null ? t("editor.createTitle") : t("editor.editTitle", { key: story.jiraKey })
      }
      isCloseDisabled={isSaving}
      action={{
        label: story === null ? t("editor.create") : t("editor.save"),
        formId,
        isLoading: isSaving,
      }}
    >
      <form id={formId} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSInput
            label={t("editor.title")}
            value={form.values.title}
            onChange={(value) => {
              form.setFieldValue("title", value);
            }}
            error={typeof form.errors.title === "string" ? form.errors.title : undefined}
            isRequired
            isAutoFocused
          />
          <DSTextarea
            label={t("editor.description")}
            description={t("editor.descriptionHint")}
            value={form.values.description}
            onChange={(value) => {
              form.setFieldValue("description", value);
            }}
            minRows={4}
            maxLength={MAX_STORY_DESCRIPTION_LENGTH}
          />
          <CriteriaEditor
            criteria={form.values.criteria}
            onChange={(criteria) => {
              form.setFieldValue("criteria", criteria);
            }}
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
