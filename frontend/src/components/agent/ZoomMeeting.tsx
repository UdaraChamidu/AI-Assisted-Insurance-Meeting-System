import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/api';
import { config } from '../../config';
import './ZoomMeeting.css';

interface ZoomMeetingProps {
  meetingId: string;
  password?: string;
  userName?: string;
  isCustomer?: boolean;
}

// Declare ZoomMtg on window object
declare global {
  interface Window {
    ZoomMtg: any;
  }
}

const ZoomMeeting: React.FC<ZoomMeetingProps> = ({
  meetingId,
  password = '',
  userName = 'Guest',
  isCustomer = false
}) => {
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isJoining, setIsJoining] = useState(false);

  useEffect(() => {
    loadZoomSDK();
  }, []);

  useEffect(() => {
    if (!isLoading && meetingId) {
      joinMeeting();
    }
  }, [isLoading, meetingId]);

  const loadZoomSDK = async () => {
    // Check if already loaded
    if (window.ZoomMtg) {
      setIsLoading(false);
      return;
    }

    try {
      // Load CSS files
      const cssFiles = [
        'https://source.zoom.us/3.9.0/css/bootstrap.css',
        'https://source.zoom.us/3.9.0/css/react-select.css'
      ];

      cssFiles.forEach(href => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        document.head.appendChild(link);
      });

      // Load JavaScript files in sequence
      const loadScript = (src: string): Promise<void> => {
        return new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = src;
          script.async = false;
          script.onload = () => resolve();
          script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
          document.body.appendChild(script);
        });
      };

      await loadScript('https://source.zoom.us/3.9.0/lib/vendor/react.min.js');
      await loadScript('https://source.zoom.us/3.9.0/lib/vendor/react-dom.min.js');
      await loadScript('https://source.zoom.us/3.9.0/lib/vendor/redux.min.js');
      await loadScript('https://source.zoom.us/3.9.0/lib/vendor/redux-thunk.min.js');
      await loadScript('https://source.zoom.us/3.9.0/lib/vendor/lodash.min.js');
      await loadScript('https://source.zoom.us/3.9.0/zoom-meeting-3.9.0.min.js');

      // Verify ZoomMtg is loaded
      if (!window.ZoomMtg) {
        throw new Error('Zoom SDK failed to load');
      }

      // Set Zoom JS lib path
      window.ZoomMtg.setZoomJSLib('https://source.zoom.us/3.9.0/lib', '/av');
      window.ZoomMtg.preLoadWasm();
      window.ZoomMtg.prepareWebSDK();

      console.log('Zoom SDK loaded successfully');
      setIsLoading(false);
    } catch (err: any) {
      console.error('Failed to load Zoom SDK:', err);
      setError('Failed to load Zoom SDK. Please refresh the page.');
      setIsLoading(false);
    }
  };

  const joinMeeting = async () => {
    try {
      setIsJoining(true);
      setError('');

      const sdkKey = config.zoomSdkKey;
      if (!sdkKey) {
        throw new Error('Zoom SDK Key not configured');
      }

      // Get signature from backend
      const response = await apiClient.generateZoomSignature(
        meetingId,
        isCustomer ? 0 : 1
      );

      console.log('Initializing Zoom meeting...');

      // Initialize Zoom SDK
      window.ZoomMtg.init({
        leaveUrl: window.location.origin,
        patchJsMedia: true,
        success: () => {
          console.log('Zoom SDK initialized, joining meeting...');

          // Join the meeting
          window.ZoomMtg.join({
            sdkKey: sdkKey,
            signature: response.signature,
            meetingNumber: meetingId,
            passWord: password,
            userName: userName,
            userEmail: '',
            success: () => {
              console.log('Successfully joined meeting');
              setIsJoining(false);
            },
            error: (error: any) => {
              console.error('Join error:', JSON.stringify(error, null, 2));
              setError(`Failed to join: ${error?.reason || JSON.stringify(error) || 'Unknown error'}`);
              setIsJoining(false);
            }
          });
        },
        error: (error: any) => {
          console.error('Init error:', error);
          setError(`Failed to initialize: ${error.reason || 'Unknown error'}`);
          setIsJoining(false);
        }
      });
    } catch (err: any) {
      console.error('Meeting error:', err);
      setError(err.message || 'Failed to start meeting');
      setIsJoining(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{
        width: '100%',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#232333',
        color: '#fff'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '4px solid rgba(255,255,255,0.3)',
            borderTop: '4px solid #2D8CFF',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }}></div>
          <h3>Loading Zoom SDK...</h3>
        </div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="zoom-meeting-wrapper" style={{
      width: '100%',
      height: '100vh',
      position: 'relative',
      background: '#232333'
    }}>
      {error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          padding: '30px',
          textAlign: 'center',
          background: '#fff',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          zIndex: 1000,
          maxWidth: '500px'
        }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#e74c3c' }}>❌ Meeting Error</h3>
          <p style={{ margin: '0 0 20px 0', color: '#666' }}>{error}</p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 24px',
              background: '#2D8CFF',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: 500,
              fontSize: '14px'
            }}
          >
            Retry
          </button>
        </div>
      )}

      {isJoining && !error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          color: '#fff',
          zIndex: 999
        }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '4px solid rgba(255,255,255,0.3)',
            borderTop: '4px solid #2D8CFF',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }}></div>
          <h3 style={{ margin: '0 0 10px 0' }}>Joining Meeting...</h3>
          <p style={{ margin: 0, opacity: 0.7 }}>Please allow camera/microphone access</p>
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default React.memo(ZoomMeeting);
