"use client";

import { Pagination, useMatches } from "@mantine/core";
import type { FC } from "react";
import { DS_PAGINATION_SIBLINGS } from "./pagination.constant";
import styles from "./pagination.module.scss";

interface Props {
  page: number;
  pageCount: number;
  onChange: (page: number) => void;
  ariaLabel: string;
  previousLabel: string;
  nextLabel: string;
}

export const DSPagination: FC<Props> = ({
  page,
  pageCount,
  onChange,
  ariaLabel,
  previousLabel,
  nextLabel,
}) => {
  const siblings = useMatches(DS_PAGINATION_SIBLINGS);

  if (pageCount <= 1) {
    return null;
  }

  const getControlProps = (
    control: "first" | "previous" | "last" | "next",
  ): Record<string, string> => {
    if (control === "previous") {
      return { "aria-label": previousLabel };
    }
    if (control === "next") {
      return { "aria-label": nextLabel };
    }
    return {};
  };

  return (
    <nav aria-label={ariaLabel} className={styles.navigation}>
      <Pagination
        total={pageCount}
        value={page}
        onChange={onChange}
        siblings={siblings}
        getControlProps={getControlProps}
        hideWithOnePage
      />
    </nav>
  );
};
