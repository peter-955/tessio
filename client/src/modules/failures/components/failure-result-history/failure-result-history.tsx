"use client";

import { DSBadge, DSCard, DSTable, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { formatIterationNumber } from "@/modules/data-rows/utils/parameter-text.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useFormatDuration } from "@/shared/hooks/use-format-duration";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { EMPTY_VALUE, RESULT_STATUS_COLORS } from "../../typing/constants/failure.constant";
import type { FailureResult } from "../../typing/types/failure.type";
import { buildFailureRunPath } from "../../utils/failure-path.util";

interface Props {
  results: FailureResult[];
}

export const FailureResultHistory: FC<Props> = ({ results }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const formatDuration = useFormatDuration();
  const hasIterations = results.some((result) => result.iteration !== null);

  return (
    <DSCard title={t("history.title")}>
      {results.length === 0 ? (
        <DSText size="sm" color="muted">
          {t("history.empty")}
        </DSText>
      ) : (
        <DSTable label={t("history.title")}>
          <thead>
            <tr>
              <th scope="col">{t("columns.run")}</th>
              <th scope="col">{t("columns.result")}</th>
              {hasIterations && <th scope="col">{t("columns.iteration")}</th>}
              <th scope="col">{t("columns.executor")}</th>
              <th scope="col">{t("columns.duration")}</th>
              <th scope="col">{t("columns.startedBy")}</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result) => {
              return (
                <tr key={result.caseResultId}>
                  <td>
                    <Link href={buildFailureRunPath(project.key, result.runId)}>
                      {formatDate(result.recordedAt)}
                    </Link>
                  </td>
                  <td>
                    <DSBadge color={RESULT_STATUS_COLORS[result.status]}>
                      {t(`result.${result.status}`)}
                    </DSBadge>
                  </td>
                  {hasIterations && (
                    <td>
                      {result.iteration === null
                        ? EMPTY_VALUE
                        : formatIterationNumber(result.iteration)}
                    </td>
                  )}
                  <td>{t(`executor.${result.runExecutor}`)}</td>
                  <td>
                    {result.durationMs === null ? EMPTY_VALUE : formatDuration(result.durationMs)}
                  </td>
                  <td>{result.startedByName}</td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      )}
    </DSCard>
  );
};
