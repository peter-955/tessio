import { TwoFactorPage } from "@/modules/auth/two-factor";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Two-factor authentication" };

const TwoFactorRoute: FC = () => {
  return <TwoFactorPage />;
};

export default TwoFactorRoute;
