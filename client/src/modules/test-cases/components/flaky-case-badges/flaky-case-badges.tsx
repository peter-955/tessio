"use client";

import { DSBadge, DSIcon } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { FlakyCaseFlags } from "../../typing/types/flaky-case-flags.type";
import { listFlakyCaseBadges } from "../../utils/flaky-case.util";
import styles from "./flaky-case-badges.module.scss";

interface Props {
  flags: FlakyCaseFlags;
}

const BADGE_ICON_SIZE = 14;

export const FlakyCaseBadges: FC<Props> = ({ flags }) => {
  const { t } = useTranslation("flakyCases");

  return (
    <>
      {listFlakyCaseBadges(flags).map((badge) => {
        return (
          <DSBadge key={badge.kind} color={badge.color}>
            <span className={styles.content}>
              <DSIcon name={badge.icon} size={BADGE_ICON_SIZE} />
              {t(`badges.${badge.kind}`)}
            </span>
          </DSBadge>
        );
      })}
    </>
  );
};
