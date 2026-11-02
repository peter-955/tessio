import { renderHookWithProviders } from "@/test/utils/render-hook-with-providers.util";
import { describe, expect, it } from "vitest";
import {
  createReportNotification,
  createRunNotification,
  createSuiteRunNotification,
} from "../test/utils/notification.fixture";
import { useDescribeNotification } from "./use-describe-notification";

describe("useDescribeNotification", () => {
  it("names the suite and its counts for a finished suite run", () => {
    const { result } = renderHookWithProviders(useDescribeNotification);

    expect(result.current(createSuiteRunNotification())).toEqual({
      title: "Suite run passed: Checkout regression",
      description: "12 passed · 0 failed · 0 blocked",
    });
  });

  it("names the exported source and the file for a ready report", () => {
    const { result } = renderHookWithProviders(useDescribeNotification);

    expect(result.current(createReportNotification())).toEqual({
      title: "Report ready: TES-42 Refund a payment",
      description: "story-TES-42.pdf",
    });
  });

  it("keeps the story wording for a finished story run", () => {
    const { result } = renderHookWithProviders(useDescribeNotification);

    expect(result.current(createRunNotification()).title).toBe("Run failed on TES-44");
  });
});
