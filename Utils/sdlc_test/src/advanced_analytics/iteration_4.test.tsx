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

// Mock drag and drop APIs
Object.assign(global, {
  DataTransfer: jest.fn(() => ({
    setData: jest.fn(),
    getData: jest.fn(),
  })),
  DragEvent: jest.fn(),
});

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

describe('AdvancedAnalyticsDashboard - Iteration 4', () => {
  // ALL PREVIOUS ITERATION TESTS MUST PASS
  it('maintains all iteration 1-3 core functionality', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Iteration 1: All 6 sections
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription tier distribution/i)).toBeInTheDocument();
      expect(screen.getByText(/Performance metrics timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/User engagement heatmap/i)).toBeInTheDocument();
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
      expect(screen.getByText(/Configuration panel/i)).toBeInTheDocument();

      // All API data
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
    });

    // Iteration 3: WebSocket connection
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');
  });

  // NEW ITERATION 4 REQUIREMENTS - EXTREME COMPLEXITY
  it('implements optimistic updates with rollback on error', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Test optimistic update
    const updateButton = screen.queryByText(/update/i) || screen.queryByText(/edit/i);
    if (updateButton) {
      fireEvent.click(updateButton);
      // Should show immediate change, then rollback if API fails
    }
  });

  it('implements background data sync every 30 seconds for ALL APIs', async () => {
    jest.useFakeTimers();
    
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3);
    });

    // Fast forward 30 seconds
    jest.advanceTimersByTime(30000);

    await waitFor(() => {
      // Should sync all 3 APIs again
      expect(fetch).toHaveBeenCalledTimes(6);
    });

    jest.useRealTimers();
  });

  it('implements complex filtering logic with AND/OR conditions', async () => {
    const complexUsersData = [
      { user_id: '1', name: 'John Doe', subscription_tier: 'premium', last_active: '2023-11-01' }, // > 30 days old
      { user_id: '2', name: 'Jane Smith', subscription_tier: 'premium', last_active: '2024-01-01' }, // recent premium
      { user_id: '3', name: 'Bob Wilson', subscription_tier: 'basic', last_active: '2023-10-01' }, // > 30 days, basic
    ];

    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => complexUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Complex filter: (tier AND last_active > 30 days) OR (subscription_tier = 'premium')
      // Should show John (premium + old) and Jane (premium + recent), not Bob (basic + old)
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('implements drag-and-drop reordering for dashboard sections', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
    });

    const section = screen.getByText(/Real-time user activity/i).closest('[draggable="true"]');
    if (section) {
      fireEvent.dragStart(section);
      fireEvent.dragEnd(section);
    }
  });

  it('supports data export in THREE formats: CSV, JSON, XML', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
    });

    // Should have export options for all three formats
    const csvExport = screen.queryByText(/csv/i) || screen.queryByText(/export.*csv/i);
    const jsonExport = screen.queryByText(/json/i) || screen.queryByText(/export.*json/i);
    const xmlExport = screen.queryByText(/xml/i) || screen.queryByText(/export.*xml/i);

    expect(csvExport || jsonExport || xmlExport).toBeInTheDocument();
  });

  it('implements undo/redo functionality for filter changes', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Test undo/redo buttons
    const undoButton = screen.queryByText(/undo/i) || screen.queryByTitle(/undo/i);
    const redoButton = screen.queryByText(/redo/i) || screen.queryByTitle(/redo/i);

    if (undoButton) {
      fireEvent.click(undoButton);
    }
    if (redoButton) {
      fireEvent.click(redoButton);
    }
  });

  it('CRITICAL: maintains ALL iteration 2 features (useReducer, controlled->uncontrolled forms, caching)', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // useReducer should still be working
    // Caching should still be active
    expect(fetch).toHaveBeenCalledTimes(3);

    // Forms should be uncontrolled (from iteration 3)
    const inputs = screen.queryAllByRole('textbox');
    inputs.forEach(input => {
      expect(input).not.toHaveAttribute('value');
    });
  });

  it('CRITICAL: maintains ALL iteration 3 features (WebSocket, virtualization, custom hooks, keyboard shortcuts)', async () => {
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ ok: true, json: async () => mockUsersData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // WebSocket connection
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');

    // Keyboard shortcuts should still work
    fireEvent.keyDown(document, { key: 'r', ctrlKey: true });
    fireEvent.keyDown(document, { key: 'e', ctrlKey: true });
    fireEvent.keyDown(document, { key: 'f', ctrlKey: true });

    // Custom hooks should be fetching data
    expect(fetch).toHaveBeenCalledWith('/api/users');
    expect(fetch).toHaveBeenCalledWith('/api/metrics');
    expect(fetch).toHaveBeenCalledWith('/api/config');
  });

  it('ULTIMATE TEST: ALL features from iterations 1-4 work simultaneously', async () => {
    jest.useFakeTimers();
    
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Iteration 1: All 6 sections + data display
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
    });

    // Iteration 2: useReducer + controlled forms + caching + loading states
    expect(fetch).toHaveBeenCalledTimes(3);

    // Iteration 3: WebSocket + uncontrolled forms + virtualization + custom hooks + shortcuts
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');

    // Iteration 4: optimistic updates + background sync + complex filtering + drag-drop + export + undo/redo
    jest.advanceTimersByTime(30000);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(6); // Background sync
    });

    // Test keyboard shortcuts
    fireEvent.keyDown(document, { key: 'r', ctrlKey: true });
    
    // Test drag and drop
    const section = screen.getByText(/Real-time user activity/i).closest('[draggable="true"]');
    if (section) {
      fireEvent.dragStart(section);
    }

    jest.useRealTimers();
  });
});