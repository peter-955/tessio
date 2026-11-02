import type {
  ProjectMember,
  ProjectRole,
} from "@/components/project-context/typing/types/project.type";
import type { Gap } from "../../typing/types/gap.type";

export const CURRENT_USER_ID = "a1000000-0000-4000-8000-000000000001";

export const RAISER_ID = "a1000000-0000-4000-8000-000000000002";

export const ASSIGNEE_ID = "a1000000-0000-4000-8000-000000000003";

export const createGap = (overrides: Partial<Gap> = {}): Gap => {
  return {
    id: "b1000000-0000-4000-8000-000000000001",
    projectKey: "SHOP",
    projectName: "Shop",
    storyId: "c1000000-0000-4000-8000-000000000001",
    storyJiraKey: "SHOP-1",
    storyTitle: "Pay by card",
    targetType: "story",
    targetId: null,
    targetRef: null,
    type: "unclear_goal",
    dataScope: null,
    severity: "medium",
    question: "Which cards are accepted?",
    status: "open",
    assigneeId: ASSIGNEE_ID,
    assigneeName: "Bao Ba",
    assigneeStatus: "active",
    assigneeRole: null,
    raisedBy: RAISER_ID,
    raisedByName: "Quinn Qc",
    isRaisedViaClaude: false,
    answer: null,
    answeredBy: null,
    answeredByName: null,
    answeredAt: null,
    isAnsweredViaClaude: false,
    reopenedByName: null,
    reopenedAt: null,
    createdAt: "2026-10-30T09:00:00Z",
    ...overrides,
  };
};

export const createResolvedGap = (overrides: Partial<Gap> = {}): Gap => {
  return createGap({
    id: "b1000000-0000-4000-8000-000000000099",
    status: "resolved",
    question: "Is Amex accepted?",
    answer: "Yes, Amex is accepted.\nDiners is not.",
    answeredBy: ASSIGNEE_ID,
    answeredByName: "Bao Ba",
    answeredAt: "2026-10-31T10:00:00Z",
    ...overrides,
  });
};

export const createMember = (overrides: Partial<ProjectMember> = {}): ProjectMember => {
  return {
    userId: ASSIGNEE_ID,
    name: "Bao Ba",
    email: "bao@example.test",
    userStatus: "active",
    role: "ba",
    addedAt: "2026-10-01T09:00:00Z",
    ...overrides,
  };
};

export const ROLE_LABELS: Record<Exclude<ProjectRole, "viewer">, string> = {
  admin: "Admin",
  pm: "PM",
  ba: "BA",
  qc: "QC",
  dev: "Dev",
};
