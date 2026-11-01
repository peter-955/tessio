import { GET_CURRENT_USER_KEY } from "@/modules/auth/hooks/queries/use-get-current-user";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { act, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { createSignedInUser } from "../../test/utils/current-user.fixture";
import { PreferencesProbe } from "../../test/utils/preferences-probe";
import { renderSignedIn } from "../../test/utils/render-signed-in.util";
import { SavedPreferencesSync } from "./saved-preferences-sync";

const SAVED_USER = createSignedInUser({ colorScheme: "dark", language: "fr" });

const renderSync = (): ReturnType<typeof renderSignedIn> => {
  return renderSignedIn(
    <>
      <SavedPreferencesSync />
      <PreferencesProbe />
    </>,
    SAVED_USER,
  );
};

describe("SavedPreferencesSync", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("applies the saved color scheme and language", async () => {
    renderSync();

    await waitFor(() => {
      expect(screen.getByTestId("color-scheme")).toHaveTextContent("dark");
    });
    expect(screen.getByTestId("language")).toHaveTextContent("fr");
    expect(document.cookie).toContain("tessio-language=fr");
  });

  it("does not revert a local change while the saved value is unchanged", async () => {
    const user = userEvent.setup();
    const { queryClient } = renderSync();
    await waitFor(() => {
      expect(screen.getByTestId("color-scheme")).toHaveTextContent("dark");
    });

    await user.click(screen.getByRole("button", { name: "Use light" }));
    act(() => {
      queryClient.setQueryData<CurrentUser>([GET_CURRENT_USER_KEY], {
        ...SAVED_USER,
        name: "Ada King",
      });
    });

    expect(screen.getByTestId("color-scheme")).toHaveTextContent("light");
  });

  it("applies a newly saved value", async () => {
    const user = userEvent.setup();
    const { queryClient } = renderSync();
    await user.click(screen.getByRole("button", { name: "Use light" }));

    act(() => {
      queryClient.setQueryData<CurrentUser>([GET_CURRENT_USER_KEY], {
        ...SAVED_USER,
        colorScheme: "auto",
        language: "vi",
      });
    });

    await waitFor(() => {
      expect(screen.getByTestId("color-scheme")).toHaveTextContent("auto");
    });
    expect(screen.getByTestId("language")).toHaveTextContent("vi");
  });
});
