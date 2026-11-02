"use client";

import {
  DSActionIcon,
  DSButton,
  DSInput,
  DSMenu,
  DSStack,
  DSText,
} from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MAX_STORY_CRITERIA } from "../../typing/constants/story-editor.constant";
import type { CriterionDraft } from "../../typing/types/story-editor.type";
import { createCriterionDraft, moveCriterion } from "../../utils/story-editor.util";
import styles from "./criteria-editor.module.scss";

interface Props {
  criteria: readonly CriterionDraft[];
  onChange: (criteria: CriterionDraft[]) => void;
}

export const CriteriaEditor: FC<Props> = ({ criteria, onChange }) => {
  const { t } = useTranslation("stories");

  const updateText = (id: string, text: string): void => {
    onChange(
      criteria.map((criterion) => {
        return criterion.id === id ? { ...criterion, text } : criterion;
      }),
    );
  };

  return (
    <DSStack gap={2}>
      <DSText size="sm" weight="medium">
        {t("editor.criteria")}
      </DSText>
      <DSText size="sm" color="muted">
        {t("editor.criteriaHint")}
      </DSText>
      <ol className={styles.list}>
        {criteria.map((criterion, index) => {
          const code = t("editor.criterionCode", { number: index + 1 });

          return (
            <li key={criterion.id} className={styles.row}>
              <div className={styles.field}>
                <DSInput
                  label={code}
                  value={criterion.text}
                  onChange={(text) => {
                    updateText(criterion.id, text);
                  }}
                />
              </div>
              <DSMenu
                target={
                  <DSActionIcon icon="dots" ariaLabel={t("editor.criterionActions", { code })} />
                }
                items={[
                  {
                    key: "moveUp",
                    label: t("editor.moveUp"),
                    isDisabled: index === 0,
                    onClick: () => {
                      onChange(moveCriterion(criteria, index, -1));
                    },
                  },
                  {
                    key: "moveDown",
                    label: t("editor.moveDown"),
                    isDisabled: index === criteria.length - 1,
                    onClick: () => {
                      onChange(moveCriterion(criteria, index, 1));
                    },
                  },
                  { key: "divider", type: "divider" },
                  {
                    key: "remove",
                    label: t("editor.remove"),
                    icon: "trash",
                    isDanger: true,
                    onClick: () => {
                      onChange(
                        criteria.filter((candidate) => {
                          return candidate.id !== criterion.id;
                        }),
                      );
                    },
                  },
                ]}
              />
            </li>
          );
        })}
      </ol>
      <div>
        <DSButton
          type="default"
          icon="plus"
          isDisabled={criteria.length >= MAX_STORY_CRITERIA}
          onClick={() => {
            onChange([...criteria, createCriterionDraft()]);
          }}
        >
          {t("editor.addCriterion")}
        </DSButton>
      </div>
    </DSStack>
  );
};
