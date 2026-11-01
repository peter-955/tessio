"use client";

import { DSButtonLink, DSGroup } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { TestCaseFilters } from "./components/test-case-filters/test-case-filters";
import { TestCaseList } from "./components/test-case-list/test-case-list";
import styles from "./story-test-cases.module.scss";
import type { TestCaseFilters as TestCaseFilterValues } from "./typing/types/test-case-filters.type";
import { checkCanEditTestCases } from "./utils/test-case-capability.util";
import { clearTestCaseFilters, EMPTY_TEST_CASE_FILTERS } from "./utils/test-case-filters.util";
import { buildNewTestCasePath } from "./utils/test-case-path.util";

interface Props {
  jiraKey: string;
}

export const StoryTestCases: FC<Props> = ({ jiraKey }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const canEdit = checkCanEditTestCases(project);
  const [filters, setFilters] = useState<TestCaseFilterValues>({
    ...EMPTY_TEST_CASE_FILTERS,
    storyKey: jiraKey,
  });
  const storyFilters = filters.storyKey === jiraKey ? filters : { ...filters, storyKey: jiraKey };
  const newCaseLink = canEdit && (
    <DSButtonLink href={buildNewTestCasePath(project.key, jiraKey)} type="primary" icon="plus">
      {t("actions.new")}
    </DSButtonLink>
  );

  return (
    <>
      {newCaseLink && (
        <DSGroup justify="end" className={styles.actions}>
          {newCaseLink}
        </DSGroup>
      )}
      <TestCaseFilters filters={storyFilters} onChange={setFilters} isStoryFilterShown={false} />
      <TestCaseList
        projectKey={project.key}
        filters={storyFilters}
        isStoryColumnShown={false}
        emptyActions={newCaseLink}
        onClearFilters={() => {
          setFilters(clearTestCaseFilters(storyFilters, true));
        }}
      />
    </>
  );
};
