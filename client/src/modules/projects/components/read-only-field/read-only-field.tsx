import { DSInput } from "@/components/design-system";
import type { FC } from "react";

interface Props {
  label: string;
  value: string;
}

export const ReadOnlyField: FC<Props> = ({ label, value }) => {
  const ignoreChange = (): void => {
    return;
  };

  return <DSInput label={label} value={value} onChange={ignoreChange} isDisabled />;
};
