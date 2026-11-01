export const computeRunDuration = (startedAt: string, finishedAt: string | null): number | null => {
  if (finishedAt === null) {
    return null;
  }

  return Math.max(0, new Date(finishedAt).getTime() - new Date(startedAt).getTime());
};
