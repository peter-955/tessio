import { Avatar } from "@mantine/core";
import type { FC } from "react";
import { DS_AVATAR_SIZES } from "./avatar.constant";
import styles from "./avatar.module.scss";
import type { DSAvatarSize } from "./avatar.type";

interface Props {
  name: string;
  src?: string | null;
  size?: DSAvatarSize;
  isDeactivated?: boolean;
}

export const DSAvatar: FC<Props> = ({ name, src, size = "md", isDeactivated = false }) => {
  return (
    <Avatar
      name={name}
      src={src ?? undefined}
      alt={name}
      color="initials"
      size={DS_AVATAR_SIZES[size]}
      className={isDeactivated ? styles.deactivated : undefined}
    />
  );
};
