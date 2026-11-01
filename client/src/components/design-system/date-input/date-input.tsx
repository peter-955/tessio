import { DatePickerInput } from "@mantine/dates";
import type { FC } from "react";
import { DSIcon } from "../icon/icon";

interface Props {
  label: string;
  value: string | null;
  onChange: (value: string | null) => void;
  placeholder?: string;
  isClearable?: boolean;
  isRequired?: boolean;
}

export const DSDateInput: FC<Props> = ({
  label,
  value,
  onChange,
  placeholder,
  isClearable = true,
  isRequired = false,
}) => {
  return (
    <DatePickerInput
      label={label}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      clearable={isClearable}
      required={isRequired}
      valueFormat="MMM D, YYYY"
      leftSection={<DSIcon name="calendar" size={16} />}
    />
  );
};
