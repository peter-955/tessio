"use client";

import { Combobox, Textarea, useCombobox } from "@mantine/core";
import { useMergedRef } from "@mantine/hooks";
import {
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type ChangeEvent,
  type FC,
  type KeyboardEvent,
  type ReactNode,
  type Ref,
  type SyntheticEvent,
} from "react";
import { filterSuggestions, findReferenceQuery, insertReference } from "../reference-query.util";
import type { DSReferenceQuery, DSReferenceSuggestion } from "../step-editor.type";
import styles from "./reference-textarea.module.scss";

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
  suggestions: readonly DSReferenceSuggestion[];
  suggestionsLabel: string;
  noSuggestionsLabel: string;
  placeholder?: string;
  description?: string;
  error?: ReactNode;
  isRequired?: boolean;
  isDisabled?: boolean;
  minRows?: number;
  maxRows?: number;
  isAutosize?: boolean;
  maxLength?: number;
  isMonospace?: boolean;
  ref?: Ref<HTMLTextAreaElement>;
}

const buildQueryKey = (query: DSReferenceQuery | null): string => {
  return query === null ? "" : `${query.kind}:${query.start}:${query.prefix}`;
};

export const DSReferenceTextarea: FC<Props> = ({
  label,
  value,
  onChange,
  suggestions,
  suggestionsLabel,
  noSuggestionsLabel,
  placeholder,
  description,
  error,
  isRequired = false,
  isDisabled = false,
  minRows = 2,
  maxRows = 12,
  isAutosize = true,
  maxLength,
  isMonospace = false,
  ref,
}) => {
  const listId = useId();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const mergedRef = useMergedRef(textareaRef, ref);
  const pendingCaretRef = useRef<number | null>(null);
  const [caret, setCaret] = useState<number | null>(null);
  const [dismissedQueryKey, setDismissedQueryKey] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeQueryKey, setActiveQueryKey] = useState("");

  const query = caret === null || isDisabled ? null : findReferenceQuery(value, caret);
  const queryKey = buildQueryKey(query);
  const isOpened = query !== null && queryKey !== dismissedQueryKey;
  const matchingSuggestions = query === null ? [] : filterSuggestions(suggestions, query);

  if (queryKey !== activeQueryKey) {
    setActiveQueryKey(queryKey);
    setActiveIndex(0);
  }

  const combobox = useCombobox({
    opened: isOpened,
    onOpenedChange: (isNextOpened) => {
      if (!isNextOpened) {
        setDismissedQueryKey(queryKey);
      }
    },
  });

  useLayoutEffect(() => {
    const pendingCaret = pendingCaretRef.current;
    if (pendingCaret === null || textareaRef.current === null) {
      return;
    }

    pendingCaretRef.current = null;
    textareaRef.current.setSelectionRange(pendingCaret, pendingCaret);
  }, [value]);

  const buildOptionId = (index: number): string => {
    return `${listId}-option-${index}`;
  };

  const insertSuggestion = (key: string): void => {
    if (query === null || caret === null) {
      return;
    }

    const insertion = insertReference(value, query, key, caret);
    pendingCaretRef.current = insertion.caret;
    setCaret(insertion.caret);
    onChange(insertion.text);
  };

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>): void => {
    setCaret(event.currentTarget.selectionStart);
    setDismissedQueryKey(null);
    onChange(event.currentTarget.value);
  };

  const handleSelect = (event: SyntheticEvent<HTMLTextAreaElement>): void => {
    setCaret(event.currentTarget.selectionStart);
  };

  const handleBlur = (): void => {
    setCaret(null);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if (!isOpened) {
      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      setDismissedQueryKey(queryKey);
      return;
    }

    const optionCount = matchingSuggestions.length;
    if (optionCount === 0) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((activeIndex + 1) % optionCount);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((activeIndex - 1 + optionCount) % optionCount);
      return;
    }

    if (event.key === "Enter" || event.key === "Tab") {
      const suggestion = matchingSuggestions[activeIndex];
      if (suggestion !== undefined) {
        event.preventDefault();
        insertSuggestion(suggestion.key);
      }
    }
  };

  return (
    <Combobox
      store={combobox}
      onOptionSubmit={insertSuggestion}
      withinPortal
      position="bottom-start"
    >
      <Combobox.Target withKeyboardNavigation={false} withAriaAttributes={false}>
        <Textarea
          ref={mergedRef}
          label={label}
          value={value}
          onChange={handleChange}
          onSelect={handleSelect}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={placeholder}
          description={description}
          error={error}
          required={isRequired}
          disabled={isDisabled}
          minRows={minRows}
          maxRows={maxRows}
          rows={minRows}
          autosize={isAutosize}
          maxLength={maxLength}
          classNames={isMonospace ? { input: styles.monospace } : undefined}
          size="sm"
          autoComplete="off"
          aria-autocomplete="list"
          aria-haspopup="listbox"
          aria-controls={isOpened ? listId : undefined}
          aria-activedescendant={
            isOpened && matchingSuggestions.length > 0 ? buildOptionId(activeIndex) : undefined
          }
        />
      </Combobox.Target>
      {isOpened && (
        <Combobox.Dropdown>
          <Combobox.Options id={listId} aria-label={suggestionsLabel}>
            {matchingSuggestions.length === 0 ? (
              <Combobox.Empty>{noSuggestionsLabel}</Combobox.Empty>
            ) : (
              matchingSuggestions.map((suggestion, index) => {
                const isActive = index === activeIndex;

                return (
                  <Combobox.Option
                    key={`${suggestion.kind}.${suggestion.key}`}
                    id={buildOptionId(index)}
                    value={suggestion.key}
                    selected={isActive}
                    aria-selected={isActive}
                    className={styles.option}
                  >
                    {`${suggestion.kind}.${suggestion.key}`}
                    {suggestion.description !== undefined && (
                      <span className={styles.optionDescription}>{suggestion.description}</span>
                    )}
                  </Combobox.Option>
                );
              })
            )}
          </Combobox.Options>
        </Combobox.Dropdown>
      )}
    </Combobox>
  );
};
