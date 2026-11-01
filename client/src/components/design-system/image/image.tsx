"use client";

import { Image, Modal } from "@mantine/core";
import { useState, type FC } from "react";
import { DSImageFallback } from "./image-fallback/image-fallback";
import styles from "./image.module.scss";
import type { DSImageFit, DSImageZoomControl } from "./image.type";

type Props = DSImageZoomControl & {
  src: string | null;
  alt: string;
  width?: number | string;
  height?: number | string;
  fit?: DSImageFit;
  fallbackLabel: string;
};

export const DSImage: FC<Props> = ({
  src,
  alt,
  width,
  height,
  fit = "cover",
  isZoomable = false,
  closeLabel,
  fallbackLabel,
}) => {
  const [failedSource, setFailedSource] = useState<string | null>(null);
  const [isZoomOpened, setIsZoomOpened] = useState(false);

  if (src === null || failedSource === src) {
    return <DSImageFallback label={fallbackLabel} width={width} height={height} />;
  }

  const handleError = (): void => {
    setFailedSource(src);
  };

  const image = (
    <Image src={src} alt={alt} w={width} h={height} fit={fit} radius="md" onError={handleError} />
  );

  if (!isZoomable) {
    return image;
  }

  return (
    <>
      <button
        type="button"
        aria-label={alt}
        className={styles.zoomButton}
        onClick={() => {
          setIsZoomOpened(true);
        }}
      >
        {image}
      </button>
      <Modal
        opened={isZoomOpened}
        onClose={() => {
          setIsZoomOpened(false);
        }}
        title={alt}
        size="xl"
        centered
        closeButtonProps={{ "aria-label": closeLabel }}
      >
        <Image src={src} alt={alt} fit="contain" radius="md" className={styles.zoomedImage} />
      </Modal>
    </>
  );
};
