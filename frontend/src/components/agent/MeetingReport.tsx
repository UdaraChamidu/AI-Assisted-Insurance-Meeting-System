import React from 'react';
import { jsPDF } from "jspdf";

interface MeetingReportProps {
  summary: string;
  transcript: any[];
}

const MeetingReport: React.FC<MeetingReportProps> = ({ summary, transcript }) => {
  
  const handleDownloadPdf = () => {
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text("Meeting Report", 10, 10);
      
      doc.setFontSize(12);
      doc.text("AI Summary:", 10, 20);
      
      const splitSummary = doc.splitTextToSize(summary, 180);
      doc.text(splitSummary, 10, 30);
      
      let y = 30 + (splitSummary.length * 7) + 10;
      
      doc.text("Transcript:", 10, y);
      y += 10;
      
      transcript.forEach((t) => {
          if (y > 280) {
              doc.addPage();
              y = 10;
          }
          const line = `${t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : ''} [${t.speaker}]: ${t.text}`;
          const splitLine = doc.splitTextToSize(line, 180);
          doc.text(splitLine, 10, y);
          y += (splitLine.length * 7);
      });
      
      doc.save("meeting-report.pdf");
  };

  return (
    <div className="meeting-report" style={{ padding: '40px', maxWidth: '800px', margin: '0 auto', color: 'white' }}>
      <h2 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>📊 Post-Meeting Report</h2>
      
      <div className="report-section" style={{ marginTop: '30px' }}>
        <h3>🤖 AI Summary</h3>
        <div className="summary-box" style={{ background: '#1e1e24', padding: '20px', borderRadius: '8px', lineHeight: '1.6' }}>
            {summary ? (
                <p>{summary}</p>
            ) : (
                <p style={{ color: '#888', fontStyle: 'italic' }}>Generating summary...</p>
            )}
        </div>
      </div>

      <div className="report-actions" style={{ marginTop: '40px', display: 'flex', gap: '20px' }}>
        <button 
            onClick={handleDownloadPdf}
            className="btn-download"
            style={{
                padding: '12px 24px',
                background: '#667eea',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                fontWeight: 'bold',
                cursor: 'pointer'
            }}
        >
            📥 Download Report (PDF)
        </button>
        
        <button 
            onClick={() => window.location.href = '/admin'}
            className="btn-secondary"
             style={{
                padding: '12px 24px',
                background: 'transparent',
                border: '1px solid #666',
                borderRadius: '6px',
                color: '#ccc',
                cursor: 'pointer'
            }}
        >
            Back to Dashboard
        </button>
      </div>
    </div>
  );
};

export default MeetingReport;
