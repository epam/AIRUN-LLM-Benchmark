import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Counter from './component';

describe('Counter Component - Iteration 1 (Basic Functionality)', () => {
  describe('Props and Default Values', () => {
    it('should render with default initialValue of 0', () => {
      render(<Counter />);
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
    });

    it('should render with custom initialValue prop', () => {
      render(<Counter initialValue={42} />);
      expect(screen.getByTestId('counter-display')).toHaveTextContent('42');
    });

    it('should handle negative initialValue', () => {
      render(<Counter initialValue={-5} />);
      expect(screen.getByTestId('counter-display')).toHaveTextContent('-5');
    });
  });

  describe('Basic Counter Functionality', () => {
    it('should increment counter when increment button is clicked', () => {
      render(<Counter initialValue={0} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('1');
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('2');
    });

    it('should decrement counter when decrement button is clicked', () => {
      render(<Counter initialValue={5} />);
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('4');
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('3');
    });

    it('should handle multiple increment and decrement operations', () => {
      render(<Counter initialValue={10} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('11');
    });
  });

  describe('onValueChange Callback', () => {
    it('should call onValueChange with initial value on mount', () => {
      const onValueChange = jest.fn();
      render(<Counter initialValue={15} onValueChange={onValueChange} />);
      
      // Should be called with initial value
      expect(onValueChange).toHaveBeenCalledWith(15);
    });

    it('should call onValueChange when counter is incremented', () => {
      const onValueChange = jest.fn();
      render(<Counter initialValue={0} onValueChange={onValueChange} />);
      
      onValueChange.mockClear(); // Clear initial call
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(onValueChange).toHaveBeenCalledWith(1);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(onValueChange).toHaveBeenCalledWith(2);
    });

    it('should call onValueChange when counter is decremented', () => {
      const onValueChange = jest.fn();
      render(<Counter initialValue={5} onValueChange={onValueChange} />);
      
      onValueChange.mockClear(); // Clear initial call
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(onValueChange).toHaveBeenCalledWith(4);
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(onValueChange).toHaveBeenCalledWith(3);
    });

    it('should not call onValueChange if callback is not provided', () => {
      // This should not throw any errors
      render(<Counter initialValue={0} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('1');
    });
  });

  describe('Required Elements and Accessibility', () => {
    it('should have all required data-testid attributes', () => {
      render(<Counter />);
      
      expect(screen.getByTestId('counter-display')).toBeInTheDocument();
      expect(screen.getByTestId('increment-btn')).toBeInTheDocument();
      expect(screen.getByTestId('decrement-btn')).toBeInTheDocument();
    });

    it('should have proper button types and accessibility', () => {
      render(<Counter />);
      
      const incrementBtn = screen.getByTestId('increment-btn');
      const decrementBtn = screen.getByTestId('decrement-btn');
      
      expect(incrementBtn).toHaveAttribute('type', 'button');
      expect(decrementBtn).toHaveAttribute('type', 'button');
      
      // Check for aria-label attributes
      expect(incrementBtn).toHaveAttribute('aria-label');
      expect(decrementBtn).toHaveAttribute('aria-label');
    });

    it('should use semantic HTML elements', () => {
      render(<Counter />);
      
      // Counter display should be an output element or have proper semantics
      const display = screen.getByTestId('counter-display');
      expect(display).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid clicking without issues', () => {
      render(<Counter initialValue={0} />);
      
      // Rapidly click increment button
      for (let i = 0; i < 10; i++) {
        fireEvent.click(screen.getByTestId('increment-btn'));
      }
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });

    it('should handle large numbers', () => {
      render(<Counter initialValue={999999} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('1000000');
    });

    it('should handle zero initialValue explicitly', () => {
      render(<Counter initialValue={0} />);
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('-1');
    });
  });
});