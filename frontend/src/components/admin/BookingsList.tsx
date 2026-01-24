import React from 'react';
import './BookingsList.css';

interface Booking {
  id: string;
  customer_name: string;
  customer_email: string;
  scheduled_time: string;
  status: string;
  session_id?: string;
  zoom_meeting_id?: string;
}

interface BookingsListProps {
  bookings: Booking[];
  onRefresh: () => void;
  onSendReminder: (bookingId: string) => void;
}

const BookingsList: React.FC<BookingsListProps> = ({ bookings, onRefresh, onSendReminder }) => {
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  const isUpcoming = (dateString: string) => {
    return new Date(dateString) > new Date();
  };

  // Sort by date
  const sortedBookings = [...bookings].sort((a, b) => 
    new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime()
  );

  const upcomingBookings = sortedBookings.filter(b => isUpcoming(b.scheduled_time));
  const pastBookings = sortedBookings.filter(b => !isUpcoming(b.scheduled_time));

  if (bookings.length === 0) {
    return (
      <div className="bookings-empty">
        <p>📅 No bookings yet</p>
      </div>
    );
  }

  const renderBookingRow = (booking: Booking) => {
    const { date, time } = formatDateTime(booking.scheduled_time);
    const upcoming = isUpcoming(booking.scheduled_time);

    return (
      <tr key={booking.id} className={upcoming ? 'booking-upcoming' : 'booking-past'}>
        <td>{date}</td>
        <td>{time}</td>
        <td>{booking.customer_name}</td>
        <td>{booking.customer_email}</td>
        <td>
          <span className={`status-badge status-${booking.status.toLowerCase()}`}>
            {booking.status}
          </span>
        </td>
        <td>
          {upcoming && (
            <button
              onClick={() => onSendReminder(booking.id)}
              className="btn-reminder"
              title="Send reminder SMS"
            >
              ⏰ Send Reminder
            </button>
          )}
          {booking.session_id && (
            <>
              <a
                href={`/agent/${booking.session_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-join"
                title="Join as Agent (Host)"
              >
                🎥 Host Meeting
              </a>
              <button
                className="btn-copy-link"
                onClick={() => {
                  const url = `${window.location.origin}/join/${booking.session_id}`;
                  navigator.clipboard.writeText(url);
                  alert('Customer link copied to clipboard!');
                }}
                title="Copy Customer Join Link"
              >
                📋 Copy Link
              </button>
            </>
          )}
        </td>
      </tr>
    );
  };

  return (
    <div className="bookings-list">
      <div className="bookings-header">
        <h3>📅 Bookings ({upcomingBookings.length} upcoming)</h3>
        <button onClick={onRefresh} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      {upcomingBookings.length > 0 && (
        <>
          <h4 className="section-title">Upcoming Bookings</h4>
          <div className="bookings-table-wrapper">
            <table className="bookings-table">
              <thead>
                <tr>
                  <th>📅 Date</th>
                  <th>🕒 Time</th>
                  <th>👤 Name</th>
                  <th>📧 Email</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {upcomingBookings.map(renderBookingRow)}
              </tbody>
            </table>
          </div>
        </>
      )}

      {pastBookings.length > 0 && (
        <>
          <h4 className="section-title">Past Bookings</h4>
          <div className="bookings-table-wrapper">
            <table className="bookings-table">
              <thead>
                <tr>
                  <th>📅 Date</th>
                  <th>🕒 Time</th>
                  <th>👤 Name</th>
                  <th>📧 Email</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pastBookings.map(renderBookingRow)}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default BookingsList;
