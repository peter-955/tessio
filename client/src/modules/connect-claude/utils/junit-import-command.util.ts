import {
  JUNIT_IMPORT_EXAMPLE_ENVIRONMENT,
  JUNIT_IMPORT_EXAMPLE_FILE,
} from "../typing/constants/api-token.constant";
import type { JunitImportCommandOptions } from "../typing/types/junit-import-command-options.type";
import { quoteShellArgument } from "./plugin-install-command.util";

const LINE_BREAK = " \\\n  ";

export const buildJunitImportCommand = ({
  tessioUrl,
  projectKey,
  token,
}: JunitImportCommandOptions): string => {
  const importUrl = `${tessioUrl}/api/projects/${encodeURIComponent(projectKey)}/runs/import`;

  return [
    `curl -X POST ${quoteShellArgument(importUrl)}`,
    `-H ${quoteShellArgument(`Authorization: Bearer ${token}`)}`,
    `-F ${quoteShellArgument(`file=@${JUNIT_IMPORT_EXAMPLE_FILE}`)}`,
    `-F ${quoteShellArgument(`environment=${JUNIT_IMPORT_EXAMPLE_ENVIRONMENT}`)}`,
  ].join(LINE_BREAK);
};
