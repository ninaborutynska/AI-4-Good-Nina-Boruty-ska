import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "Autonomous Driving Sentiment Monitor",
  description: "Public sentiment toward self-driving cars from real YouTube comments. SDG 9 university research prototype.",
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
