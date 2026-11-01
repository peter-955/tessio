"use client";

import { DSButton, DSButtonLink, DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { ImportWizard } from "./components/import-wizard/import-wizard";
import { TestCaseFilters } from "./components/test-case-filters/test-case-filters";
import { TestCaseList } from "./components/test-case-list/test-case-list";
import type { TestCaseFilters as TestCaseFilterValues } from "./typing/types/test-case-filters.type";
import { checkCanEditTestCases } from "./utils/test-case-capability.util";
import {
  buildTestCaseFiltersSearch,
  clearTestCaseFilters,
  parseTestCaseFilters,
  readTestCaseSearchParams,
} from "./utils/test-case-filters.util";
import { buildNewTestCasePath } from "./utils/test-case-path.util";

interface Props {
  initialFilters: TestCaseFilterValues;
}

export const TestCasesPage: FC<Props> = ({ initialFilters }) => {
  const { t } = useTranslation("testCases");
  const router = useRouter();
  const pathname = usePathname();
  const project = useCurrentProject();
  const searchParams = useSearchParams();
  const search = searchParams.toString();
  const canEdit = checkCanEditTestCases(project);
  const [filters, setFilters] = useState<TestCaseFilterValues>(initialFilters);
  const [syncedSearch, setSyncedSearch] = useState(search);
  const [isImportOpened, setIsImportOpened] = useState(false);

  if (search !== syncedSearch) {
    setSyncedSearch(search);
    const urlFilters = parseTestCaseFilters(readTestCaseSearchParams(searchParams));
    if (buildTestCaseFiltersSearch(urlFilters) !== buildTestCaseFiltersSearch(filters)) {
      setFilters(urlFilters);
    }
  }

  const handleFiltersChange = (nextFilters: TestCaseFilterValues): void => {
    setFilters(nextFilters);
    router.replace(`${pathname}${buildTestCaseFiltersSearch(nextFilters)}`, { scroll: false });
  };

  const openImport = (): void => {
    setIsImportOpened(true);
  };

  const editorActions = canEdit && (
    <>
      <DSButton type="default" icon="upload" onClick={openImport}>
        {t("actions.import")}
      </DSButton>
      <DSButtonLink
        href={buildNewTestCasePath(project.key, filters.storyKey)}
        type="primary"
        icon="plus"
      >
        {t("actions.new")}
      </DSButtonLink>
    </>
  );

  return (
    <>
      <DSPageHeader title={t("title")} description={t("pageDescription")} actions={editorActions} />
      <TestCaseFilters filters={filters} onChange={handleFiltersChange} isStoryFilterShown />
      <TestCaseList
        projectKey={project.key}
        filters={filters}
        isStoryColumnShown
        emptyActions={editorActions}
        onClearFilters={() => {
          handleFiltersChange(clearTestCaseFilters(filters, false));
        }}
      />
      {isImportOpened && (
        <ImportWizard
          onClose={() => {
            setIsImportOpened(false);
          }}
        />
      )}
    </>
  );
};
