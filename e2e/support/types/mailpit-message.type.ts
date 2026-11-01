export interface MailpitMessageSummary {
  ID: string;
}

export interface MailpitSearchResult {
  messages: MailpitMessageSummary[];
}

export interface MailpitMessageDetail {
  ID: string;
  Text: string;
}
