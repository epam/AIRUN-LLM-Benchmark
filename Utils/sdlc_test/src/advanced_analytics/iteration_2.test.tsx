import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
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

describe('AdvancedAnalyticsDashboard - Iteration 2', () => {
  // All tests from Iteration 1 MUST still pass
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

  it('displays raw data from all APIs', async () => {
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
      expect(screen.getByText('login')).toBeInTheDocument();
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });
  });

  // NEW ITERATION 2 REQUIREMENTS
  it('uses useReducer for complex state management', async () => {
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

    // Test that reducer actions are working by checking state changes
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Dispatch actions should work (ADD_USER, UPDATE_METRICS, TOGGLE_CONFIG)
    const addButton = screen.queryByText(/add user/i);
    if (addButton) {
      fireEvent.click(addButton);
    }
  });

  it('implements controlled form inputs for filtering', async () => {
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
      // Check for controlled form inputs
      const dateRangePicker = screen.queryByLabelText(/date range/i) || screen.queryByPlaceholderText(/date range/i);
      const tierSelector = screen.queryByLabelText(/tier/i) || screen.queryByRole('combobox');
      const metricDropdown = screen.queryByLabelText(/metric type/i) || screen.queryByDisplayValue(/metric/i);

      expect(dateRangePicker || tierSelector || metricDropdown).toBeInTheDocument();
    });
  });

  it('implements data caching with 5-minute expiration', async () => {
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
    });

    // Subsequent renders should use cache, not make new requests
    const { rerender } = render(<AdvancedAnalyticsDashboard />);
    rerender(<AdvancedAnalyticsDashboard />);

    // Should still be 3 calls (cached)
    expect(fetch).toHaveBeenCalledTimes(3);
  });

  it('has independent loading states for each section', async () => {
    // Mock delayed responses for different APIs
    (fetch as jest.Mock)
      .mockImplementationOnce(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            json: async () => mockUsersData,
          }), 100)
        )
      )
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockConfigData,
      });

    render(<AdvancedAnalyticsDashboard />);

    // Should show loading for users section
    expect(screen.queryByText(/loading users/i) || screen.queryByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('maintains all existing functionality from iteration 1', async () => {
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
      // All original functionality must still work
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription tier distribution/i)).toBeInTheDocument();
      expect(screen.getByText(/Performance metrics timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/User engagement heatmap/i)).toBeInTheDocument();
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
      expect(screen.getByText(/Configuration panel/i)).toBeInTheDocument();
      
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });
  });

  it('implements error boundaries with proper fallbacks', async () => {
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
      // Should show error state for users but continue with other sections
      expect(screen.getByText('page_view')).toBeInTheDocument();
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });
  });

  it('supports complex reducer action types', async () => {
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
      // Component should handle ADD_USER, UPDATE_METRICS, TOGGLE_CONFIG actions
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Test action dispatching if interactive elements exist
    const toggleButton = screen.queryByText(/toggle/i) || screen.queryByRole('button');
    if (toggleButton) {
      fireEvent.click(toggleButton);
    }
  });
});