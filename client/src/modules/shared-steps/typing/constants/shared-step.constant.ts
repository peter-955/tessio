import type { SharedStepFormValues } from "../types/shared-step-form-values.type";

export const SHARED_STEP_KEY_PATTERN = /^[a-z][a-z0-9_]{0,63}$/;

export const MAX_SHARED_STEP_KEY_LENGTH = 64;

export const MAX_SHARED_STEP_TITLE_LENGTH = 200;

export const MAX_SHARED_STEP_ACTIONS = 50;

export const MAX_SHARED_STEP_TEXT_LENGTH = 5000;

export const NOT_FOUND_STATUS = 404;

export const LOADING_ROW_COUNT = 5;

export const LOADING_LINE_COUNT = 8;

export const EMPTY_SHARED_STEP_FORM_VALUES: Omit<SharedStepFormValues, "steps"> = {
  key: "",
  title: "",
};
