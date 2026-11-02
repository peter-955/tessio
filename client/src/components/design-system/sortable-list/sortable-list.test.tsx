import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSSortableList } from "./sortable-list";
import type { DSSortableListLabels } from "./sortable-list.type";

const LABELS: DSSortableListLabels = {
  list: "Suite cases",
  handle: (index) => {
    return `Move case ${index}`;
  },
  instructions: "Drag to reorder, or press the up and down arrow keys.",
  moved: (index, total) => {
    return `Moved to position ${index} of ${total}`;
  },
};

const NAMES = ["Alpha", "Beta", "Gamma"];

const SortableNames: FC<{ onMove?: (fromIndex: number, toIndex: number) => void }> = ({
  onMove,
}) => {
  const [names, setNames] = useState(NAMES);

  return (
    <DSSortableList
      labels={LABELS}
      items={names.map((name) => {
        return { key: name, content: name };
      })}
      onMove={(fromIndex, toIndex) => {
        onMove?.(fromIndex, toIndex);
        setNames((current) => {
          const next = [...current];
          const [moved] = next.splice(fromIndex, 1);
          next.splice(toIndex, 0, moved);

          return next;
        });
      }}
    />
  );
};

const readNames = (): string[] => {
  return within(screen.getByRole("list", { name: LABELS.list }))
    .getAllByRole("listitem")
    .map((item) => {
      return item.textContent ?? "";
    });
};

const createDataTransfer = (): Pick<DataTransfer, "setData" | "effectAllowed" | "dropEffect"> => {
  return { setData: vi.fn(), effectAllowed: "none", dropEffect: "none" };
};

describe("DSSortableList", () => {
  it("lists the items in order with a labelled handle each", async () => {
    const { container } = render(<SortableNames />);

    expect(readNames()).toEqual(NAMES);
    expect(screen.getByRole("button", { name: "Move case 2" })).toHaveAccessibleDescription(
      LABELS.instructions,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("moves an item with the arrow keys and keeps the focus on its handle", async () => {
    const user = userEvent.setup();
    render(<SortableNames />);

    screen.getByRole("button", { name: "Move case 1" }).focus();
    await user.keyboard("{ArrowDown}");

    expect(readNames()).toEqual(["Beta", "Alpha", "Gamma"]);
    expect(screen.getByRole("button", { name: "Move case 2" })).toHaveFocus();
    expect(screen.getByRole("status")).toHaveTextContent("Moved to position 2 of 3");

    await user.keyboard("{ArrowUp}{ArrowUp}");

    expect(readNames()).toEqual(NAMES);
  });

  it("moves an item dragged by its handle onto another item", () => {
    const onMove = vi.fn();
    render(<SortableNames onMove={onMove} />);
    const items = screen.getAllByRole("listitem");

    fireEvent.pointerDown(screen.getByRole("button", { name: "Move case 3" }));
    fireEvent.dragStart(items[2], { dataTransfer: createDataTransfer() });
    fireEvent.dragOver(items[0], { dataTransfer: createDataTransfer() });
    fireEvent.drop(items[0], { dataTransfer: createDataTransfer() });

    expect(onMove).toHaveBeenCalledWith(2, 0);
    expect(readNames()).toEqual(["Gamma", "Alpha", "Beta"]);
  });

  it("does not start a drag that does not begin on the handle", () => {
    const onMove = vi.fn();
    render(<SortableNames onMove={onMove} />);
    const items = screen.getAllByRole("listitem");

    fireEvent.dragStart(items[2], { dataTransfer: createDataTransfer() });
    fireEvent.drop(items[0], { dataTransfer: createDataTransfer() });

    expect(onMove).not.toHaveBeenCalled();
    expect(readNames()).toEqual(NAMES);
  });
});
