import React from 'react';
import './AISuggestions.css';

interface AISuggestionsProps {
  response: any;
}

const AISuggestions: React.FC<AISuggestionsProps> = ({ response }) => {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#4caf50';
    if (confidence >= 0.5) return '#ff9800';
    return '#f44336';
  };

  if (!response) {
    return (
      <div className="ai-suggestions">
        <p className="no-response">AI suggestions will appear here when the customer asks a question.</p>
      </div>
    );
  }

  return (
    <div className="ai-suggestions">
      <div className="ai-answer-section">
        <h4>💡 Suggested Answer</h4>
        <div className="ai-answer">
          {response.answer}
        </div>
        <button
          onClick={() => copyToClipboard(response.answer)}
          className="copy-button"
        >
          📋 Copy Answer
        </button>
      </div>

      {response.follow_up_question && (
        <div className="follow-up-section">
          <h4>❓ Suggested Follow-up Question</h4>
          <div className="follow-up-question">
            {response.follow_up_question}
          </div>
        </div>
      )}

      <div className="confidence-section">
        <h4>Confidence Level</h4>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{
              width: `${response.confidence * 100}%`,
              backgroundColor: getConfidenceColor(response.confidence),
            }}
          />
        </div>
        <span className="confidence-text">
          {Math.round(response.confidence * 100)}%
        </span>
      </div>
    </div>
  );
};

export default AISuggestions;
