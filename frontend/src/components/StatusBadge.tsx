// StatusBadge — colored badge for a lead's status (VERIFIED / GOLD).
// STUB — finalize in M6. Status enum mirrors LeadStatus (../../../docs/architecture/data-model.md).

// TODO(M6): map status -> label + color.
export default function StatusBadge({ status }: { status: string }) {
  return <span>{status}</span>;
}
