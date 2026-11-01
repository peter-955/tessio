import { Textarea } from "@mantine/core";
import type { ChangeEvent, FC, ReactNode } from "react";
import styles from "./textarea.module.scss";

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  description?: string;
  error?: ReactNode;
  isRequired?: boolean;
  isDisabled?: boolean;
  minRows?: number;
  maxRows?: number;
  isAutosize?: boolean;
  maxLength?: number;
  isMonospace?: boolean;
}

export const DSTextarea: FC<Props> = ({
  label,
  value,
  onChange,
  placeholder,
  description,
  error,
  isRequired = false,
  isDisabled = false,
  minRows = 3,
  maxRows = 12,
  isAutosize = true,
  maxLength,
  isMonospace = false,
}) => {
  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>): void => {
    onChange(event.currentTarget.value);
  };

  return (
    <Textarea
      label={label}
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      description={description}
      error={error}
      required={isRequired}
      disabled={isDisabled}
      minRows={minRows}
      maxRows={maxRows}
      rows={minRows}
      autosize={isAutosize}
      maxLength={maxLength}
      classNames={isMonospace ? { input: styles.monospace } : undefined}
      size="sm"
    />
  );
};
