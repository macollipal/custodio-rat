import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    rules: {
      // Desactivado: es un false positive constante en initialization from localStorage/SSR hydration
      "react-hooks/set-state-in-effect": "off",
      // Desactivado: es un false positive en useCallback con dependencias que React infiere de forma diferente
      "react-hooks/preserve-manual-memoization": "off",
    },
  },
]);

export default eslintConfig;
