import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../services/api';
import { wsService } from '../services/websocket';
import ZoomMeeting from '../components/agent/ZoomMeeting';
import LiveTranscription from '../components/agent/LiveTranscription';
import AISuggestions from '../components/agent/AISuggestions';
import RAGContext from '../components/agent/RAGContext';
import './AgentAssistPage.css';

const AgentAssistPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<any>(null);
  const [transcripts, setTranscripts] = useState<any[]>([]);
  const [aiResponse, setAIResponse] = useState<any>(null);
  const [ragContext, setRAGContext] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;

    loadSession();
    connectWebSocket();

    return () => {
      wsService.disconnect();
    };
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const data = await apiClient.getSession(sessionId!);
      setSession(data);
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    // Connect as staff
    wsService.connect(sessionId!, 'staff');

    // Listen for transcription events
    wsService.on('transcription.new', (event) => {
      setTranscripts((prev) => [...prev, event.data]);
    });

    // Listen for AI responses
    wsService.on('ai.response', (event) => {
      setAIResponse(event.data);
    });

    // Listen for RAG context
    wsService.on('rag.context', (event) => {
      setRAGContext(event.data);
    });
  };

  // Audio Capture Ref
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);

  const startAudioCapture = async () => {
    try {
      // 1. Capture Agent's Mic
      const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // 2. Capture System Audio (Customer) - Requires user interaction
      alert("Please select the 'Browser Tab' or 'Entire Screen' sharing option and ensure 'Share system audio' is CHECKED.");
      const sysStream = await navigator.mediaDevices.getDisplayMedia({ 
        video: true, // Required to get audio on some browsers
        audio: true 
      });

      // 3. Mix streams
      const audioContext = new AudioContext();
      const destination = audioContext.createMediaStreamDestination();

      if (micStream.getAudioTracks().length > 0) {
        const micSource = audioContext.createMediaStreamSource(micStream);
        micSource.connect(destination);
      }

      if (sysStream.getAudioTracks().length > 0) {
        const sysSource = audioContext.createMediaStreamSource(sysStream);
        sysSource.connect(destination);
      }

      // 4. Record and Stream
      console.log('DEBUG: Starting MediaRecorder...');
      const mixedStream = destination.stream;
      const mediaRecorder = new MediaRecorder(mixedStream, { mimeType: 'audio/webm' });
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && wsService) {
          console.log(`DEBUG: Sending audio chunk size: ${event.data.size}`);
          wsService.sendAudio(event.data);
        }
      };

      mediaRecorder.start(250); // Send chunks every 250ms
      mediaRecorderRef.current = mediaRecorder;
      
      // Stop screen share should stop recording
      sysStream.getVideoTracks()[0].onended = () => {
        stopAudioCapture();
      };

      console.log('Audio capture started');
    } catch (err) {
      console.error('Error starting audio capture:', err);
      alert('Failed to start audio capture. Please try again.');
    }
  };

  const stopAudioCapture = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
      console.log('Audio capture stopped');
    }
  };

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  if (loading) {
    return (
      <div className="loading-container">
        <h2>Loading session...</h2>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="error-container">
        <h2>Session not found</h2>
      </div>
    );
  }

  return (
    <div className="agent-assist-page" style={{ position: 'relative', height: '100vh', overflow: 'hidden', background: '#000' }}>
      
      {/* Zoom Container - Resizes based on sidebar */}
      <div style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        // If sidebar is open, leave space on the right. Otherwise full width.
        right: isSidebarOpen ? '380px' : '0', 
        bottom: 0, 
        transition: 'right 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        zIndex: 0 
      }}>
        <ZoomMeeting
          meetingId={session.zoom_meeting_id}
          password={session.zoom_meeting_password}
          isCustomer={false}
          userName="Agent"
        />
      </div>

      {/* Floating Control Dock - Below Navbar */}
      <div className="floating-dock" style={{
        position: 'fixed',
        top: '80px', // Pushed down to avoid Navbar overlap
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        background: 'rgba(26, 27, 38, 0.85)',
        backdropFilter: 'blur(8px)',
        padding: '8px 20px',
        borderRadius: '50px',
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
        border: '1px solid rgba(255,255,255,0.08)',
        transition: 'all 0.3s ease'
      }}>
        {/* Audio Control */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ color: '#fff', fontSize: '14px', fontWeight: 600 }}>🎙️ Audio:</span>
          {!mediaRecorderRef.current ? (
            <button 
              onClick={startAudioCapture}
              style={{
                background: '#3b82f6',
                color: '#fff',
                border: 'none',
                padding: '6px 14px',
                borderRadius: '20px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '13px',
                transition: 'background 0.2s'
              }}
            >
              Start Stream
            </button>
          ) : (
            <button 
              onClick={stopAudioCapture}
              style={{
                background: '#ef4444',
                color: '#fff',
                border: 'none',
                padding: '6px 14px',
                borderRadius: '20px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '13px',
                animation: 'pulse 2s infinite'
              }}
            >
              Stop
            </button>
          )}
        </div>

        <div style={{ width: '1px', height: '16px', background: 'rgba(255,255,255,0.2)' }} />

        {/* Sidebar Toggle */}
        <button 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          style={{
            background: 'transparent',
            color: '#fff',
            border: 'none',
            padding: '4px 8px',
            cursor: 'pointer',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            opacity: 0.9
          }}
        >
          {isSidebarOpen ? 'Hide Panel' : 'Show Panel'} 
          <span style={{ fontSize: '16px' }}>{isSidebarOpen ? '→' : '←'}</span>
        </button>
      </div>

      {/* Fixed Sidebar - Takes up actual space now (via Zoom container resizing) */}
      <div className={`floating-sidebar ${isSidebarOpen ? 'open' : ''}`} style={{
        position: 'fixed',
        top: '64px', // Below standard navbar height
        right: 0,
        bottom: 0,
        width: '380px',
        background: '#1a1b26',
        borderLeft: '1px solid rgba(255,255,255,0.1)',
        zIndex: 100,
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '-4px 0 20px rgba(0,0,0,0.2)',
        transform: isSidebarOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        overflow: 'hidden'
      }}>
        <div style={{ padding: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(0,0,0,0.2)' }}>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '15px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            🤖 Agent Assistant
          </h3>
        </div>

        <div style={{ overflowY: 'auto', flex: 1, padding: '0' }}>
          <div className="panel-section transcription-section" style={{ padding: '16px' }}>
            <h4 style={{ color: '#60a5fa', margin: '0 0 10px 0', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Live Transcription</h4>
            <LiveTranscription transcripts={transcripts} />
          </div>

          <div className="panel-section ai-section" style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <h4 style={{ color: '#c084fc', margin: '0 0 10px 0', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>AI Suggestions</h4>
            <AISuggestions response={aiResponse} />
          </div>

          <div className="panel-section rag-section" style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <h4 style={{ color: '#4ade80', margin: '0 0 10px 0', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Knowledge Base</h4>
            <RAGContext context={ragContext} />
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
          70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
          100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
      `}</style>
    </div>
  );
};

export default AgentAssistPage;
