import type { FC, ReactNode } from "react";
import { readLanguageFromCookies } from "../utils/language-cookie.util";
import { AppProvider } from "./app-provider";

interface Props {
  children: ReactNode;
}

export const AppRoot: FC<Props> = async ({ children }) => {
  const language = await readLanguageFromCookies();

  return <AppProvider language={language}>{children}</AppProvider>;
};
