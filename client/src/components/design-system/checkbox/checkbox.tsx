import { Checkbox } from "@mantine/core";
import type { ChangeEvent, FC, ReactNode } from "react";

interface Props {
  label: ReactNode;
  isChecked: boolean;
  onChange: (isChecked: boolean) => void;
  description?: string;
  error?: ReactNode;
  isDisabled?: boolean;
  isIndeterminate?: boolean;
}

export const DSCheckbox: FC<Props> = ({
  label,
  isChecked,
  onChange,
  description,
  error,
  isDisabled = false,
  isIndeterminate = false,
}) => {
  const handleChange = (event: ChangeEvent<HTMLInputElement>): void => {
    onChange(event.currentTarget.checked);
  };

  return (
    <Checkbox
      label={label}
      checked={isChecked}
      onChange={handleChange}
      description={description}
      error={error}
      disabled={isDisabled}
      indeterminate={isIndeterminate}
      size="sm"
    />
  );
};
