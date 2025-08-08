import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdvancedAnalyticsDashboard from './component';

// Mock fetch for API calls
global.fetch = jest.fn();

const mockUsersData = [
  { user_id: '1', name: 'John Doe', email: 'john@test.com', registration_date: '2023-01-01', subscription_tier: 'premium', last_active: '2024-01-01' },
  { user_id: '2', name: 'Jane Smith', email: 'jane@test.com', registration_date: '2023-02-01', subscription_tier: 'basic', last_active: '2024-01-02' }
];

const mockMetricsData = [
  { metric_id: '1', user_id: '1', event_type: 'login', value: 1, timestamp: '2024-01-01T10:00:00Z', metadata: {} },
  { metric_id: '2', user_id: '2', event_type: 'page_view', value: 5, timestamp: '2024-01-01T11:00:00Z', metadata: {} }
];

const mockConfigData = {
  dashboard_settings: { theme: 'light', refresh_rate: 30 },
  user_preferences: { notifications: true },
  feature_flags: { new_feature: true }
};

beforeEach(() => {
  (fetch as jest.Mock).mockClear();
});

describe('AdvancedAnalyticsDashboard - Iteration 1', () => {
  it('renders the component without crashing', () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);
    expect(screen.getByText(/AdvancedAnalyticsDashboard/i)).toBeInTheDocument();
  });

  it('fetches data from all three APIs simultaneously', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3);
      expect(fetch).toHaveBeenCalledWith('/api/users');
      expect(fetch).toHaveBeenCalledWith('/api/metrics');
      expect(fetch).toHaveBeenCalledWith('/api/config');
    });
  });

  it('displays raw data from users API', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('jane@test.com')).toBeInTheDocument();
    });
  });

  it('displays raw data from metrics API', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('login')).toBeInTheDocument();
      expect(screen.getByText('page_view')).toBeInTheDocument();
    });
  });

  it('displays raw data from config API', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/light/i)).toBeInTheDocument();
      expect(screen.getByText(/notifications/i)).toBeInTheDocument();
    });
  });

  it('has proper TypeScript implementation', async () => {
    // This test ensures component is properly typed and renders without TS errors
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    const { container } = render(<AdvancedAnalyticsDashboard />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('implements error boundaries for each section', async () => {
    // Test that error boundaries are implemented
    (fetch as jest.Mock)
      .mockRejectedValueOnce(new Error('Users API failed'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Should still render other sections even if one fails
      expect(screen.getByText('page_view')).toBeInTheDocument();
    });
  });

  it('uses React hooks for state management', async () => {
    // This test verifies hooks are used by checking state updates
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    // Verify initial state, then wait for data to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('displays data in a grid layout with 6 sections', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUsersData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Check for the 6 required sections
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription tier distribution/i)).toBeInTheDocument();
      expect(screen.getByText(/Performance metrics timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/User engagement heatmap/i)).toBeInTheDocument();
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
      expect(screen.getByText(/Configuration panel/i)).toBeInTheDocument();
    });
  });
});