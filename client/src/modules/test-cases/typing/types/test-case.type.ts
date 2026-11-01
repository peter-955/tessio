import type { components } from "@/lib/api/openapi.type";

export type TestCaseSummary = components["schemas"]["TestCaseSummaryResponse"];

export type TestCaseDetail = components["schemas"]["TestCaseDetailResponse"];

export type TestCaseVersion = components["schemas"]["TestCaseVersionResponse"];

export type TestStep = components["schemas"]["TestStepResponse"];

export type TestStepRequest = components["schemas"]["TestStepRequest"];

export type LinkedCriterion = components["schemas"]["LinkedCriterionResponse"];

export type TestFile = components["schemas"]["TestFileResponse"];

export type TestFileVersion = components["schemas"]["TestFileVersionResponse"];

export type TestCaseStatus = components["schemas"]["TestCaseStatus"];

export type TestCasePriority = components["schemas"]["TestCasePriority"];

export type CreateTestCaseRequest = components["schemas"]["CreateTestCaseRequest"];

export type UpdateTestCaseRequest = components["schemas"]["UpdateTestCaseRequest"];

export type AttachTestFileRequest = components["schemas"]["AttachTestFileRequest"];

export type CaseImportPreviewRequest = components["schemas"]["CaseImportPreviewRequest"];

export type CaseImportCommitRequest = components["schemas"]["CaseImportCommitRequest"];

export type CaseImportPreview = components["schemas"]["CaseImportPreviewResponse"];

export type CaseImportPreviewItem = components["schemas"]["CaseImportPreviewItemResponse"];

export type CaseImportSkip = components["schemas"]["CaseImportSkipResponse"];

export type CaseImportResult = components["schemas"]["CaseImportResultResponse"];

export type CaseImportProblem = components["schemas"]["CaseImportProblem"];

export type CaseImportSkipReason = components["schemas"]["CaseImportSkipReason"];

export type DownloadLink = components["schemas"]["DownloadLinkResponse"];
