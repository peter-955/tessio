import {
  ADMIN_CAPABILITIES,
  buildProject,
  VIEWER_CAPABILITIES,
} from "@/components/project-context/test/utils/project-fixture.util";
import { describe, expect, it } from "vitest";
import {
  buildProjectHref,
  buildProjectSwitchHref,
  checkIsActiveRoute,
  readProjectSection,
} from "./navigation.util";

const viewerProject = buildProject({ key: "DOCS", capabilities: VIEWER_CAPABILITIES });
const adminProject = buildProject({ key: "DOCS", capabilities: ADMIN_CAPABILITIES });

describe("buildProjectHref", () => {
  it("builds the overview and section hrefs", () => {
    expect(buildProjectHref("SHOP", "")).toBe("/projects/SHOP");
    expect(buildProjectHref("SHOP", "runs")).toBe("/projects/SHOP/runs");
  });
});

describe("checkIsActiveRoute", () => {
  it("matches only the exact path when the match is exact", () => {
    expect(checkIsActiveRoute("/projects/SHOP", "/projects/SHOP", true)).toBe(true);
    expect(checkIsActiveRoute("/projects/SHOP/runs", "/projects/SHOP", true)).toBe(false);
  });

  it("matches nested paths by segment when the match is a prefix", () => {
    expect(checkIsActiveRoute("/projects/SHOP/runs", "/projects/SHOP/runs", false)).toBe(true);
    expect(checkIsActiveRoute("/projects/SHOP/runs/42", "/projects/SHOP/runs", false)).toBe(true);
    expect(checkIsActiveRoute("/projects/SHOP/runsheet", "/projects/SHOP/runs", false)).toBe(false);
  });
});

describe("readProjectSection", () => {
  it("reads the first part after the project key", () => {
    expect(readProjectSection("/projects/SHOP/runs/42", "SHOP")).toBe("runs");
    expect(readProjectSection("/projects/SHOP", "SHOP")).toBe("");
    expect(readProjectSection("/projects/OTHER/runs", "SHOP")).toBe("");
    expect(readProjectSection("/", "SHOP")).toBe("");
  });
});

describe("buildProjectSwitchHref", () => {
  it("keeps the section the target project allows", () => {
    expect(buildProjectSwitchHref("/projects/SHOP/stories", "SHOP", viewerProject)).toBe(
      "/projects/DOCS/stories",
    );
  });

  it("goes to the overview when the target project lacks the section capability", () => {
    expect(buildProjectSwitchHref("/projects/SHOP/settings", "SHOP", viewerProject)).toBe(
      "/projects/DOCS",
    );
    expect(buildProjectSwitchHref("/projects/SHOP/settings", "SHOP", adminProject)).toBe(
      "/projects/DOCS/settings",
    );
  });

  it("sends a deep page to its section", () => {
    expect(buildProjectSwitchHref("/projects/SHOP/runs/42", "SHOP", viewerProject)).toBe(
      "/projects/DOCS/runs",
    );
  });

  it("goes to the overview without a current project or a known section", () => {
    expect(buildProjectSwitchHref("/projects", null, viewerProject)).toBe("/projects/DOCS");
    expect(buildProjectSwitchHref("/projects/SHOP/unknown", "SHOP", viewerProject)).toBe(
      "/projects/DOCS",
    );
  });
});
