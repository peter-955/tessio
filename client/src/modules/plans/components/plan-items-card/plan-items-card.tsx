"use client";

import { DSBadge, DSCard, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { PlanItem } from "../../typing/types/plan.type";
import { buildPlanSuitePath } from "../../utils/plan-path.util";
import styles from "./plan-items-card.module.scss";

interface Props {
  items: PlanItem[];
}

export const PlanItemsCard: FC<Props> = ({ items }) => {
  const { t } = useTranslation("plans");
  const project = useCurrentProject();

  const buildItemPath = (item: PlanItem): string | null => {
    if (item.kind === "suite" && item.suiteId !== null) {
      return buildPlanSuitePath(project.key, item.suiteId);
    }

    if (item.kind === "story" && item.storyJiraKey !== null) {
      return buildStoryPath(project.key, item.storyJiraKey);
    }

    return null;
  };

  return (
    <DSCard title={t("items.title")}>
      {items.length === 0 ? (
        <DSText size="sm" color="muted">
          {t("items.none")}
        </DSText>
      ) : (
        <ul className={styles.list}>
          {items.map((item) => {
            const path = buildItemPath(item);
            const name =
              item.kind === "story" && item.storyJiraKey !== null
                ? `${item.storyJiraKey} · ${item.name}`
                : item.name;

            return (
              <li key={`${item.kind}-${item.position}`} className={styles.item}>
                <DSBadge color={item.kind === "suite" ? "violet" : "blue"}>
                  {t(`items.kind.${item.kind}`)}
                </DSBadge>
                <span className={styles.name}>
                  {path === null ? name : <Link href={path}>{name}</Link>}
                </span>
                {item.archivedAt !== null && <DSBadge>{t("items.archivedBadge")}</DSBadge>}
                <DSText size="xs" color="muted" component="span">
                  {t("items.caseCount", { count: item.caseCount })}
                </DSText>
              </li>
            );
          })}
        </ul>
      )}
    </DSCard>
  );
};
