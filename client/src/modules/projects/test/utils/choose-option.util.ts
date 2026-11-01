import { screen, within } from "@testing-library/react";
import type { UserEvent } from "@testing-library/user-event";

export const chooseOption = async (
  user: UserEvent,
  combobox: HTMLElement,
  optionName: string,
): Promise<void> => {
  await user.click(combobox);
  const listboxId = combobox.getAttribute("aria-controls");
  const listbox = listboxId === null ? null : document.getElementById(listboxId);
  const scope = listbox === null ? screen : within(listbox);

  await user.click(await scope.findByRole("option", { name: optionName, hidden: true }));
};
