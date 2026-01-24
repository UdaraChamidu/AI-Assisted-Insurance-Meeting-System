import React from 'react';
import { useNavigate } from 'react-router-dom';
import './SessionList.css';

interface SessionListProps {
  sessions: any[];
  onRefresh: () => void;
}

const SessionList: React.FC<SessionListProps> = ({ sessions, onRefresh }) => {
  const navigate = useNavigate();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#4caf50';
      case 'pending':
        return '#ff9800';
      case 'completed':
        return '#2196f3';
      case 'expired':
        return '#f44336';
      default:
        return '#999';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleOpenSession = (sessionId: string) => {
    navigate(`/agent/${sessionId}`);
  };

  return (
    <div className="session-list">
      <div className="list-header">
        <span>Total sessions: {sessions.length}</span>
        <button onClick={onRefresh} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {sessions.length === 0 ? (
        <p className="no-sessions">No sessions yet. Create a lead and send SMS to get started!</p>
      ) : (
        <div className="sessions-table">
          <table>
            <thead>
              <tr>
                <th>Session ID</th>
                <th>Status</th>
                <th>Created</th>
                <th>Participants</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.id}>
                  <td>
                    <code>{session.id.substring(0, 8)}...</code>
                  </td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(session.status) }}
                    >
                      {session.status}
                    </span>
                  </td>
                  <td>{formatDate(session.created_at)}</td>
                  <td>
                    {session.participants.length > 0
                      ? session.participants.map((p: any) => p.role).join(', ')
                      : 'None'}
                  </td>
                  <td>
                    <button
                      onClick={() => handleOpenSession(session.id)}
                      className="open-button"
                      disabled={session.status === 'expired'}
                    >
                      Open Session
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default SessionList;
