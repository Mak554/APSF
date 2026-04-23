import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "APSF – Adaptive Phishing Simulation Framework",
  description: "A data-driven framework to reduce phishing susceptibility through adaptive training and real-time risk scoring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
