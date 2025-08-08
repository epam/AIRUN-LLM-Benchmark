import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdvancedAnalyticsDashboard from './component';

// Mock WebSocket
(global as any).WebSocket = jest.fn().mockImplementation(() => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  send: jest.fn(),
  close: jest.fn(),
  readyState: 1
}));

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
  jest.clearAllMocks();
});

describe('AdvancedAnalyticsDashboard - Iteration 3', () => {
  // All tests from previous iterations MUST still pass
  it('renders the component without crashing', () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);
    expect(screen.getByText(/AdvancedAnalyticsDashboard/i)).toBeInTheDocument();
  });

  it('maintains all iteration 1 functionality', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription tier distribution/i)).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
    });
  });

  it('maintains all iteration 2 functionality (useReducer and controlled forms)', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Check for controlled form inputs from iteration 2
    const formInputs = screen.queryAllByRole('combobox');
    expect(formInputs.length).toBeGreaterThan(0);
  });

  // NEW ITERATION 3 REQUIREMENTS - The KILLER Features
  it('converts to UNCONTROLLED forms using useRef (OPPOSITE of iteration 2)', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Should now be uncontrolled forms (using defaultValue instead of value)
      const inputs = screen.queryAllByRole('textbox');
      const selects = screen.queryAllByRole('combobox');
      
      // Check that forms are uncontrolled (this contradicts iteration 2!)
      [...inputs, ...selects].forEach(input => {
        expect(input).not.toHaveAttribute('value');
      });
    });
  });

  it('establishes WebSocket connection for live metric updates', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');
    });
  });

  it('implements data virtualization for large lists', async () => {
    const largeUserList = Array.from({ length: 1000 }, (_, i) => ({
      user_id: `${i}`,
      name: `User ${i}`,
      email: `user${i}@test.com`,
      registration_date: '2023-01-01',
      subscription_tier: 'basic',
      last_active: '2024-01-01'
    }));

    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => largeUserList })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Should only render visible items (not all 1000)
      const userItems = screen.queryAllByText(/User \d+/);
      expect(userItems.length).toBeLessThan(100); // Virtualized rendering
    });
  });

  it('implements keyboard shortcuts (Ctrl+R, Ctrl+E, Ctrl+F)', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Test keyboard shortcuts
    fireEvent.keyDown(document, { key: 'r', ctrlKey: true });
    fireEvent.keyDown(document, { key: 'e', ctrlKey: true });
    fireEvent.keyDown(document, { key: 'f', ctrlKey: true });

    // Should handle these keyboard events without errors
  });

  it('creates custom hooks for each data source', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Custom hooks (useUsers, useMetrics, useConfig) should be working
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });

    // Data should be properly managed by custom hooks
    expect(fetch).toHaveBeenCalledWith('/api/users');
    expect(fetch).toHaveBeenCalledWith('/api/metrics');
    expect(fetch).toHaveBeenCalledWith('/api/config');
  });

  it('maintains reducer state management from iteration 2', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Should still use reducer for state management
    const actionButton = screen.queryByText(/add/i) || screen.queryByText(/update/i);
    if (actionButton) {
      fireEvent.click(actionButton);
    }
  });

  it('maintains independent loading states for each section', async () => {
    (fetch as jest.Mock)
      .mockImplementationOnce(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            json: async () => mockUsersData,
          }), 100)
        )
      )
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    // Should show loading states
    expect(screen.queryByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('maintains data caching with expiration', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3);
    });

    // Cache should still be working from iteration 2
    const { rerender } = render(<AdvancedAnalyticsDashboard />);
    rerender(<AdvancedAnalyticsDashboard />);

    expect(fetch).toHaveBeenCalledTimes(3); // Should use cache
  });

  it('CRITICAL: All previous features must work together', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // All 6 sections from iteration 1
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription tier distribution/i)).toBeInTheDocument();
      expect(screen.getByText(/Performance metrics timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/User engagement heatmap/i)).toBeInTheDocument();
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
      expect(screen.getByText(/Configuration panel/i)).toBeInTheDocument();

      // Data from all APIs
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });

    // WebSocket from iteration 3
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');
    
    // useReducer state management from iteration 2
    // Data caching from iteration 2
    // Custom hooks from iteration 3
    // Uncontrolled forms from iteration 3 (contradicting iteration 2)
    // Virtualization from iteration 3
    // Keyboard shortcuts from iteration 3
  });
});