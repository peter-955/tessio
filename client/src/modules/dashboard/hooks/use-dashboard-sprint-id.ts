"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import {
  buildDashboardSearch,
  parseDashboardSprintId,
  readDashboardSearchParams,
} from "../utils/dashboard-search.util";

interface Result {
  sprintId: string | null;
  changeSprintId: (nextSprintId: string | null) => void;
}

export const useDashboardSprintId = (initialSprintId: string | null): Result => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const search = searchParams.toString();
  const [sprintId, setSprintId] = useState<string | null>(initialSprintId);
  const [syncedSearch, setSyncedSearch] = useState(search);

  if (search !== syncedSearch) {
    setSyncedSearch(search);
    const urlSprintId = parseDashboardSprintId(readDashboardSearchParams(searchParams));
    if (urlSprintId !== sprintId) {
      setSprintId(urlSprintId);
    }
  }

  const changeSprintId = (nextSprintId: string | null): void => {
    setSprintId(nextSprintId);
    router.replace(`${pathname}${buildDashboardSearch(nextSprintId)}`, { scroll: false });
  };

  return { sprintId, changeSprintId };
};
