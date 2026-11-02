import type { components } from "@/lib/api/openapi.type";

export type JunitImport = components["schemas"]["JunitImportResponse"];

export type UnmappedTest = components["schemas"]["UnmappedTestResponse"];

export type UnmappedTestReason = components["schemas"]["UnmappedTestReason"];

export type JunitImportFormFields =
  components["schemas"]["Body_import_junit_run_api_projects__project_key__runs_import_post"];

export interface JunitImportRequest {
  file: File;
  environment: string;
  suite: string | null;
}
