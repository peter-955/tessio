import type { SuiteFilterValues } from "../typing/types/suite-filter-values.type";
import type { SuiteFormValues } from "../typing/types/suite-form-values.type";
import type {
  AddSuiteCasesByFilterRequest,
  CreateSuiteRequest,
  SuiteDetail,
  UpdateSuiteRequest,
} from "../typing/types/suite.type";

const toDescription = (value: string): string | null => {
  const description = value.trim();

  return description === "" ? null : description;
};

export const buildSuiteFormValues = (suite: SuiteDetail | null): SuiteFormValues => {
  return { name: suite?.name ?? "", description: suite?.description ?? "" };
};

export const buildCreateSuiteRequest = (values: SuiteFormValues): CreateSuiteRequest => {
  return { name: values.name.trim(), description: toDescription(values.description) };
};

export const buildUpdateSuiteRequest = (
  values: SuiteFormValues,
  suite: SuiteDetail,
): UpdateSuiteRequest => {
  const name = values.name.trim();
  const description = toDescription(values.description);

  return {
    ...(name === suite.name ? {} : { name }),
    ...(description === suite.description ? {} : { description }),
  };
};

export const checkHasSuiteFilter = (values: SuiteFilterValues): boolean => {
  return (
    values.labels.length > 0 ||
    values.priorities.length > 0 ||
    values.storyKey !== null ||
    values.sprintId !== null
  );
};

export const buildSuiteFilterRequest = (
  values: SuiteFilterValues,
): AddSuiteCasesByFilterRequest => {
  return {
    ...(values.labels.length === 0 ? {} : { labels: values.labels }),
    ...(values.priorities.length === 0 ? {} : { priorities: values.priorities }),
    ...(values.storyKey === null ? {} : { storyKey: values.storyKey }),
    ...(values.sprintId === null ? {} : { sprintId: values.sprintId }),
  };
};
