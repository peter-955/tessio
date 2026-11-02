# Tessio docs

The shared place to think through Tessio while we build it. Anything we discuss and want to keep ends up here. To run the code, start at the [root README](../README.md).

## Layout

| Folder | What goes in it |
| --- | --- |
| [product/](product/) | Vision, built features, glossary, [release plan](product/release-plan.md). |
| [spec/](spec/) | Functional specs per feature module and the non-functional requirements: what the code does today ([index](spec/README.md)). |
| [guides/](guides/) | [User guide per role](guides/user/README.md), [pilot checklist](guides/pilot.md), [Claude setup](guides/claude-setup.md). |
| [architecture/](architecture/) | How the system fits together: client, server, Claude integration ([overview](architecture/overview.md)). |
| [wbs/](wbs/) | Work Breakdown Structure: every deliverable, with MVP / Later phase ([wbs.md](wbs/wbs.md)). |
| [decisions/](decisions/) | Architecture Decision Records (ADRs): one file per decision, never rewritten once accepted. |
| [design/](design/) | UI references, including the Mobbin components we adopt, the [brand](design/brand/) (logo, colors) and the [user flows and state diagrams](design/user-flows.md). |
| [discussions/](discussions/) | Open questions and proposals. Start with the [testing workflow proposal](discussions/testing-workflow-proposal.md) and the [platform features proposal](discussions/platform-features-proposal.md) (auth, roles, projects, users, files, design system), then the [server proposal](discussions/server-proposal.md) the [Claude drafts test cases proposal](discussions/claude-drafts-cases-proposal.md) and the [readable test cases proposal](discussions/readable-cases-proposal.md). Newest: [execution log](discussions/execution-log-proposal.md), [test data descriptions](discussions/test-data-descriptions-proposal.md) and [projects without Jira](discussions/projects-without-jira-proposal.md) and [why it failed](discussions/failure-diagnosis-proposal.md). Accepted, being built: [competitive features](discussions/competitive-features-proposal.md) (suites, answering gaps with Claude, two-way Jira, scripts from runs) and its [build plan](discussions/competitive-features-plan.md). Proposals record the design; where code differs, spec/ wins. |

## How we work with these docs

1. **New idea or question** → add it to [discussions/open-questions.md](discussions/open-questions.md), or start a new file in `discussions/` if it needs room.
2. **Agreed on something** → write an ADR in `decisions/` (copy [0000-template.md](decisions/0000-template.md)) and link it from the discussion.
3. **Feature takes shape** → write or update its spec file in `spec/` (see [spec/README.md](spec/README.md) for the format), and move it out of the backlog in [product/features.md](product/features.md).
4. **New domain term** → add it to [product/glossary.md](product/glossary.md) so the docs, UI and code use the same words.

Mark each doc's status at the top: `Draft`, `In discussion`, `Accepted` or `Superseded`.
