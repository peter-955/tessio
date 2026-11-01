import type { NextRouter } from "next/dist/shared/lib/router/router";
import { vi } from "vitest";

export const createNextRouter = (): NextRouter => {
  return {
    route: "/",
    pathname: "/",
    query: {},
    asPath: "/",
    basePath: "",
    isLocaleDomain: false,
    isFallback: false,
    isReady: true,
    isPreview: false,
    push: vi.fn<NextRouter["push"]>().mockResolvedValue(true),
    replace: vi.fn<NextRouter["replace"]>().mockResolvedValue(true),
    reload: vi.fn<NextRouter["reload"]>(),
    back: vi.fn<NextRouter["back"]>(),
    forward: vi.fn<NextRouter["forward"]>(),
    prefetch: vi.fn<NextRouter["prefetch"]>().mockResolvedValue(undefined),
    beforePopState: vi.fn<NextRouter["beforePopState"]>(),
    events: {
      on: vi.fn<NextRouter["events"]["on"]>(),
      off: vi.fn<NextRouter["events"]["off"]>(),
      emit: vi.fn<NextRouter["events"]["emit"]>(),
    },
  };
};
