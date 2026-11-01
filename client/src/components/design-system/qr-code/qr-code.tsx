"use client";

import { QRCodeSVG } from "qrcode.react";
import type { FC } from "react";
import styles from "./qr-code.module.scss";

interface Props {
  value: string;
  ariaLabel: string;
  size?: number;
}

export const DSQrCode: FC<Props> = ({ value, ariaLabel, size = 192 }) => {
  return (
    <div className={styles.frame} role="img" aria-label={ariaLabel}>
      <QRCodeSVG
        value={value}
        size={size}
        level="M"
        marginSize={2}
        bgColor="#ffffff"
        fgColor="#000000"
        aria-hidden
      />
    </div>
  );
};
