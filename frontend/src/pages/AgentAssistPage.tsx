import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../services/api';
// import { wsService } from '../services/websocket';
import ZoomMeeting from '../components/agent/ZoomMeeting';
import LiveTranscription from '../components/agent/LiveTranscription';
import AISuggestions from '../components/agent/AISuggestions';
import './AgentAssistPage.css';

const AgentAssistPage: React.FC = () => {
  const { sessionId} = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<any>(null);
  const [transcripts, setTranscripts] = useState<any[]>([]);
  const [aiResponse, setAIResponse] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;

    loadSession();
    // WebSocket disabled - using client-side Deepgram SDK for transcription
    // connectWebSocket();

    return () => {
      // wsService.disconnect();
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



  // Deepgram Connection Refs
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const deepgramConnectionRef = React.useRef<any>(null);

  const startAudioCapture = async () => {
    try {
      console.log('🎤 Starting Deepgram live transcription...');
      
      // Dynamic import Deepgram SDK
      const { createClient, LiveTranscriptionEvents } = await import('@deepgram/sdk');
      
      // Get API key from env
      const DEEPGRAM_API_KEY = import.meta.env.VITE_DEEPGRAM_API_KEY || '29fe47a51ed2f1aec2ecca0e1cd38fa1bdb457bb';
      
      // Create Deepgram client
      const deepgram = createClient(DEEPGRAM_API_KEY);
      
      // Create live transcription connection
      const connection = deepgram.listen.live({
        model: 'nova-2',
        language: 'en-US',
        smart_format: true,
        punctuate: true,
        interim_results: false, // Only final results to avoid duplicates
      });
      
      deepgramConnectionRef.current = connection;
      
      // Handle connection opened
      connection.on(LiveTranscriptionEvents.Open, () => {
        console.log('✅ Deepgram connection opened');
        
        // Start capturing microphone
        navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
          }
        }).then((stream) => {
          console.log('🎤 Microphone access granted');
          
          const mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm',
          });
          
          mediaRecorder.ondataavailable = (event) => {
            console.log(`📊 Audio chunk: ${event.data.size} bytes, Deepgram state: ${connection.getReadyState()}`);
            if (event.data.size > 0 && connection.getReadyState() === 1) {
              connection.send(event.data);
              console.log('✅ Sent to Deepgram');
            }
          };
          
          mediaRecorder.start(250); // Send chunks every 250ms
          mediaRecorderRef.current = mediaRecorder;
          
          console.log('🎙️ Recording started');
          alert('✅ Live transcription started! Speak now.');
        }).catch((err) => {
          console.error('❌ Microphone error:', err);
          alert(`Microphone error: ${err.message}`);
        });
      });
      
      // Handle transcripts
      connection.on(LiveTranscriptionEvents.Transcript, (data) => {
        console.log('🔔 TRANSCRIPT EVENT:', data);
        const transcript = data.channel?.alternatives?.[0]?.transcript;
        const isFinal = data.is_final;
        
        console.log(`Text: "${transcript}", isFinal: ${isFinal}`);
        
        if (transcript && isFinal) {
          console.log('📝 Adding FINAL transcript:', transcript);
          
          setTranscripts((prev) => [...prev, {
            text: transcript,
            speaker: 'customer',
            timestamp: new Date().toISOString(),
            confidence: data.channel.alternatives[0].confidence
          }]);

          // Trigger AI Suggestion for customer queries
          console.log('🤖 Triggering AI for:', transcript);
          apiClient.chatAI(transcript, sessionId)
            .then(aiRes => {
                console.log('💡 AI Response:', aiRes);
                setAIResponse(aiRes);
                
                // --- BROWSER TTS (Simple Mode) ---
                if (window.speechSynthesis) {
                    window.speechSynthesis.cancel(); // Stop talking if already talking
                    const utterance = new SpeechSynthesisUtterance(aiRes.answer);
                    // Try to pick a female voice if available for "Assistant" feel
                    const voices = window.speechSynthesis.getVoices();
                    const preferredVoice = voices.find(v => v.name.includes("Google US English") || v.name.includes("Samantha")) || voices[0];
                    if (preferredVoice) utterance.voice = preferredVoice;
                    
                    utterance.rate = 1.0;
                    utterance.pitch = 1.0;
                    window.speechSynthesis.speak(utterance);
                }
            })
            .catch(err => {
                console.error('❌ AI Suggestion failed:', err);
            });
        }
      });
      
      // Handle errors
      connection.on(LiveTranscriptionEvents.Error, (error) => {
        console.error('❌ Deepgram error:', error);
      });
      
      // Handle close
      connection.on(LiveTranscriptionEvents.Close, () => {
        console.log('🔌 Deepgram connection closed');
      });
      
    } catch (err: any) {
      console.error('❌ Error starting transcription:', err);
      alert(`Failed to start: ${err.message}`);
    }
  };

  const stopAudioCapture = () => {
    // Stop media recorder
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      mediaRecorderRef.current = null;
    }
    
    // Close Deepgram connection
    if (deepgramConnectionRef.current) {
      deepgramConnectionRef.current.finish();
      deepgramConnectionRef.current = null;
    }
    
    console.log('⏹️ Transcription stopped');
  };

  if (loading) {
    return <div className="loading">Loading session...</div>;
  }

  if (!session) {
    return <div className="error">Session not found</div>;
  }

  return (
    <div className="agent-assist-page">
      
      {/* 1. Zoom Column (20%) */}
      <div className="col-zoom">
        <div className="panel full-height">
            <ZoomMeeting
              meetingId={session.zoom_meeting_id}
              password={session.zoom_meeting_password}
            />
        </div>
      </div>

      {/* 2. Live Transcription Column */}
      <div className="col-transcript">
        <div className="panel full-height">
          <div className="panel-header">
            <h3>📝 Live Transcription</h3>
            <div className="controls">
              <button onClick={startAudioCapture} className="btn-primary">
                Start Stream
              </button>
              <button onClick={stopAudioCapture} className="btn-secondary">
                Stop Stream
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

      {/* 4. RAG Context Column - Hidden for now or integrated differently since grid is 3-col */}
      {/* <div className="col-rag"> ... </div> */}
    </div>
  );
};

export default AgentAssistPage;
