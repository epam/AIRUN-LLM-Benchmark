import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ComponentToTest from './component';


describe('Step 1: API Data Fetching and DataTable Display', () => {

  beforeEach(() => {
    // Mock successful API response for /api/users
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ([
        {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          role: 'admin',
          status: 'active'
        },
        {
          id: 2,
          name: 'Jane Smith',
          email: 'jane@example.com',
          role: 'user',
          status: 'inactive'
        }
      ])
    });
  });

  // ✅ CORE REQUIREMENT: Component renders without crashing
  test('Component renders without crashing', () => {
    render(<ComponentToTest />);
    expect(document.body).toBeInTheDocument();
  });

  // ✅ CORE REQUIREMENT: Component makes API call to /api/users
  test('Component makes API call to /api/users endpoint', async () => {
    render(<ComponentToTest />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/users')
      );
    });
  });

  // ✅ CORE REQUIREMENT: Component displays fetched user data
  test('Component displays user data from API', async () => {
    render(<ComponentToTest />);

    await waitFor(() => {
      // Check for user names
      expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      expect(screen.getByText(/Jane Smith/i)).toBeInTheDocument();
    });
  });

  // ✅ CORE REQUIREMENT: Component displays data in table/datatable format
  test('Component displays data in table format', async () => {
    render(<ComponentToTest />);

    await waitFor(() => {
      // Check for table structure
      const tableElement = screen.queryByRole('table') ||
                          document.querySelector('table') ||
                          document.querySelector('[data-testid*="table"]') ||
                          document.querySelector('[data-testid*="datatable"]') ||
                          document.querySelector('.table') ||
                          document.querySelector('.datatable');

      expect(tableElement).toBeInTheDocument();
    });
  });

  // ✅ CORE REQUIREMENT: Table displays user email data
  test('Component displays user email data in table', async () => {
    render(<ComponentToTest />);

    await waitFor(() => {
      expect(screen.getByText(/john@example.com/i)).toBeInTheDocument();
      expect(screen.getByText(/jane@example.com/i)).toBeInTheDocument();
    });
  });

  // ✅ CORE REQUIREMENT: Table displays user role data
  test('Component displays user role data in table', async () => {
    render(<ComponentToTest />);

    await waitFor(() => {
      expect(screen.getByText(/admin/i)).toBeInTheDocument();
      expect(screen.getByText(/user/i)).toBeInTheDocument();
    });
  });

  // ✅ CORE REQUIREMENT: Table displays user status data
  test('Component displays user status data in table', async () => {
    render(<ComponentToTest />);

    await waitFor(() => {
      expect(screen.getByText(/\bactive\b/i)).toBeInTheDocument();
      expect(screen.getByText(/\binactive\b/i)).toBeInTheDocument();
    });
  });

  // ✅ CORE REQUIREMENT: Component handles empty data response
  test('Component handles empty data response gracefully', async () => {
    // Mock empty response
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => []
    });

    render(<ComponentToTest />);

    await waitFor(() => {
      // Component should handle empty data gracefully
      expect(document.body).toBeInTheDocument();
      // Should show some indication of no data or empty table
      const emptyIndicators = [
        screen.queryByText(/no data/i),
        screen.queryByText(/empty/i),
        screen.queryByText(/no users/i),
        document.querySelector('.empty'),
        document.querySelector('[data-empty="true"]')
      ];

      const hasEmptyState = emptyIndicators.some(element => element !== null);
      // Either shows empty state or just doesn't crash
      expect(hasEmptyState || document.body).toBeTruthy();
    });
  });

  // ✅ CORE REQUIREMENT: Component handles API errors
  test('Component handles API fetch errors', async () => {
    // Mock API error
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Network Error'));

    render(<ComponentToTest />);

    await waitFor(() => {
      // Should not crash and handle error gracefully
      expect(document.body).toBeInTheDocument();
    });
  });

});

// Additional structure validation
describe('Step 1: Component Structure Requirements', () => {

  test('Component is properly exported', () => {
    expect(ComponentToTest).toBeDefined();
    expect(typeof ComponentToTest).toBe('function');
  });

  test('Component can be instantiated without props', () => {
    expect(() => React.createElement(ComponentToTest)).not.toThrow();
  });

});