"use client";

import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { createContext } from "react";

export const SessionGuardContext = createContext<CurrentUser | null>(null);
