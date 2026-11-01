import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { TextDiff } from "./text-diff";

const LABELS = { added: "Added", removed: "Removed" };

describe("TextDiff", () => {
  it("labels added and removed text for screen readers, not only by colour", async () => {
    const { container } = render(
      <TextDiff
        tokens={[
          { kind: "unchanged", value: "Sign in with " },
          { kind: "removed", value: "an old" },
          { kind: "added", value: "a valid" },
          { kind: "unchanged", value: " password" },
        ]}
        labels={LABELS}
      />,
    );

    const added = container.querySelector("ins");
    const removed = container.querySelector("del");
    expect(added).toHaveTextContent("Added: a valid");
    expect(removed).toHaveTextContent("Removed: an old");
    expect(screen.getByText("Added:", { exact: false })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
