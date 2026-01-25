import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/api';
import { config } from '../../config';
import ZoomMtgEmbedded from '@zoom/meetingsdk/embedded';
import './ZoomMeeting.css';

interface ZoomMeetingProps {
  meetingId: string;
  password?: string;
  userName?: string;
  isCustomer?: boolean;
}

const ZoomMeeting: React.FC<ZoomMeetingProps> = ({
  meetingId,
  password,
  userName = 'Guest',
  isCustomer = false
}) => {
  const [error, setError] = useState('');
  const [client] = useState(() => ZoomMtgEmbedded.createClient());

  useEffect(() => {
    if (meetingId) {
      launchMeeting();
    }
  }, [meetingId]);

  const launchMeeting = async () => {
    try {
      setError('');
      
      // 1. Get Signature
      const response = await apiClient.generateZoomSignature(
        meetingId,
        isCustomer ? 0 : 1
      );

      const sdkKey = config.zoomSdkKey;
      if (!sdkKey) throw new Error('Zoom SDK Key not configured');

      // 2. Init Client
      const meetingSDKElement = document.getElementById('meetingSDKElement');
      if (!meetingSDKElement) throw new Error('Meeting SDK element not found');

      await client.init({
        zoomAppRoot: meetingSDKElement,
        language: 'en-US',
        customize: {
          video: {
            isResizable: true,
            // viewSizes: default is to match container
            popper: {
              disableDraggable: true
            }
          }
        }
      });

      // 3. Join
      await client.join({
        signature: response.signature,
        sdkKey: sdkKey,
        meetingNumber: meetingId,
        password: password || '',
        userName: userName,
        zak: undefined // Use ZAK if you have it for host start, but verified user just joins usually
      });

      console.log('Zoom meeting joined successfully');

    } catch (err: any) {
      console.error("Launch Error", err);
      // Detailed error stringify for debugging
      const errorMsg = err.reason || err.message || JSON.stringify(err);
      setError("Failed to launch meeting: " + errorMsg);
    }
  };

  return (
    <div className="zoom-meeting-wrapper" style={{ width: '100%', height: '100vh', position: 'relative' }}>
      {error ? (
        <div className="zoom-fallback">
          <div className="fallback-content">
            <div className="fallback-icon">📹</div>
            <h3>Video Feed Unavailable</h3>
            <p className="fallback-message">
              {error.includes("Client Error") 
                ? "Simulation Mode: Meeting ID is invalid or expired." 
                : error}
            </p>
            <div className="fallback-actions">
              <button onClick={() => window.location.reload()} className="btn-retry">
                Retry Connection
              </button>
              <button onClick={() => setError('')} className="btn-dismiss">
                Dismiss
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {/* Embedded SDK renders here */}
      <div id="meetingSDKElement" style={{ width: '100%', height: '100%' }}></div>
    </div>
  );
};

export default React.memo(ZoomMeeting);
