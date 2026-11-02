"use client";

import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { SessionGuardContext } from "@/components/session-guard/session-guard.context";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { use } from "react";
import { checkIsAuthorReviewBlocked } from "../utils/review-comment.util";

export const useIsAuthorReviewBlocked = (
  detail: Pick<TestCaseDetail, "currentVersion">,
): boolean => {
  const project = useCurrentProject();
  const currentUser = use(SessionGuardContext);

  return checkIsAuthorReviewBlocked(project, detail, currentUser?.id ?? null);
};
