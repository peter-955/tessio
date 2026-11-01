import { UserAccessPage } from "@/modules/users/user-access";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "User access" };

const UserAccessRoute: FC<PageProps<"/users/[userId]">> = async ({ params }) => {
  const { userId } = await params;

  return <UserAccessPage userId={userId} />;
};

export default UserAccessRoute;
