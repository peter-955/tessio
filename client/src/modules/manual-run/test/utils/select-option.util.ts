import { screen, waitFor, within } from "@testing-library/react";
import type { UserEvent } from "@testing-library/user-event";

export const openSelectListbox = async (
  user: UserEvent,
  selectLabel: string | RegExp,
): Promise<HTMLElement> => {
  const combobox = screen.getByRole("combobox", { name: selectLabel });
  await user.click(combobox);

  return waitFor(() => {
    const listboxId = combobox.getAttribute("aria-controls");
    const listbox = listboxId === null ? null : document.getElementById(listboxId);
    if (listbox === null) {
      throw new Error("The select options are not rendered.");
    }

    return listbox;
  });
};

export const chooseSelectOption = async (
  user: UserEvent,
  selectLabel: string | RegExp,
  optionName: string,
): Promise<void> => {
  const listbox = await openSelectListbox(user, selectLabel);
  await user.click(within(listbox).getByRole("option", { name: optionName, hidden: true }));
};

export const readSelectOptionNames = async (
  user: UserEvent,
  selectLabel: string | RegExp,
): Promise<string[]> => {
  const listbox = await openSelectListbox(user, selectLabel);

  return within(listbox)
    .getAllByRole("option", { hidden: true })
    .map((option) => {
      return option.textContent;
    });
};
