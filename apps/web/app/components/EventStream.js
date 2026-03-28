export default function EventStream({ events }) {
  if (!events.length) {
    return <div className="empty-state">Connect a run to start receiving live orchestration events.</div>;
  }

  return (
    <div className="event-list">
      {events.slice().reverse().map((event) => (
        <div className="event-item" key={`${event.sequence}-${event.type}`}>
          <div className="topbar">
            <strong>{event.type}</strong>
            <span className="subtle">#{event.sequence}</span>
          </div>
          <div className="subtle">{new Date(event.timestamp).toLocaleString()}</div>
          <code>{JSON.stringify(event.payload, null, 2)}</code>
        </div>
      ))}
    </div>
  );
}
