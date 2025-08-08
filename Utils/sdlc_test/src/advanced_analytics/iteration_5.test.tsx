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

// Mock service worker
Object.defineProperty(global.navigator, 'serviceWorker', {
  value: {
    register: jest.fn(() => Promise.resolve()),
    ready: Promise.resolve()
  },
  writable: true
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Mock internationalization
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en' }
  })
}));

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
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
});

describe('AdvancedAnalyticsDashboard - Iteration 5 - FINAL CHALLENGE', () => {
  // ULTIMATE TEST: ALL PREVIOUS ITERATIONS MUST WORK PERFECTLY
  it('CRITICAL: maintains EVERY feature from iterations 1-4 flawlessly', async () => {
    jest.useFakeTimers();
    
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // ITERATION 1: All 6 sections + TypeScript + error boundaries + data display
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription tier distribution/i)).toBeInTheDocument();
      expect(screen.getByText(/Performance metrics timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/User engagement heatmap/i)).toBeInTheDocument();
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
      expect(screen.getByText(/Configuration panel/i)).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
    });

    // ITERATION 2: useReducer + controlled->uncontrolled forms + caching + loading states
    expect(fetch).toHaveBeenCalledTimes(3);

    // ITERATION 3: WebSocket + virtualization + custom hooks + keyboard shortcuts
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');

    // ITERATION 4: optimistic updates + background sync + complex filtering + drag-drop + export + undo/redo
    jest.advanceTimersByTime(30000);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(6); // Background sync
    });

    jest.useRealTimers();
  });

  // NEW ITERATION 5 REQUIREMENTS - PRODUCTION READINESS
  it('implements comprehensive error handling with retry logic and exponential backoff', async () => {
    let retryCount = 0;
    (fetch as jest.Mock).mockImplementation(() => {
      retryCount++;
      if (retryCount < 3) {
        return Promise.reject(new Error('Network error'));
      }
      return Promise.resolve({ ok: true, json: async () => mockUsersData });
    });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Should retry failed requests with exponential backoff
      expect(fetch).toHaveBeenCalledTimes(3);
    }, { timeout: 10000 });
  });

  it('prevents memory leaks by cleaning up subscriptions, timers, and listeners', async () => {
    const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');
    const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
    const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');

    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    const { unmount } = render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Unmount component to trigger cleanup
    unmount();

    // Should clean up all subscriptions
    expect(removeEventListenerSpy).toHaveBeenCalled();
    expect(clearIntervalSpy).toHaveBeenCalled() || expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('adds performance monitoring with React.Profiler and custom metrics', async () => {
    const onRenderSpy = jest.fn();
    
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(
      <React.Profiler id="dashboard" onRender={onRenderSpy}>
        <AdvancedAnalyticsDashboard />
      </React.Profiler>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Should have performance monitoring
    expect(onRenderSpy).toHaveBeenCalled();
  });

  it('creates component testing coverage for all interactive elements', async () => {
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Test all interactive elements
    const buttons = screen.getAllByRole('button');
    const inputs = screen.getAllByRole('textbox');
    const selects = screen.getAllByRole('combobox');

    // All interactive elements should be testable
    [...buttons, ...inputs, ...selects].forEach(element => {
      expect(element).toBeInTheDocument();
      fireEvent.click(element);
    });
  });

  it('adds data validation schemas for all API responses with error reporting', async () => {
    // Test invalid API response
    (fetch as jest.Mock)
      .mockResolvedValueOnce({ 
        ok: true, 
        json: async () => ({ invalid: 'data' }) // Invalid user data
      })
      .mockResolvedValueOnce({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValueOnce({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Should handle invalid data gracefully with error reporting
      expect(screen.queryByText(/error/i) || screen.queryByText(/invalid/i)).toBeInTheDocument();
    });
  });

  it('implements progressive enhancement with graceful WebSocket degradation', async () => {
    // Mock WebSocket failure
    const mockWS = {
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      send: jest.fn(),
      close: jest.fn(),
      readyState: 3 // CLOSED
    };
    ((global as any).WebSocket as jest.Mock).mockImplementation(() => mockWS);

    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Should work even if WebSocket fails
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
    });
  });

  it('adds internationalization support for at least 3 languages', async () => {
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Should support i18n (mocked above)
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Test language switching
    const languageButtons = screen.queryAllByText(/EN|FR|ES|DE/i);
    if (languageButtons.length > 0) {
      fireEvent.click(languageButtons[0]);
    }
  });

  it('creates advanced caching strategy with cache invalidation and background refresh', async () => {
    jest.useFakeTimers();
    
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3);
    });

    // Test cache invalidation
    jest.advanceTimersByTime(300000); // 5 minutes - cache expiration

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(6); // Cache refresh
    });

    jest.useRealTimers();
  });

  it('ULTIMATE FINAL TEST: Every single feature from 4 previous iterations preserved and working', async () => {
    jest.useFakeTimers();
    
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    const { unmount } = render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // ITERATION 1: All 6 sections, TypeScript, error boundaries, grid layout
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
      expect(screen.getByText(/Subscription tier distribution/i)).toBeInTheDocument();
      expect(screen.getByText(/Performance metrics timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/User engagement heatmap/i)).toBeInTheDocument();
      expect(screen.getByText(/Export controls/i)).toBeInTheDocument();
      expect(screen.getByText(/Configuration panel/i)).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
    });

    // ITERATION 2: useReducer, controlled->uncontrolled forms, caching, loading states
    expect(fetch).toHaveBeenCalledTimes(3);
    const forms = screen.queryAllByRole('textbox');
    forms.forEach(form => expect(form).not.toHaveAttribute('value')); // uncontrolled

    // ITERATION 3: WebSocket, virtualization, custom hooks, keyboard shortcuts
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');
    fireEvent.keyDown(document, { key: 'r', ctrlKey: true });
    fireEvent.keyDown(document, { key: 'e', ctrlKey: true });
    fireEvent.keyDown(document, { key: 'f', ctrlKey: true });

    // ITERATION 4: optimistic updates, background sync, complex filtering, drag-drop, export, undo/redo
    jest.advanceTimersByTime(30000);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(6); // Background sync
    });

    const exportButtons = screen.queryAllByText(/csv|json|xml/i);
    const undoButton = screen.queryByText(/undo/i);
    const dragSection = screen.getByText(/Real-time user activity/i).closest('[draggable="true"]');
    
    if (exportButtons.length > 0) fireEvent.click(exportButtons[0]);
    if (undoButton) fireEvent.click(undoButton);
    if (dragSection) fireEvent.dragStart(dragSection);

    // ITERATION 5: error handling, memory leaks, performance monitoring, testing, validation, progressive enhancement, i18n, advanced caching
    
    // Test cleanup on unmount
    unmount();

    jest.useRealTimers();
  });

  it('NIGHTMARE SCENARIO: All contradictory requirements must coexist', async () => {
    // This is the KILLER test - controlled AND uncontrolled forms must somehow work
    // Background sync AND caching must work together
    // Progressive enhancement AND advanced features must coexist
    // WebSocket AND graceful degradation must work simultaneously
    
    (fetch as jest.Mock)
      .mockResolvedValue({ ok: true, json: async () => mockUsersData })
      .mockResolvedValue({ ok: true, json: async () => mockMetricsData })
      .mockResolvedValue({ ok: true, json: async () => mockConfigData });

    render(<AdvancedAnalyticsDashboard />);

    await waitFor(() => {
      // Component should somehow handle all contradictory requirements
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText(/Real-time user activity/i)).toBeInTheDocument();
    });

    // The LLM must maintain:
    // 1. Controlled forms (iteration 2) AND uncontrolled forms (iteration 3)
    // 2. Data caching (iteration 2) AND background sync (iteration 4) AND advanced caching (iteration 5)
    // 3. Simple state (iteration 1) AND useReducer (iteration 2) AND custom hooks (iteration 3)
    // 4. Basic API calls AND WebSocket AND progressive enhancement
    // 5. All while adding 13 new production features in iteration 5

    expect(fetch).toHaveBeenCalledWith('/api/users');
    expect(fetch).toHaveBeenCalledWith('/api/metrics');
    expect(fetch).toHaveBeenCalledWith('/api/config');
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/metrics');
  });
});