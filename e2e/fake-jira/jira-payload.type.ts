export interface JiraAccountPayload {
  accountId: string;
  displayName: string;
  emailAddress: string;
}

export interface JiraProjectPayload {
  id: string;
  key: string;
  name: string;
}

export interface JiraBoardPayload {
  id: number;
  name: string;
  type: string;
}

export interface JiraSprintPayload {
  id: number;
  name: string;
  state: "active" | "future" | "closed";
  startDate: string;
  endDate: string;
}

export interface AdfTextNode {
  type: "text";
  text: string;
}

export interface AdfParagraphNode {
  type: "paragraph";
  content: AdfTextNode[];
}

export interface AdfHeadingNode {
  type: "heading";
  attrs: { level: number };
  content: AdfTextNode[];
}

export interface AdfListItemNode {
  type: "listItem";
  content: AdfParagraphNode[];
}

export interface AdfBulletListNode {
  type: "bulletList";
  content: AdfListItemNode[];
}

export interface AdfDocument {
  type: "doc";
  version: 1;
  content: Array<AdfParagraphNode | AdfHeadingNode | AdfBulletListNode>;
}

export interface JiraIssuePayload {
  id: string;
  key: string;
  fields: {
    summary: string;
    description: AdfDocument | null;
    status: { name: string };
    issuetype: { name: string; subtask: boolean };
    updated: string;
  };
}

export interface JiraStoryFixture {
  key: string;
  summary: string;
  acceptanceCriteria: string[];
}
