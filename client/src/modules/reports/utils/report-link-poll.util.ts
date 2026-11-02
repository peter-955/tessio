import {
  REPORT_LINK_MAX_POLL_COUNT,
  REPORT_LINK_POLL_INTERVAL_IN_MILLISECONDS,
  REPORT_LINK_REFRESH_INTERVAL_IN_MILLISECONDS,
} from "../typing/constants/report.constant";

interface PollState {
  hasLink: boolean;
  failedPollCount: number;
}

export const pickReportLinkPollInterval = ({
  hasLink,
  failedPollCount,
}: PollState): number | false => {
  if (hasLink) {
    return REPORT_LINK_REFRESH_INTERVAL_IN_MILLISECONDS;
  }
  if (failedPollCount >= REPORT_LINK_MAX_POLL_COUNT) {
    return false;
  }

  return REPORT_LINK_POLL_INTERVAL_IN_MILLISECONDS;
};
