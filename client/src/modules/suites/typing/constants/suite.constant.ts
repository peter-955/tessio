import type { SuiteFilterValues } from "../types/suite-filter-values.type";
import type { SuiteFormValues } from "../types/suite-form-values.type";

export const MAX_SUITE_NAME_LENGTH = 120;

export const MAX_SUITE_DESCRIPTION_LENGTH = 2000;

export const MAX_SUITE_CASES = 1000;

export const MAX_FILTER_LABELS = 20;

export const RUN_SUITE_COMMAND_PREFIX = "/tessio:run-suite";

export const SUITE_PARAMETER = "suite";

export const SUITE_ID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const NOT_FOUND_STATUS = 404;

export const LOADING_ROW_COUNT = 5;

export const EMPTY_SUITE_FORM_VALUES: SuiteFormValues = { name: "", description: "" };

export const EMPTY_SUITE_FILTER_VALUES: SuiteFilterValues = {
  labels: [],
  priorities: [],
  storyKey: null,
  sprintId: null,
};

export const NO_STORY_GROUP_KEY = "no-story";
