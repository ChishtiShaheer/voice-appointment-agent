import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Voice Appointment Agent",
  description: "AI voice appointment booking prototype",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-body">{children}</body>
    </html>
  );
}
