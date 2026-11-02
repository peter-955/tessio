export type DataTableCellErrorKey = "required" | "invalidName" | "duplicateName" | "tooLong";

export type DataTableErrorKey =
  "tooManyParameters" | "tooManyRows" | "rowsWithoutParameters" | "parametersWithoutRows";

export interface DataTableErrors {
  parameters: Record<string, DataTableCellErrorKey>;
  values: Record<string, DataTableCellErrorKey>;
  table?: DataTableErrorKey;
}
