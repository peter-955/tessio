import { PROJECT_SCOPE_ID } from "../typing/constants/test-data.constant";
import type { DataItemFormValues } from "../typing/types/data-item-form-values.type";
import type { DataItemModalState } from "../typing/types/data-item-modal-state.type";
import type {
  CreateDataItemRequest,
  DataItem,
  DataItemKind,
  UpdateDataItemRequest,
} from "../typing/types/data-item.type";
import { resolveDataItemScopeId } from "./build-data-grid-rows.util";

export const buildDataItemFormValues = (state: DataItemModalState): DataItemFormValues => {
  if (state.mode === "edit") {
    const { item } = state;

    return {
      key: item.key,
      kind: item.kind,
      scopeId: resolveDataItemScopeId(item),
      value: item.kind === "secret" ? "" : (item.value ?? ""),
    };
  }

  return {
    key: state.preset?.key ?? "",
    kind: state.preset?.kind ?? "variable",
    scopeId: state.preset?.scopeId ?? PROJECT_SCOPE_ID,
    value: "",
  };
};

export const isKeepingSecretValue = (item: DataItem | null, kind: DataItemKind): boolean => {
  return item?.kind === "secret" && kind === "secret";
};

export const buildCreateDataItemRequest = (values: DataItemFormValues): CreateDataItemRequest => {
  return {
    key: values.key.trim(),
    kind: values.kind,
    value: values.value,
    environmentId: values.scopeId === PROJECT_SCOPE_ID ? null : values.scopeId,
  };
};

export const buildUpdateDataItemRequest = (
  values: DataItemFormValues,
  item: DataItem,
): UpdateDataItemRequest => {
  const isKeepingValue = values.value === "" && isKeepingSecretValue(item, values.kind);

  return {
    key: values.key.trim(),
    kind: values.kind,
    value: isKeepingValue ? null : values.value,
  };
};
