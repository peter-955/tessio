export interface DSSelectOption<T extends string> {
  value: T;
  label: string;
  isDisabled?: boolean;
}
