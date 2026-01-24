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
      <div className="main-panel">
        <ZoomMeeting
          meetingId={session.zoom_meeting_id}
          password={session.zoom_meeting_password}
          isCustomer={false}
          userName="Agent"
        />
      </div>

      <div className="side-panel">
        <div className="panel-section transcription-section">
          <h3>📝 Live Transcription</h3>
          <LiveTranscription transcripts={transcripts} />
        </div>

        <div className="panel-section ai-section">
          <h3>🤖 AI Assistant</h3>
          <AISuggestions response={aiResponse} />
        </div>

        <div className="panel-section rag-section">
          <h3>📚 Knowledge Base Context</h3>
          <RAGContext context={ragContext} />
        </div>
      </div>
    </div>
  );
};

export default AgentAssistPage;
