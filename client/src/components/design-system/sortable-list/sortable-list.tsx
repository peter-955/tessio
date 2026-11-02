"use client";

import classNames from "classnames";
import {
  useEffect,
  useEffectEvent,
  useId,
  useRef,
  useState,
  type FC,
  type KeyboardEvent,
} from "react";
import { DSIcon } from "../icon/icon";
import styles from "./sortable-list.module.scss";
import type { DSSortableListItem, DSSortableListLabels } from "./sortable-list.type";

interface Props {
  items: DSSortableListItem[];
  onMove: (fromIndex: number, toIndex: number) => void;
  labels: DSSortableListLabels;
  isDisabled?: boolean;
}

const DRAG_DATA_TYPE = "text/plain";

const HANDLE_ICON_SIZE = 18;

const ITEM_INDEX_ATTRIBUTE = "data-sortable-index";

const KEY_OFFSETS: Readonly<Record<string, number>> = { ArrowUp: -1, ArrowDown: 1 };

const findItemIndex = (list: HTMLElement, event: Event): number | null => {
  if (!(event.target instanceof Element)) {
    return null;
  }

  const item = event.target.closest(`[${ITEM_INDEX_ATTRIBUTE}]`);
  if (item === null || !list.contains(item)) {
    return null;
  }

  const index = Number(item.getAttribute(ITEM_INDEX_ATTRIBUTE));

  return Number.isInteger(index) ? index : null;
};

export const DSSortableList: FC<Props> = ({ items, onMove, labels, isDisabled = false }) => {
  const instructionsId = useId();
  const listRef = useRef<HTMLOListElement>(null);
  const handlesRef = useRef(new Map<string, HTMLButtonElement>());
  const pendingFocusKeyRef = useRef<string | null>(null);
  const [armedKey, setArmedKey] = useState<string | null>(null);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [targetIndex, setTargetIndex] = useState<number | null>(null);
  const [announcement, setAnnouncement] = useState("");

  useEffect(() => {
    const pendingFocusKey = pendingFocusKeyRef.current;
    if (pendingFocusKey === null) {
      return;
    }

    pendingFocusKeyRef.current = null;
    handlesRef.current.get(pendingFocusKey)?.focus();
  }, [items]);

  const resetDrag = (): void => {
    setArmedKey(null);
    setDraggedIndex(null);
    setTargetIndex(null);
  };

  const moveItem = (fromIndex: number, toIndex: number): void => {
    if (fromIndex === toIndex || toIndex < 0 || toIndex >= items.length) {
      return;
    }

    setAnnouncement(labels.moved(toIndex + 1, items.length));
    onMove(fromIndex, toIndex);
  };

  const handleDragStart = useEffectEvent((event: DragEvent, index: number): void => {
    const item = items[index];
    if (isDisabled || item === undefined || armedKey !== item.key) {
      event.preventDefault();
      return;
    }

    event.dataTransfer?.setData(DRAG_DATA_TYPE, item.key);
    if (event.dataTransfer !== null) {
      event.dataTransfer.effectAllowed = "move";
    }
    setDraggedIndex(index);
  });

  const handleDragOver = useEffectEvent((event: DragEvent, index: number): void => {
    if (draggedIndex === null) {
      return;
    }

    event.preventDefault();
    if (event.dataTransfer !== null) {
      event.dataTransfer.dropEffect = "move";
    }
    setTargetIndex(index);
  });

  const handleDrop = useEffectEvent((event: DragEvent, index: number): void => {
    if (draggedIndex === null) {
      return;
    }

    event.preventDefault();
    moveItem(draggedIndex, index);
    resetDrag();
  });

  const handleDragEnd = useEffectEvent((): void => {
    resetDrag();
  });

  useEffect(() => {
    const list = listRef.current;
    if (list === null) {
      return;
    }

    const listenTo = (handler: (event: DragEvent, index: number) => void) => {
      return (event: DragEvent): void => {
        const index = findItemIndex(list, event);
        if (index !== null) {
          handler(event, index);
        }
      };
    };
    const onDragStart = listenTo(handleDragStart);
    const onDragOver = listenTo(handleDragOver);
    const onDrop = listenTo(handleDrop);
    const onDragEnd = (): void => {
      handleDragEnd();
    };
    list.addEventListener("dragstart", onDragStart);
    list.addEventListener("dragover", onDragOver);
    list.addEventListener("drop", onDrop);
    list.addEventListener("dragend", onDragEnd);

    return () => {
      list.removeEventListener("dragstart", onDragStart);
      list.removeEventListener("dragover", onDragOver);
      list.removeEventListener("drop", onDrop);
      list.removeEventListener("dragend", onDragEnd);
    };
  }, []);

  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number): void => {
    const offset = KEY_OFFSETS[event.key];
    if (offset === undefined || isDisabled) {
      return;
    }

    event.preventDefault();
    const item = items[index];
    if (item !== undefined) {
      pendingFocusKeyRef.current = item.key;
    }
    moveItem(index, index + offset);
  };

  const registerHandle = (key: string, element: HTMLButtonElement | null): void => {
    if (element === null) {
      handlesRef.current.delete(key);
      return;
    }

    handlesRef.current.set(key, element);
  };

  return (
    <>
      <span id={instructionsId} className={styles.hidden}>
        {labels.instructions}
      </span>
      <ol ref={listRef} className={styles.list} aria-label={labels.list}>
        {items.map((item, index) => {
          const isTarget = targetIndex === index && draggedIndex !== null && draggedIndex !== index;

          return (
            <li
              key={item.key}
              data-sortable-index={index}
              className={classNames(styles.item, {
                [styles.dragged]: draggedIndex === index,
                [styles.dropBefore]: isTarget && draggedIndex > index,
                [styles.dropAfter]: isTarget && draggedIndex < index,
              })}
              draggable={!isDisabled && armedKey === item.key}
            >
              <button
                ref={(element) => {
                  registerHandle(item.key, element);
                }}
                type="button"
                className={styles.handle}
                aria-label={labels.handle(index + 1)}
                aria-describedby={instructionsId}
                disabled={isDisabled}
                onPointerDown={() => {
                  setArmedKey(item.key);
                }}
                onPointerUp={() => {
                  if (draggedIndex === null) {
                    setArmedKey(null);
                  }
                }}
                onKeyDown={(event) => {
                  handleKeyDown(event, index);
                }}
              >
                <DSIcon name="dragHandle" size={HANDLE_ICON_SIZE} />
              </button>
              <div className={styles.content}>{item.content}</div>
            </li>
          );
        })}
      </ol>
      <span className={styles.hidden} role="status" aria-live="polite">
        {announcement}
      </span>
    </>
  );
};
