import { Dropzone } from "@mantine/dropzone";
import { useId, type FC } from "react";
import { DSGroup } from "../group/group";
import { DSIcon } from "../icon/icon";
import { DSStack } from "../stack/stack";
import { DSText } from "../text/text";
import styles from "./dropzone.module.scss";

interface Props {
  title: string;
  description: string;
  onDrop: (files: File[]) => void;
  acceptedTypes?: string[];
  maxSizeInBytes?: number;
  isMultiple?: boolean;
  isLoading?: boolean;
}

export const DSDropzone: FC<Props> = ({
  title,
  description,
  onDrop,
  acceptedTypes,
  maxSizeInBytes,
  isMultiple = true,
  isLoading = false,
}) => {
  const descriptionId = useId();

  return (
    <Dropzone
      onDrop={onDrop}
      accept={acceptedTypes}
      maxSize={maxSizeInBytes}
      multiple={isMultiple}
      loading={isLoading}
      radius="lg"
      className={styles.root}
      role="button"
      aria-label={title}
      aria-describedby={descriptionId}
      aria-disabled={isLoading || undefined}
      inputProps={{ "aria-label": title, style: { display: "none" } }}
    >
      <DSGroup gap={4} justify="center" className={styles.content}>
        <DSIcon name="upload" size={32} className={styles.icon} />
        <DSStack gap={1}>
          <DSText weight="medium">{title}</DSText>
          <DSText size="sm" color="muted" id={descriptionId}>
            {description}
          </DSText>
        </DSStack>
      </DSGroup>
    </Dropzone>
  );
};
