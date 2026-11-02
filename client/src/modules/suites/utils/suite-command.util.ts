import { RUN_SUITE_COMMAND_PREFIX } from "../typing/constants/suite.constant";

const WHITESPACE_PATTERN = /\s/;

const QUOTE = '"';

export const buildRunSuiteCommand = (suite: { id: string; name: string }): string => {
  if (suite.name.includes(QUOTE)) {
    return `${RUN_SUITE_COMMAND_PREFIX} ${suite.id}`;
  }

  const reference = WHITESPACE_PATTERN.test(suite.name)
    ? `${QUOTE}${suite.name}${QUOTE}`
    : suite.name;

  return `${RUN_SUITE_COMMAND_PREFIX} ${reference}`;
};
