import React, { useState } from 'react';
import { apiClient } from '../../services/api';
import './SendSMS.css';

interface SendSMSProps {
  onSuccess?: () => void;
}

const SendSMS: React.FC<SendSMSProps> = ({ onSuccess }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await apiClient.createLead({
        phone_number: phoneNumber,
        customer_name: customerName || undefined,
        notes: notes || undefined,
      });

      setMessage('✅ SMS sent successfully!');
      setPhoneNumber('');
      setCustomerName('');
      setNotes('');

      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      setMessage(`❌ Failed to send SMS: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="send-sms">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="phoneNumber">Phone Number *</label>
          <input
            type="tel"
            id="phoneNumber"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder="+1234567890"
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="customerName">Customer Name (Optional)</label>
          <input
            type="text"
            id="customerName"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            placeholder="John Doe"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">Notes (Optional)</label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any notes about the lead..."
            rows={3}
            disabled={loading}
          />
        </div>

        <button type="submit" disabled={loading} className="send-button">
          {loading ? 'Sending...' : '📱 Send SMS with Booking Link'}
        </button>
      </form>

      {message && (
        <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default SendSMS;
