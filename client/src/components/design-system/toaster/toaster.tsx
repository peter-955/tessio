"use client";

import { useComputedColorScheme } from "@mantine/core";
import type { FC } from "react";
import { Toaster } from "sonner";
import styles from "./toaster.module.scss";

export const DSToaster: FC = () => {
  const colorScheme = useComputedColorScheme("light", { getInitialValueInEffect: true });

  return <Toaster theme={colorScheme} toastOptions={{ classNames: { toast: styles.toast } }} />;
};
