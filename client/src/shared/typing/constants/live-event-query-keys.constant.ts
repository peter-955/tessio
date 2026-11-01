import { GET_DASHBOARD_KEY } from "@/modules/dashboard/hooks/queries/use-get-dashboard";
import { GET_MY_WORK_KEY } from "@/modules/dashboard/hooks/queries/use-get-my-work";
import { GET_RECENT_RUNS_KEY } from "@/modules/dashboard/hooks/queries/use-get-recent-runs";
import { GET_FAILURE_KEY } from "@/modules/failures/hooks/queries/use-get-failure";
import { GET_FAILURE_RUN_KEY } from "@/modules/failures/hooks/queries/use-get-failure-run";
import { GET_FAILURES_KEY } from "@/modules/failures/hooks/queries/use-get-failures";
import { GET_GAP_INBOX_KEY } from "@/modules/gaps/hooks/queries/use-get-gap-inbox";
import { GET_STORY_GAPS_KEY } from "@/modules/gaps/hooks/queries/use-get-story-gaps";
import { GET_MANUAL_RUN_KEY } from "@/modules/manual-run/hooks/queries/use-get-manual-run";
import { GET_READY_TEST_CASES_KEY } from "@/modules/manual-run/hooks/queries/use-get-ready-test-cases";
import { GET_RUN_STORIES_KEY } from "@/modules/manual-run/hooks/queries/use-get-run-stories";
import { GET_NOTIFICATIONS_KEY } from "@/modules/notifications/hooks/queries/use-get-notifications";
import { GET_UNREAD_NOTIFICATION_COUNT_KEY } from "@/modules/notifications/hooks/queries/use-get-unread-notification-count";
import { GET_MEMBER_CANDIDATES_KEY } from "@/modules/projects/hooks/queries/use-get-member-candidates";
import { GET_RUN_KEY } from "@/modules/runs/hooks/queries/use-get-run";
import { GET_RUNS_KEY } from "@/modules/runs/hooks/queries/use-get-runs";
import { GET_SPRINT_KEY } from "@/modules/sprints/hooks/queries/use-get-sprint";
import { GET_SPRINTS_KEY } from "@/modules/sprints/hooks/queries/use-get-sprints";
import { GET_STORIES_KEY } from "@/modules/stories/hooks/queries/use-get-stories";
import { GET_STORY_KEY } from "@/modules/stories/hooks/queries/use-get-story";
import { GET_STORY_PROGRESS_KEY } from "@/modules/stories/hooks/queries/use-get-story-progress";
import { GET_SYNC_STATUS_KEY } from "@/modules/stories/hooks/queries/use-get-sync-status";
import { GET_CASE_LATEST_RESULTS_KEY } from "@/modules/test-cases/hooks/queries/use-get-case-latest-results";
import { GET_TEST_CASE_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-case";
import { GET_TEST_CASE_VERSIONS_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-case-versions";
import { GET_TEST_CASES_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-cases";
import { GET_TEST_FILE_VERSIONS_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-file-versions";
import { GET_TRACEABILITY_KEY } from "@/modules/traceability/hooks/queries/use-get-traceability";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { GET_PROJECT_MEMBERS_KEY } from "@/shared/hooks/queries/use-get-project-members";
import { GET_PROJECTS_KEY } from "@/shared/hooks/queries/use-get-projects";
import { LiveEventType } from "../enums/live-event-type.enum";

export const LIVE_EVENT_QUERY_KEYS: Record<LiveEventType, readonly string[]> = {
  [LiveEventType.RUN_STARTED]: [
    GET_RUNS_KEY,
    GET_RUN_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_RECENT_RUNS_KEY,
  ],
  [LiveEventType.RUN_CASE_RECORDED]: [
    GET_RUNS_KEY,
    GET_RUN_KEY,
    GET_FAILURES_KEY,
    GET_FAILURE_KEY,
    GET_FAILURE_RUN_KEY,
    GET_TRACEABILITY_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_CASE_LATEST_RESULTS_KEY,
    GET_RECENT_RUNS_KEY,
    GET_MANUAL_RUN_KEY,
  ],
  [LiveEventType.RUN_FINISHED]: [
    GET_RUNS_KEY,
    GET_RUN_KEY,
    GET_FAILURES_KEY,
    GET_FAILURE_KEY,
    GET_FAILURE_RUN_KEY,
    GET_TRACEABILITY_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_CASE_LATEST_RESULTS_KEY,
    GET_RECENT_RUNS_KEY,
    GET_DASHBOARD_KEY,
    GET_MY_WORK_KEY,
    GET_MANUAL_RUN_KEY,
  ],
  [LiveEventType.JIRA_SYNC_STARTED]: [GET_SYNC_STATUS_KEY],
  [LiveEventType.JIRA_SYNC_FINISHED]: [
    GET_SYNC_STATUS_KEY,
    GET_SPRINTS_KEY,
    GET_SPRINT_KEY,
    GET_STORIES_KEY,
    GET_STORY_KEY,
    GET_TRACEABILITY_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_DASHBOARD_KEY,
    GET_MY_WORK_KEY,
    GET_RUN_STORIES_KEY,
  ],
  [LiveEventType.JIRA_SYNC_FAILED]: [GET_SYNC_STATUS_KEY],
  [LiveEventType.NOTIFICATION_CREATED]: [GET_NOTIFICATIONS_KEY, GET_UNREAD_NOTIFICATION_COUNT_KEY],
  [LiveEventType.PROJECT_MEMBERS_CHANGED]: [
    GET_PROJECT_MEMBERS_KEY,
    GET_PROJECT_KEY,
    GET_PROJECTS_KEY,
    GET_MEMBER_CANDIDATES_KEY,
  ],
  [LiveEventType.GAP_CHANGED]: [
    GET_STORY_GAPS_KEY,
    GET_GAP_INBOX_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_DASHBOARD_KEY,
    GET_MY_WORK_KEY,
  ],
  [LiveEventType.FAILURE_CHANGED]: [
    GET_FAILURES_KEY,
    GET_FAILURE_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_DASHBOARD_KEY,
    GET_MY_WORK_KEY,
  ],
  [LiveEventType.TEST_CASE_CHANGED]: [
    GET_TEST_CASES_KEY,
    GET_TEST_CASE_KEY,
    GET_TEST_CASE_VERSIONS_KEY,
    GET_TEST_FILE_VERSIONS_KEY,
    GET_TRACEABILITY_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_CASE_LATEST_RESULTS_KEY,
    GET_DASHBOARD_KEY,
    GET_MY_WORK_KEY,
    GET_READY_TEST_CASES_KEY,
  ],
  [LiveEventType.STORY_CHANGED]: [
    GET_STORIES_KEY,
    GET_STORY_KEY,
    GET_TRACEABILITY_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_DASHBOARD_KEY,
    GET_RUN_STORIES_KEY,
  ],
};
