import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../services/api';
import { wsService } from '../services/websocket';
import ZoomMeeting from '../components/agent/ZoomMeeting';
import LiveTranscription from '../components/agent/LiveTranscription';
import AISuggestions from '../components/agent/AISuggestions';
import MeetingReport from '../components/agent/MeetingReport'; // Import Report Component
import './AgentAssistPage.css';

const AgentAssistPage: React.FC = () => {
  const { sessionId} = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<any>(null);
  const [transcripts, setTranscripts] = useState<any[]>([]);
  const [aiResponse, setAIResponse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // New State for Meeting Status
  const [meetingStatus, setMeetingStatus] = useState<'active' | 'ended'>('active');
  const [summary, setSummary] = useState<string>('');

  useEffect(() => {
    if (!sessionId) return;

    loadSession();
    wsService.connect(sessionId, 'staff');

    // Subscribe to events
    const handleRemoteTranscript = (data: any) => {
        console.log('📨 Received remote transcript:', data);
        if (data.data && data.data.speaker === 'customer') {
             setTranscripts((prev) => [...prev, {
                text: data.data.text,
                speaker: 'customer',
                timestamp: data.timestamp || new Date().toISOString(),
                confidence: data.data.confidence || 1.0
              }]);
              
              triggerAIReferences(data.data.text);
        }
    };
    
    // Listen for meeting ended event
    const handleMeetingEnded = (data: any) => {
        console.log("🛑 Meeting ended event received", data);
        setMeetingStatus('ended');
        generateMeetingSummary();
    };

    wsService.on('transcription.new', handleRemoteTranscript);
    wsService.on('meeting.ended', handleMeetingEnded);

    return () => {
      wsService.off('transcription.new', handleRemoteTranscript);
      wsService.off('meeting.ended', handleMeetingEnded);
      wsService.disconnect();
    };
  }, [sessionId]);

  // Clean up WebSocket when meeting ends
  useEffect(() => {
    if (meetingStatus === 'ended') {
      wsService.disconnect();
    }
  }, [meetingStatus]);
  
  // Listen for Navbar "End Meeting" trigger
  useEffect(() => {
      const handleTriggerEnd = () => {
          if (sessionId && meetingStatus === 'active') {
              if (window.confirm("Are you sure you want to end the meeting for everyone?")) {
                  apiClient.endSession(sessionId)
                      .then(() => {
                          setMeetingStatus('ended');
                          generateMeetingSummary();
                      })
                      .catch(console.error);
              }
          }
      };
      
      window.addEventListener('triggerEndMeeting', handleTriggerEnd);
      return () => window.removeEventListener('triggerEndMeeting', handleTriggerEnd);
  }, [sessionId, meetingStatus]);

  const triggerAIReferences = (text: string) => {
      apiClient.chatAI(text, sessionId)
            .then(aiRes => {
                setAIResponse(aiRes);
                
                // Add AI response to transcript
                setTranscripts((prev) => [...prev, {
                    text: aiRes.answer,
                    speaker: 'ai',
                    timestamp: new Date().toISOString(),
                    confidence: 1.0
                }]);

                wsService.send('ai.response', {
                    text: aiRes.answer,
                    speaker: 'ai'
                });
            })
            .catch(err => console.error(err));
  };
  
  const handleDownloadTranscript = () => {
      const element = document.createElement("a");
      const file = new Blob(
          [transcripts.map(t => `[${t.timestamp}] ${t.speaker.toUpperCase()}: ${t.text}`).join('\n')], 
          {type: 'text/plain'}
      );
      element.href = URL.createObjectURL(file);
      element.download = `transcript-${sessionId}.txt`;
      document.body.appendChild(element); // Required for this to work in FireFox
      element.click();
      document.body.removeChild(element);
  };

  const generateMeetingSummary = async () => {
      try {
          if (transcripts.length === 0) {
              setSummary("No transcript available to generate summary.");
              return;
          }
          
          // Use full conversation for summary
          const fullText = transcripts.map(t => `${t.speaker}: ${t.text}`).join("\n");

          console.log("Generating summary for:", fullText.substring(0, 100) + "...");
          
          const res = await apiClient.generateSummary(fullText);
          setSummary(res.summary);
          
      } catch (err) {
          console.error("Failed to generate summary", err);
          setSummary("Failed to generate summary.");
      }
  };

  const loadSession = async () => {
    try {
      const data = await apiClient.getSession(sessionId!);
      setSession(data);
      // Check if already completed?
      if (data.status === 'completed') {
          setMeetingStatus('ended');
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading session...</div>;
  }

  if (!session) {
    return <div className="error">Session not found</div>;
  }
  
  if (meetingStatus === 'ended') {
      return (
          <div className="agent-assist-page ended">
              <MeetingReport 
                  summary={summary} 
                  transcript={transcripts}
              />
          </div>
      );
  }

  return (
    <div className="agent-assist-page">
      
      {/* 1. Zoom Column (Flexible) */}
      <div className="col-zoom">
        <div className="panel full-height">
            <ZoomMeeting
              meetingId={session.zoom_meeting_id}
              password={session.zoom_meeting_password}
              mute={true}
            />
        </div>
      </div>

      {/* 2. Live Transcription Column */}
      <div className="col-transcript">
        <div className="panel full-height">
          <div className="panel-header">
            <h3>📝 Live Transcription</h3>
            <div className="controls">
              <span className="status-badge status-active">
                🎧 Live
              </span>
              <button onClick={handleDownloadTranscript} className="btn-icon" title="Download Transcript">
                📥
              </button>
            </div>
          </div>
          <div className="panel-content">
            <LiveTranscription transcripts={transcripts} />
          </div>
        </div>
      </div>

      {/* 3. AI Suggestions Column */}
      <div className="col-ai">
        <div className="panel full-height">
          <div className="panel-header">
            <h3>🤖 AI Suggestions</h3>
          </div>
          <div className="panel-content">
            <AISuggestions response={aiResponse} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentAssistPage;
