"use client";

import { useEffect, useId, useRef, type FC, type ReactNode } from "react";
import { DSActionIcon } from "../action-icon/action-icon";
import { DSButton } from "../button/button";
import { DSMenu } from "../menu/menu";
import { DSStepTimeline } from "../step-timeline/step-timeline";
import type { DSStepTimelineStep } from "../step-timeline/step-timeline.type";
import { DSReferenceTextarea } from "./reference-textarea/reference-textarea";
import styles from "./step-editor.module.scss";
import type {
  DSReferenceSuggestion,
  DSStepEditorLabels,
  DSStepEditorStep,
} from "./step-editor.type";
import { createStep, moveStep, removeStep } from "./step-list.util";

interface Props {
  steps: DSStepEditorStep[];
  onChange: (steps: DSStepEditorStep[]) => void;
  suggestions: readonly DSReferenceSuggestion[];
  labels: DSStepEditorLabels;
  maxSteps: number;
  maxTextLength?: number;
  isDisabled?: boolean;
  errors?: Record<string, string>;
  renderSharedStep?: (step: DSStepEditorStep, position: number) => ReactNode;
  footerActions?: ReactNode;
}

export const DSStepEditor: FC<Props> = ({
  steps,
  onChange,
  suggestions,
  labels,
  maxSteps,
  maxTextLength,
  isDisabled = false,
  errors = {},
  renderSharedStep,
  footerActions,
}) => {
  const editorId = useId();
  const actionFieldsRef = useRef(new Map<string, HTMLTextAreaElement>());
  const pendingFocusStepIdRef = useRef<string | null>(null);

  useEffect(() => {
    const pendingFocusStepId = pendingFocusStepIdRef.current;
    if (pendingFocusStepId === null) {
      return;
    }

    pendingFocusStepIdRef.current = null;
    actionFieldsRef.current.get(pendingFocusStepId)?.focus();
  }, [steps]);

  const updateStep = (stepId: string, update: Partial<DSStepEditorStep>): void => {
    onChange(
      steps.map((step) => {
        return step.id === stepId ? { ...step, ...update } : step;
      }),
    );
  };

  const handleAdd = (): void => {
    const step = createStep();
    onChange([...steps, step]);
    pendingFocusStepIdRef.current = step.id;
  };

  const registerActionField = (stepId: string, element: HTMLTextAreaElement | null): void => {
    if (element === null) {
      actionFieldsRef.current.delete(stepId);
      return;
    }

    actionFieldsRef.current.set(stepId, element);
  };

  return (
    <div>
      <DSStepTimeline
        labels={{ step: labels.step, expected: labels.expected }}
        steps={steps.map((step, index): DSStepTimelineStep => {
          const position = index + 1;
          const positionId = `${editorId}-step-${step.id}`;

          return {
            key: step.id,
            order: position,
            action: null,
            expected: null,
            titleId: positionId,
            headerAction: isDisabled ? undefined : (
              <DSMenu
                target={<DSActionIcon icon="dots" ariaLabel={labels.stepActions(position)} />}
                items={[
                  {
                    key: "moveUp",
                    label: labels.moveUp,
                    isDisabled: index === 0,
                    onClick: () => {
                      onChange(moveStep(steps, index, -1));
                    },
                  },
                  {
                    key: "moveDown",
                    label: labels.moveDown,
                    isDisabled: index === steps.length - 1,
                    onClick: () => {
                      onChange(moveStep(steps, index, 1));
                    },
                  },
                  { key: "divider", type: "divider" },
                  {
                    key: "remove",
                    label: labels.remove,
                    icon: "trash",
                    isDanger: true,
                    onClick: () => {
                      onChange(removeStep(steps, step.id));
                    },
                  },
                ]}
              />
            ),
            details:
              typeof step.sharedStepKey === "string" && renderSharedStep !== undefined ? (
                <div className={styles.shared} role="group" aria-labelledby={positionId}>
                  {renderSharedStep(step, position)}
                </div>
              ) : (
                <div className={styles.fields} role="group" aria-labelledby={positionId}>
                  <DSReferenceTextarea
                    ref={(element: HTMLTextAreaElement | null) => {
                      registerActionField(step.id, element);
                    }}
                    label={labels.action}
                    value={step.action}
                    onChange={(action) => {
                      updateStep(step.id, { action });
                    }}
                    suggestions={suggestions}
                    suggestionsLabel={labels.suggestions}
                    noSuggestionsLabel={labels.noSuggestions}
                    error={errors[step.id]}
                    maxLength={maxTextLength}
                    isDisabled={isDisabled}
                    isRequired
                  />
                  <DSReferenceTextarea
                    label={labels.expected}
                    value={step.expected}
                    onChange={(expected) => {
                      updateStep(step.id, { expected });
                    }}
                    suggestions={suggestions}
                    suggestionsLabel={labels.suggestions}
                    noSuggestionsLabel={labels.noSuggestions}
                    maxLength={maxTextLength}
                    isDisabled={isDisabled}
                  />
                </div>
              ),
          };
        })}
      />
      {!isDisabled && (
        <div className={styles.footer}>
          <DSButton
            type="default"
            icon="plus"
            isDisabled={steps.length >= maxSteps}
            onClick={handleAdd}
          >
            {labels.addStep}
          </DSButton>
          {footerActions}
        </div>
      )}
    </div>
  );
};
