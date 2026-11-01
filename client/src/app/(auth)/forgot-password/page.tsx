import { ForgotPasswordPage } from "@/modules/auth/forgot-password";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Forgot password" };

const ForgotPasswordRoute: FC = () => {
  return <ForgotPasswordPage />;
};

export default ForgotPasswordRoute;
