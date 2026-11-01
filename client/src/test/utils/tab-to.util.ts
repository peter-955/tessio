import type { UserEvent } from "@testing-library/user-event";

const MAXIMUM_TAB_COUNT = 40;

export const tabTo = async (user: UserEvent, target: Element): Promise<void> => {
  for (let count = 0; count < MAXIMUM_TAB_COUNT; count += 1) {
    if (document.activeElement === target) {
      return;
    }
    await user.tab();
  }
  if (document.activeElement !== target) {
    throw new Error(`Tab did not reach the element within ${MAXIMUM_TAB_COUNT} presses`);
  }
};
