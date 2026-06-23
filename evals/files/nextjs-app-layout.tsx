import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My App",
  description: "Sample Next.js application",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
