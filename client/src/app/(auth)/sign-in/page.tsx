import { SignInPage } from "@/modules/auth/sign-in";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Sign in" };

const SignInRoute: FC = () => {
  return <SignInPage />;
};

export default SignInRoute;
