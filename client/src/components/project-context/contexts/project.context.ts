"use client";

import { createContext } from "react";
import type { Project } from "../typing/types/project.type";

export const ProjectContext = createContext<Project | null>(null);
