import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Counter from './component';

describe('Counter Component - Iteration 2 (Reset + Custom Step)', () => {
  describe('All Previous Functionality (Backward Compatibility)', () => {
    it('should maintain basic increment/decrement functionality', () => {
      render(<Counter initialValue={5} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('6');
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('5');
    });

    it('should still call onValueChange callback', () => {
      const onValueChange = jest.fn();
      render(<Counter initialValue={10} onValueChange={onValueChange} />);
      
      onValueChange.mockClear();
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(onValueChange).toHaveBeenCalledWith(11);
    });
  });

  describe('Reset Functionality', () => {
    it('should have reset button with correct data-testid', () => {
      render(<Counter />);
      expect(screen.getByTestId('reset-btn')).toBeInTheDocument();
    });

    it('should reset to default resetValue (0) when reset button is clicked', () => {
      render(<Counter initialValue={25} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('26');
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
    });

    it('should reset to custom resetValue when provided', () => {
      render(<Counter initialValue={50} resetValue={10} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('51');
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });

    it('should handle negative resetValue', () => {
      render(<Counter initialValue={20} resetValue={-5} />);
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('-5');
    });

    it('should work from any counter value', () => {
      render(<Counter initialValue={100} resetValue={42} />);
      
      // Modify counter first
      fireEvent.click(screen.getByTestId('decrement-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('98');
      
      // Reset should work
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('42');
    });
  });

  describe('onReset Callback', () => {
    it('should call onReset callback when reset button is clicked', () => {
      const onReset = jest.fn();
      render(<Counter initialValue={15} resetValue={5} onReset={onReset} />);
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(onReset).toHaveBeenCalledWith(5);
    });

    it('should call onReset with default resetValue (0) if not specified', () => {
      const onReset = jest.fn();
      render(<Counter initialValue={20} onReset={onReset} />);
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(onReset).toHaveBeenCalledWith(0);
    });

    it('should not call onReset if callback is not provided', () => {
      // Should not throw errors
      render(<Counter initialValue={10} resetValue={3} />);
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('3');
    });
  });

  describe('Custom Step Functionality', () => {
    it('should have step input with correct data-testid', () => {
      render(<Counter />);
      expect(screen.getByTestId('step-input')).toBeInTheDocument();
    });

    it('should use default step of 1', () => {
      render(<Counter initialValue={10} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('11');
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });

    it('should use custom step prop', () => {
      render(<Counter initialValue={10} step={5} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('15');
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });

    it('should update step via input field', () => {
      render(<Counter initialValue={0} />);
      
      const stepInput = screen.getByTestId('step-input');
      
      // Change step to 3
      fireEvent.change(stepInput, { target: { value: '3' } });
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('3');
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('6');
    });

    it('should handle large step values', () => {
      render(<Counter initialValue={0} />);
      
      const stepInput = screen.getByTestId('step-input');
      fireEvent.change(stepInput, { target: { value: '100' } });
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('100');
    });

    it('should display current step value in input', () => {
      render(<Counter step={7} />);
      
      const stepInput = screen.getByTestId('step-input') as HTMLInputElement;
      expect(stepInput.value).toBe('7');
    });
  });

  describe('Step Input Edge Cases', () => {
    it('should handle invalid step input gracefully', () => {
      render(<Counter initialValue={5} />);
      
      const stepInput = screen.getByTestId('step-input');
      
      // Try to enter invalid value
      fireEvent.change(stepInput, { target: { value: 'invalid' } });
      
      // Should still work with previous valid step
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('6');
    });

    it('should handle zero step input', () => {
      render(<Counter initialValue={10} />);
      
      const stepInput = screen.getByTestId('step-input');
      fireEvent.change(stepInput, { target: { value: '0' } });
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      // Should not change or handle gracefully
      const display = screen.getByTestId('counter-display');
      expect(['10', '10']).toContain(display.textContent);
    });

    it('should handle negative step input', () => {
      render(<Counter initialValue={10} />);
      
      const stepInput = screen.getByTestId('step-input');
      fireEvent.change(stepInput, { target: { value: '-2' } });
      
      // Behavior may vary - increment with negative step
      fireEvent.click(screen.getByTestId('increment-btn'));
      const result = screen.getByTestId('counter-display').textContent;
      expect(['8', '12', '10']).toContain(result); // Allow different implementations
    });
  });

  describe('Integration: Reset + Custom Step', () => {
    it('should reset work correctly with custom step', () => {
      render(<Counter initialValue={0} step={5} resetValue={20} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('5');
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('20');
      
      // Step should still work after reset
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('25');
    });

    it('should maintain step value after reset', () => {
      render(<Counter initialValue={0} />);
      
      // Change step
      const stepInput = screen.getByTestId('step-input');
      fireEvent.change(stepInput, { target: { value: '4' } });
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('4');
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
      
      // Step should still be 4
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('4');
    });
  });

  describe('Callbacks Integration', () => {
    it('should call both onValueChange and onReset appropriately', () => {
      const onValueChange = jest.fn();
      const onReset = jest.fn();
      
      render(<Counter 
        initialValue={10} 
        resetValue={5} 
        onValueChange={onValueChange}
        onReset={onReset}
      />);
      
      onValueChange.mockClear();
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(onValueChange).toHaveBeenCalledWith(11);
      expect(onReset).not.toHaveBeenCalled();
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(onReset).toHaveBeenCalledWith(5);
      // onValueChange should also be called for reset value
    });
  });
});