"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TEST_CASE_PRIORITY_COLORS } from "../../typing/constants/test-case.constant";
import type { TestCasePriority } from "../../typing/types/test-case.type";

interface Props {
  priority: TestCasePriority;
}

export const TestCasePriorityBadge: FC<Props> = ({ priority }) => {
  const { t } = useTranslation("testCases");

  return <DSBadge color={TEST_CASE_PRIORITY_COLORS[priority]}>{t(`priority.${priority}`)}</DSBadge>;
};
