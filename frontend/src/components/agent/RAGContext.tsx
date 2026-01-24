import React from 'react';
import './RAGContext.css';

interface RAGContextProps {
  context: any;
}

const RAGContext: React.FC<RAGContextProps> = ({ context }) => {
  if (!context || !context.chunks || context.chunks.length === 0) {
    return (
      <div className="rag-context">
        <p className="no-context">Knowledge base context will appear here.</p>
      </div>
    );
  }

  return (
    <div className="rag-context">
      <div className="context-query">
        <strong>Query:</strong> {context.query}
      </div>

      <div className="context-results">
        <p><strong>{context.total_results} relevant sources found</strong></p>

        {context.chunks.map((chunk: any, index: number) => (
          <div key={index} className="context-chunk">
            <div className="chunk-header">
              <span className="chunk-source">📄 {chunk.metadata?.source || 'Unknown Source'}</span>
              <span className="chunk-score">
                {Math.round(chunk.score * 100)}% match
              </span>
            </div>
            <div className="chunk-text">
              {chunk.text || chunk.metadata?.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RAGContext;
