"use client";

import { useState } from "react";
import type { InsightsRange } from "../typing/types/insights-range.type";
import type { TrendGrouping } from "../typing/types/insights.type";
import { buildDefaultRange, buildSprintRange } from "../utils/insights-range.util";

interface FilterSprint {
  id: string;
  startAt: string | null;
  endAt: string | null;
}

interface Result {
  range: InsightsRange;
  groupBy: TrendGrouping;
  sprintId: string | null;
  changeFrom: (day: string | null) => void;
  changeTo: (day: string | null) => void;
  changeSprint: (sprint: FilterSprint | null) => void;
  changeGroupBy: (groupBy: TrendGrouping) => void;
}

export const useInsightsFilters = (): Result => {
  const [today] = useState(() => {
    return new Date();
  });
  const [range, setRange] = useState(() => {
    return buildDefaultRange(today);
  });
  const [groupBy, setGroupBy] = useState<TrendGrouping>("day");
  const [sprintId, setSprintId] = useState<string | null>(null);

  const changeFrom = (day: string | null): void => {
    if (day === null) {
      return;
    }
    setSprintId(null);
    setRange((current) => {
      return { ...current, from: day };
    });
  };

  const changeTo = (day: string | null): void => {
    if (day === null) {
      return;
    }
    setSprintId(null);
    setRange((current) => {
      return { ...current, to: day };
    });
  };

  const changeSprint = (sprint: FilterSprint | null): void => {
    if (sprint === null) {
      setSprintId(null);
      setRange(buildDefaultRange(today));
      return;
    }

    const sprintRange = buildSprintRange(sprint, today);
    if (sprintRange === null) {
      return;
    }
    setSprintId(sprint.id);
    setRange(sprintRange);
  };

  return {
    range,
    groupBy,
    sprintId,
    changeFrom,
    changeTo,
    changeSprint,
    changeGroupBy: setGroupBy,
  };
};
