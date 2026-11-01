"use client";

import { useEffect, useState } from "react";

const readActiveElement = (isOpened: boolean): HTMLElement | null => {
  if (!isOpened || typeof document === "undefined") {
    return null;
  }
  const activeElement = document.activeElement;

  return activeElement instanceof HTMLElement && activeElement !== document.body
    ? activeElement
    : null;
};

const returnFocus = (trigger: HTMLElement): void => {
  window.setTimeout(() => {
    const activeElement = document.activeElement;
    const isFocusLost = activeElement === null || activeElement === document.body;
    if (isFocusLost && trigger.isConnected) {
      trigger.focus({ preventScroll: true });
    }
  });
};

export const useDSFocusReturn = (isOpened: boolean): void => {
  const [trigger] = useState(() => readActiveElement(isOpened));

  useEffect(() => {
    if (!isOpened || trigger === null) {
      return;
    }

    return () => {
      returnFocus(trigger);
    };
  }, [isOpened, trigger]);
};
