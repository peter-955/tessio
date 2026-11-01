"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TEST_CASE_STATUS_COLORS } from "../../typing/constants/test-case.constant";
import type { TestCaseStatus } from "../../typing/types/test-case.type";

interface Props {
  status: TestCaseStatus;
}

export const TestCaseStatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("testCases");

  return (
    <DSBadge color={TEST_CASE_STATUS_COLORS[status]} hasDot>
      {t(`status.${status}`)}
    </DSBadge>
  );
};
