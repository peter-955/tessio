"use client";

import { DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { FailureFilters } from "./components/failure-filters/failure-filters";
import { FailureList } from "./components/failure-list/failure-list";
import type { FailureFilters as FailureFilterValues } from "./typing/types/failure-filters.type";
import {
  buildFailureFiltersSearch,
  clearFailureFilters,
  parseFailureFilters,
  readFailureSearchParams,
} from "./utils/failure-filters.util";

interface Props {
  initialFilters: FailureFilterValues;
}

export const FailuresPage: FC<Props> = ({ initialFilters }) => {
  const { t } = useTranslation("failures");
  const router = useRouter();
  const pathname = usePathname();
  const project = useCurrentProject();
  const searchParams = useSearchParams();
  const search = searchParams.toString();
  const [filters, setFilters] = useState<FailureFilterValues>(initialFilters);
  const [syncedSearch, setSyncedSearch] = useState(search);

  if (search !== syncedSearch) {
    setSyncedSearch(search);
    const urlFilters = parseFailureFilters(readFailureSearchParams(searchParams));
    if (buildFailureFiltersSearch(urlFilters) !== buildFailureFiltersSearch(filters)) {
      setFilters(urlFilters);
    }
  }

  const handleFiltersChange = (nextFilters: FailureFilterValues): void => {
    setFilters(nextFilters);
    router.replace(`${pathname}${buildFailureFiltersSearch(nextFilters)}`, { scroll: false });
  };

  return (
    <>
      <DSPageHeader title={t("title")} description={t("pageDescription")} />
      <FailureFilters filters={filters} onChange={handleFiltersChange} />
      <FailureList
        projectKey={project.key}
        filters={filters}
        onClearFilters={() => {
          handleFiltersChange(clearFailureFilters());
        }}
      />
    </>
  );
};
