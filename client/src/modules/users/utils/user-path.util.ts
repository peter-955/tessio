import { USERS_PATH } from "../typing/constants/user.constant";

export const buildUserAccessPath = (userId: string): string => {
  return `${USERS_PATH}/${userId}`;
};

export const buildProjectPath = (projectKey: string): string => {
  return `/projects/${projectKey}`;
};
