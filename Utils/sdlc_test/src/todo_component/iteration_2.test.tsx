import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoList from './component';

// Mock window.confirm for delete confirmation tests
const originalConfirm = window.confirm;

describe('TodoList Component - Iteration 2 (Delete + Validation)', () => {
  beforeEach(() => {
    window.confirm = jest.fn();
  });

  afterEach(() => {
    window.confirm = originalConfirm;
  });

  describe('All Previous Functionality (Backward Compatibility)', () => {
    it('should maintain basic todo addition functionality', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Test todo' } });
      fireEvent.click(addButton);
      
      expect(screen.getByText('Test todo')).toBeInTheDocument();
    });

    it('should still call onTodoAdd callback', () => {
      const onTodoAdd = jest.fn();
      render(<TodoList onTodoAdd={onTodoAdd} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Callback test' } });
      fireEvent.click(addButton);
      
      expect(onTodoAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Callback test',
          completed: false,
        })
      );
    });

    it('should maintain initialTodos prop functionality', () => {
      const initialTodos = [
        {
          id: '1',
          text: 'Initial todo',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      expect(screen.getByTestId('todo-item-1')).toBeInTheDocument();
      expect(screen.getByText('Initial todo')).toBeInTheDocument();
    });
  });

  describe('Delete Functionality', () => {
    it('should render delete buttons for each todo with correct data-testid', () => {
      const initialTodos = [
        {
          id: 'todo-1',
          text: 'Test todo 1',
          completed: false,
          createdAt: new Date(),
        },
        {
          id: 'todo-2',
          text: 'Test todo 2',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      expect(screen.getByTestId('todo-delete-todo-1')).toBeInTheDocument();
      expect(screen.getByTestId('todo-delete-todo-2')).toBeInTheDocument();
    });

    it('should delete todo when delete button is clicked and confirmed', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
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
      expect(screen.queryByTestId('todo-item-delete-test')).not.toBeInTheDocument();
    });

    it('should not delete todo when confirmation is cancelled', () => {
      (window.confirm as jest.Mock).mockReturnValue(false);
      
      const initialTodos = [
        {
          id: 'keep-test',
          text: 'Todo to keep',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      const deleteButton = screen.getByTestId('todo-delete-keep-test');
      fireEvent.click(deleteButton);
      
      expect(screen.getByText('Todo to keep')).toBeInTheDocument();
      expect(screen.getByTestId('todo-item-keep-test')).toBeInTheDocument();
    });

    it('should show confirmation dialog with todo text', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      const initialTodos = [
        {
          id: 'confirm-test',
          text: 'Confirm delete text',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      const deleteButton = screen.getByTestId('todo-delete-confirm-test');
      fireEvent.click(deleteButton);
      
      expect(window.confirm).toHaveBeenCalledWith('Delete todo: "Confirm delete text"?');
    });

    it('should handle deleting from multiple todos', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      const initialTodos = [
        {
          id: 'multi-1',
          text: 'First todo',
          completed: false,
          createdAt: new Date(),
        },
        {
          id: 'multi-2',
          text: 'Second todo',
          completed: false,
          createdAt: new Date(),
        },
        {
          id: 'multi-3',
          text: 'Third todo',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      // Delete second todo
      const deleteButton = screen.getByTestId('todo-delete-multi-2');
      fireEvent.click(deleteButton);
      
      expect(screen.getByText('First todo')).toBeInTheDocument();
      expect(screen.queryByText('Second todo')).not.toBeInTheDocument();
      expect(screen.getByText('Third todo')).toBeInTheDocument();
    });
  });

  describe('confirmDelete Prop', () => {
    it('should use confirmDelete prop (default: true)', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      const initialTodos = [
        {
          id: 'default-confirm',
          text: 'Default confirm test',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      const deleteButton = screen.getByTestId('todo-delete-default-confirm');
      fireEvent.click(deleteButton);
      
      expect(window.confirm).toHaveBeenCalled();
    });

    it('should skip confirmation when confirmDelete is false', () => {
      const initialTodos = [
        {
          id: 'no-confirm',
          text: 'No confirm test',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} confirmDelete={false} />);
      
      const deleteButton = screen.getByTestId('todo-delete-no-confirm');
      fireEvent.click(deleteButton);
      
      expect(window.confirm).not.toHaveBeenCalled();
      expect(screen.queryByText('No confirm test')).not.toBeInTheDocument();
    });

    it('should use confirmation when confirmDelete is explicitly true', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      const initialTodos = [
        {
          id: 'explicit-confirm',
          text: 'Explicit confirm test',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} confirmDelete={true} />);
      
      const deleteButton = screen.getByTestId('todo-delete-explicit-confirm');
      fireEvent.click(deleteButton);
      
      expect(window.confirm).toHaveBeenCalled();
    });
  });

  describe('Enhanced Validation', () => {
    it('should have validation-error data-testid', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
    });

    it('should validate todo text length with default maxLength (100)', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      const longText = 'A'.repeat(101);
      fireEvent.change(input, { target: { value: longText } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      expect(screen.getByText(/cannot exceed 100 characters/i)).toBeInTheDocument();
    });

    it('should validate todo text length with custom maxLength', () => {
      render(<TodoList maxLength={50} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      const longText = 'A'.repeat(51);
      fireEvent.change(input, { target: { value: longText } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      expect(screen.getByText(/cannot exceed 50 characters/i)).toBeInTheDocument();
    });

    it('should accept text at exact maxLength limit', () => {
      render(<TodoList maxLength={20} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      const exactLengthText = 'A'.repeat(20);
      fireEvent.change(input, { target: { value: exactLengthText } });
      fireEvent.click(addButton);
      
      expect(screen.queryByTestId('validation-error')).not.toBeInTheDocument();
      expect(screen.getByText(exactLengthText)).toBeInTheDocument();
    });

    it('should maintain minimum length validation (min 1)', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      expect(screen.getByText(/cannot be empty/i)).toBeInTheDocument();
    });

    it('should set maxLength attribute on input element', () => {
      render(<TodoList maxLength={75} />);
      
      const input = screen.getByTestId('todo-input');
      expect(input).toHaveAttribute('maxLength', '75');
    });
  });

  describe('onError Callback', () => {
    it('should call onError callback for validation errors', () => {
      const onError = jest.fn();
      render(<TodoList onError={onError} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(onError).toHaveBeenCalledWith('Todo cannot be empty');
    });

    it('should call onError for length validation', () => {
      const onError = jest.fn();
      render(<TodoList onError={onError} maxLength={10} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'A'.repeat(11) } });
      fireEvent.click(addButton);
      
      expect(onError).toHaveBeenCalledWith('Todo cannot exceed 10 characters');
    });

    it('should not call onError for valid todos', () => {
      const onError = jest.fn();
      render(<TodoList onError={onError} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Valid todo' } });
      fireEvent.click(addButton);
      
      expect(onError).not.toHaveBeenCalled();
    });

    it('should not crash if onError callback is not provided', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
    });
  });

  describe('Error State Management', () => {
    it('should clear error when user starts typing valid input', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      // Trigger error
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      
      // Start typing
      fireEvent.change(input, { target: { value: 'Valid' } });
      
      expect(screen.queryByTestId('validation-error')).not.toBeInTheDocument();
    });

    it('should clear error after successful todo addition', () => {
      render(<TodoList maxLength={5} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      // Trigger error
      fireEvent.change(input, { target: { value: 'Too long text' } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      
      // Add valid todo
      fireEvent.change(input, { target: { value: 'OK' } });
      fireEvent.click(addButton);
      
      expect(screen.queryByTestId('validation-error')).not.toBeInTheDocument();
    });
  });

  describe('Integration: Delete + Validation', () => {
    it('should work together - add, validate, delete', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      render(<TodoList maxLength={20} confirmDelete={true} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      // Add valid todo
      fireEvent.change(input, { target: { value: 'Valid todo' } });
      fireEvent.click(addButton);
      
      expect(screen.getByText('Valid todo')).toBeInTheDocument();
      
      // Try invalid todo
      fireEvent.change(input, { target: { value: 'A'.repeat(21) } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      
      // Delete valid todo
      const deleteButton = screen.getByTestId(/todo-delete-/);
      fireEvent.click(deleteButton);
      
      expect(screen.queryByText('Valid todo')).not.toBeInTheDocument();
    });

    it('should maintain validation state after deleting todos', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      const initialTodos = [
        {
          id: 'maintain-test',
          text: 'Initial todo',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} maxLength={5} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      // Trigger validation error
      fireEvent.change(input, { target: { value: 'Too long' } });
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
      
      // Delete existing todo
      const deleteButton = screen.getByTestId('todo-delete-maintain-test');
      fireEvent.click(deleteButton);
      
      // Validation error should still be there
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle deleting non-existent todo gracefully', () => {
      const initialTodos = [
        {
          id: 'existing',
          text: 'Existing todo',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      // Manually trigger delete with non-existent ID
      const component = screen.getByTestId('todo-list').closest('section');
      
      expect(screen.getByText('Existing todo')).toBeInTheDocument();
    });

    it('should handle very long todo text in confirmation dialog', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      const longText = 'A'.repeat(50);
      const initialTodos = [
        {
          id: 'long-text',
          text: longText,
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} maxLength={100} />);
      
      const deleteButton = screen.getByTestId('todo-delete-long-text');
      fireEvent.click(deleteButton);
      
      expect(window.confirm).toHaveBeenCalledWith(`Delete todo: "${longText}"?`);
    });

    it('should handle special characters in delete confirmation', () => {
      (window.confirm as jest.Mock).mockReturnValue(true);
      
      const specialText = 'Special "quotes" and \'apostrophes\'';
      const initialTodos = [
        {
          id: 'special-chars',
          text: specialText,
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      const deleteButton = screen.getByTestId('todo-delete-special-chars');
      fireEvent.click(deleteButton);
      
      expect(window.confirm).toHaveBeenCalledWith(`Delete todo: "${specialText}"?`);
    });
  });
});