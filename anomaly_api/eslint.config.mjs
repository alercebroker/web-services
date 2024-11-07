import globals from "globals";
import pluginJs from "@eslint/js";

export default [
  {
    ignores: [
      ".venv",
      "tailwind.config.js",
    ],
  },
  {
    languageOptions: { globals: globals.browser },
  },
  pluginJs.configs.recommended,
];
