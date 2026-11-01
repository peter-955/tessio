import { describe, expect, it } from "vitest";
import {
  createFailureNotification,
  createGapNotification,
  createRunNotification,
} from "../test/utils/notification.fixture";
import { buildNotificationHref } from "./notification-href.util";

describe("buildNotificationHref", () => {
  it("links a gap to its story's gaps tab", () => {
    expect(buildNotificationHref(createGapNotification())).toBe(
      "/projects/TES/stories/TES-42?tab=gaps",
    );
  });

  it("links a failure to its failure page", () => {
    expect(buildNotificationHref(createFailureNotification())).toBe(
      "/projects/TES/failures/1f6c8b3e-0a9d-4e4f-9b7a-8c9d0e1f2a07",
    );
  });

  it("links a run to its run page", () => {
    expect(buildNotificationHref(createRunNotification())).toBe(
      "/projects/TES/runs/4c9f1e6b-3d2a-4b7c-8e0d-1f2a3b4c5d10",
    );
  });

  it("encodes the project and story keys", () => {
    const notification = createGapNotification({
      projectKey: "A B/C",
      payload: {
        kind: "gap_assigned",
        gapId: "8c3f5e0b-7d6a-4b1c-8e4d-5f6a7b8c9d04",
        storyId: "9d4a6f1c-8e7b-4c2d-9f5e-6a7b8c9d0e05",
        storyJiraKey: "TES-1?x=#y",
        question: "Why?",
      },
    });

    expect(buildNotificationHref(notification)).toBe(
      "/projects/A%20B%2FC/stories/TES-1%3Fx%3D%23y?tab=gaps",
    );
  });
});
