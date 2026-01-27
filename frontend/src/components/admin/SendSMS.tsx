import React, { useState } from 'react';
import emailjs from '@emailjs/browser';
import { apiClient } from '../../services/api';
import './SendSMS.css';

// Ensure EmailJS is initialized
// We might have initialized it in BookingPage, but safe to do here too or move to App.tsx
// To avoid double init warning, we check if window has it, but standard init is idempotent usually.
emailjs.init(import.meta.env.VITE_EMAILJS_PUBLIC_KEY);

interface SendSMSProps {
  onSuccess?: () => void;
}

const SendSMS: React.FC<SendSMSProps> = ({ onSuccess }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [email, setEmail] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [notes, setNotes] = useState('');
  
  const [sendSMS, setSendSMS] = useState(true);
  const [sendEmail, setSendEmail] = useState(true);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    if (!sendSMS && !sendEmail) {
        setMessage('❌ Please select at least one method (SMS or Email).');
        setLoading(false);
        return;
    }

    try {
      let smsSuccess = false;
      let emailSuccess = false;

      // 1. Send SMS (via Backend Create Lead)
      if (sendSMS) {
          if (!phoneNumber) throw new Error("Phone number required for SMS");
          await apiClient.createLead({
            phone_number: phoneNumber,
            customer_name: customerName || undefined,
            notes: notes || undefined,
          });
          smsSuccess = true;
      }

      // 2. Send Email (via EmailJS)
      if (sendEmail) {
          if (!email) throw new Error("Email required for Email notification");
          
          const bookingUrl = `${window.location.origin}/booking?from_admin=true`; // Generic booking link
          
          await emailjs.send(
              import.meta.env.VITE_EMAILJS_SERVICE_ID,
              import.meta.env.VITE_EMAILJS_TEMPLATE_ID,
              {
                  customer_email: email,
                  customer_name: customerName || 'Customer',
                  meeting_time: 'Ready to schedule',
                  join_link: bookingUrl,
                  description: notes || 'Please verify your contact info.',
              }
          );
          emailSuccess = true;
      }

      let successMsg = '✅ ';
      if (smsSuccess && emailSuccess) successMsg += 'SMS & Email sent!';
      else if (smsSuccess) successMsg += 'SMS sent!';
      else if (emailSuccess) successMsg += 'Email sent!';

      setMessage(successMsg);
      
      // Reset form
      setPhoneNumber('');
      setEmail('');
      setCustomerName('');
      setNotes('');

      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      setMessage(`❌ Failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="send-sms">
      <form onSubmit={handleSubmit}>
        <div style={{display: 'flex', gap: '20px', marginBottom: '15px'}}>
            <label>
                <input 
                    type="checkbox" 
                    checked={sendSMS} 
                    onChange={e => setSendSMS(e.target.checked)} 
                /> Send SMS
            </label>
            <label>
                <input 
                    type="checkbox" 
                    checked={sendEmail} 
                    onChange={e => setSendEmail(e.target.checked)} 
                /> Send Email
            </label>
        </div>

        {sendSMS && (
            <div className="form-group">
            <label htmlFor="phoneNumber">Phone Number *</label>
            <input
                type="tel"
                id="phoneNumber"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+1234567890"
                required={sendSMS}
                disabled={loading}
            />
            </div>
        )}

        {sendEmail && (
            <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="email@example.com"
                required={sendEmail}
                disabled={loading}
            />
            </div>
        )}

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
            placeholder="Add any notes..."
            rows={3}
            disabled={loading}
          />
        </div>

        <button type="submit" disabled={loading} className="send-button">
          {loading ? 'Sending...' : '� Send Notification'}
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
