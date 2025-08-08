import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoList from './component';

// Mock window.confirm for delete confirmation tests
const originalConfirm = window.confirm;

describe('TodoList Component - Iteration 3 (Filters + Search)', () => {
  beforeEach(() => {
    window.confirm = jest.fn().mockReturnValue(true);
  });

  afterEach(() => {
    window.confirm = originalConfirm;
  });

  describe('All Previous Functionality (Backward Compatibility)', () => {
    it('should maintain all basic functionality', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Test todo' } });
      fireEvent.click(addButton);
      
      expect(screen.getByText('Test todo')).toBeInTheDocument();
    });

    it('should maintain delete functionality', () => {
      const initialTodos = [
        {
          id: 'delete-test',
          text: 'Todo to delete',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      const deleteButton = screen.getByTestId('todo-delete-delete-test');
      fireEvent.click(deleteButton);
      
      expect(screen.queryByText('Todo to delete')).not.toBeInTheDocument();
    });

    it('should maintain validation functionality', () => {
      render(<TodoList maxLength={5} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Too long text' } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
    });
  });

  describe('Filter Functionality', () => {
    const sampleTodos = [
      {
        id: 'active-1',
        text: 'Active todo 1',
        completed: false,
        createdAt: new Date(),
      },
      {
        id: 'active-2',
        text: 'Active todo 2',
        completed: false,
        createdAt: new Date(),
      },
      {
        id: 'completed-1',
        text: 'Completed todo 1',
        completed: true,
        createdAt: new Date(),
      },
      {
        id: 'completed-2',
        text: 'Completed todo 2',
        completed: true,
        createdAt: new Date(),
      },
    ];

    it('should render filter buttons with correct data-testids', () => {
      render(<TodoList />);
      
      expect(screen.getByTestId('filter-all')).toBeInTheDocument();
      expect(screen.getByTestId('filter-active')).toBeInTheDocument();
      expect(screen.getByTestId('filter-completed')).toBeInTheDocument();
    });

    it('should default to "all" filter', () => {
      render(<TodoList initialTodos={sampleTodos} />);
      
      const allButton = screen.getByTestId('filter-all');
      expect(allButton).toHaveAttribute('aria-pressed', 'true');
      
      // All todos should be visible
      expect(screen.getByText('Active todo 1')).toBeInTheDocument();
      expect(screen.getByText('Active todo 2')).toBeInTheDocument();
      expect(screen.getByText('Completed todo 1')).toBeInTheDocument();
      expect(screen.getByText('Completed todo 2')).toBeInTheDocument();
    });

    it('should filter to show only active todos', () => {
      render(<TodoList initialTodos={sampleTodos} />);
      
      const activeButton = screen.getByTestId('filter-active');
      fireEvent.click(activeButton);
      
      expect(activeButton).toHaveAttribute('aria-pressed', 'true');
      expect(screen.getByTestId('filter-all')).toHaveAttribute('aria-pressed', 'false');
      
      // Only active todos should be visible
      expect(screen.getByText('Active todo 1')).toBeInTheDocument();
      expect(screen.getByText('Active todo 2')).toBeInTheDocument();
      expect(screen.queryByText('Completed todo 1')).not.toBeInTheDocument();
      expect(screen.queryByText('Completed todo 2')).not.toBeInTheDocument();
    });

    it('should filter to show only completed todos', () => {
      render(<TodoList initialTodos={sampleTodos} />);
      
      const completedButton = screen.getByTestId('filter-completed');
      fireEvent.click(completedButton);
      
      expect(completedButton).toHaveAttribute('aria-pressed', 'true');
      
      // Only completed todos should be visible
      expect(screen.queryByText('Active todo 1')).not.toBeInTheDocument();
      expect(screen.queryByText('Active todo 2')).not.toBeInTheDocument();
      expect(screen.getByText('Completed todo 1')).toBeInTheDocument();
      expect(screen.getByText('Completed todo 2')).toBeInTheDocument();
    });

    it('should accept filter prop from parent', () => {
      render(<TodoList initialTodos={sampleTodos} filter="active" />);
      
      const activeButton = screen.getByTestId('filter-active');
      expect(activeButton).toHaveAttribute('aria-pressed', 'true');
      
      // Only active todos should be visible
      expect(screen.getByText('Active todo 1')).toBeInTheDocument();
      expect(screen.queryByText('Completed todo 1')).not.toBeInTheDocument();
    });

    it('should switch between filters correctly', () => {
      render(<TodoList initialTodos={sampleTodos} />);
      
      // Start with all
      expect(screen.getByText('Active todo 1')).toBeInTheDocument();
      expect(screen.getByText('Completed todo 1')).toBeInTheDocument();
      
      // Switch to active
      fireEvent.click(screen.getByTestId('filter-active'));
      expect(screen.getByText('Active todo 1')).toBeInTheDocument();
      expect(screen.queryByText('Completed todo 1')).not.toBeInTheDocument();
      
      // Switch to completed
      fireEvent.click(screen.getByTestId('filter-completed'));
      expect(screen.queryByText('Active todo 1')).not.toBeInTheDocument();
      expect(screen.getByText('Completed todo 1')).toBeInTheDocument();
      
      // Switch back to all
      fireEvent.click(screen.getByTestId('filter-all'));
      expect(screen.getByText('Active todo 1')).toBeInTheDocument();
      expect(screen.getByText('Completed todo 1')).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    const searchTodos = [
      {
        id: 'search-1',
        text: 'Buy groceries',
        completed: false,
        createdAt: new Date(),
      },
      {
        id: 'search-2',
        text: 'Walk the dog',
        completed: false,
        createdAt: new Date(),
      },
      {
        id: 'search-3',
        text: 'Buy coffee',
        completed: true,
        createdAt: new Date(),
      },
      {
        id: 'search-4',
        text: 'Read book',
        completed: false,
        createdAt: new Date(),
      },
    ];

    it('should render search input with correct data-testid', () => {
      render(<TodoList />);
      
      expect(screen.getByTestId('search-input')).toBeInTheDocument();
    });

    it('should filter todos by search term', () => {
      render(<TodoList initialTodos={searchTodos} />);
      
      const searchInput = screen.getByTestId('search-input');
      fireEvent.change(searchInput, { target: { value: 'buy' } });
      
      // Should show todos containing "buy" (case insensitive)
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.getByText('Buy coffee')).toBeInTheDocument();
      expect(screen.queryByText('Walk the dog')).not.toBeInTheDocument();
      expect(screen.queryByText('Read book')).not.toBeInTheDocument();
    });

    it('should perform case-insensitive search', () => {
      render(<TodoList initialTodos={searchTodos} />);
      
      const searchInput = screen.getByTestId('search-input');
      fireEvent.change(searchInput, { target: { value: 'BUY' } });
      
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.getByText('Buy coffee')).toBeInTheDocument();
    });

    it('should accept searchTerm prop from parent', () => {
      render(<TodoList initialTodos={searchTodos} searchTerm="dog" />);
      
      const searchInput = screen.getByTestId('search-input');
      expect(searchInput).toHaveValue('dog');
      
      expect(screen.getByText('Walk the dog')).toBeInTheDocument();
      expect(screen.queryByText('Buy groceries')).not.toBeInTheDocument();
    });

    it('should show all todos when search is empty', () => {
      render(<TodoList initialTodos={searchTodos} />);
      
      const searchInput = screen.getByTestId('search-input');
      
      // Start with search
      fireEvent.change(searchInput, { target: { value: 'buy' } });
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.queryByText('Walk the dog')).not.toBeInTheDocument();
      
      // Clear search
      fireEvent.change(searchInput, { target: { value: '' } });
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.getByText('Walk the dog')).toBeInTheDocument();
      expect(screen.getByText('Read book')).toBeInTheDocument();
    });

    it('should handle partial matches', () => {
      render(<TodoList initialTodos={searchTodos} />);
      
      const searchInput = screen.getByTestId('search-input');
      fireEvent.change(searchInput, { target: { value: 'oo' } });
      
      // Should match "book" and "coffee"
      expect(screen.getByText('Read book')).toBeInTheDocument();
      expect(screen.getByText('Buy coffee')).toBeInTheDocument();
      expect(screen.queryByText('Buy groceries')).not.toBeInTheDocument();
      expect(screen.queryByText('Walk the dog')).not.toBeInTheDocument();
    });
  });

  describe('Combined Filter + Search', () => {
    const combinedTodos = [
      {
        id: 'combined-1',
        text: 'Buy groceries',
        completed: false,
        createdAt: new Date(),
      },
      {
        id: 'combined-2',
        text: 'Buy coffee',
        completed: true,
        createdAt: new Date(),
      },
      {
        id: 'combined-3',
        text: 'Walk the dog',
        completed: false,
        createdAt: new Date(),
      },
      {
        id: 'combined-4',
        text: 'Buy milk',
        completed: true,
        createdAt: new Date(),
      },
    ];

    it('should apply both filter and search together', () => {
      render(<TodoList initialTodos={combinedTodos} />);
      
      // Filter to completed and search for "buy"
      fireEvent.click(screen.getByTestId('filter-completed'));
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'buy' } });
      
      // Should only show completed todos that contain "buy"
      expect(screen.getByText('Buy coffee')).toBeInTheDocument();
      expect(screen.getByText('Buy milk')).toBeInTheDocument();
      expect(screen.queryByText('Buy groceries')).not.toBeInTheDocument(); // active
      expect(screen.queryByText('Walk the dog')).not.toBeInTheDocument(); // doesn't contain "buy"
    });

    it('should update search while maintaining filter', () => {
      render(<TodoList initialTodos={combinedTodos} />);
      
      // Set filter to active
      fireEvent.click(screen.getByTestId('filter-active'));
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.getByText('Walk the dog')).toBeInTheDocument();
      
      // Add search term
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'buy' } });
      
      // Should maintain active filter and apply search
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.queryByText('Walk the dog')).not.toBeInTheDocument();
      expect(screen.queryByText('Buy coffee')).not.toBeInTheDocument(); // completed
    });

    it('should update filter while maintaining search', () => {
      render(<TodoList initialTodos={combinedTodos} />);
      
      // Set search term
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'buy' } });
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.getByText('Buy coffee')).toBeInTheDocument();
      expect(screen.getByText('Buy milk')).toBeInTheDocument();
      
      // Change filter to active
      fireEvent.click(screen.getByTestId('filter-active'));
      
      // Should maintain search and apply active filter
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.queryByText('Buy coffee')).not.toBeInTheDocument(); // completed
      expect(screen.queryByText('Buy milk')).not.toBeInTheDocument(); // completed
    });
  });

  describe('Filtered Count Display', () => {
    const countTodos = [
      {
        id: 'count-1',
        text: 'Todo 1',
        completed: false,
        createdAt: new Date(),
      },
      {
        id: 'count-2',
        text: 'Todo 2',
        completed: true,
        createdAt: new Date(),
      },
      {
        id: 'count-3',
        text: 'Todo 3',
        completed: false,
        createdAt: new Date(),
      },
    ];

    it('should render filtered count with correct data-testid', () => {
      render(<TodoList />);
      
      expect(screen.getByTestId('filtered-count')).toBeInTheDocument();
    });

    it('should show correct count for all filter', () => {
      render(<TodoList initialTodos={countTodos} />);
      
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('3 shown');
    });

    it('should show correct count for active filter', () => {
      render(<TodoList initialTodos={countTodos} />);
      
      fireEvent.click(screen.getByTestId('filter-active'));
      
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('2 shown');
    });

    it('should show correct count for completed filter', () => {
      render(<TodoList initialTodos={countTodos} />);
      
      fireEvent.click(screen.getByTestId('filter-completed'));
      
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('1 shown');
    });

    it('should update count with search', () => {
      render(<TodoList initialTodos={countTodos} />);
      
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: '1' } });
      
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('1 shown');
    });

    it('should show 0 when no todos match', () => {
      render(<TodoList initialTodos={countTodos} />);
      
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'nonexistent' } });
      
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('0 shown');
    });
  });

  describe('onFilterChange Callback', () => {
    it('should call onFilterChange when filter changes', () => {
      const onFilterChange = jest.fn();
      render(<TodoList onFilterChange={onFilterChange} />);
      
      fireEvent.click(screen.getByTestId('filter-active'));
      
      expect(onFilterChange).toHaveBeenCalledWith('active', '');
    });

    it('should call onFilterChange when search changes', () => {
      const onFilterChange = jest.fn();
      render(<TodoList onFilterChange={onFilterChange} />);
      
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'test' } });
      
      expect(onFilterChange).toHaveBeenCalledWith('all', 'test');
    });

    it('should call onFilterChange with current filter when search changes', () => {
      const onFilterChange = jest.fn();
      render(<TodoList onFilterChange={onFilterChange} />);
      
      // Set filter to active first
      fireEvent.click(screen.getByTestId('filter-active'));
      onFilterChange.mockClear();
      
      // Change search
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'test' } });
      
      expect(onFilterChange).toHaveBeenCalledWith('active', 'test');
    });

    it('should not crash if onFilterChange is not provided', () => {
      render(<TodoList />);
      
      fireEvent.click(screen.getByTestId('filter-active'));
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'test' } });
      
      // Should not throw errors
      expect(screen.getByTestId('filtered-count')).toBeInTheDocument();
    });
  });

  describe('Dynamic Updates', () => {
    it('should update filtered view when adding new todos', () => {
      render(<TodoList />);
      
      // Set filter to active
      fireEvent.click(screen.getByTestId('filter-active'));
      
      // Add new todo
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'New active todo' } });
      fireEvent.click(addButton);
      
      // Should appear in active filter
      expect(screen.getByText('New active todo')).toBeInTheDocument();
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('1 shown');
    });

    it('should update filtered view when deleting todos', () => {
      const initialTodos = [
        {
          id: 'delete-active',
          text: 'Active todo',
          completed: false,
          createdAt: new Date(),
        },
        {
          id: 'delete-completed',
          text: 'Completed todo',
          completed: true,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      // Set filter to active
      fireEvent.click(screen.getByTestId('filter-active'));
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('1 shown');
      
      // Delete the active todo
      fireEvent.click(screen.getByTestId('todo-delete-delete-active'));
      
      // Count should update
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('0 shown');
    });

    it('should maintain filter state when todos are modified', () => {
      const initialTodos = [
        {
          id: 'maintain-1',
          text: 'First todo',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      // Set search
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'first' } });
      expect(screen.getByText('First todo')).toBeInTheDocument();
      
      // Add another todo
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Second todo' } });
      fireEvent.click(addButton);
      
      // Search should still be active
      expect(screen.getByText('First todo')).toBeInTheDocument();
      expect(screen.queryByText('Second todo')).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty todo list with filters', () => {
      render(<TodoList />);
      
      fireEvent.click(screen.getByTestId('filter-active'));
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'test' } });
      
      expect(screen.getByTestId('filtered-count')).toHaveTextContent('0 shown');
      expect(screen.getByTestId('todo-list')).toBeInTheDocument();
    });

    it('should handle special characters in search', () => {
      const specialTodos = [
        {
          id: 'special-1',
          text: 'Todo with @#$%^&*()',
          completed: false,
          createdAt: new Date(),
        },
        {
          id: 'special-2',
          text: 'Normal todo',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={specialTodos} />);
      
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: '@#$' } });
      
      expect(screen.getByText('Todo with @#$%^&*()')).toBeInTheDocument();
      expect(screen.queryByText('Normal todo')).not.toBeInTheDocument();
    });

    it('should handle very long search terms', () => {
      const todos = [
        {
          id: 'long-1',
          text: 'A'.repeat(200),
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={todos} />);
      
      const longSearch = 'A'.repeat(50);
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: longSearch } });
      
      expect(screen.getByText('A'.repeat(200))).toBeInTheDocument();
    });
  });
});