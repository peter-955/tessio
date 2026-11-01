import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ErrorPage } from "./error-page";
import { NotFoundPage } from "./not-found";

vi.mock("next/navigation", () => {
  return {
    useRouter: () => {
      return { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() };
    },
  };
});

const renderWithProviders = (element: ReactElement): ReturnType<typeof render> => {
  return render(<TestProviders queryClient={createTestQueryClient()}>{element}</TestProviders>);
};

beforeEach(() => {
  vi.spyOn(console, "error").mockImplementation(() => {
    return;
  });
});

describe("ErrorPage", () => {
  it("shows the translated error, retries and links home", async () => {
    const handleRetry = vi.fn<() => void>();
    const error = Object.assign(new Error("Boom"), { digest: "4021337" });

    const { container } = renderWithProviders(<ErrorPage error={error} onRetry={handleRetry} />);

    expect(screen.getByRole("alert")).toHaveTextContent("Something went wrong");
    expect(
      screen.getByRole("heading", { level: 1, name: "Something went wrong" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "An unexpected error stopped this page. Try again, or go back to the home page.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Error reference: 4021337")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Go to the home page" })).toHaveAttribute("href", "/");
    expect(console.error).toHaveBeenCalledWith(error);
    expect(await axe(container)).toHaveNoViolations();

    await userEvent.click(screen.getByRole("button", { name: "Try again" }));

    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it("hides the reference without a digest", () => {
    renderWithProviders(<ErrorPage error="Boom" onRetry={vi.fn()} />);

    expect(screen.queryByText(/Error reference/)).not.toBeInTheDocument();
  });
});

describe("NotFoundPage", () => {
  it("shows a full-page empty state with a link home", async () => {
    const { container } = renderWithProviders(<NotFoundPage />);

    expect(screen.getByRole("heading", { level: 1, name: "Page not found" })).toBeInTheDocument();
    expect(screen.getByText("This page does not exist or has moved.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to the home page" })).toHaveAttribute(
      "href",
      "/",
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
