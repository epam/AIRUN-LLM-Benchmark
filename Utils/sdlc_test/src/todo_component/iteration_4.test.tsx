import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoList from './component';

// Mock window.confirm for delete confirmation tests
const originalConfirm = window.confirm;

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

describe('TodoList Component - Iteration 4 (Persistence + Bulk Actions)', () => {
  beforeEach(() => {
    window.confirm = jest.fn().mockReturnValue(true);
    mockLocalStorage.clear();
    jest.clearAllMocks();
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

    it('should maintain delete and validation functionality', () => {
      render(<TodoList maxLength={5} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      // Test validation
      fireEvent.change(input, { target: { value: 'Too long text' } });
      fireEvent.click(addButton);
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      
      // Test adding valid todo
      fireEvent.change(input, { target: { value: 'OK' } });
      fireEvent.click(addButton);
      expect(screen.getByText('OK')).toBeInTheDocument();
      
      // Test delete
      fireEvent.click(screen.getByTestId(/todo-delete-/));
      expect(screen.queryByText('OK')).not.toBeInTheDocument();
    });

    it('should maintain filter and search functionality', () => {
      const todos = [
        { id: '1', text: 'Active todo', completed: false, createdAt: new Date() },
        { id: '2', text: 'Completed todo', completed: true, createdAt: new Date() },
      ];

      render(<TodoList initialTodos={todos} />);
      
      // Test filter
      fireEvent.click(screen.getByTestId('filter-active'));
      expect(screen.getByText('Active todo')).toBeInTheDocument();
      expect(screen.queryByText('Completed todo')).not.toBeInTheDocument();
      
      // Test search
      fireEvent.click(screen.getByTestId('filter-all'));
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'active' } });
      expect(screen.getByText('Active todo')).toBeInTheDocument();
      expect(screen.queryByText('Completed todo')).not.toBeInTheDocument();
    });
  });

  describe('Persistence with localStorage', () => {
    it('should save to localStorage when persistKey is provided', () => {
      render(<TodoList persistKey="test-todos" />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Persistent todo' } });
      fireEvent.click(addButton);
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'test-todos',
        expect.stringContaining('Persistent todo')
      );
    });

    it('should not save to localStorage when persistKey is not provided', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Non-persistent todo' } });
      fireEvent.click(addButton);
      
      expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
    });

    it('should load from localStorage on mount when persistKey is provided', () => {
      const storedTodos = [
        { id: 'stored-1', text: 'Stored todo', completed: false, createdAt: '2024-01-01T00:00:00.000Z' },
      ];
      
      mockLocalStorage.setItem('test-todos', JSON.stringify(storedTodos));
      
      render(<TodoList persistKey="test-todos" />);
      
      expect(screen.getByText('Stored todo')).toBeInTheDocument();
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('test-todos');
    });

    it('should handle corrupted localStorage data gracefully', () => {
      mockLocalStorage.setItem('test-todos', 'invalid-json');
      
      render(<TodoList persistKey="test-todos" initialTodos={[]} />);
      
      expect(screen.getByTestId('todo-list')).toBeInTheDocument();
      // Should not crash and show empty list
    });

    it('should handle missing localStorage data', () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      
      const initialTodos = [
        { id: 'initial', text: 'Initial todo', completed: false, createdAt: new Date() },
      ];
      
      render(<TodoList persistKey="test-todos" initialTodos={initialTodos} />);
      
      expect(screen.getByText('Initial todo')).toBeInTheDocument();
    });

    it('should update localStorage on every todo change', () => {
      render(<TodoList persistKey="test-todos" />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Todo 1' } });
      fireEvent.click(addButton);
      
      fireEvent.change(input, { target: { value: 'Todo 2' } });
      fireEvent.click(addButton);
      
      // Should be called for each addition plus initial empty state
      expect(mockLocalStorage.setItem).toHaveBeenCalledTimes(3);
    });

    it('should serialize and deserialize dates correctly', () => {
      const testDate = new Date('2024-01-15T10:30:00.000Z');
      const storedTodos = [
        { id: 'date-test', text: 'Date todo', completed: false, createdAt: testDate.toISOString() },
      ];
      
      mockLocalStorage.setItem('test-todos', JSON.stringify(storedTodos));
      
      render(<TodoList persistKey="test-todos" />);
      
      expect(screen.getByText('Date todo')).toBeInTheDocument();
    });
  });

  describe('Bulk Actions Functionality', () => {
    const bulkTodos = [
      { id: 'bulk-1', text: 'Todo 1', completed: false, createdAt: new Date() },
      { id: 'bulk-2', text: 'Todo 2', completed: true, createdAt: new Date() },
      { id: 'bulk-3', text: 'Todo 3', completed: false, createdAt: new Date() },
      { id: 'bulk-4', text: 'Todo 4', completed: true, createdAt: new Date() },
    ];

    it('should not show bulk actions when showBulkActions is false or undefined', () => {
      render(<TodoList initialTodos={bulkTodos} />);
      
      expect(screen.queryByTestId('select-all-checkbox')).not.toBeInTheDocument();
      expect(screen.queryByTestId('clear-completed-btn')).not.toBeInTheDocument();
      expect(screen.queryByTestId('delete-selected-btn')).not.toBeInTheDocument();
    });

    it('should show bulk actions when showBulkActions is true', () => {
      render(<TodoList initialTodos={bulkTodos} showBulkActions={true} />);
      
      expect(screen.getByTestId('select-all-checkbox')).toBeInTheDocument();
      expect(screen.getByTestId('clear-completed-btn')).toBeInTheDocument();
      expect(screen.getByTestId('delete-selected-btn')).toBeInTheDocument();
    });

    it('should show individual selection checkboxes when showBulkActions is true', () => {
      render(<TodoList initialTodos={bulkTodos} showBulkActions={true} />);
      
      const todoItems = screen.getAllByTestId(/todo-item-/);
      todoItems.forEach(item => {
        expect(item.querySelector('input[type="checkbox"]')).toBeInTheDocument();
      });
    });

    it('should show completion checkboxes for marking todos as complete', () => {
      render(<TodoList initialTodos={bulkTodos} showBulkActions={true} />);
      
      // Each todo should have at least one checkbox (completion), possibly two with bulk actions
      const allCheckboxes = screen.getAllByRole('checkbox');
      expect(allCheckboxes.length).toBeGreaterThanOrEqual(bulkTodos.length);
    });
  });

  describe('Select All Functionality', () => {
    const selectTodos = [
      { id: 'select-1', text: 'Todo 1', completed: false, createdAt: new Date() },
      { id: 'select-2', text: 'Todo 2', completed: true, createdAt: new Date() },
      { id: 'select-3', text: 'Todo 3', completed: false, createdAt: new Date() },
    ];

    it('should select all filtered todos when select all is checked', () => {
      render(<TodoList initialTodos={selectTodos} showBulkActions={true} />);
      
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      fireEvent.click(selectAllCheckbox);
      
      expect(selectAllCheckbox).toBeChecked();
      
      // Delete selected button should be enabled
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      expect(deleteSelectedBtn).not.toBeDisabled();
    });

    it('should deselect all todos when select all is unchecked', () => {
      render(<TodoList initialTodos={selectTodos} showBulkActions={true} />);
      
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      
      // First select all
      fireEvent.click(selectAllCheckbox);
      expect(selectAllCheckbox).toBeChecked();
      
      // Then deselect all
      fireEvent.click(selectAllCheckbox);
      expect(selectAllCheckbox).not.toBeChecked();
      
      // Delete selected button should be disabled
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      expect(deleteSelectedBtn).toBeDisabled();
    });

    it('should only select filtered todos', () => {
      render(<TodoList initialTodos={selectTodos} showBulkActions={true} />);
      
      // Filter to show only active todos
      fireEvent.click(screen.getByTestId('filter-active'));
      
      // Select all should only select visible (active) todos
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      fireEvent.click(selectAllCheckbox);
      
      expect(selectAllCheckbox).toBeChecked();
    });

    it('should update select all state when individual todos are selected', () => {
      render(<TodoList initialTodos={selectTodos} showBulkActions={true} />);
      
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      
      // Initially unchecked
      expect(selectAllCheckbox).not.toBeChecked();
      
      // When all are manually selected, select all should become checked
      const todoCheckboxes = screen.getAllByRole('checkbox');
      const selectionCheckboxes = todoCheckboxes.filter(cb => 
        cb.getAttribute('data-testid') !== 'select-all-checkbox' &&
        cb.getAttribute('aria-label')?.includes('Select todo')
      );
      
      selectionCheckboxes.forEach(checkbox => {
        fireEvent.click(checkbox);
      });
      
      // Select all should now be checked
      expect(selectAllCheckbox).toBeChecked();
    });
  });

  describe('Clear Completed Functionality', () => {
    const completedTodos = [
      { id: 'clear-1', text: 'Active todo 1', completed: false, createdAt: new Date() },
      { id: 'clear-2', text: 'Completed todo 1', completed: true, createdAt: new Date() },
      { id: 'clear-3', text: 'Active todo 2', completed: false, createdAt: new Date() },
      { id: 'clear-4', text: 'Completed todo 2', completed: true, createdAt: new Date() },
    ];

    it('should clear all completed todos when clear completed is clicked', () => {
      render(<TodoList initialTodos={completedTodos} showBulkActions={true} />);
      
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      fireEvent.click(clearCompletedBtn);
      
      // Only active todos should remain
      expect(screen.getByText('Active todo 1')).toBeInTheDocument();
      expect(screen.getByText('Active todo 2')).toBeInTheDocument();
      expect(screen.queryByText('Completed todo 1')).not.toBeInTheDocument();
      expect(screen.queryByText('Completed todo 2')).not.toBeInTheDocument();
    });

    it('should disable clear completed button when no todos are completed', () => {
      const activeTodos = [
        { id: 'active-1', text: 'Active todo 1', completed: false, createdAt: new Date() },
        { id: 'active-2', text: 'Active todo 2', completed: false, createdAt: new Date() },
      ];

      render(<TodoList initialTodos={activeTodos} showBulkActions={true} />);
      
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      expect(clearCompletedBtn).toBeDisabled();
    });

    it('should enable clear completed button when there are completed todos', () => {
      render(<TodoList initialTodos={completedTodos} showBulkActions={true} />);
      
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      expect(clearCompletedBtn).not.toBeDisabled();
    });
  });

  describe('Delete Selected Functionality', () => {
    const deleteTodos = [
      { id: 'del-1', text: 'Todo 1', completed: false, createdAt: new Date() },
      { id: 'del-2', text: 'Todo 2', completed: true, createdAt: new Date() },
      { id: 'del-3', text: 'Todo 3', completed: false, createdAt: new Date() },
    ];

    it('should delete selected todos when delete selected is clicked', () => {
      render(<TodoList initialTodos={deleteTodos} showBulkActions={true} />);
      
      // Select some todos
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      fireEvent.click(selectAllCheckbox);
      
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      fireEvent.click(deleteSelectedBtn);
      
      // All todos should be deleted
      expect(screen.queryByText('Todo 1')).not.toBeInTheDocument();
      expect(screen.queryByText('Todo 2')).not.toBeInTheDocument();
      expect(screen.queryByText('Todo 3')).not.toBeInTheDocument();
    });

    it('should disable delete selected button when no todos are selected', () => {
      render(<TodoList initialTodos={deleteTodos} showBulkActions={true} />);
      
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      expect(deleteSelectedBtn).toBeDisabled();
    });

    it('should enable delete selected button when todos are selected', () => {
      render(<TodoList initialTodos={deleteTodos} showBulkActions={true} />);
      
      // Select one todo
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      fireEvent.click(selectAllCheckbox);
      
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      expect(deleteSelectedBtn).not.toBeDisabled();
    });

    it('should clear selection after deleting selected todos', () => {
      render(<TodoList initialTodos={deleteTodos} showBulkActions={true} />);
      
      // Select all todos
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      fireEvent.click(selectAllCheckbox);
      
      // Add a new todo so we have something left after deletion
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      fireEvent.change(input, { target: { value: 'New todo' } });
      fireEvent.click(addButton);
      
      // Delete selected (the original todos)
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      fireEvent.click(deleteSelectedBtn);
      
      // Delete button should be disabled again
      expect(deleteSelectedBtn).toBeDisabled();
      expect(selectAllCheckbox).not.toBeChecked();
    });
  });

  describe('onBulkAction Callback', () => {
    const callbackTodos = [
      { id: 'cb-1', text: 'Todo 1', completed: false, createdAt: new Date() },
      { id: 'cb-2', text: 'Todo 2', completed: true, createdAt: new Date() },
      { id: 'cb-3', text: 'Todo 3', completed: false, createdAt: new Date() },
    ];

    it('should call onBulkAction for clear completed', () => {
      const onBulkAction = jest.fn();
      render(<TodoList 
        initialTodos={callbackTodos} 
        showBulkActions={true} 
        onBulkAction={onBulkAction}
      />);
      
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      fireEvent.click(clearCompletedBtn);
      
      expect(onBulkAction).toHaveBeenCalledWith('clear-completed', ['cb-2']);
    });

    it('should call onBulkAction for delete selected', () => {
      const onBulkAction = jest.fn();
      render(<TodoList 
        initialTodos={callbackTodos} 
        showBulkActions={true} 
        onBulkAction={onBulkAction}
      />);
      
      // Select all todos
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      fireEvent.click(selectAllCheckbox);
      
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      fireEvent.click(deleteSelectedBtn);
      
      expect(onBulkAction).toHaveBeenCalledWith('delete-selected', ['cb-1', 'cb-2', 'cb-3']);
    });

    it('should not crash if onBulkAction is not provided', () => {
      render(<TodoList initialTodos={callbackTodos} showBulkActions={true} />);
      
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      fireEvent.click(clearCompletedBtn);
      
      // Should not crash
      expect(screen.getByText('Todo 1')).toBeInTheDocument();
    });
  });

  describe('Todo Completion Toggle', () => {
    const toggleTodos = [
      { id: 'toggle-1', text: 'Active todo', completed: false, createdAt: new Date() },
      { id: 'toggle-2', text: 'Completed todo', completed: true, createdAt: new Date() },
    ];

    it('should toggle todo completion state', () => {
      render(<TodoList initialTodos={toggleTodos} showBulkActions={true} />);
      
      // Find completion checkboxes (not selection checkboxes)
      const completionCheckboxes = screen.getAllByRole('checkbox').filter(cb => 
        cb.getAttribute('aria-label')?.includes('Mark todo as')
      );
      
      expect(completionCheckboxes).toHaveLength(2);
      
      // Toggle first todo (active -> completed)
      fireEvent.click(completionCheckboxes[0]);
      
      // The todo should now be marked as completed visually
      const todoElement = screen.getByText('Active todo').closest('li');
      expect(todoElement?.style.textDecoration).toBe('line-through');
    });

    it('should show completed todos with line-through styling', () => {
      render(<TodoList initialTodos={toggleTodos} showBulkActions={true} />);
      
      const completedTodoElement = screen.getByText('Completed todo').parentElement;
      expect(completedTodoElement?.style.textDecoration).toBe('line-through');
    });

    it('should update clear completed button state when todos are toggled', () => {
      const activeTodos = [
        { id: 'toggle-active', text: 'Active todo', completed: false, createdAt: new Date() },
      ];

      render(<TodoList initialTodos={activeTodos} showBulkActions={true} />);
      
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      expect(clearCompletedBtn).toBeDisabled();
      
      // Mark todo as completed
      const completionCheckbox = screen.getAllByRole('checkbox').find(cb => 
        cb.getAttribute('aria-label')?.includes('Mark todo as')
      );
      
      if (completionCheckbox) {
        fireEvent.click(completionCheckbox);
        expect(clearCompletedBtn).not.toBeDisabled();
      }
    });
  });

  describe('Integration: Persistence + Bulk Actions', () => {
    it('should save bulk action results to localStorage', () => {
      const persistTodos = [
        { id: 'persist-1', text: 'Todo 1', completed: false, createdAt: new Date() },
        { id: 'persist-2', text: 'Todo 2', completed: true, createdAt: new Date() },
      ];

      render(<TodoList 
        initialTodos={persistTodos} 
        persistKey="bulk-test" 
        showBulkActions={true}
      />);
      
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      fireEvent.click(clearCompletedBtn);
      
      // Should save updated todo list to localStorage
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'bulk-test',
        expect.not.stringContaining('Todo 2')
      );
    });

    it('should handle all features together', () => {
      const onBulkAction = jest.fn();
      const onFilterChange = jest.fn();
      
      render(<TodoList 
        persistKey="integration-test"
        showBulkActions={true}
        onBulkAction={onBulkAction}
        onFilterChange={onFilterChange}
        maxLength={50}
      />);
      
      // Add some todos
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'First todo' } });
      fireEvent.click(addButton);
      
      fireEvent.change(input, { target: { value: 'Second todo' } });
      fireEvent.click(addButton);
      
      // Mark one as completed
      const completionCheckboxes = screen.getAllByRole('checkbox').filter(cb => 
        cb.getAttribute('aria-label')?.includes('Mark todo as')
      );
      if (completionCheckboxes[0]) {
        fireEvent.click(completionCheckboxes[0]);
      }
      
      // Filter to show only completed
      fireEvent.click(screen.getByTestId('filter-completed'));
      expect(onFilterChange).toHaveBeenCalledWith('completed', '');
      
      // Clear completed
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      fireEvent.click(clearCompletedBtn);
      
      expect(onBulkAction).toHaveBeenCalledWith('clear-completed', expect.any(Array));
      expect(mockLocalStorage.setItem).toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle localStorage being unavailable', () => {
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage unavailable');
      });
      
      render(<TodoList persistKey="error-test" showBulkActions={true} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      // Should not crash
      fireEvent.change(input, { target: { value: 'Test todo' } });
      fireEvent.click(addButton);
      
      expect(screen.getByText('Test todo')).toBeInTheDocument();
    });

    it('should handle empty todo list with bulk actions', () => {
      render(<TodoList showBulkActions={true} />);
      
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      const clearCompletedBtn = screen.getByTestId('clear-completed-btn');
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      
      expect(selectAllCheckbox).not.toBeChecked();
      expect(clearCompletedBtn).toBeDisabled();
      expect(deleteSelectedBtn).toBeDisabled();
    });

    it('should handle bulk actions with filtered todos', () => {
      const filteredTodos = [
        { id: 'filter-1', text: 'Buy groceries', completed: false, createdAt: new Date() },
        { id: 'filter-2', text: 'Buy coffee', completed: true, createdAt: new Date() },
        { id: 'filter-3', text: 'Walk dog', completed: false, createdAt: new Date() },
      ];

      render(<TodoList initialTodos={filteredTodos} showBulkActions={true} />);
      
      // Filter to show only "buy" todos
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'buy' } });
      
      // Select all should only select filtered todos
      const selectAllCheckbox = screen.getByTestId('select-all-checkbox');
      fireEvent.click(selectAllCheckbox);
      
      expect(selectAllCheckbox).toBeChecked();
      
      // Delete selected should only delete filtered todos
      const deleteSelectedBtn = screen.getByTestId('delete-selected-btn');
      fireEvent.click(deleteSelectedBtn);
      
      // "Walk dog" should still be there
      expect(screen.getByText('Walk dog')).toBeInTheDocument();
      expect(screen.queryByText('Buy groceries')).not.toBeInTheDocument();
      expect(screen.queryByText('Buy coffee')).not.toBeInTheDocument();
    });
  });
});