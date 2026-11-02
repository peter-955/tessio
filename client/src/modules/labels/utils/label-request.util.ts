import { DEFAULT_LABEL_COLOR } from "../typing/constants/label.constant";
import type { LabelFormValues } from "../typing/types/label-form-values.type";
import type { CreateLabelRequest, Label, UpdateLabelRequest } from "../typing/types/label.type";

export const buildLabelFormValues = (label: Label | null): LabelFormValues => {
  return { name: label?.name ?? "", color: label?.color ?? DEFAULT_LABEL_COLOR };
};

export const buildCreateLabelRequest = (values: LabelFormValues): CreateLabelRequest => {
  return { name: values.name.trim(), color: values.color };
};

export const buildUpdateLabelRequest = (
  values: LabelFormValues,
  label: Label,
): UpdateLabelRequest => {
  const name = values.name.trim();

  return {
    ...(name === label.name ? {} : { name }),
    ...(values.color === label.color ? {} : { color: values.color }),
  };
};
