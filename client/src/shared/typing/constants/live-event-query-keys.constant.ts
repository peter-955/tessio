import { GET_REVIEW_COMMENTS_KEY } from "@/modules/case-review/hooks/queries/use-get-review-comments";
import { GET_CHAT_CHANNELS_KEY } from "@/modules/chat-channels/hooks/queries/use-get-chat-channels";
import { GET_DASHBOARD_KEY } from "@/modules/dashboard/hooks/queries/use-get-dashboard";
import { GET_MY_WORK_KEY } from "@/modules/dashboard/hooks/queries/use-get-my-work";
import { GET_RECENT_RUNS_KEY } from "@/modules/dashboard/hooks/queries/use-get-recent-runs";
import { GET_FAILURE_KEY } from "@/modules/failures/hooks/queries/use-get-failure";
import { GET_FAILURE_RUN_KEY } from "@/modules/failures/hooks/queries/use-get-failure-run";
import { GET_FAILURES_KEY } from "@/modules/failures/hooks/queries/use-get-failures";
import { GET_GAP_INBOX_KEY } from "@/modules/gaps/hooks/queries/use-get-gap-inbox";
import { GET_STORY_GAPS_KEY } from "@/modules/gaps/hooks/queries/use-get-story-gaps";
import { GET_FLAKY_CASES_KEY } from "@/modules/insights/hooks/queries/use-get-flaky-cases";
import { GET_INSIGHT_TRENDS_KEY } from "@/modules/insights/hooks/queries/use-get-insight-trends";
import { GET_LABEL_COVERAGE_KEY } from "@/modules/insights/hooks/queries/use-get-label-coverage";
import { GET_SPRINT_COVERAGE_KEY } from "@/modules/insights/hooks/queries/use-get-sprint-coverage";
import { GET_TOKEN_USAGE_KEY } from "@/modules/insights/hooks/queries/use-get-token-usage";
import { GET_TOP_FAILING_CASES_KEY } from "@/modules/insights/hooks/queries/use-get-top-failing-cases";
import { GET_LABELS_KEY } from "@/modules/labels/hooks/queries/use-get-labels";
import { GET_MANUAL_RUN_KEY } from "@/modules/manual-run/hooks/queries/use-get-manual-run";
import { GET_READY_TEST_CASES_KEY } from "@/modules/manual-run/hooks/queries/use-get-ready-test-cases";
import { GET_RUN_STORIES_KEY } from "@/modules/manual-run/hooks/queries/use-get-run-stories";
import { GET_NOTIFICATIONS_KEY } from "@/modules/notifications/hooks/queries/use-get-notifications";
import { GET_UNREAD_NOTIFICATION_COUNT_KEY } from "@/modules/notifications/hooks/queries/use-get-unread-notification-count";
import { GET_PLAN_KEY } from "@/modules/plans/hooks/queries/use-get-plan";
import { GET_PLANS_KEY } from "@/modules/plans/hooks/queries/use-get-plans";
import { GET_MEMBER_CANDIDATES_KEY } from "@/modules/projects/hooks/queries/use-get-member-candidates";
import { GET_REPORT_LINK_KEY } from "@/modules/reports/hooks/queries/use-get-report-link";
import { GET_RUN_LOG_KEY } from "@/modules/run-log/hooks/queries/use-get-run-log";
import { GET_RUN_KEY } from "@/modules/runs/hooks/queries/use-get-run";
import { GET_RUNS_KEY } from "@/modules/runs/hooks/queries/use-get-runs";
import { GET_SHARED_STEP_KEY } from "@/modules/shared-steps/hooks/queries/use-get-shared-step";
import { GET_SHARED_STEP_USAGE_KEY } from "@/modules/shared-steps/hooks/queries/use-get-shared-step-usage";
import { GET_SHARED_STEPS_KEY } from "@/modules/shared-steps/hooks/queries/use-get-shared-steps";
import { GET_SPRINT_KEY } from "@/modules/sprints/hooks/queries/use-get-sprint";
import { GET_SPRINTS_KEY } from "@/modules/sprints/hooks/queries/use-get-sprints";
import { GET_STORIES_KEY } from "@/modules/stories/hooks/queries/use-get-stories";
import { GET_STORY_KEY } from "@/modules/stories/hooks/queries/use-get-story";
import { GET_STORY_PROGRESS_KEY } from "@/modules/stories/hooks/queries/use-get-story-progress";
import { GET_SYNC_STATUS_KEY } from "@/modules/stories/hooks/queries/use-get-sync-status";
import { GET_SUITE_KEY } from "@/modules/suites/hooks/queries/use-get-suite";
import { GET_SUITES_KEY } from "@/modules/suites/hooks/queries/use-get-suites";
import { GET_CASE_LATEST_RESULTS_KEY } from "@/modules/test-cases/hooks/queries/use-get-case-latest-results";
import { GET_QUARANTINE_EVENTS_KEY } from "@/modules/test-cases/hooks/queries/use-get-quarantine-events";
import { GET_TEST_CASE_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-case";
import { GET_TEST_CASE_VERSIONS_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-case-versions";
import { GET_TEST_CASES_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-cases";
import { GET_TEST_FILE_VERSIONS_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-file-versions";
import { GET_TRACEABILITY_KEY } from "@/modules/traceability/hooks/queries/use-get-traceability";
import { GET_WEBHOOK_DELIVERIES_KEY } from "@/modules/webhooks/hooks/queries/use-get-webhook-deliveries";
import { GET_WEBHOOKS_KEY } from "@/modules/webhooks/hooks/queries/use-get-webhooks";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { GET_PROJECT_MEMBERS_KEY } from "@/shared/hooks/queries/use-get-project-members";
import { GET_PROJECTS_KEY } from "@/shared/hooks/queries/use-get-projects";
import { LiveEventType } from "../enums/live-event-type.enum";

export const LIVE_EVENT_QUERY_KEYS: Record<LiveEventType, readonly string[]> = {
  [LiveEventType.RUN_LOG_RECEIVED]: [GET_RUN_LOG_KEY, GET_TOKEN_USAGE_KEY],
  [LiveEventType.RUN_STARTED]: [
    GET_RUNS_KEY,
    GET_RUN_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_RECENT_RUNS_KEY,
    GET_SUITES_KEY,
    GET_SUITE_KEY,
    GET_INSIGHT_TRENDS_KEY,
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
    GET_PLANS_KEY,
    GET_PLAN_KEY,
    GET_INSIGHT_TRENDS_KEY,
    GET_TOP_FAILING_CASES_KEY,
    GET_FLAKY_CASES_KEY,
    GET_LABEL_COVERAGE_KEY,
    GET_SPRINT_COVERAGE_KEY,
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
    GET_PLANS_KEY,
    GET_PLAN_KEY,
    GET_SUITES_KEY,
    GET_SUITE_KEY,
    GET_INSIGHT_TRENDS_KEY,
    GET_TOP_FAILING_CASES_KEY,
    GET_FLAKY_CASES_KEY,
    GET_LABEL_COVERAGE_KEY,
    GET_SPRINT_COVERAGE_KEY,
    GET_TOKEN_USAGE_KEY,
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
    GET_SPRINT_COVERAGE_KEY,
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
    GET_PLAN_KEY,
    GET_INSIGHT_TRENDS_KEY,
  ],
  [LiveEventType.FAILURE_CHANGED]: [
    GET_FAILURES_KEY,
    GET_FAILURE_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_DASHBOARD_KEY,
    GET_MY_WORK_KEY,
    GET_PLAN_KEY,
    GET_INSIGHT_TRENDS_KEY,
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
    GET_QUARANTINE_EVENTS_KEY,
    GET_SHARED_STEPS_KEY,
    GET_SHARED_STEP_KEY,
    GET_SHARED_STEP_USAGE_KEY,
    GET_SUITES_KEY,
    GET_SUITE_KEY,
    GET_PLANS_KEY,
    GET_PLAN_KEY,
    GET_TOP_FAILING_CASES_KEY,
    GET_FLAKY_CASES_KEY,
    GET_LABEL_COVERAGE_KEY,
    GET_SPRINT_COVERAGE_KEY,
  ],
  [LiveEventType.STORY_CHANGED]: [
    GET_STORIES_KEY,
    GET_STORY_KEY,
    GET_TRACEABILITY_KEY,
    GET_STORY_PROGRESS_KEY,
    GET_DASHBOARD_KEY,
    GET_RUN_STORIES_KEY,
    GET_PLANS_KEY,
    GET_PLAN_KEY,
    GET_SPRINT_COVERAGE_KEY,
  ],
  [LiveEventType.LABEL_CHANGED]: [
    GET_TEST_CASES_KEY,
    GET_TEST_CASE_KEY,
    GET_LABELS_KEY,
    GET_LABEL_COVERAGE_KEY,
  ],
  [LiveEventType.REVIEW_COMMENT_CHANGED]: [
    GET_TEST_CASES_KEY,
    GET_TEST_CASE_KEY,
    GET_REVIEW_COMMENTS_KEY,
  ],
  [LiveEventType.SUITE_CHANGED]: [GET_SUITES_KEY, GET_SUITE_KEY, GET_PLANS_KEY, GET_PLAN_KEY],
  [LiveEventType.PLAN_CHANGED]: [GET_PLANS_KEY, GET_PLAN_KEY],
  [LiveEventType.PLAN_SIGNED_OFF]: [],
  [LiveEventType.SHARED_STEP_CHANGED]: [
    GET_SHARED_STEPS_KEY,
    GET_SHARED_STEP_KEY,
    GET_SHARED_STEP_USAGE_KEY,
  ],
  [LiveEventType.FAILURE_OPENED]: [],
  [LiveEventType.FAILURE_STATUS_CHANGED]: [],
  [LiveEventType.GAP_RAISED]: [],
  [LiveEventType.STORY_SIGNED_OFF]: [],
  [LiveEventType.CHAT_CHANNEL_CHANGED]: [GET_CHAT_CHANNELS_KEY],
  [LiveEventType.WEBHOOK_CHANGED]: [GET_WEBHOOKS_KEY, GET_WEBHOOK_DELIVERIES_KEY],
  [LiveEventType.INSIGHTS_CHANGED]: [
    GET_INSIGHT_TRENDS_KEY,
    GET_LABEL_COVERAGE_KEY,
    GET_TOP_FAILING_CASES_KEY,
    GET_FLAKY_CASES_KEY,
    GET_TOKEN_USAGE_KEY,
    GET_SPRINT_COVERAGE_KEY,
  ],
  [LiveEventType.REPORT_READY]: [
    GET_REPORT_LINK_KEY,
    GET_NOTIFICATIONS_KEY,
    GET_UNREAD_NOTIFICATION_COUNT_KEY,
  ],
};
