import React, { useEffect, useRef } from 'react';
import './LiveTranscription.css';

interface LiveTranscriptionProps {
  transcripts: any[];
}

const LiveTranscription: React.FC<LiveTranscriptionProps> = ({ transcripts }) => {
  const containerRef = useRef<HTMLDivElement>(null);



  useEffect(() => {
    // Auto-scroll to bottom
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [transcripts]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <div className="live-transcription" ref={containerRef}>
      {transcripts.length === 0 ? (
        <p className="no-transcripts">Waiting for customer to speak...</p>
      ) : (
        <div className="transcript-list">
          {transcripts.map((transcript, index) => (
            <div key={index} className={`transcript-item ${transcript.speaker}`}>
              <div className="transcript-header">
                <span className="speaker">{transcript.speaker === 'customer' ? '👤 Customer' : '👨‍💼 Staff'}</span>
                <span className="timestamp">{formatTime(transcript.timestamp)}</span>
              </div>
              <div className="transcript-text">{transcript.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LiveTranscription;
