import { screen, waitFor, within } from "@testing-library/react";
import type { UserEvent } from "@testing-library/user-event";

export const openSelectOption = async (
  user: UserEvent,
  selectLabel: RegExp,
  optionName: string,
): Promise<HTMLElement> => {
  const combobox = screen.getByRole("combobox", { name: selectLabel });
  await user.click(combobox);
  const listbox = await waitFor(() => {
    const listboxId = combobox.getAttribute("aria-controls");
    const element = listboxId === null ? null : document.getElementById(listboxId);
    if (element === null) {
      throw new Error("The select options are not rendered.");
    }

    return element;
  });

  return within(listbox).getByRole("option", { name: optionName, hidden: true });
};
