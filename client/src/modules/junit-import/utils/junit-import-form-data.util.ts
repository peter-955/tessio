import { JUNIT_FORM_FIELDS } from "../typing/constants/junit-import.constant";
import type { JunitImportRequest } from "../typing/types/junit-import.type";

export const buildJunitImportFormData = ({
  file,
  environment,
  suite,
}: JunitImportRequest): FormData => {
  const formData = new FormData();
  formData.append(JUNIT_FORM_FIELDS.file, file, file.name);
  formData.append(JUNIT_FORM_FIELDS.environment, environment);
  if (suite !== null) {
    formData.append(JUNIT_FORM_FIELDS.suite, suite);
  }

  return formData;
};
