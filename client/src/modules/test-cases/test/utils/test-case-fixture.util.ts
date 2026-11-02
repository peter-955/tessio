import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import type {
  AcceptanceCriterion,
  StoryDetail,
  StorySummary,
} from "@/modules/stories/typing/types/story.type";
import type {
  CaseImportPreviewItem,
  TestCaseDetail,
  TestCaseSummary,
  TestCaseVersion,
  TestFile,
  TestFileVersion,
} from "../../typing/types/test-case.type";

export const STORY_ID = "c1000000-0000-4000-8000-000000000001";

export const QC_USER_ID = "b1000000-0000-4000-8000-000000000001";

export const FORMER_USER_ID = "b1000000-0000-4000-8000-000000000009";

export const FIRST_CRITERION_ID = "d1000000-0000-4000-8000-000000000001";

export const SECOND_CRITERION_ID = "d1000000-0000-4000-8000-000000000002";

export const REMOVED_CRITERION_ID = "d1000000-0000-4000-8000-000000000003";

export const buildCriterion = (
  overrides: Partial<AcceptanceCriterion> = {},
): AcceptanceCriterion => {
  return {
    id: FIRST_CRITERION_ID,
    code: "AC1",
    position: 1,
    text: "Card payment succeeds",
    removedAt: null,
    isRemoved: false,
    ...overrides,
  };
};

export const STORY_CRITERIA: AcceptanceCriterion[] = [
  buildCriterion(),
  buildCriterion({
    id: SECOND_CRITERION_ID,
    code: "AC2",
    position: 2,
    text: "Declined card shows an error",
  }),
  buildCriterion({
    id: REMOVED_CRITERION_ID,
    code: "AC3",
    position: 3,
    text: "Old rule",
    isRemoved: true,
    removedAt: "2026-10-18T09:00:00Z",
  }),
];

export const buildStorySummary = (overrides: Partial<StorySummary> = {}): StorySummary => {
  return {
    id: STORY_ID,
    jiraKey: "SHOP-1",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-1",
    title: "Pay by card",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    source: "jira",
    testStatus: "not_started",
    sprintId: null,
    sprintName: null,
    criterionCount: 3,
    syncedAt: "2026-10-20T09:00:00Z",
    jiraMissingAt: null,
    ...overrides,
  };
};

export const buildStoryDetail = (overrides: Partial<StoryDetail> = {}): StoryDetail => {
  return {
    id: STORY_ID,
    jiraKey: "SHOP-1",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-1",
    title: "Pay by card",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    source: "jira",
    testStatus: "not_started",
    syncedAt: "2026-10-20T09:00:00Z",
    jiraMissingAt: null,
    description: null,
    sprint: null,
    criteria: STORY_CRITERIA,
    availableTestStatuses: [],
    testStatusChangedAt: null,
    jiraUpdatedAt: "2026-10-19T09:00:00Z",
    descriptionText: null,
    ...overrides,
  };
};

export const buildMember = (overrides: Partial<ProjectMember> = {}): ProjectMember => {
  return {
    userId: QC_USER_ID,
    name: "Quinn Tester",
    email: "quinn@example.test",
    userStatus: "active",
    role: "qc",
    addedAt: "2026-10-01T09:00:00Z",
    ...overrides,
  };
};

export const buildTestCaseSummary = (overrides: Partial<TestCaseSummary> = {}): TestCaseSummary => {
  return {
    id: "e1000000-0000-4000-8000-000000000001",
    code: "TC-1",
    storyId: STORY_ID,
    storyKey: "SHOP-1",
    title: "Pay with a valid card",
    priority: "high",
    status: "draft",
    currentVersionId: "a2000000-0000-4000-8000-000000000002",
    currentVersionNumber: 2,
    stepCount: 3,
    criterionIds: [FIRST_CRITERION_ID],
    needsReview: false,
    needsReviewAt: null,
    lastSavedAt: "2026-10-21T09:00:00Z",
    labels: [],
    isFlaky: false,
    flakyScore: 0,
    isDisagreeing: false,
    isQuarantined: false,
    quarantinedAt: null,
    ...overrides,
  };
};

export const buildTestCaseVersion = (overrides: Partial<TestCaseVersion> = {}): TestCaseVersion => {
  return {
    id: "a2000000-0000-4000-8000-000000000002",
    number: 2,
    title: "Pay with a valid card",
    priority: "high",
    businessValue: "Customers can pay",
    preconditions: null,
    steps: [
      { order: 1, action: "Open the cart", expected: null, sharedStepKey: null },
      {
        order: 2,
        action: "Pay as {{data.username}}",
        expected: "The order is paid",
        sharedStepKey: null,
      },
    ],
    criterionIds: [FIRST_CRITERION_ID],
    dataKeys: ["username"],
    fileVersionIds: [],
    createdBy: QC_USER_ID,
    createdAt: "2026-10-21T09:00:00Z",
    parameters: [],
    dataRows: [],
    ...overrides,
  };
};

export const buildTestFileVersion = (overrides: Partial<TestFileVersion> = {}): TestFileVersion => {
  return {
    id: "a3000000-0000-4000-8000-000000000001",
    number: 1,
    storedFileId: "f2000000-0000-4000-8000-000000000001",
    fileName: "avatar.png",
    contentType: "image/png",
    size: 2048,
    createdBy: QC_USER_ID,
    createdAt: "2026-10-21T09:00:00Z",
    ...overrides,
  };
};

export const buildTestFile = (overrides: Partial<TestFile> = {}): TestFile => {
  return {
    id: "a4000000-0000-4000-8000-000000000001",
    key: "avatar",
    currentVersion: buildTestFileVersion(),
    versionCount: 1,
    ...overrides,
  };
};

export const buildTestCaseDetail = (overrides: Partial<TestCaseDetail> = {}): TestCaseDetail => {
  return {
    id: "e1000000-0000-4000-8000-000000000001",
    code: "TC-1",
    story: { id: STORY_ID, jiraKey: "SHOP-1", title: "Pay by card" },
    title: "Pay with a valid card",
    priority: "high",
    status: "draft",
    statusChangedAt: null,
    currentVersion: buildTestCaseVersion(),
    criteria: [
      { id: FIRST_CRITERION_ID, code: "AC1", text: "Card payment succeeds", isRemoved: false },
    ],
    files: [],
    unknownReferences: [],
    needsReview: false,
    needsReviewCriterionIds: [],
    needsReviewAt: null,
    reviewedAt: null,
    reviewedBy: null,
    createdBy: QC_USER_ID,
    createdAt: "2026-10-20T09:00:00Z",
    labels: [],
    isFlaky: false,
    flakyScore: 0,
    isDisagreeing: false,
    isQuarantined: false,
    quarantinedAt: null,
    flakySince: null,
    disagreedAt: null,
    quarantinedBy: null,
    quarantineReason: null,
    ...overrides,
  };
};

export const buildImportItem = (
  overrides: Partial<CaseImportPreviewItem> = {},
): CaseImportPreviewItem => {
  return {
    index: 0,
    location: "SHOP-1!A2",
    storyKey: "SHOP-1",
    title: "Pay with a valid card",
    priority: "medium",
    stepCount: 2,
    criterionCodes: ["AC1"],
    unknownCriterionCodes: [],
    isDuplicate: false,
    problem: null,
    ...overrides,
  };
};
