import { SIGN_OFF_STATUSES } from "../typing/constants/story.constant";
import type { TestStatus } from "../typing/types/story.type";
import type { SignOffTestStatus } from "../typing/types/test-status-action.type";

export const checkIsSignOffStatus = (status: TestStatus): status is SignOffTestStatus => {
  return (SIGN_OFF_STATUSES as readonly TestStatus[]).includes(status);
};
