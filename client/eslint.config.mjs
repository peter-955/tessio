import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import { defineConfig, globalIgnores } from "eslint/config";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      curly: ["error", "all"],
      "prefer-arrow-callback": "error",
      "no-restricted-syntax": [
        "error",
        {
          selector: "FunctionDeclaration",
          message: "Use an arrow function: const name = (...) => { ... }.",
        },
        {
          selector: "FunctionExpression:not(MethodDefinition > FunctionExpression)",
          message: "Use an arrow function.",
        },
        {
          selector: "Literal[raw=/\\d_\\d/]",
          message: "Write numbers without digit separators.",
        },
      ],
      "react/no-multi-comp": ["error", { ignoreStateless: false }],
      "@typescript-eslint/consistent-type-imports": ["error", { fixStyle: "inline-type-imports" }],
      "@typescript-eslint/no-explicit-any": "error",
      "jsx-a11y/click-events-have-key-events": "error",
      "jsx-a11y/no-static-element-interactions": "error",
      "jsx-a11y/no-noninteractive-element-interactions": "error",
      "jsx-a11y/interactive-supports-focus": "error",
      "jsx-a11y/label-has-associated-control": "error",
      "jsx-a11y/anchor-is-valid": "error",
      "jsx-a11y/no-redundant-roles": "error",
      "jsx-a11y/aria-role": "error",
      "jsx-a11y/alt-text": "error",
      "jsx-a11y/aria-props": "error",
      "jsx-a11y/aria-proptypes": "error",
      "jsx-a11y/role-has-required-aria-props": "error",
      "jsx-a11y/role-supports-aria-props": "error",
    },
  },
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts", "src/lib/api/openapi.type.ts"]),
]);

export default eslintConfig;
