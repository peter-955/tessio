import { UsersPage } from "@/modules/users/users";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Users" };

const UsersRoute: FC = () => {
  return <UsersPage />;
};

export default UsersRoute;
