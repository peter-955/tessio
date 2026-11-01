import { Select, type ComboboxItem } from "@mantine/core";
import type { ReactElement, ReactNode } from "react";
import type { DSSelectOption } from "./select.type";

interface Props<T extends string> {
  label: string;
  value: T | null;
  options: DSSelectOption<T>[];
  onChange: (value: T | null) => void;
  placeholder?: string;
  description?: string;
  error?: ReactNode;
  isRequired?: boolean;
  isDisabled?: boolean;
  isClearable?: boolean;
  isSearchable?: boolean;
  nothingFoundLabel?: string;
}

export const DSSelect = <T extends string>({
  label,
  value,
  options,
  onChange,
  placeholder,
  description,
  error,
  isRequired = false,
  isDisabled = false,
  isClearable = false,
  isSearchable = false,
  nothingFoundLabel,
}: Props<T>): ReactElement => {
  const data: ComboboxItem<T>[] = options.map((option) => {
    return { value: option.value, label: option.label, disabled: option.isDisabled };
  });

  const handleChange = (selectedValue: string | null): void => {
    onChange(options.find((option) => option.value === selectedValue)?.value ?? null);
  };

  return (
    <Select
      label={label}
      value={value}
      data={data}
      onChange={handleChange}
      placeholder={placeholder}
      description={description}
      error={error}
      required={isRequired}
      disabled={isDisabled}
      allowDeselect={isClearable}
      clearable={isClearable}
      searchable={isSearchable}
      nothingFoundMessage={nothingFoundLabel}
      comboboxProps={{ withinPortal: true }}
      size="sm"
    />
  );
};
