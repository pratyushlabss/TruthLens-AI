import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TruthLens - AI Misinformation Analysis",
  description: "Professional-grade AI Misinformation Analysis Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.variable} bg-background text-foreground font-inter antialiased overflow-hidden`}
      >
        {children}
      </body>
    </html>
  );
}
