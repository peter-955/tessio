import { describe, expect, it } from "vitest";
import {
  REPORT_LINK_MAX_POLL_COUNT,
  REPORT_LINK_POLL_INTERVAL_IN_MILLISECONDS,
  REPORT_LINK_REFRESH_INTERVAL_IN_MILLISECONDS,
} from "../typing/constants/report.constant";
import { pickReportLinkPollInterval } from "./report-link-poll.util";

describe("pickReportLinkPollInterval", () => {
  it("polls while the report is not ready", () => {
    expect(pickReportLinkPollInterval({ hasLink: false, failedPollCount: 3 })).toBe(
      REPORT_LINK_POLL_INTERVAL_IN_MILLISECONDS,
    );
  });

  it("stops polling after the last try", () => {
    expect(
      pickReportLinkPollInterval({ hasLink: false, failedPollCount: REPORT_LINK_MAX_POLL_COUNT }),
    ).toBe(false);
  });

  it("renews a ready link before its 5 minutes run out", () => {
    const interval = pickReportLinkPollInterval({ hasLink: true, failedPollCount: 0 });

    expect(interval).toBe(REPORT_LINK_REFRESH_INTERVAL_IN_MILLISECONDS);
    expect(REPORT_LINK_REFRESH_INTERVAL_IN_MILLISECONDS).toBeLessThan(300000);
  });
});
