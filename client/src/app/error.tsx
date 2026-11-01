"use client";

import { ErrorPage } from "@/modules/errors/error-page";
import type { FC } from "react";

interface Props {
  error: unknown;
  retry: () => void;
}

const ErrorRoute: FC<Props> = ({ error, retry }) => {
  return <ErrorPage error={error} onRetry={retry} />;
};

export default ErrorRoute;
