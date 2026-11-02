"use client";

import { DSText, type DSTitleOrder } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { CaseDataTable } from "./case-data-table/case-data-table";
import { CaseSheetSection } from "./case-sheet-section/case-sheet-section";
import styles from "./case-sheet.module.scss";
import { CaseSteps } from "./case-steps/case-steps";
import { ReferenceText } from "./reference-text/reference-text";
import type {
  CaseCriterion,
  CaseReferences,
  CaseSecretReveal,
  CaseStep,
} from "./typing/types/case-sheet.type";
import { listReferencedKeys } from "./utils/split-references.util";

interface Props {
  criteria: readonly CaseCriterion[];
  businessValue: string | null;
  preconditions: string | null;
  steps: readonly CaseStep[];
  references: CaseReferences;
  isStepListShown: boolean;
  headingOrder: DSTitleOrder;
  secretReveal?: CaseSecretReveal;
  renderSharedStep?: (sharedStepKey: string) => ReactNode;
  footer?: ReactNode;
}

export const CaseSheet: FC<Props> = ({
  criteria,
  businessValue,
  preconditions,
  steps,
  references,
  isStepListShown,
  headingOrder,
  secretReveal,
  renderSharedStep,
  footer,
}) => {
  const { t } = useTranslation("caseSheet");
  const { dataKeys } = listReferencedKeys([businessValue, preconditions], steps);
  const dataTitle =
    references.environmentName === null
      ? t("testData")
      : t("testDataOn", { environment: references.environmentName });

  return (
    <div className={styles.sheet}>
      {criteria.length > 0 && (
        <CaseSheetSection headingOrder={headingOrder} title={t("covers")}>
          <ul className={styles.criteria}>
            {criteria.map((criterion) => {
              return (
                <li key={criterion.code} className={styles.criterion}>
                  <span className={styles.criterionCode}>{criterion.code}</span>
                  <DSText component="span">{criterion.text}</DSText>
                </li>
              );
            })}
          </ul>
        </CaseSheetSection>
      )}
      {businessValue !== null && businessValue !== "" && (
        <CaseSheetSection headingOrder={headingOrder} title={t("whyItMatters")}>
          <DSText component="div">
            <ReferenceText text={businessValue} references={references} />
          </DSText>
        </CaseSheetSection>
      )}
      {preconditions !== null && preconditions !== "" && (
        <CaseSheetSection headingOrder={headingOrder} title={t("beforeYouStart")} isHighlighted>
          <DSText component="div">
            <ReferenceText text={preconditions} references={references} />
          </DSText>
        </CaseSheetSection>
      )}
      {dataKeys.length > 0 && (
        <CaseSheetSection headingOrder={headingOrder} title={dataTitle}>
          <CaseDataTable dataKeys={dataKeys} references={references} secretReveal={secretReveal} />
        </CaseSheetSection>
      )}
      {isStepListShown && (
        <CaseSheetSection headingOrder={headingOrder} title={t("steps")}>
          <CaseSteps steps={steps} references={references} renderSharedStep={renderSharedStep} />
        </CaseSheetSection>
      )}
      {footer}
    </div>
  );
};
