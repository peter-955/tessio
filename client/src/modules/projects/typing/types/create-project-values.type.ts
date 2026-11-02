export type StorySourceChoice = "jira" | "tessio";

export interface CreateProjectValues {
  storySource: StorySourceChoice;
  jiraProjectKey: string | null;
  jiraBoardId: string | null;
  name: string;
  key: string;
  description: string;
}
