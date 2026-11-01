import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { TestProviders } from "./test-providers";
import { createTestQueryClient } from "./utils/create-test-query-client.util";

describe("TestProviders", () => {
  it("renders children inside the app providers without accessibility violations", async () => {
    const { container } = render(
      <TestProviders queryClient={createTestQueryClient()}>
        <button type="button">Save</button>
      </TestProviders>,
    );

    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
