"use client";

import type { FC, ReactNode } from "react";
import { DSButton } from "../button/button";
import { DSEmptyState } from "../empty-state/empty-state";
import type { DSTitleOrder } from "../typing/types/text.type";
import type { DSErrorStateRetryControl } from "./error-state.type";

type Props = DSErrorStateRetryControl & {
  title: string;
  description?: ReactNode;
  titleOrder?: DSTitleOrder;
};

export const DSErrorState: FC<Props> = ({
  title,
  description,
  retryLabel,
  onRetry,
  isRetrying = false,
  titleOrder,
}) => {
  return (
    <div role="alert">
      <DSEmptyState
        title={title}
        description={description}
        titleOrder={titleOrder}
        icon="alertCircle"
        action={
          onRetry && (
            <DSButton type="default" icon="refresh" isLoading={isRetrying} onClick={onRetry}>
              {retryLabel}
            </DSButton>
          )
        }
      />
    </div>
  );
};
