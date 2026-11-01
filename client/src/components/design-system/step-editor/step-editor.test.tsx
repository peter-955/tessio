import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type FC, type ReactNode } from "react";
import { beforeAll, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSStepEditor } from "./step-editor";
import type {
  DSReferenceSuggestion,
  DSStepEditorLabels,
  DSStepEditorStep,
} from "./step-editor.type";

vi.mock("next/navigation", () => {
  return {
    useRouter: () => {
      return { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() };
    },
  };
});

const LABELS: DSStepEditorLabels = {
  step: (position) => `Step ${position}`,
  action: "Action",
  expected: "Expected result",
  addStep: "Add step",
  moveUp: "Move up",
  moveDown: "Move down",
  remove: "Remove step",
  stepActions: (position) => `Step ${position} actions`,
  suggestions: "References",
  noSuggestions: "No matching keys",
};

const SUGGESTIONS: DSReferenceSuggestion[] = [
  { kind: "data", key: "password" },
  { kind: "data", key: "username" },
  { kind: "file", key: "users.csv" },
];

const INITIAL_STEPS: DSStepEditorStep[] = [
  { id: "first", action: "Open the shop", expected: "" },
  { id: "second", action: "Pay", expected: "Paid" },
];

interface HarnessProps {
  initialSteps: DSStepEditorStep[];
  maxSteps?: number;
  onStepsChange?: (steps: DSStepEditorStep[]) => void;
}

const Harness: FC<HarnessProps> = ({ initialSteps, maxSteps = 100, onStepsChange }) => {
  const [steps, setSteps] = useState(initialSteps);

  return (
    <DSStepEditor
      steps={steps}
      onChange={(nextSteps) => {
        setSteps(nextSteps);
        onStepsChange?.(nextSteps);
      }}
      suggestions={SUGGESTIONS}
      labels={LABELS}
      maxSteps={maxSteps}
    />
  );
};

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

const readActions = (): string[] => {
  return screen.getAllByRole("textbox", { name: /^Action/ }).map((field) => {
    return (field as HTMLTextAreaElement).value;
  });
};

describe("DSStepEditor", () => {
  beforeAll(() => {
    Object.defineProperty(Element.prototype, "scrollIntoView", {
      configurable: true,
      writable: true,
      value: (): void => {
        return;
      },
    });
    if (!("fonts" in document)) {
      Object.defineProperty(document, "fonts", {
        configurable: true,
        value: {
          ready: Promise.resolve(),
          addEventListener: (): void => {
            return;
          },
          removeEventListener: (): void => {
            return;
          },
        },
      });
    }
  });

  it("adds a step and moves focus to its action", async () => {
    const user = userEvent.setup();
    const { container } = render(<Harness initialSteps={INITIAL_STEPS} />, { wrapper });

    expect(await axe(container)).toHaveNoViolations();
    await user.click(screen.getByRole("button", { name: "Add step" }));

    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(3);
    expect(within(items[2] as HTMLElement).getByText("Step 3")).toBeInTheDocument();
    expect(within(items[2] as HTMLElement).getByRole("textbox", { name: /^Action/ })).toHaveFocus();
  });

  it("names each step's fields after its position", () => {
    render(<Harness initialSteps={INITIAL_STEPS} />, { wrapper });

    const secondStep = screen.getByRole("group", { name: "Step 2" });
    expect(within(secondStep).getByRole("textbox", { name: /^Action/ })).toHaveValue("Pay");
    expect(within(secondStep).getByRole("textbox", { name: /^Expected result/ })).toHaveValue(
      "Paid",
    );
  });

  it("moves and removes steps from the row menu", async () => {
    const user = userEvent.setup();
    render(<Harness initialSteps={INITIAL_STEPS} />, { wrapper });

    await user.click(screen.getByRole("button", { name: "Step 1 actions" }));
    expect(await screen.findByRole("menuitem", { name: "Move up" })).toBeDisabled();
    await user.click(screen.getByRole("menuitem", { name: "Move down" }));
    expect(readActions()).toEqual(["Pay", "Open the shop"]);

    await user.click(screen.getByRole("button", { name: "Step 2 actions" }));
    expect(await screen.findByRole("menuitem", { name: "Move down" })).toBeDisabled();
    await user.click(screen.getByRole("menuitem", { name: "Remove step" }));
    expect(readActions()).toEqual(["Pay"]);
  });

  it("disables Add step at the limit", () => {
    render(<Harness initialSteps={INITIAL_STEPS} maxSteps={2} />, { wrapper });

    expect(screen.getByRole("button", { name: "Add step" })).toBeDisabled();
  });

  it("suggests data keys and inserts the full reference with Enter", async () => {
    const user = userEvent.setup();
    const handleStepsChange = vi.fn<(steps: DSStepEditorStep[]) => void>();
    render(
      <Harness
        initialSteps={[{ id: "first", action: "", expected: "" }]}
        onStepsChange={handleStepsChange}
      />,
      { wrapper },
    );

    const action = screen.getByRole("textbox", { name: /^Action/ });
    await user.click(action);
    await user.type(action, "Log in as {{{{data.us");

    const listbox = await screen.findByRole("listbox", { name: "References" });
    const options = within(listbox).getAllByRole("option");
    expect(options.map((option) => option.textContent)).toEqual(["data.username"]);
    expect(action).toHaveAttribute("aria-autocomplete", "list");
    expect(action).toHaveAttribute("aria-activedescendant", options[0]?.id);
    expect(
      await axe(document.body, { rules: { region: { enabled: false } } }),
    ).toHaveNoViolations();

    await user.keyboard("{Enter}");

    expect(action).toHaveValue("Log in as {{data.username}}");
    expect(handleStepsChange).toHaveBeenLastCalledWith([
      { id: "first", action: "Log in as {{data.username}}", expected: "" },
    ]);
    expect(screen.queryByRole("listbox", { name: "References" })).toBeNull();
  });

  it("moves through file suggestions with the arrow keys and closes on Escape", async () => {
    const user = userEvent.setup();
    render(<Harness initialSteps={[{ id: "first", action: "", expected: "" }]} />, { wrapper });

    const expected = screen.getByRole("textbox", { name: "Expected result" });
    await user.click(expected);
    await user.type(expected, "{{{{file.");

    const listbox = await screen.findByRole("listbox", { name: "References" });
    const options = within(listbox).getAllByRole("option");
    expect(options.map((option) => option.textContent)).toEqual(["file.users.csv"]);
    await user.keyboard("{ArrowDown}");
    expect(expected).toHaveAttribute("aria-activedescendant", options[0]?.id);
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("listbox", { name: "References" })).toBeNull();

    await user.type(expected, "zz");
    expect(await screen.findByText("No matching keys")).toBeInTheDocument();
    await user.keyboard("{Enter}");
    expect(expected).toHaveValue("{{file.zz\n");
  });
});
