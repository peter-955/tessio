export const HEADING_BULLET_LIST_DOCUMENT: unknown = {
  type: "doc",
  version: 1,
  content: [
    { type: "paragraph", content: [{ type: "text", text: "As a shopper I want to pay by card." }] },
    {
      type: "bulletList",
      content: [
        {
          type: "listItem",
          content: [
            {
              type: "paragraph",
              content: [{ type: "text", text: "Context note, not a criterion" }],
            },
          ],
        },
      ],
    },
    {
      type: "heading",
      attrs: { level: 2 },
      content: [{ type: "text", text: "Acceptance Criteria" }],
    },
    {
      type: "bulletList",
      content: [
        {
          type: "listItem",
          content: [
            { type: "paragraph", content: [{ type: "text", text: "Card   payment   succeeds" }] },
          ],
        },
        {
          type: "listItem",
          content: [
            {
              type: "paragraph",
              content: [
                { type: "text", text: "Declined card shows " },
                { type: "text", text: "an error", marks: [{ type: "strong" }] },
              ],
            },
          ],
        },
        {
          type: "listItem",
          content: [{ type: "paragraph", content: [{ type: "text", text: "   " }] }],
        },
      ],
    },
    { type: "heading", attrs: { level: 2 }, content: [{ type: "text", text: "Notes" }] },
    {
      type: "bulletList",
      content: [
        {
          type: "listItem",
          content: [{ type: "paragraph", content: [{ type: "text", text: "Out of scope" }] }],
        },
      ],
    },
  ],
};

export const LIST_IN_PANEL_DOCUMENT: unknown = {
  type: "doc",
  version: 1,
  content: [
    { type: "paragraph", content: [{ type: "text", text: "Search products by name." }] },
    {
      type: "panel",
      attrs: { panelType: "info" },
      content: [
        {
          type: "heading",
          attrs: { level: 4 },
          content: [{ type: "text", text: "Acceptance criteria" }],
        },
        {
          type: "bulletList",
          content: [
            {
              type: "listItem",
              content: [
                {
                  type: "paragraph",
                  content: [{ type: "text", text: "Results match the search text" }],
                },
              ],
            },
            {
              type: "listItem",
              content: [
                {
                  type: "paragraph",
                  content: [{ type: "text", text: "No results shows an empty state" }],
                },
              ],
            },
          ],
        },
      ],
    },
  ],
};

export const TASK_LIST_DOCUMENT: unknown = {
  type: "doc",
  version: 1,
  content: [
    { type: "paragraph", content: [{ type: "text", text: "Critères d’acceptation" }] },
    {
      type: "taskList",
      attrs: { localId: "list-1" },
      content: [
        {
          type: "taskItem",
          attrs: { localId: "item-1", state: "TODO" },
          content: [{ type: "text", text: "Le panier se vide" }],
        },
        {
          type: "taskItem",
          attrs: { localId: "item-2", state: "DONE" },
          content: [{ type: "text", text: "Le total est mis à jour" }],
        },
        {
          type: "taskList",
          attrs: { localId: "list-2" },
          content: [
            {
              type: "taskItem",
              attrs: { localId: "item-3", state: "TODO" },
              content: [{ type: "text", text: "TVA incluse" }],
            },
          ],
        },
      ],
    },
  ],
};

export const MENTIONS_HARD_BREAK_DOCUMENT: unknown = {
  type: "doc",
  version: 1,
  content: [
    {
      type: "heading",
      attrs: { level: 1 },
      content: [{ type: "text", text: "Acceptance criteria" }],
    },
    {
      type: "bulletList",
      content: [
        {
          type: "listItem",
          content: [
            {
              type: "paragraph",
              content: [
                { type: "mention", attrs: { id: "abc", text: "@Alice" } },
                { type: "text", text: " approves the refund" },
                { type: "hardBreak" },
                { type: "text", text: "within  2 days " },
                { type: "emoji", attrs: { shortName: ":tada:", text: "🎉" } },
              ],
            },
            {
              type: "bulletList",
              content: [
                {
                  type: "listItem",
                  content: [
                    { type: "paragraph", content: [{ type: "text", text: "Email is sent" }] },
                  ],
                },
                {
                  type: "listItem",
                  content: [
                    {
                      type: "paragraph",
                      content: [
                        { type: "text", text: "Status becomes " },
                        { type: "status", attrs: { text: "REFUNDED", color: "green" } },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },
        {
          type: "listItem",
          content: [
            {
              type: "paragraph",
              content: [
                { type: "text", text: "See " },
                { type: "inlineCard", attrs: { url: "https://docs.shop.test/refunds" } },
              ],
            },
          ],
        },
      ],
    },
  ],
};

export const RICH_DOCUMENT: unknown = {
  type: "doc",
  version: 1,
  content: [
    {
      type: "table",
      attrs: { layout: "default" },
      content: [
        {
          type: "tableRow",
          content: [
            {
              type: "tableHeader",
              content: [{ type: "paragraph", content: [{ type: "text", text: "Card" }] }],
            },
            {
              type: "tableHeader",
              content: [{ type: "paragraph", content: [{ type: "text", text: "Result" }] }],
            },
          ],
        },
        {
          type: "tableRow",
          content: [
            {
              type: "tableCell",
              attrs: { colspan: 2 },
              content: [{ type: "paragraph", content: [{ type: "text", text: "Visa approved" }] }],
            },
          ],
        },
      ],
    },
    {
      type: "codeBlock",
      attrs: { language: "json" },
      content: [{ type: "text", text: '{"amount": 10}' }],
    },
    {
      type: "paragraph",
      content: [
        { type: "text", text: "Read the ", marks: [] },
        {
          type: "text",
          text: "guide",
          marks: [{ type: "link", attrs: { href: "https://docs.shop.test/guide" } }],
        },
        { type: "text", text: " but not " },
        {
          type: "text",
          text: "this trap",
          marks: [{ type: "link", attrs: { href: "javascript:alert(1)" } }, { type: "strong" }],
        },
        { type: "text", text: " or ", marks: [] },
        { type: "text", text: "old", marks: [{ type: "strike" }] },
        { type: "text", text: "x", marks: [{ type: "subsup", attrs: { type: "sub" } }] },
        { type: "text", text: "2", marks: [{ type: "subsup", attrs: { type: "sup" } }] },
        { type: "text", text: "tap", marks: [{ type: "code" }] },
      ],
    },
    {
      type: "orderedList",
      attrs: { order: 3 },
      content: [
        {
          type: "listItem",
          content: [{ type: "paragraph", content: [{ type: "text", text: "Third step" }] }],
        },
      ],
    },
    { type: "rule" },
    {
      type: "expand",
      attrs: { title: "More details" },
      content: [{ type: "paragraph", content: [{ type: "text", text: "Hidden text" }] }],
    },
    { type: "mediaSingle", content: [{ type: "media", attrs: { id: "m1", type: "file" } }] },
    { type: "paragraph", content: [{ type: "date", attrs: { timestamp: "1761868800000" } }] },
    {
      type: "inlineCardWrapper",
      content: [
        {
          type: "paragraph",
          content: [{ type: "inlineCard", attrs: { url: "javascript:alert(2)" } }],
        },
      ],
    },
    { type: "unknownLeaf" },
  ],
};
