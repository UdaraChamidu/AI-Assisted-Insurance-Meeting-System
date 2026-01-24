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
    <div className="agent-assist-page">
      
      {/* 1. Zoom Column (20%) */}
      <div className="col-zoom">
        <div style={{ position: 'absolute', top: 100, left: 27, right: 0, bottom: 0 }}>
             <ZoomMeeting
              meetingId={session.zoom_meeting_id}
              password={session.zoom_meeting_password}
              isCustomer={false}
              userName="Agent"
            />
        </div>
        
        {/* Overlay Controls for Audio */}
        <div style={{
            position: 'absolute',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 10,
            background: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(8px)',
            padding: '8px 16px',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.1)',
            display: 'flex',
            gap: '12px',
            alignItems: 'center',
            justifyContent: 'center',
        }}>
             {!mediaRecorderRef.current ? (
                <button className="btn-control btn-primary" onClick={startAudioCapture}>
                    <span>🎙️</span> Start Stream
                </button>
             ) : (
                <button className="btn-control btn-danger" onClick={stopAudioCapture}>
                    <span>⏹️</span> Stop Stream
                </button>
             )}
        </div>
      </div>

      {/* 2. AI Suggestions Column (35%) */}
      <div className="col-ai">
        <div className="col-header" style={{ color: '#c084fc' }}>
            <span>✨</span> AI Copilot
        </div>
        <div className="col-content">
            <div style={{ padding: '0' }}>
                <AISuggestions response={aiResponse} />
            </div>
            <div style={{ padding: '0', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <div className="col-header" style={{ color: '#4ade80', fontSize: '12px', padding: '12px 16px' }}>
                    <span>📚</span> Knowledge Base
                </div>
                <RAGContext context={ragContext} />
            </div>
        </div>
      </div>

      {/* 3. Live Transcription Column (35%) */}
      <div className="col-transcript">
        <div className="col-header" style={{ color: '#60a5fa' }}>
            <span>📝</span> Live Transcript
        </div>
        <div className="col-content">
            <LiveTranscription transcripts={transcripts} />
        </div>
      </div>

    </div>
  );
};

export default AgentAssistPage;
