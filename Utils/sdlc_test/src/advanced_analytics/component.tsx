import React, { useEffect, useState } from 'react';

// TypeScript interfaces for API responses
type User = {
  user_id: string;
  name: string;
  email: string;
  registration_date: string;
  subscription_tier: string;
  last_active: string;
};

type Metric = {
  metric_id: string;
  user_id: string;
  event_type: string;
  value: number;
  timestamp: string;
  metadata: Record<string, any>;
};

type Config = {
  dashboard_settings: Record<string, any>;
  user_preferences: Record<string, any>;
  feature_flags: Record<string, boolean>;
};

// Error boundary for each section
class SectionErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean}> {
  constructor(props: {children: React.ReactNode}) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: any, info: any) {
    // Log error if needed
  }
  render() {
    if (this.state.hasError) {
      return <div style={{color: 'red'}}>Something went wrong in this section.</div>;
    }
    return this.props.children;
  }
}

export const AdvancedAnalyticsDashboard: React.FC = () => {
  const [users, setUsers] = useState<User[] | null>(null);
  const [metrics, setMetrics] = useState<Metric[] | null>(null);
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      fetch('/api/users').then(res => res.json()),
      fetch('/api/metrics').then(res => res.json()),
      fetch('/api/config').then(res => res.json()),
    ])
      .then(([usersData, metricsData, configData]) => {
        setUsers(usersData);
        setMetrics(metricsData);
        setConfig(configData);
        setLoading(false);
      })
      .catch((err) => {
        setError('Failed to fetch data.');
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div style={{color: 'red'}}>{error}</div>;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gridTemplateRows: '1fr 1fr 1fr',
      gap: '16px',
      height: '100vh',
      padding: '16px',
      boxSizing: 'border-box',
    }}>
      {/* Top-left: Real-time user activity feed */}
      <SectionErrorBoundary>
        <div style={{ gridColumn: 1, gridRow: 1, border: '1px solid #ccc', padding: '8px' }}>
          <h3>Real-time User Activity Feed</h3>
          <pre style={{fontSize: '0.85em', overflow: 'auto', maxHeight: '200px'}}>{JSON.stringify(users, null, 2)}</pre>
        </div>
      </SectionErrorBoundary>
      {/* Top-right: Subscription tier distribution chart */}
      <SectionErrorBoundary>
        <div style={{ gridColumn: 2, gridRow: 1, border: '1px solid #ccc', padding: '8px' }}>
          <h3>Subscription Tier Distribution</h3>
          <pre style={{fontSize: '0.85em', overflow: 'auto', maxHeight: '200px'}}>{JSON.stringify(users, null, 2)}</pre>
        </div>
      </SectionErrorBoundary>
      {/* Middle-left: Performance metrics timeline */}
      <SectionErrorBoundary>
        <div style={{ gridColumn: 1, gridRow: 2, border: '1px solid #ccc', padding: '8px' }}>
          <h3>Performance Metrics Timeline</h3>
          <pre style={{fontSize: '0.85em', overflow: 'auto', maxHeight: '200px'}}>{JSON.stringify(metrics, null, 2)}</pre>
        </div>
      </SectionErrorBoundary>
      {/* Middle-right: User engagement heatmap */}
      <SectionErrorBoundary>
        <div style={{ gridColumn: 2, gridRow: 2, border: '1px solid #ccc', padding: '8px' }}>
          <h3>User Engagement Heatmap</h3>
          <pre style={{fontSize: '0.85em', overflow: 'auto', maxHeight: '200px'}}>{JSON.stringify(metrics, null, 2)}</pre>
        </div>
      </SectionErrorBoundary>
      {/* Bottom-left: Export controls and filters */}
      <SectionErrorBoundary>
        <div style={{ gridColumn: 1, gridRow: 3, border: '1px solid #ccc', padding: '8px' }}>
          <h3>Export Controls & Filters</h3>
          <pre style={{fontSize: '0.85em', overflow: 'auto', maxHeight: '200px'}}>{JSON.stringify(users, null, 2)}</pre>
        </div>
      </SectionErrorBoundary>
      {/* Bottom-right: Configuration panel */}
      <SectionErrorBoundary>
        <div style={{ gridColumn: 2, gridRow: 3, border: '1px solid #ccc', padding: '8px' }}>
          <h3>Configuration Panel</h3>
          <pre style={{fontSize: '0.85em', overflow: 'auto', maxHeight: '200px'}}>{JSON.stringify(config, null, 2)}</pre>
        </div>
      </SectionErrorBoundary>
    </div>
  );
};
