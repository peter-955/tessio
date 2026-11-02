import {
  MAX_DATA_ROWS,
  MAX_DATA_VALUE_LENGTH,
  MAX_PARAMETERS,
  PARAMETER_NAME_PATTERN,
} from "../typing/constants/data-table.constant";
import type {
  DataTableCellErrorKey,
  DataTableErrors,
} from "../typing/types/data-table-errors.type";
import type {
  DataParameter,
  DataRow,
  DataRowDraft,
  DataTableValues,
} from "../typing/types/data-table.type";

export const buildCellKey = (rowId: string, parameterId: string): string => {
  return `${rowId}:${parameterId}`;
};

export const createDataParameter = (name = ""): DataParameter => {
  return { id: crypto.randomUUID(), name };
};

export const createDataRow = (
  parameters: readonly DataParameter[],
  values: DataRow = {},
): DataRowDraft => {
  return {
    id: crypto.randomUUID(),
    values: Object.fromEntries(
      parameters.map((parameter) => [parameter.id, values[parameter.name] ?? ""]),
    ),
  };
};

export const createEmptyDataTable = (): DataTableValues => {
  return { parameters: [], rows: [] };
};

export const buildDataTableValues = (
  parameterNames: readonly string[],
  dataRows: readonly DataRow[],
): DataTableValues => {
  const parameters = parameterNames.map((name) => createDataParameter(name));

  return { parameters, rows: dataRows.map((row) => createDataRow(parameters, row)) };
};

export const addDataParameter = (table: DataTableValues): DataTableValues => {
  const parameter = createDataParameter();

  return {
    parameters: [...table.parameters, parameter],
    rows: table.rows.map((row) => ({ ...row, values: { ...row.values, [parameter.id]: "" } })),
  };
};

export const renameDataParameter = (
  table: DataTableValues,
  parameterId: string,
  name: string,
): DataTableValues => {
  return {
    ...table,
    parameters: table.parameters.map((parameter) => {
      return parameter.id === parameterId ? { ...parameter, name } : parameter;
    }),
  };
};

export const removeDataParameter = (
  table: DataTableValues,
  parameterId: string,
): DataTableValues => {
  const parameters = table.parameters.filter((parameter) => parameter.id !== parameterId);

  return {
    parameters,
    rows:
      parameters.length === 0
        ? []
        : table.rows.map((row) => {
            const values = { ...row.values };
            delete values[parameterId];

            return { ...row, values };
          }),
  };
};

export const addDataRow = (table: DataTableValues): DataTableValues => {
  return { ...table, rows: [...table.rows, createDataRow(table.parameters)] };
};

export const removeDataRow = (table: DataTableValues, rowId: string): DataTableValues => {
  return { ...table, rows: table.rows.filter((row) => row.id !== rowId) };
};

export const changeDataValue = (
  table: DataTableValues,
  rowId: string,
  parameterId: string,
  value: string,
): DataTableValues => {
  return {
    ...table,
    rows: table.rows.map((row) => {
      return row.id === rowId ? { ...row, values: { ...row.values, [parameterId]: value } } : row;
    }),
  };
};

export const listParameterNames = (table: DataTableValues): string[] => {
  return table.parameters.map((parameter) => parameter.name.trim());
};

export const buildDataRows = (table: DataTableValues): DataRow[] => {
  return table.rows.map((row) => {
    return Object.fromEntries(
      table.parameters.map((parameter) => [parameter.name.trim(), row.values[parameter.id] ?? ""]),
    );
  });
};

const findParameterError = (
  parameter: DataParameter,
  names: readonly string[],
): DataTableCellErrorKey | undefined => {
  const name = parameter.name.trim();
  if (name === "") {
    return "required";
  }

  if (!PARAMETER_NAME_PATTERN.test(name)) {
    return "invalidName";
  }

  const foldedName = name.toLowerCase();
  const sameNameCount = names.filter((candidate) => candidate.toLowerCase() === foldedName).length;

  return sameNameCount > 1 ? "duplicateName" : undefined;
};

export const validateDataTable = (table: DataTableValues): DataTableErrors => {
  const names = listParameterNames(table);
  const parameters: Record<string, DataTableCellErrorKey> = {};
  const values: Record<string, DataTableCellErrorKey> = {};

  for (const parameter of table.parameters) {
    const error = findParameterError(parameter, names);
    if (error !== undefined) {
      parameters[parameter.id] = error;
    }
  }

  for (const row of table.rows) {
    for (const parameter of table.parameters) {
      if ((row.values[parameter.id] ?? "").length > MAX_DATA_VALUE_LENGTH) {
        values[buildCellKey(row.id, parameter.id)] = "tooLong";
      }
    }
  }

  const tableError =
    table.parameters.length > MAX_PARAMETERS
      ? "tooManyParameters"
      : table.rows.length > MAX_DATA_ROWS
        ? "tooManyRows"
        : table.rows.length > 0 && table.parameters.length === 0
          ? "rowsWithoutParameters"
          : table.parameters.length > 0 && table.rows.length === 0
            ? "parametersWithoutRows"
            : undefined;

  return tableError === undefined
    ? { parameters, values }
    : { parameters, values, table: tableError };
};

export const checkHasDataTableErrors = (errors: DataTableErrors): boolean => {
  return (
    errors.table !== undefined ||
    Object.keys(errors.parameters).length > 0 ||
    Object.keys(errors.values).length > 0
  );
};

export const checkAreParametersEqual = (
  table: DataTableValues,
  parameterNames: readonly string[],
): boolean => {
  const names = listParameterNames(table);

  return (
    names.length === parameterNames.length &&
    names.every((name, index) => name === parameterNames[index])
  );
};

export const checkAreDataRowsEqual = (
  table: DataTableValues,
  dataRows: readonly DataRow[],
): boolean => {
  const rows = buildDataRows(table);

  return (
    rows.length === dataRows.length &&
    rows.every((row, index) => {
      const savedRow = dataRows[index] ?? {};
      const names = Object.keys(row);

      return (
        names.length === Object.keys(savedRow).length &&
        names.every((name) => row[name] === savedRow[name])
      );
    })
  );
};
