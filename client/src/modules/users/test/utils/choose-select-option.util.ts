import { screen, waitFor, within } from "@testing-library/react";
import type { UserEvent } from "@testing-library/user-event";

const findListbox = async (combobox: HTMLElement): Promise<HTMLElement> => {
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
  selectLabel: string,
  optionName: string,
): Promise<void> => {
  const combobox = screen.getByRole("combobox", { name: selectLabel });
  await user.click(combobox);
  const listbox = await findListbox(combobox);
  await user.click(within(listbox).getByRole("option", { name: optionName, hidden: true }));
};

export const readSelectOption = async (
  user: UserEvent,
  selectLabel: string,
  optionName: string,
): Promise<HTMLElement> => {
  const combobox = screen.getByRole("combobox", { name: selectLabel });
  await user.click(combobox);
  const listbox = await findListbox(combobox);

  return within(listbox).getByRole("option", { name: optionName, hidden: true });
};
