"use client";

import { DSTable } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { Sprint } from "../../typing/types/sprint.type";
import { buildSprintPath } from "../../utils/sprint-path.util";
import { SprintDates } from "../sprint-dates/sprint-dates";
import { SprintStateBadge } from "../sprint-state-badge/sprint-state-badge";
import styles from "./sprint-table.module.scss";

interface Props {
  projectKey: string;
  sprints: Sprint[];
}

export const SprintTable: FC<Props> = ({ projectKey, sprints }) => {
  const { t } = useTranslation("sprints");

  return (
    <DSTable label={t("title")}>
      <thead>
        <tr>
          <th scope="col">{t("columns.name")}</th>
          <th scope="col">{t("columns.state")}</th>
          <th scope="col">{t("columns.dates")}</th>
          <th scope="col" className={styles.numeric}>
            {t("columns.stories")}
          </th>
        </tr>
      </thead>
      <tbody>
        {sprints.map((sprint) => {
          return (
            <tr key={sprint.id}>
              <th scope="row">
                <Link href={buildSprintPath(projectKey, sprint.id)}>{sprint.name}</Link>
              </th>
              <td>
                <SprintStateBadge state={sprint.state} />
              </td>
              <td>
                <SprintDates sprint={sprint} />
              </td>
              <td className={styles.numeric}>{sprint.storyCount}</td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
