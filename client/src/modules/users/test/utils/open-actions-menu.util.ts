import { screen, waitFor, within } from "@testing-library/react";
import type { UserEvent } from "@testing-library/user-event";

export const openActionsMenu = async (user: UserEvent, userName: string): Promise<HTMLElement> => {
  const target = screen.getByRole("button", { name: `Actions for ${userName}` });
  await user.click(target);

  return waitFor(() => {
    const menuId = target.getAttribute("aria-controls");
    const menu = menuId === null ? null : document.getElementById(menuId);
    if (menu === null) {
      throw new Error("The actions menu is not rendered.");
    }

    return menu;
  });
};

export const readMenuItemNames = (menu: HTMLElement): string[] => {
  return within(menu)
    .queryAllByRole("menuitem", { hidden: true })
    .map((item) => {
      return item.textContent;
    });
};
