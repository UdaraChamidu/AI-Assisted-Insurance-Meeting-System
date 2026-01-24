import React from 'react';
import './LeadsList.css';

interface Lead {
  id: string;
  phone_number: string;
  customer_name?: string;
  notes?: string;
  sms_sent: boolean;
  sms_sent_at?: string;
  created_at: string;
}

interface LeadsListProps {
  leads: Lead[];
  onRefresh: () => void;
  onResendSMS: (leadId: string) => void;
}

const LeadsList: React.FC<LeadsListProps> = ({ leads, onRefresh, onResendSMS }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (leads.length === 0) {
    return (
      <div className="leads-empty">
        <p>📭 No leads yet. Send your first SMS to get started!</p>
      </div>
    );
  }

  return (
    <div className="leads-list">
      <div className="leads-header">
        <h3>📊 All Leads ({leads.length})</h3>
        <button onClick={onRefresh} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="leads-table-wrapper">
        <table className="leads-table">
          <thead>
            <tr>
              <th>📅 Date</th>
              <th>👤 Name</th>
              <th>📱 Phone</th>
              <th>📝 Description</th>
              <th>📧 SMS Status</th>
              <th>⚙️ Actions</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id}>
                <td>{formatDate(lead.created_at)}</td>
                <td>{lead.customer_name || '—'}</td>
                <td>{lead.phone_number}</td>
                <td className="notes-cell">
                  {lead.notes ? (
                    <div className="notes-content" title={lead.notes}>
                      {lead.notes}
                    </div>
                  ) : (
                    '—'
                  )}
                </td>
                <td>
                  {lead.sms_sent ? (
                    <span className="status-sent">
                      ✅ Sent
                      {lead.sms_sent_at && (
                        <small className="sent-time">
                          {formatDate(lead.sms_sent_at)}
                        </small>
                      )}
                    </span>
                  ) : (
                    <span className="status-failed">❌ Failed</span>
                  )}
                </td>
                <td>
                  <button
                    onClick={() => onResendSMS(lead.id)}
                    className="resend-btn"
                    title="Resend SMS"
                  >
                    📤 Resend
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LeadsList;
