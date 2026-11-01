import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, expect } from "vitest";
import * as axeMatchers from "vitest-axe/matchers";

class ResizeObserverStub {
  observe(): void {
    return;
  }

  unobserve(): void {
    return;
  }

  disconnect(): void {
    return;
  }
}

const createMediaQueryList = (query: string): MediaQueryList => {
  return {
    matches: false,
    media: query,
    onchange: null,
    addListener: (): void => {
      return;
    },
    removeListener: (): void => {
      return;
    },
    addEventListener: (): void => {
      return;
    },
    removeEventListener: (): void => {
      return;
    },
    dispatchEvent: (): boolean => {
      return false;
    },
  };
};

expect.extend(axeMatchers);

Object.defineProperty(window, "matchMedia", { writable: true, value: createMediaQueryList });
Object.defineProperty(window, "ResizeObserver", { writable: true, value: ResizeObserverStub });
Object.defineProperty(globalThis, "ResizeObserver", { writable: true, value: ResizeObserverStub });

afterEach(() => {
  cleanup();
});
