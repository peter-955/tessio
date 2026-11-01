import { TwoFactorSetupPage } from "@/modules/auth/two-factor-setup";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Set up two-factor authentication" };

const TwoFactorSetupRoute: FC = () => {
  return <TwoFactorSetupPage />;
};

export default TwoFactorSetupRoute;
