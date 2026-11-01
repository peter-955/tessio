import { DSSkeleton } from "@/components/design-system";
import type { FC } from "react";
import styles from "./loading-state.module.scss";

interface Props {
  label: string;
  lineCount?: number;
}

export const LoadingState: FC<Props> = ({ label, lineCount = 4 }) => {
  return (
    <div className={styles.root} role="status" aria-busy="true" aria-label={label}>
      <DSSkeleton height={20} width="40%" />
      <DSSkeleton lineCount={lineCount} />
    </div>
  );
};
