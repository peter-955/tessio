import { Switch } from "@mantine/core";
import type { ChangeEvent, FC } from "react";

interface Props {
  label: string;
  isChecked: boolean;
  onChange: (isChecked: boolean) => void;
  description?: string;
  isDisabled?: boolean;
  labelPosition?: "left" | "right";
}

export const DSSwitch: FC<Props> = ({
  label,
  isChecked,
  onChange,
  description,
  isDisabled = false,
  labelPosition = "right",
}) => {
  const handleChange = (event: ChangeEvent<HTMLInputElement>): void => {
    onChange(event.currentTarget.checked);
  };

  return (
    <Switch
      label={label}
      checked={isChecked}
      onChange={handleChange}
      description={description}
      disabled={isDisabled}
      labelPosition={labelPosition}
      size="sm"
    />
  );
};
