import globals from "globals";
import pluginJs from "@eslint/js";

export default [
  {
    ignores: [
      ".venv",
      "tailwind.config.js",
      "**/echarts.js",
      "**/echarts.min.js",
      "**/astro-dates.js",
      "**/jszip.js",
    ],
  },
  {
    languageOptions: { globals: globals.browser },
  },
  pluginJs.configs.recommended,
];
