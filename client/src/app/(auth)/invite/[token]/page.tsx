import { AcceptInvitePage } from "@/modules/auth/accept-invite";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Accept invite" };

const AcceptInviteRoute: FC<PageProps<"/invite/[token]">> = async ({ params }) => {
  const { token } = await params;

  return <AcceptInvitePage token={token} />;
};

export default AcceptInviteRoute;
