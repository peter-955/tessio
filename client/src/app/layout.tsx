import "@/shared/styles/globals.scss";
import "@mantine/charts/styles.layer.css";
import "@mantine/core/styles.layer.css";
import "@mantine/dates/styles.layer.css";
import "@mantine/dropzone/styles.layer.css";

import { DS_HTML_ATTRIBUTES, DSColorSchemeScript } from "@/components/design-system";
import { AppRoot } from "@/shared/providers/app-root";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Suspense, type FC } from "react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin", "latin-ext", "vietnamese"],
});
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin", "latin-ext", "vietnamese"],
});

export const metadata: Metadata = {
  title: { default: "Tessio", template: "%s · Tessio" },
  description: "Manage automation testing for web development.",
};

const RootLayout: FC<LayoutProps<"/">> = ({ children }) => {
  return (
    <html
      lang="en"
      {...DS_HTML_ATTRIBUTES}
      className={`${geistSans.variable} ${geistMono.variable}`}
    >
      <head>
        <DSColorSchemeScript />
      </head>
      <body>
        <Suspense>
          <AppRoot>{children}</AppRoot>
        </Suspense>
      </body>
    </html>
  );
};

export default RootLayout;
