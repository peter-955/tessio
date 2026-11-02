import { PARAMETER_REFERENCE_PATTERN } from "../typing/constants/data-table.constant";
import type { DataRow } from "../typing/types/data-table.type";

export const fillParameters = (text: string, values: DataRow): string => {
  return text.replace(PARAMETER_REFERENCE_PATTERN, (reference, name: string) => {
    return Object.hasOwn(values, name) ? (values[name] ?? reference) : reference;
  });
};

export const fillOptionalParameters = (text: string | null, values: DataRow): string | null => {
  return text === null ? null : fillParameters(text, values);
};

export const formatIterationNumber = (iteration: number): number => {
  return iteration + 1;
};
