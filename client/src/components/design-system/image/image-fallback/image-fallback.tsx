import type { FC } from "react";
import { DSIcon } from "../../icon/icon";
import { DSText } from "../../text/text";
import styles from "./image-fallback.module.scss";

interface Props {
  label: string;
  width?: number | string;
  height?: number | string;
}

export const DSImageFallback: FC<Props> = ({ label, width, height }) => {
  return (
    <div className={styles.fallback} style={{ width, height }}>
      <DSIcon name="photoOff" size={24} />
      <DSText size="sm" color="muted">
        {label}
      </DSText>
    </div>
  );
};
