import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage: React.FC = () => {
  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            AI-Powered Insurance Consultations
          </h1>
          <p className="hero-subtitle">
            Experience the future of insurance advising with our AI-assisted platform.
            Connect with expert agents through seamless video meetings.
          </p>
          <div className="hero-buttons">
            <Link to="/booking" className="btn-primary-large">
              📅 Book a Consultation
            </Link>
          </div>
        </div>
        <div className="hero-image">
          <div className="floating-card">
            <span className="card-icon">🤖</span>
            <h3>AI Assistant</h3>
            <p>Real-time guidance during meetings</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2 className="section-title">Why Choose Us?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📹</div>
            <h3>Video Consultations</h3>
            <p>Meet with insurance experts via secure video calls from anywhere</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Assisted</h3>
            <p>Real-time AI support helps agents provide accurate information</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📅</div>
            <h3>Easy Scheduling</h3>
            <p>Book consultations at your convenience with our simple booking system</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📧</div>
            <h3>Automated Reminders</h3>
            <p>Never miss a meeting with SMS and email notifications</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>Secure & Private</h3>
            <p>Your information is protected with enterprise-grade security</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Instant Join</h3>
            <p>Join meetings directly from your browser - no downloads needed</p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works">
        <h2 className="section-title">How It Works</h2>
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Book Your Consultation</h3>
            <p>Choose a convenient date and time for your meeting</p>
          </div>

          <div className="step-arrow">→</div>

          <div className="step">
            <div className="step-number">2</div>
            <h3>Get Confirmation</h3>
            <p>Receive SMS with your meeting link and details</p>
          </div>

          <div className="step-arrow">→</div>

          <div className="step">
            <div className="step-number">3</div>
            <h3>Join the Meeting</h3>
            <p>Click the link to connect with your insurance expert</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <h2>Ready to Get Started?</h2>
        <p>Book your free insurance consultation today</p>
        <Link to="/booking" className="btn-cta">
          Schedule Now
        </Link>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>InsuranceAI</h4>
            <p>AI-powered insurance consultations</p>
          </div>
          <div className="footer-section">
            <h4>Quick Links</h4>
            <Link to="/booking">Book Consultation</Link>
            <Link to="/login">Admin Login</Link>
          </div>
          <div className="footer-section">
            <h4>Contact</h4>
            <p>Support available 24/7</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 InsuranceAI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
