import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../services/api';
import './BookingPage.css';

const BookingPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const leadId = searchParams.get('lead_id');

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [isValidLead, setIsValidLead] = useState(false); // Track if leadId is valid

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    date: '',
    time: '',
    notes: ''
  });

  // Load lead data if lead_id provided
  useEffect(() => {
    if (leadId) {
      loadLeadData();
    }
  }, [leadId]);

  const loadLeadData = async () => {
    if (!leadId) return;
    
    try {
      const lead: any = await apiClient.getLead(leadId);
      setFormData({
        ...formData,
        name: lead.customer_name || '',
        phone: lead.phone_number || '',
      });
      setIsValidLead(true); // Mark as valid ID
    } catch (err) {
      console.error('Failed to load lead:', err);
      // Don't set isValidLead to true, so we ignore the ID later
    }
  };

  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const timeSlots = [
    { value: '09:00', label: '09:00 AM' },
    { value: '09:30', label: '09:30 AM' },
    { value: '10:00', label: '10:00 AM' },
    { value: '10:30', label: '10:30 AM' },
    { value: '11:00', label: '11:00 AM' },
    { value: '11:30', label: '11:30 AM' },
    { value: '12:00', label: '12:00 PM' },
    { value: '12:30', label: '12:30 PM' },
    { value: '13:00', label: '01:00 PM' },
    { value: '13:30', label: '01:30 PM' },
    { value: '14:00', label: '02:00 PM' },
    { value: '14:30', label: '02:30 PM' },
    { value: '15:00', label: '03:00 PM' },
    { value: '15:30', label: '03:30 PM' },
    { value: '16:00', label: '04:00 PM' },
    { value: '16:30', label: '04:30 PM' },
    { value: '17:00', label: '05:00 PM' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate
      if (!formData.name || !formData.email || !formData.phone || !formData.date || !formData.time) {
        throw new Error('Please fill in all required fields');
      }

      // Create booking
      // Only include lead_id if we successfully validated it
      await apiClient.createBooking({
        lead_id: (isValidLead && leadId) ? leadId : undefined,
        customer_name: formData.name,
        customer_email: formData.email,
        customer_phone: formData.phone,
        scheduled_date: formData.date,
        scheduled_time: formData.time,
        notes: formData.notes
      });

      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="booking-page">
        <div className="booking-success">
          <div className="success-icon">✅</div>
          <h1>Booking Confirmed!</h1>
          <p className="success-message">
            Thank you for scheduling your insurance consultation.
          </p>
          <div className="booking-details">
            <h3>Meeting Details:</h3>
            <p><strong>📅 Date:</strong> {new Date(formData.date).toLocaleDateString()}</p>
            <p><strong>🕒 Time:</strong> {formData.time}</p>
          </div>
          <p className="confirmation-note">
            You will receive an SMS with your meeting link shortly.
          </p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="booking-page">
      <div className="booking-container">
        <header className="booking-header">
          <h1>📅 Schedule Your Consultation</h1>
          <p>Book a convenient time for your insurance consultation</p>
        </header>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="booking-form">
          <div className="form-section">
            <h3>Your Information</h3>
            
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="John Doe"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                placeholder="john@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone Number *</label>
              <input
                type="tel"
                id="phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                required
                placeholder="+1 234 567 8900"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Select Date & Time</h3>
            
            <div className="form-group">
              <label htmlFor="date">Preferred Date *</label>
              <input
                type="date"
                id="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                min={getMinDate()}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="time">Preferred Time *</label>
              <select
                id="time"
                value={formData.time}
                onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                required
              >
                <option value="">Select a time</option>
                {timeSlots.map((slot) => (
                  <option key={slot.value} value={slot.value}>
                    {slot.label}
                  </option>
                ))}
              </select>
              <small>Available: Monday - Friday, 9:00 AM - 5:00 PM</small>
            </div>
          </div>

          <div className="form-section">
            <h3>Additional Information</h3>
            
            <div className="form-group">
              <label htmlFor="notes">Reason for Consultation (Optional)</label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={4}
                placeholder="Tell us what you'd like to discuss..."
              />
            </div>
          </div>

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? '⏳ Booking...' : '📅 Confirm Booking'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default BookingPage;
