import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import SendSMS from '../components/admin/SendSMS';
import SessionList from '../components/admin/SessionList';
import LeadsList from '../components/admin/LeadsList';
import BookingsList from '../components/admin/BookingsList';
import './AdminPage.css';

const AdminPage: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [leads, setLeads] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [sessionsData, leadsData, bookingsData] = await Promise.all([
        apiClient.listSessions(),
        apiClient.listLeads(),
        apiClient.listBookings(),
      ]);
      setSessions(sessionsData);
      setLeads(leadsData);
      setBookings(bookingsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSMSSent = () => {
    // Refresh leads list after sending SMS
    loadData();
  };

  const handleResendSMS = async (leadId: string) => {
    try {
      await apiClient.resendSMS(leadId);
      alert('SMS resent successfully!');
      loadData();
    } catch (error) {
      console.error('Failed to resend SMS:', error);
      alert('Failed to resend SMS. Please try again.');
    }
  };

  const handleSendReminder = async (bookingId: string) => {
    try {
      await apiClient.sendReminder(bookingId);
      alert('Reminder sent successfully!');
    } catch (error) {
      console.error('Failed to send reminder:', error);
      alert('Failed to send reminder. Please try again.');
    }
  };

  return (
    <div className="admin-page">
      <header className="admin-header">
        <h1>🏥 Insurance Agent Admin Panel</h1>
        <p>Manage leads, bookings, sessions, and monitor AI-assisted meetings</p>
      </header>

      <div className="admin-content">
        <section className="admin-section">
          <h2>📱 Send SMS to Customer</h2>
          <SendSMS onSuccess={handleSMSSent} />
        </section>

        <section className="admin-section">
          <h2>📅 Bookings</h2>
          {loading ? (
            <p>Loading bookings...</p>
          ) : (
            <BookingsList
              bookings={bookings}
              onRefresh={loadData}
              onSendReminder={handleSendReminder}
            />
          )}
        </section>

        <section className="admin-section">
          <h2>👥 Leads Database</h2>
          {loading ? (
            <p>Loading leads...</p>
          ) : (
            <LeadsList
              leads={leads}
              onRefresh={loadData}
              onResendSMS={handleResendSMS}
            />
          )}
        </section>

        <section className="admin-section">
          <h2>📊 Active & Recent Sessions</h2>
          {loading ? (
            <p>Loading sessions...</p>
          ) : (
            <SessionList sessions={sessions} onRefresh={loadData} />
          )}
        </section>
      </div>
    </div>
  );
};

export default AdminPage;
