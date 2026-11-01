import { NewProjectPage } from "@/modules/projects/new-project";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "New project" };

const NewProjectRoute: FC = () => {
  return <NewProjectPage />;
};

export default NewProjectRoute;
