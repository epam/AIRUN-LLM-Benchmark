import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TodoList from './component';

describe('TodoList Component - Iteration 1 (Basic Functionality)', () => {
  describe('Basic Rendering', () => {
    it('should render todo input with correct data-testid', () => {
      render(<TodoList />);
      expect(screen.getByTestId('todo-input')).toBeInTheDocument();
    });

    it('should render add button with correct data-testid', () => {
      render(<TodoList />);
      expect(screen.getByTestId('add-btn')).toBeInTheDocument();
    });

    it('should render todo list container with correct data-testid', () => {
      render(<TodoList />);
      expect(screen.getByTestId('todo-list')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<TodoList />);
      const input = screen.getByTestId('todo-input');
      const button = screen.getByTestId('add-btn');
      
      expect(input).toHaveAttribute('type', 'text');
      expect(button).toHaveAttribute('aria-label', 'Add todo');
      expect(screen.getByRole('button', { name: /add todo/i })).toBeInTheDocument();
    });
  });

  describe('Props Interface', () => {
    it('should accept initialTodos prop and display them', () => {
      const initialTodos = [
        {
          id: '1',
          text: 'Test todo 1',
          completed: false,
          createdAt: new Date('2024-01-01'),
        },
        {
          id: '2',
          text: 'Test todo 2',
          completed: true,
          createdAt: new Date('2024-01-02'),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      expect(screen.getByTestId('todo-item-1')).toBeInTheDocument();
      expect(screen.getByTestId('todo-item-2')).toBeInTheDocument();
      expect(screen.getByText('Test todo 1')).toBeInTheDocument();
      expect(screen.getByText('Test todo 2')).toBeInTheDocument();
    });

    it('should work without initialTodos prop', () => {
      render(<TodoList />);
      
      const todoList = screen.getByTestId('todo-list');
      expect(todoList).toBeInTheDocument();
      expect(todoList.children).toHaveLength(0);
    });

    it('should call onTodoAdd callback when new todo is added', () => {
      const onTodoAdd = jest.fn();
      render(<TodoList onTodoAdd={onTodoAdd} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'New todo' } });
      fireEvent.click(addButton);
      
      expect(onTodoAdd).toHaveBeenCalledTimes(1);
      expect(onTodoAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'New todo',
          completed: false,
          id: expect.any(String),
          createdAt: expect.any(Date),
        })
      );
    });

    it('should not crash if onTodoAdd callback is not provided', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'New todo' } });
      fireEvent.click(addButton);
      
      expect(screen.getByText('New todo')).toBeInTheDocument();
    });
  });

  describe('Adding Todos', () => {
    it('should add a new todo when add button is clicked', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'My new todo' } });
      fireEvent.click(addButton);
      
      expect(screen.getByText('My new todo')).toBeInTheDocument();
    });

    it('should add a new todo when form is submitted', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      
      fireEvent.change(input, { target: { value: 'Submit test todo' } });
      fireEvent.submit(input.closest('form')!);
      
      expect(screen.getByText('Submit test todo')).toBeInTheDocument();
    });

    it('should clear input after adding a todo', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input') as HTMLInputElement;
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Test clearing' } });
      fireEvent.click(addButton);
      
      expect(input.value).toBe('');
    });

    it('should generate unique IDs for each todo', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Todo 1' } });
      fireEvent.click(addButton);
      
      fireEvent.change(input, { target: { value: 'Todo 2' } });
      fireEvent.click(addButton);
      
      const todo1 = screen.getByTestId(/todo-item-\d+/);
      const todo2 = screen.getAllByTestId(/todo-item-\d+/)[1];
      
      expect(todo1).toBeInTheDocument();
      expect(todo2).toBeInTheDocument();
      expect(todo1.getAttribute('data-testid')).not.toBe(todo2.getAttribute('data-testid'));
    });

    it('should trim whitespace from todo text', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '  Trimmed todo  ' } });
      fireEvent.click(addButton);
      
      expect(screen.getByText('Trimmed todo')).toBeInTheDocument();
      expect(screen.queryByText('  Trimmed todo  ')).not.toBeInTheDocument();
    });

    it('should set createdAt to current date', () => {
      const onTodoAdd = jest.fn();
      render(<TodoList onTodoAdd={onTodoAdd} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      const beforeAdd = new Date();
      fireEvent.change(input, { target: { value: 'Date test' } });
      fireEvent.click(addButton);
      const afterAdd = new Date();
      
      expect(onTodoAdd).toHaveBeenCalledWith(
        expect.objectContaining({
          createdAt: expect.any(Date),
        })
      );
      
      const createdAt = onTodoAdd.mock.calls[0][0].createdAt;
      expect(createdAt.getTime()).toBeGreaterThanOrEqual(beforeAdd.getTime());
      expect(createdAt.getTime()).toBeLessThanOrEqual(afterAdd.getTime());
    });
  });

  describe('Input Validation', () => {
    it('should not add empty todos', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      const todoList = screen.getByTestId('todo-list');
      expect(todoList.children).toHaveLength(0);
    });

    it('should not add todos with only whitespace', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '   ' } });
      fireEvent.click(addButton);
      
      const todoList = screen.getByTestId('todo-list');
      expect(todoList.children).toHaveLength(0);
    });

    it('should show error message for empty todos', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/cannot be empty/i)).toBeInTheDocument();
    });

    it('should clear error when user starts typing', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      // Trigger error
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(screen.getByRole('alert')).toBeInTheDocument();
      
      // Start typing
      fireEvent.change(input, { target: { value: 'N' } });
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('Todo Display', () => {
    it('should display todos with correct data-testid format', () => {
      const initialTodos = [
        {
          id: 'custom-id-123',
          text: 'Custom ID todo',
          completed: false,
          createdAt: new Date(),
        },
      ];

      render(<TodoList initialTodos={initialTodos} />);
      
      expect(screen.getByTestId('todo-item-custom-id-123')).toBeInTheDocument();
    });

    it('should display multiple todos in order', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'First todo' } });
      fireEvent.click(addButton);
      
      fireEvent.change(input, { target: { value: 'Second todo' } });
      fireEvent.click(addButton);
      
      fireEvent.change(input, { target: { value: 'Third todo' } });
      fireEvent.click(addButton);
      
      const todoList = screen.getByTestId('todo-list');
      expect(todoList.children).toHaveLength(3);
      
      // Check order
      expect(todoList.children[0]).toHaveTextContent('First todo');
      expect(todoList.children[1]).toHaveTextContent('Second todo');
      expect(todoList.children[2]).toHaveTextContent('Third todo');
    });

    it('should handle special characters in todo text', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      const specialText = 'Special chars: @#$%^&*()_+{}|:"<>?[]\\;\',./ 123';
      fireEvent.change(input, { target: { value: specialText } });
      fireEvent.click(addButton);
      
      expect(screen.getByText(specialText)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle large number of todos', () => {
      const largeTodoList = Array.from({ length: 100 }, (_, i) => ({
        id: `todo-${i}`,
        text: `Todo number ${i}`,
        completed: i % 2 === 0,
        createdAt: new Date(),
      }));

      render(<TodoList initialTodos={largeTodoList} />);
      
      const todoList = screen.getByTestId('todo-list');
      expect(todoList.children).toHaveLength(100);
      
      expect(screen.getByText('Todo number 0')).toBeInTheDocument();
      expect(screen.getByText('Todo number 99')).toBeInTheDocument();
    });

    it('should handle very long todo text', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      const longText = 'A'.repeat(500);
      fireEvent.change(input, { target: { value: longText } });
      fireEvent.click(addButton);
      
      expect(screen.getByText(longText)).toBeInTheDocument();
    });

    it('should handle rapid consecutive additions', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      for (let i = 0; i < 10; i++) {
        fireEvent.change(input, { target: { value: `Rapid todo ${i}` } });
        fireEvent.click(addButton);
      }
      
      const todoList = screen.getByTestId('todo-list');
      expect(todoList.children).toHaveLength(10);
    });

    it('should handle unicode characters', () => {
      render(<TodoList />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      const unicodeText = '🚀 Unicode test: 中文 العربية 🎉';
      fireEvent.change(input, { target: { value: unicodeText } });
      fireEvent.click(addButton);
      
      expect(screen.getByText(unicodeText)).toBeInTheDocument();
    });
  });

  describe('Callback Integration', () => {
    it('should call onTodoAdd with correct todo structure', () => {
      const onTodoAdd = jest.fn();
      render(<TodoList onTodoAdd={onTodoAdd} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'Callback test' } });
      fireEvent.click(addButton);
      
      expect(onTodoAdd).toHaveBeenCalledWith({
        id: expect.any(String),
        text: 'Callback test',
        completed: false,
        createdAt: expect.any(Date),
      });
    });

    it('should not call onTodoAdd for invalid todos', () => {
      const onTodoAdd = jest.fn();
      render(<TodoList onTodoAdd={onTodoAdd} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: '' } });
      fireEvent.click(addButton);
      
      expect(onTodoAdd).not.toHaveBeenCalled();
    });

    it('should call onTodoAdd for each valid addition', () => {
      const onTodoAdd = jest.fn();
      render(<TodoList onTodoAdd={onTodoAdd} />);
      
      const input = screen.getByTestId('todo-input');
      const addButton = screen.getByTestId('add-btn');
      
      fireEvent.change(input, { target: { value: 'First' } });
      fireEvent.click(addButton);
      
      fireEvent.change(input, { target: { value: 'Second' } });
      fireEvent.click(addButton);
      
      expect(onTodoAdd).toHaveBeenCalledTimes(2);
    });
  });
});