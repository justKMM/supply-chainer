import { useState, useEffect, useRef } from 'react';
import type { ReportData } from './types';
import { Header } from './components/Header';
import { ProgressBar } from './components/ProgressBar';
import { Dashboard } from './components/Dashboard';
import { useSSE } from './hooks/useSSE';
import { triggerCascadeRequest, fetchProgress, fetchReport } from './api';

const STAGES = [
  [0, 'Initializing agent network & event subscriptions...'],
  [10, 'Decomposing intent into Bill of Materials...'],
  [20, 'Discovering suppliers across registry...'],
  [40, 'Requesting quotes from qualified suppliers...'],
  [55, 'Negotiating prices with suppliers...'],
  [70, 'Running compliance checks...'],
  [80, 'Issuing purchase orders...'],
  [88, 'Planning logistics routes...'],
  [91, 'Simulating disruption & recovery...'],
  [93, 'Recording transaction attestations...'],
  [95, 'Scanning intelligence feeds (weather, regulatory, commodity)...'],
  [97, 'Generating final report...'],
] as const;

function App() {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressLabel, setProgressLabel] = useState('Initializing...');
  const [reportData, setReportData] = useState<ReportData | null>(null);
  
  const { messages, clearMessages } = useSSE(isRunning);
  const pollInterval = useRef<number | undefined>(undefined);

  const handleTrigger = async () => {
    setIsRunning(true);
    setProgress(0);
    setReportData(null);
    clearMessages();
    
    try {
      await triggerCascadeRequest();
      startPolling();
    } catch (e) {
      console.error('Trigger failed:', e);
      setIsRunning(false);
    }
  };

  const startPolling = () => {
    if (pollInterval.current) clearInterval(pollInterval.current);
    
    pollInterval.current = window.setInterval(async () => {
      try {
        const data = await fetchProgress();
        setProgress(data.progress);

        let stageText = 'Processing...';
        for (const [thresh, text] of STAGES) {
          if (data.progress >= thresh) stageText = text;
        }
        setProgressLabel(stageText);

        if (!data.running && data.progress >= 100) {
          clearInterval(pollInterval.current);
          setIsRunning(false);
          await loadReport();
        }
      } catch (e) {
        console.error('Poll failed', e);
      }
    }, 500);
  };

  const loadReport = async () => {
    try {
      const data = await fetchReport();
      setReportData(data);
    } catch (e) {
      console.error('Failed to load report:', e);
      // Retry once after a delay if needed
      setTimeout(async () => {
        try {
          const data = await fetchReport();
          setReportData(data);
        } catch (e2) { console.error('Retry failed', e2); }
      }, 2000);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollInterval.current) clearInterval(pollInterval.current);
    };
  }, []);

  return (
    <>
      <Header onTrigger={handleTrigger} isRunning={isRunning} />
      
      {(isRunning || progress > 0) && (
        <ProgressBar progress={progress} label={progressLabel} />
      )}

      {!isRunning && !reportData && progress === 0 && (
        <div className="empty-state" id="emptyState">
          <div className="icon">⚙</div>
          <h3>Supply Chain Agent Network Ready</h3>
          <p>
            Click "Buy Ferrari in One Click" to launch the full AI-powered procurement cascade.
            Watch as autonomous agents discover suppliers, negotiate prices, validate compliance,
            and orchestrate logistics in real time.
          </p>
        </div>
      )}

      {/* Show dashboard if we have data OR if we are running (to show live feed) */}
      {(reportData || isRunning) && (
        <div className={reportData || isRunning ? 'block' : 'hidden'}>
           <Dashboard 
             data={(reportData || {}) as ReportData} 
             messages={messages} 
             messageCount={messages.length} 
           />
        </div>
      )}
    </>
  );
}

export default App;