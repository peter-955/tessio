import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSButton } from "../button/button";
import { DSModal } from "./modal";

const MountedModal: FC = () => {
  const [isShown, setIsShown] = useState(false);

  return (
    <>
      <DSButton
        onClick={() => {
          setIsShown(true);
        }}
      >
        Delete run
      </DSButton>
      {isShown && (
        <DSModal
          isOpened
          title="Delete this run?"
          onClose={() => {
            setIsShown(false);
          }}
          action={{ label: "Delete", type: "danger", onClick: vi.fn() }}
        >
          The run and its results are removed.
        </DSModal>
      )}
    </>
  );
};

describe("DSModal", () => {
  it("traps focus, has no axe violations and returns focus to the trigger after Escape", async () => {
    const user = userEvent.setup();
    render(
      <TestProviders queryClient={createTestQueryClient()}>
        <MountedModal />
      </TestProviders>,
    );

    const trigger = screen.getByRole("button", { name: "Delete run" });
    await user.tab();
    expect(trigger).toHaveFocus();
    await user.keyboard("{Enter}");

    const dialog = await screen.findByRole("dialog", { name: "Delete this run?" });
    await waitFor(() => {
      expect(dialog).toContainElement(document.activeElement as HTMLElement);
    });
    expect(await axe(dialog)).toHaveNoViolations();
    await user.tab();
    await user.tab();
    await user.tab();
    await user.tab();
    expect(dialog).toContainElement(document.activeElement as HTMLElement);

    await user.keyboard("{Escape}");
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
    await waitFor(() => {
      expect(trigger).toHaveFocus();
    });
  });
});
