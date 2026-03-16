import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: "#6b88ff",
          600: "#5a77ff",
        },
        secondary: {
          500: "#a855f7",
          600: "#9d3ff7",
        },
        background: "#0a0a0a",
        foreground: "#ffffff",
        card: "rgba(20, 20, 20, 0.8)",
      },
      fontFamily: {
        inter: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
