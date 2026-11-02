export interface DataParameter {
  id: string;
  name: string;
}

export interface DataRowDraft {
  id: string;
  values: Record<string, string>;
}

export interface DataTableValues {
  parameters: DataParameter[];
  rows: DataRowDraft[];
}

export type DataRow = Record<string, string>;
