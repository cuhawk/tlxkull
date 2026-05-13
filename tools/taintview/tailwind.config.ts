import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        src: "#dc2626",
        sink: "#9f1239",
        hop: "#475569",
      },
    },
  },
  plugins: [],
} satisfies Config;
