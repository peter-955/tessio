import { Loader } from "@mantine/core";
import type { FC } from "react";

interface Props {
  size?: "sm" | "md";
}

export const DSLoader: FC<Props> = ({ size = "sm" }) => {
  return <Loader size={size} />;
};
