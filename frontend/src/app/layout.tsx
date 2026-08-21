// Root layout for the InstaLeads dashboard (Next.js App Router).
// STUB — finalize in M6. See ../../../docs/implementation-plan.md.

// TODO(M6): add metadata, global styles, and app shell.
export const metadata = {
  title: "InstaLeads Dashboard",
  description: "Verified Instagram creator leads",
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
