export default function StatusPill({ status }) {
  const normalized = (status || 'UNKNOWN').toLowerCase();
  const className = ['status-pill'];

  if (normalized.includes('fail') || normalized.includes('blocked')) {
    className.push('failed');
  }

  return <span className={className.join(' ')}>{status}</span>;
}
