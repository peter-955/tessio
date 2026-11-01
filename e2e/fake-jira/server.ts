import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import {
  JIRA_ACCOUNT,
  JIRA_ACTIVE_SPRINT,
  JIRA_BOARD,
  JIRA_PROJECT,
  SPRINT_ISSUES,
} from "./jira-fixtures.ts";

const DEFAULT_PORT = 3000;
const SPRINT_CLAUSE_PATTERN = /\bsprint\s*=\s*(\d+)/i;
const BOARD_SPRINTS_PATH = `/rest/agile/1.0/board/${JIRA_BOARD.id}/sprint`;

const sendJson = (response: ServerResponse, statusCode: number, body: unknown): void => {
  response.writeHead(statusCode, { "Content-Type": "application/json" });
  response.end(JSON.stringify(body));
};

const hasBasicAuthorization = (request: IncomingMessage): boolean =>
  (request.headers.authorization ?? "").startsWith("Basic ");

const readBody = async (request: IncomingMessage): Promise<string> => {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk)));
  }
  return Buffer.concat(chunks).toString("utf8");
};

const readJql = (body: string): string => {
  try {
    const parsed: unknown = JSON.parse(body);
    if (typeof parsed === "object" && parsed !== null && "jql" in parsed) {
      return typeof parsed.jql === "string" ? parsed.jql : "";
    }
  } catch {
    return "";
  }
  return "";
};

const readSprintId = (jql: string): number | null => {
  const sprintMatch = SPRINT_CLAUSE_PATTERN.exec(jql);
  return sprintMatch?.[1] === undefined ? null : Number(sprintMatch[1]);
};

const handleRequest = async (request: IncomingMessage, response: ServerResponse): Promise<void> => {
  const url = new URL(request.url ?? "/", "http://fake-jira");
  const method = request.method ?? "GET";

  if (method === "GET" && url.pathname === "/health") {
    sendJson(response, 200, { status: "ok" });
    return;
  }
  if (!hasBasicAuthorization(request)) {
    sendJson(response, 401, { errorMessages: ["Authentication required"] });
    return;
  }
  if (method === "GET" && url.pathname === "/rest/api/3/myself") {
    sendJson(response, 200, JIRA_ACCOUNT);
    return;
  }
  if (method === "GET" && url.pathname === "/rest/api/3/project/search") {
    sendJson(response, 200, {
      startAt: 0,
      maxResults: 50,
      total: 1,
      isLast: true,
      values: [JIRA_PROJECT],
    });
    return;
  }
  if (method === "GET" && url.pathname === "/rest/agile/1.0/board") {
    const projectKeyOrId = url.searchParams.get("projectKeyOrId");
    if (projectKeyOrId !== JIRA_PROJECT.key && projectKeyOrId !== JIRA_PROJECT.id) {
      sendJson(response, 404, { errorMessages: ["No project could be found"] });
      return;
    }
    sendJson(response, 200, {
      startAt: 0,
      maxResults: 50,
      total: 1,
      isLast: true,
      values: [JIRA_BOARD],
    });
    return;
  }
  if (method === "GET" && url.pathname === BOARD_SPRINTS_PATH) {
    sendJson(response, 200, {
      startAt: 0,
      maxResults: 50,
      isLast: true,
      values: [JIRA_ACTIVE_SPRINT],
    });
    return;
  }
  if (method === "POST" && url.pathname === "/rest/api/3/search/jql") {
    const sprintId = readSprintId(readJql(await readBody(request)));
    const issues = sprintId === JIRA_ACTIVE_SPRINT.id ? SPRINT_ISSUES : [];
    sendJson(response, 200, { issues, isLast: true });
    return;
  }
  sendJson(response, 404, { errorMessages: ["Not found"] });
};

const port = Number(process.env.PORT ?? DEFAULT_PORT);

createServer((request, response) => {
  handleRequest(request, response).catch((error: unknown) => {
    sendJson(response, 500, { errorMessages: [String(error)] });
  });
}).listen(port, () => {
  process.stdout.write(`Fake Jira listening on ${port}\n`);
});
