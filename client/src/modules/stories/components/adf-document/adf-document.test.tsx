import englishStories from "@/lib/i18n/locales/en/stories.json";
import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen, within, type RenderResult } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import {
  HEADING_BULLET_LIST_DOCUMENT,
  LIST_IN_PANEL_DOCUMENT,
  MENTIONS_HARD_BREAK_DOCUMENT,
  RICH_DOCUMENT,
  TASK_LIST_DOCUMENT,
} from "../../test/utils/adf-fixture.util";
import { AdfDocument } from "./adf-document";

const renderDocument = (value: unknown): RenderResult => {
  return render(
    <TestProviders queryClient={createTestQueryClient()}>
      <AdfDocument value={value} />
    </TestProviders>,
  );
};

describe("AdfDocument", () => {
  it("shows the empty text without a description", () => {
    renderDocument(null);

    expect(screen.getByText(englishStories.description.empty)).toBeInTheDocument();
  });

  it("shows the empty text for garbage", () => {
    renderDocument({ type: "paragraph", content: "nope" });

    expect(screen.getByText(englishStories.description.empty)).toBeInTheDocument();
  });

  it("renders headings and bullet lists", async () => {
    const { container } = renderDocument(HEADING_BULLET_LIST_DOCUMENT);

    expect(screen.getByText("As a shopper I want to pay by card.").tagName).toBe("P");
    expect(screen.getByRole("heading", { level: 3, name: "Acceptance Criteria" })).toBeVisible();
    expect(screen.getByRole("heading", { level: 3, name: "Notes" })).toBeVisible();
    const lists = screen.getAllByRole("list");
    expect(lists).toHaveLength(3);
    expect(within(lists[1] as HTMLElement).getAllByRole("listitem")).toHaveLength(3);
    expect(screen.getByText("an error").tagName).toBe("STRONG");
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders a panel as a note", async () => {
    const { container } = renderDocument(LIST_IN_PANEL_DOCUMENT);

    const note = screen.getByRole("note");
    expect(
      within(note).getByRole("heading", { level: 3, name: "Acceptance criteria" }),
    ).toBeVisible();
    expect(within(note).getByText("Results match the search text")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders task lists with read-only checkboxes", async () => {
    const { container } = renderDocument(TASK_LIST_DOCUMENT);

    const todo = screen.getByRole("checkbox", { name: "Le panier se vide" });
    const done = screen.getByRole("checkbox", { name: "Le total est mis à jour" });
    expect(todo).not.toBeChecked();
    expect(todo).toBeDisabled();
    expect(done).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "TVA incluse" })).not.toBeChecked();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("keeps deeper headings below the top heading", () => {
    renderDocument({
      type: "doc",
      content: [
        { type: "heading", attrs: { level: 1 }, content: [{ type: "text", text: "Top" }] },
        { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Second" }] },
        { type: "heading", attrs: { level: 6 }, content: [{ type: "text", text: "Deep" }] },
      ],
    });

    expect(screen.getByRole("heading", { level: 3, name: "Top" })).toBeVisible();
    expect(screen.getByRole("heading", { level: 4, name: "Second" })).toBeVisible();
    expect(screen.getByRole("heading", { level: 5, name: "Deep" })).toBeVisible();
  });

  it("renders mentions, hard breaks, emoji, status and inline cards", () => {
    const { container } = renderDocument(MENTIONS_HARD_BREAK_DOCUMENT);

    expect(screen.getByRole("heading", { level: 3, name: "Acceptance criteria" })).toBeVisible();
    expect(screen.getByText("@Alice")).toBeInTheDocument();
    expect(screen.queryByText("@@Alice")).toBeNull();
    expect(container.querySelectorAll("br")).toHaveLength(1);
    expect(container.textContent).toContain("within  2 days 🎉");
    expect(screen.getByText("REFUNDED")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "https://docs.shop.test/refunds" })).toHaveAttribute(
      "href",
      "https://docs.shop.test/refunds",
    );
  });

  it("renders an inline status inside a paragraph without invalid nesting", () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => undefined);

    try {
      renderDocument({
        type: "doc",
        content: [
          {
            type: "paragraph",
            content: [
              { type: "text", text: "Order is " },
              { type: "status", attrs: { text: "DONE", color: "green" } },
            ],
          },
        ],
      });

      expect(screen.getByText("DONE").closest("p")).not.toBeNull();
      expect(screen.getByText("DONE").closest("p")?.querySelector("div")).toBeNull();
      expect(consoleError).not.toHaveBeenCalled();
    } finally {
      consoleError.mockRestore();
    }
  });

  it("renders tables, code blocks and marks, and keeps unsafe links as text", async () => {
    const { container } = renderDocument(RICH_DOCUMENT);

    expect(screen.getByRole("columnheader", { name: "Card" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "Visa approved" })).toHaveAttribute("colspan", "2");
    const code = container.querySelector("pre > code");
    expect(code).toHaveAttribute("data-language", "json");
    expect(code).toHaveTextContent('{"amount": 10}');
    const guide = screen.getByRole("link", { name: "guide" });
    expect(guide).toHaveAttribute("href", "https://docs.shop.test/guide");
    expect(guide).toHaveAttribute("target", "_blank");
    expect(guide).toHaveAttribute("rel", "noopener noreferrer");
    expect(screen.getByText("this trap").tagName).toBe("STRONG");
    expect(screen.getByText("this trap").closest("a")).toBeNull();
    expect(screen.getByText("javascript:alert(2)").closest("a")).toBeNull();
    expect(container.querySelector('a[href^="javascript"]')).toBeNull();
    expect(screen.getByText("old").tagName).toBe("S");
    expect(screen.getByText("x").tagName).toBe("SUB");
    expect(screen.getByText("2").tagName).toBe("SUP");
    expect(screen.getByText("tap").tagName).toBe("CODE");
    expect(container.querySelector("ol")).toHaveAttribute("start", "3");
    expect(container.querySelector("hr")).not.toBeNull();
    expect(screen.getByText("More details").tagName).toBe("SUMMARY");
    expect(screen.getByText(englishStories.adf.attachment)).toBeInTheDocument();
    expect(screen.getByText("Oct 31, 2025")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
