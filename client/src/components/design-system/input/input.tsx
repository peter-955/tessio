import { TextInput } from "@mantine/core";
import type { ChangeEvent, FC } from "react";

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  description?: string;
  error?: string;
  isRequired?: boolean;
  isDisabled?: boolean;
  type?: "text" | "email";
  autoComplete?: string;
  isAutoFocused?: boolean;
}

export const DSInput: FC<Props> = ({
  label,
  value,
  onChange,
  placeholder,
  description,
  error,
  isRequired = false,
  isDisabled = false,
  type = "text",
  autoComplete,
  isAutoFocused = false,
}) => {
  const handleChange = (event: ChangeEvent<HTMLInputElement>): void => {
    onChange(event.currentTarget.value);
  };

  return (
    <TextInput
      label={label}
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      description={description}
      error={error}
      required={isRequired}
      disabled={isDisabled}
      type={type}
      autoComplete={autoComplete}
      autoFocus={isAutoFocused}
    />
  );
};
