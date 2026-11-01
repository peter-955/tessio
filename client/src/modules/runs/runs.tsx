"use client";

import { DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { RunList } from "./components/run-list/run-list";
import { RunsFilters } from "./components/runs-filters/runs-filters";
import type { RunFilters } from "./typing/types/run.type";
import {
  EMPTY_RUN_FILTERS,
  buildRunFiltersSearch,
  parseRunFilters,
  readRunSearchParams,
} from "./utils/run-filters.util";

interface Props {
  initialFilters: RunFilters;
  actions?: ReactNode;
}

export const RunsPage: FC<Props> = ({ initialFilters, actions }) => {
  const { t } = useTranslation("runs");
  const router = useRouter();
  const pathname = usePathname();
  const project = useCurrentProject();
  const searchParams = useSearchParams();
  const search = searchParams.toString();
  const [filters, setFilters] = useState<RunFilters>(initialFilters);
  const [syncedSearch, setSyncedSearch] = useState(search);

  if (search !== syncedSearch) {
    setSyncedSearch(search);
    const urlFilters = parseRunFilters(readRunSearchParams(searchParams));
    if (buildRunFiltersSearch(urlFilters) !== buildRunFiltersSearch(filters)) {
      setFilters(urlFilters);
    }
  }

  const handleFiltersChange = (nextFilters: RunFilters): void => {
    setFilters(nextFilters);
    router.replace(`${pathname}${buildRunFiltersSearch(nextFilters)}`, { scroll: false });
  };

  return (
    <>
      <DSPageHeader title={t("title")} description={t("description")} actions={actions} />
      <RunsFilters projectKey={project.key} filters={filters} onChange={handleFiltersChange} />
      <RunList
        projectKey={project.key}
        filters={filters}
        onClearFilters={() => {
          handleFiltersChange(EMPTY_RUN_FILTERS);
        }}
      />
    </>
  );
};
