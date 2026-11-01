"use client";

import { DSButton, DSCard, DSStack, DSText } from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { ArchiveProjectModal } from "../archive-project-modal/archive-project-modal";

interface Props {
  project: Project;
}

export const ArchiveProjectCard: FC<Props> = ({ project }) => {
  const { t } = useTranslation("projects");
  const [isModalOpened, setIsModalOpened] = useState(false);

  return (
    <DSCard title={t("settings.archive.title")}>
      <DSStack gap={3} align="start">
        <DSText color="muted">{t("settings.archive.description")}</DSText>
        <DSButton
          type="danger"
          icon="archive"
          onClick={() => {
            setIsModalOpened(true);
          }}
        >
          {t("settings.archive.action")}
        </DSButton>
      </DSStack>
      <ArchiveProjectModal
        target={{ project, mode: "archive" }}
        isOpened={isModalOpened}
        onClose={() => {
          setIsModalOpened(false);
        }}
      />
    </DSCard>
  );
};
