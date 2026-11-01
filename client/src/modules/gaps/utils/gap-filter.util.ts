import type { Gap, GapStatusFilter } from "../typing/types/gap.type";

export const filterGapsByStatus = (gaps: Gap[], filter: GapStatusFilter): Gap[] => {
  if (filter === "all") {
    return gaps;
  }

  return gaps.filter((gap) => {
    return gap.status === filter;
  });
};

export const countOpenGaps = (gaps: Gap[]): number => {
  return filterGapsByStatus(gaps, "open").length;
};

export const countGapsByFilter = (gaps: Gap[]): Record<GapStatusFilter, number> => {
  const openCount = countOpenGaps(gaps);

  return { open: openCount, resolved: gaps.length - openCount, all: gaps.length };
};
