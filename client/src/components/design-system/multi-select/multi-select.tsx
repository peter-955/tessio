import { MultiSelect, type ComboboxItem } from "@mantine/core";
import type { ReactElement, ReactNode } from "react";
import type { DSSelectOption } from "../select/select.type";

interface Props<T extends string> {
  label: string;
  value: T[];
  options: DSSelectOption<T>[];
  onChange: (values: T[]) => void;
  placeholder?: string;
  description?: string;
  error?: ReactNode;
  isRequired?: boolean;
  isDisabled?: boolean;
  isSearchable?: boolean;
  maxValues?: number;
  nothingFoundLabel?: string;
}

export const DSMultiSelect = <T extends string>({
  label,
  value,
  options,
  onChange,
  placeholder,
  description,
  error,
  isRequired = false,
  isDisabled = false,
  isSearchable = true,
  maxValues,
  nothingFoundLabel,
}: Props<T>): ReactElement => {
  const data: ComboboxItem<T>[] = options.map((option) => {
    return { value: option.value, label: option.label, disabled: option.isDisabled };
  });

  const handleChange = (selectedValues: string[]): void => {
    onChange(
      selectedValues.flatMap((selectedValue) => {
        const matchingOption = options.find((option) => option.value === selectedValue);

        return matchingOption ? [matchingOption.value] : [];
      }),
    );
  };

  return (
    <MultiSelect
      label={label}
      value={value}
      data={data}
      onChange={handleChange}
      placeholder={placeholder}
      description={description}
      error={error}
      required={isRequired}
      disabled={isDisabled}
      searchable={isSearchable}
      maxValues={maxValues}
      nothingFoundMessage={nothingFoundLabel}
      comboboxProps={{ withinPortal: true }}
      size="sm"
    />
  );
};
