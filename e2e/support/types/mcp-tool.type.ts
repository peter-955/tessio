export interface McpToolCallResponse {
  result?: {
    isError?: boolean;
    content: { type: string; text: string }[];
  };
  error?: { code: number; message: string };
}

export interface MyGapsReply {
  gap_count: number;
  gaps: {
    id: string;
    story_key: string;
    question: string;
    is_assigned_to_me: boolean;
  }[];
}

export interface AnsweredGapReply {
  status: string;
  open_gap_count: number;
  is_ready: boolean;
}

export interface CreatedApiToken {
  token: string;
  apiToken: { id: string };
}
