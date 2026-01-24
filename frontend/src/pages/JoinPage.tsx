import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../services/api';
import ZoomMeeting from '../components/agent/ZoomMeeting';
import './JoinPage.css';

const JoinPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [joined, setJoined] = useState(false);
  const [name, setName] = useState('');

  // Presentation slides (placeholders)
  const [currentSlide, setCurrentSlide] = useState(0);
  const slides = [
    {
      title: "Welcome to InsuranceAI",
      subtitle: "Your trusted partner in future security",
      color: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" 
    },
    {
      title: "Smart Coverage",
      subtitle: "AI-driven analysis for the best policies",
      color: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)"
    },
    {
      title: "Expert Guidance",
      subtitle: "Licensed agents supported by advanced AI",
      color: "linear-gradient(135deg, #2d3748 0%, #4a5568 100%)"
    }
  ];

  useEffect(() => {
    // Auto-rotate slides only if not joined
    let timer: any;
    if (!joined) {
      timer = setInterval(() => {
        setCurrentSlide((prev) => (prev + 1) % slides.length);
      }, 5000);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [joined]);

  useEffect(() => {
    if (sessionId) {
      loadSession();
    }
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const data = await apiClient.getSession(sessionId!);
      setSession(data);
    } catch (err) {
      setError('Failed to load meeting details. Please check the link.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    setJoined(true);
  };

  if (loading) return <div className="join-loading">Loading meeting details...</div>;
  if (error) return <div className="join-error">{error}</div>;

  return (
    <div className="join-page">
      {joined ? (
        <div className="zoom-container">
          <ZoomMeeting
            meetingId={session?.zoom_meeting_id}
            password={session?.zoom_meeting_password}
            isCustomer={true}
            userName={name}
          />
        </div>
      ) : (
        <div className="join-content">
          {/* Left Side - Presentation */}
          <div className="presentation-section">
            <div 
              className="presentation-slide"
              style={{ background: slides[currentSlide].color }}
            >
              <div className="slide-content">
                <h1>{slides[currentSlide].title}</h1>
                <p>{slides[currentSlide].subtitle}</p>
                <div className="slide-dots">
                  {slides.map((_, idx) => (
                    <span 
                      key={idx} 
                      className={`dot ${idx === currentSlide ? 'active' : ''}`}
                    />
                  ))}
                </div>
              </div>
            </div>
            <div className="presentation-footer">
              <p>✨ While you wait, learn about our AI technology</p>
            </div>
          </div>

          {/* Right Side - Join Form */}
          <div className="join-form-section">
            <div className="meeting-card">
              <div className="meeting-header">
                <h2>Ready to Join?</h2>
                <div className="meeting-credentials" style={{ background: '#f5f7fa', padding: '10px', borderRadius: '8px', marginBottom: '15px' }}>
                  <p className="meeting-id" style={{ margin: '5px 0', fontWeight: 'bold', color: '#4a5568' }}>Meeting ID: {session?.zoom_meeting_id}</p>
                  <p className="meeting-passcode" style={{ margin: '5px 0', fontWeight: 'bold', color: '#4a5568' }}>Passcode: {session?.zoom_meeting_password}</p>
                </div>
              </div>

              <div className="meeting-info">
                <div className="info-item">
                  <span className="icon">📅</span>
                  <div>
                    <label>Date</label>
                    <p>{new Date(session.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <div className="info-item">
                  <span className="icon">⏰</span>
                  <div>
                    <label>Status</label>
                    <span className={`status-badge status-${session.status.toLowerCase()}`}>
                      {session.status}
                    </span>
                  </div>
                </div>
              </div>

              <form onSubmit={handleJoin} className="name-form">
                <div className="form-group">
                  <label htmlFor="name">Enter your name to join</label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="E.g., John Doe"
                    required
                    className="name-input"
                  />
                </div>
                <button type="submit" className="join-button">
                  🎥 Join Meeting Now
                </button>
              </form>
              
              <p className="secure-note">
                🔒 Secure connection via Zoom
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JoinPage;
