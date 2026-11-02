export const parseVersionNumber = (value: string | null): number | null => {
  if (value === null || !/^[1-9]\d*$/.test(value)) {
    return null;
  }

  return Number(value);
};
