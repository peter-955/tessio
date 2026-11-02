import type { DataRow } from "../typing/types/data-table.type";

const VALUE_SEPARATOR = " | ";

const LINE_SEPARATOR = "\n";

const readRowValues = (parameters: readonly string[], row: DataRow): string[] => {
  return parameters.map((parameter) => row[parameter] ?? "");
};

export const formatDataTableText = (
  parameters: readonly string[],
  dataRows: readonly DataRow[],
): string => {
  if (parameters.length === 0 && dataRows.length === 0) {
    return "";
  }

  const rowLines = dataRows.map((row, index) => {
    return `${index + 1}. ${readRowValues(parameters, row).join(VALUE_SEPARATOR)}`;
  });

  return [parameters.join(VALUE_SEPARATOR), ...rowLines].join(LINE_SEPARATOR);
};

export const checkIsSameDataTable = (
  first: { parameters: readonly string[]; dataRows: readonly DataRow[] },
  second: { parameters: readonly string[]; dataRows: readonly DataRow[] },
): boolean => {
  if (
    first.parameters.length !== second.parameters.length ||
    first.dataRows.length !== second.dataRows.length
  ) {
    return false;
  }

  if (first.parameters.some((parameter, index) => parameter !== second.parameters[index])) {
    return false;
  }

  return first.dataRows.every((row, index) => {
    const otherRow = second.dataRows[index] ?? {};
    const names = Object.keys(row);

    return (
      names.length === Object.keys(otherRow).length &&
      names.every((name) => row[name] === otherRow[name])
    );
  });
};
