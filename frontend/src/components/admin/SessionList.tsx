import React from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../../services/api';
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

  const handleEndSession = async (sessionId: string) => {
      if (window.confirm("Are you sure you want to FORCE END this session? This will disconnect all participants.")) {
          try {
              await apiClient.endSession(sessionId); // Assuming apiClient is imported or available via context if not global
              // But wait, apiClient is imported at top.
              // We need to import it if it's not.
              // It is imported as: import { apiClient } from '../services/api'; in line 2 of previous file read?
              // Wait, I need to check imports.
              // Checking file read... Yes line 2 has `import { apiClient } from '../services/api';`
              // So I can use it.
              
              onRefresh(); // Refresh list to show updated status
              alert("Session ended successfully.");
          } catch (e) {
              console.error(e);
              alert("Failed to end session.");
          }
      }
  };

  // Split sessions
  // Active Only (Live) - Removed 'pending' to avoid duplication with Bookings list
  const activeSessions = sessions
    .filter(s => ['active'].includes(s.status))
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const participantSessions = sessions
    .filter(s => !['active', 'pending'].includes(s.status))
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const renderTable = (data: any[], title: string, showEndButton: boolean = false) => {
      if (data.length === 0) return null;
      return (
        <div className="sessions-section">
            <h4 style={{ margin: '20px 0 10px', color: '#555' }}>{title}</h4>
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
                  {data.map((session) => (
                    <tr key={session.id} className={session.status === 'active' ? 'row-active' : ''}>
                      <td>
                        {session.status === 'active' && <span className="active-dot"></span>}
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
                          className={`open-button ${session.status === 'active' ? 'btn-active-join' : ''}`}
                          disabled={session.status === 'expired'}
                        >
                          {session.status === 'active' ? 'Join Active Meeting' : 'Open Details'}
                        </button>
                        
                        {showEndButton && (
                            <button
                                onClick={() => handleEndSession(session.id)}
                                className="end-button"
                                title="Force End Session"
                                style={{ marginLeft: '8px', background: '#dc3545' }}
                            >
                                End
                            </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
        </div>
      );
  };

  return (
    <div className="session-list">
      <div className="list-header">
        <div className="header-left">
            <span>Total sessions: {sessions.length}</span>
             {/* Filter removed as we are splitting tables now, less needed, but could keep if requested. 
                 User asked for "another place", so splitting is better. */}
        </div>
        <button onClick={onRefresh} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {sessions.length === 0 ? (
        <p className="no-sessions">No sessions found.</p>
      ) : (
        <>
            {activeSessions.length > 0 ? renderTable(activeSessions, "🟢 Live Active Sessions", true) : <p style={{padding: '20px', textAlign: 'center', background: '#f9f9f9', borderRadius: '8px', color: '#888'}}>No meetings are currently running (Live).</p>}
            
            {participantSessions.length > 0 && renderTable(participantSessions, "📜 Past Sessions (Completed / Expired)")}
        </>
      )}
    </div>
  );
};

export default SessionList;
