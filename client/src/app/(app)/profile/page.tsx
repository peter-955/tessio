import { ProfilePage } from "@/modules/profile/profile";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Profile" };

const ProfileRoute: FC = () => {
  return <ProfilePage />;
};

export default ProfileRoute;
