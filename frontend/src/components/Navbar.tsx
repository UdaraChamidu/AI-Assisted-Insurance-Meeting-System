import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    const email = localStorage.getItem('user_email');
    setIsLoggedIn(!!token);
    setUserEmail(email || '');
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    setIsLoggedIn(false);
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🏥 InsuranceAI
        </Link>

        <button 
          className="menu-toggle"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          ☰
        </button>

        <ul className={`navbar-menu ${menuOpen ? 'active' : ''}`}>
          <li>
            <Link 
              to="/" 
              className={isActive('/') ? 'active' : ''}
              onClick={() => setMenuOpen(false)}
            >
              Home
            </Link>
          </li>

          {isLoggedIn && (
            <>
              <li>
                <Link 
                  to="/admin" 
                  className={isActive('/admin') ? 'active' : ''}
                  onClick={() => setMenuOpen(false)}
                >
                  Admin Dashboard
                </Link>
              </li>
            </>
          )}

          <li className="navbar-auth">
            {location.pathname.startsWith('/agent/') ? (
              <button 
                onClick={() => {
                   // Dispatch a custom event that AgentAssistPage can listen to, or we can use a context.
                   // For simplicity, let's trigger a window event or just navigate?
                   // No, we need to call the API.
                   // Let's emit a global event "triggerEndMeeting"
                   window.dispatchEvent(new CustomEvent('triggerEndMeeting'));
                }} 
                className="btn-end-meeting"
              >
                End Meeting
              </button>
            ) : isLoggedIn ? (
              <div className="user-menu">
                <span className="user-email">{userEmail}</span>
                <button onClick={handleLogout} className="btn-logout">
                  Logout
                </button>
              </div>
            ) : (
              <Link 
                to="/login" 
                className="btn-login"
                onClick={() => setMenuOpen(false)}
              >
                Admin Login
              </Link>
            )}
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
