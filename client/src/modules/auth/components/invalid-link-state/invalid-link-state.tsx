import { DSAlert, DSButtonLink, DSStack } from "@/components/design-system";
import type { FC } from "react";

interface Props {
  message: string;
  href: string;
  linkLabel: string;
}

export const InvalidLinkState: FC<Props> = ({ message, href, linkLabel }) => {
  return (
    <DSStack gap={4}>
      <DSAlert color="danger">{message}</DSAlert>
      <DSButtonLink href={href} type="primary" isFullWidth>
        {linkLabel}
      </DSButtonLink>
    </DSStack>
  );
};
