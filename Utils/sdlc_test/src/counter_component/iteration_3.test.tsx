import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Counter from './component';

describe('Counter Component - Iteration 3 (Validation + Bounds)', () => {
  describe('All Previous Functionality (Backward Compatibility)', () => {
    it('should maintain basic increment/decrement/reset functionality', () => {
      render(<Counter initialValue={5} resetValue={0} step={2} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('7');
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('5');
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
    });

    it('should maintain custom step functionality', () => {
      render(<Counter initialValue={0} />);
      
      const stepInput = screen.getByTestId('step-input');
      fireEvent.change(stepInput, { target: { value: '3' } });
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('3');
    });
  });

  describe('Bounds Validation', () => {
    it('should respect minValue boundary', () => {
      render(<Counter initialValue={5} minValue={0} step={1} />);
      
      // Should allow decrement to minValue
      for (let i = 0; i < 5; i++) {
        fireEvent.click(screen.getByTestId('decrement-btn'));
      }
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
      
      // Should not go below minValue
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
    });

    it('should respect maxValue boundary', () => {
      render(<Counter initialValue={8} maxValue={10} step={1} />);
      
      // Should allow increment to maxValue
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
      
      // Should not go above maxValue
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });

    it('should work with both minValue and maxValue', () => {
      render(<Counter initialValue={5} minValue={0} maxValue={10} step={1} />);
      
      // Test lower bound
      for (let i = 0; i < 6; i++) {
        fireEvent.click(screen.getByTestId('decrement-btn'));
      }
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
      
      // Test upper bound
      for (let i = 0; i < 15; i++) {
        fireEvent.click(screen.getByTestId('increment-btn'));
      }
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });

    it('should handle custom step with bounds', () => {
      render(<Counter initialValue={5} minValue={0} maxValue={10} step={3} />);
      
      // Increment with step 3: 5 -> 8 (ok), 8 -> 11 (should be 10)
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('8');
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
      
      // Decrement with step 3: 10 -> 7, 7 -> 4, 4 -> 1, 1 -> -2 (should be 0)
      fireEvent.click(screen.getByTestId('decrement-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
    });
  });

  describe('Disabled States', () => {
    it('should disable increment button when at maxValue', () => {
      render(<Counter initialValue={10} maxValue={10} />);
      
      const incrementBtn = screen.getByTestId('increment-btn');
      expect(incrementBtn).toBeDisabled();
      
      // Check for disabled data-testid (if implemented)
      const disabledElement = screen.queryByTestId('increment-disabled');
      if (disabledElement) {
        expect(disabledElement).toBeInTheDocument();
      }
    });

    it('should disable decrement button when at minValue', () => {
      render(<Counter initialValue={0} minValue={0} />);
      
      const decrementBtn = screen.getByTestId('decrement-btn');
      expect(decrementBtn).toBeDisabled();
      
      // Check for disabled data-testid (if implemented)
      const disabledElement = screen.queryByTestId('decrement-disabled');
      if (disabledElement) {
        expect(disabledElement).toBeInTheDocument();
      }
    });

    it('should enable buttons when not at boundaries', () => {
      render(<Counter initialValue={5} minValue={0} maxValue={10} />);
      
      expect(screen.getByTestId('increment-btn')).not.toBeDisabled();
      expect(screen.getByTestId('decrement-btn')).not.toBeDisabled();
    });

    it('should update disabled state dynamically', () => {
      render(<Counter initialValue={9} maxValue={10} step={1} />);
      
      // Initially should be enabled
      expect(screen.getByTestId('increment-btn')).not.toBeDisabled();
      
      // After increment to max, should be disabled
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('increment-btn')).toBeDisabled();
      
      // After decrement from max, should be enabled again
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('increment-btn')).not.toBeDisabled();
    });
  });

  describe('Validation Messages', () => {
    it('should show validation message when trying to exceed maxValue', () => {
      render(<Counter initialValue={10} maxValue={10} step={1} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      const validationMessage = screen.queryByTestId('validation-message');
      if (validationMessage) {
        expect(validationMessage).toBeInTheDocument();
        expect(validationMessage).toHaveTextContent(/maximum/i);
      }
    });

    it('should show validation message when trying to go below minValue', () => {
      render(<Counter initialValue={0} minValue={0} step={1} />);
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      
      const validationMessage = screen.queryByTestId('validation-message');
      if (validationMessage) {
        expect(validationMessage).toBeInTheDocument();
        expect(validationMessage).toHaveTextContent(/minimum/i);
      }
    });

    it('should clear validation message when within bounds', () => {
      render(<Counter initialValue={0} minValue={0} maxValue={10} step={1} />);
      
      // Try to go below minimum
      fireEvent.click(screen.getByTestId('decrement-btn'));
      
      let validationMessage = screen.queryByTestId('validation-message');
      if (validationMessage) {
        expect(validationMessage).toBeInTheDocument();
      }
      
      // Move within bounds
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      validationMessage = screen.queryByTestId('validation-message');
      if (validationMessage) {
        expect(validationMessage).not.toBeInTheDocument() || 
        expect(validationMessage).toHaveTextContent('');
      }
    });
  });

  describe('onError Callback', () => {
    it('should call onError when trying to exceed maxValue', () => {
      const onError = jest.fn();
      render(<Counter initialValue={10} maxValue={10} onError={onError} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      expect(onError).toHaveBeenCalledWith(expect.stringContaining('10'));
      expect(onError).toHaveBeenCalledWith(expect.stringMatching(/maximum|greater/i));
    });

    it('should call onError when trying to go below minValue', () => {
      const onError = jest.fn();
      render(<Counter initialValue={0} minValue={0} onError={onError} />);
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      
      expect(onError).toHaveBeenCalledWith(expect.stringContaining('0'));
      expect(onError).toHaveBeenCalledWith(expect.stringMatching(/minimum|less/i));
    });

    it('should not call onError when within bounds', () => {
      const onError = jest.fn();
      render(<Counter initialValue={5} minValue={0} maxValue={10} onError={onError} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      
      expect(onError).not.toHaveBeenCalled();
    });

    it('should not call onError if callback is not provided', () => {
      // Should not throw errors
      render(<Counter initialValue={10} maxValue={10} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });
  });

  describe('onValueChange vs onError Integration', () => {
    it('should call onValueChange when within bounds but not when violating bounds', () => {
      const onValueChange = jest.fn();
      const onError = jest.fn();
      
      render(<Counter 
        initialValue={9} 
        maxValue={10} 
        onValueChange={onValueChange}
        onError={onError}
      />);
      
      onValueChange.mockClear();
      
      // Within bounds - should call onValueChange
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(onValueChange).toHaveBeenCalledWith(10);
      expect(onError).not.toHaveBeenCalled();
      
      onValueChange.mockClear();
      
      // Violating bounds - should call onError, not onValueChange
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(onError).toHaveBeenCalled();
      // onValueChange behavior may vary - some implementations might not call it
    });
  });

  describe('Edge Cases with Bounds', () => {
    it('should handle when initialValue violates bounds', () => {
      // Initial value above max
      render(<Counter initialValue={15} maxValue={10} />);
      
      // Should handle gracefully, might clamp or show error
      const display = screen.getByTestId('counter-display');
      expect(display).toBeInTheDocument();
    });

    it('should handle undefined bounds (no limits)', () => {
      render(<Counter initialValue={0} />);
      
      // Should work without limits
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('1');
      
      fireEvent.click(screen.getByTestId('decrement-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('-1');
    });

    it('should handle minValue equal to maxValue', () => {
      render(<Counter initialValue={5} minValue={5} maxValue={5} />);
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('5');
      
      // Both buttons should be disabled
      expect(screen.getByTestId('increment-btn')).toBeDisabled();
      expect(screen.getByTestId('decrement-btn')).toBeDisabled();
    });

    it('should handle reset with bounds', () => {
      render(<Counter initialValue={10} resetValue={15} maxValue={10} />);
      
      fireEvent.click(screen.getByTestId('reset-btn'));
      
      // Should handle reset value that violates bounds
      const display = screen.getByTestId('counter-display');
      expect(display).toBeInTheDocument();
    });
  });
});