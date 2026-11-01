import { ResetPasswordPage } from "@/modules/auth/reset-password";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Reset password" };

const ResetPasswordRoute: FC<PageProps<"/reset-password/[token]">> = async ({ params }) => {
  const { token } = await params;

  return <ResetPasswordPage token={token} />;
};

export default ResetPasswordRoute;
