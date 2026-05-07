/**
 * @file Root Layout
 * @module app/layout
 * @description The global layout wrapper for the application. Configures fonts,
 * global providers (React Query), and document-level metadata.
 */

import type { Metadata } from "next";
import { Inter, Newsreader } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/core/providers/QueryProvider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI News Aggregator",
  description: "Personalized AI news curation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${newsreader.variable} antialiased font-sans`} suppressHydrationWarning>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
