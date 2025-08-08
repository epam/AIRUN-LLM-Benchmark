import React, { createRef } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Counter from './component';

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

describe('Counter Component - Iteration 4 (Persistence + History)', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    jest.clearAllMocks();
  });

  describe('All Previous Functionality (Backward Compatibility)', () => {
    it('should maintain all previous functionality', () => {
      render(<Counter 
        initialValue={5} 
        resetValue={0} 
        step={2} 
        minValue={0} 
        maxValue={20} 
      />);
      
      // Basic functionality
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('7');
      
      // Reset
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
      
      // Bounds
      for (let i = 0; i < 15; i++) {
        fireEvent.click(screen.getByTestId('increment-btn'));
      }
      expect(screen.getByTestId('counter-display')).toHaveTextContent('20');
    });
  });

  describe('Persistence with localStorage', () => {
    it('should save to localStorage when persistKey is provided', () => {
      render(<Counter initialValue={5} persistKey="test-counter" />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'test-counter',
        expect.stringContaining('6')
      );
    });

    it('should not save to localStorage when persistKey is not provided', () => {
      render(<Counter initialValue={5} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
    });

    it('should load from localStorage on mount when persistKey is provided', () => {
      // Pre-populate localStorage
      mockLocalStorage.setItem('test-counter', JSON.stringify({
        count: 42,
        history: [40, 41, 42]
      }));
      
      render(<Counter initialValue={0} persistKey="test-counter" />);
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('42');
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith('test-counter');
    });

    it('should handle corrupted localStorage data gracefully', () => {
      mockLocalStorage.setItem('test-counter', 'invalid-json');
      
      // Should not crash and use initialValue
      render(<Counter initialValue={10} persistKey="test-counter" />);
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
    });

    it('should handle missing localStorage data', () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      
      render(<Counter initialValue={15} persistKey="test-counter" />);
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('15');
    });

    it('should update localStorage on every counter change', () => {
      render(<Counter initialValue={0} persistKey="test-counter" />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('decrement-btn'));
      
      expect(mockLocalStorage.setItem).toHaveBeenCalledTimes(3);
    });
  });

  describe('History Functionality', () => {
    it('should show history when showHistory is true', () => {
      render(<Counter initialValue={0} showHistory={true} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      const historyElement = screen.getByTestId('counter-history');
      expect(historyElement).toBeInTheDocument();
      
      // Should show recent values
      expect(historyElement).toHaveTextContent('2');
      expect(historyElement).toHaveTextContent('1');
    });

    it('should not show history when showHistory is false or undefined', () => {
      render(<Counter initialValue={0} showHistory={false} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      expect(screen.queryByTestId('counter-history')).not.toBeInTheDocument();
    });

    it('should limit history to last 5 values', () => {
      render(<Counter initialValue={0} showHistory={true} />);
      
      // Generate more than 5 changes
      for (let i = 0; i < 8; i++) {
        fireEvent.click(screen.getByTestId('increment-btn'));
      }
      
      const historyElement = screen.getByTestId('counter-history');
      const historyItems = historyElement.querySelectorAll('li');
      
      expect(historyItems).toHaveLength(5);
      
      // Should contain recent values (4, 5, 6, 7, 8)
      expect(historyElement).toHaveTextContent('8');
      expect(historyElement).toHaveTextContent('7');
      expect(historyElement).toHaveTextContent('6');
      expect(historyElement).toHaveTextContent('5');
      expect(historyElement).toHaveTextContent('4');
      expect(historyElement).not.toHaveTextContent('3');
    });

    it('should update history on reset', () => {
      render(<Counter initialValue={10} resetValue={0} showHistory={true} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('reset-btn'));
      
      const historyElement = screen.getByTestId('counter-history');
      expect(historyElement).toHaveTextContent('0');
      expect(historyElement).toHaveTextContent('11');
    });

    it('should load history from localStorage', () => {
      mockLocalStorage.setItem('test-counter', JSON.stringify({
        count: 5,
        history: [3, 4, 5]
      }));
      
      render(<Counter 
        initialValue={0} 
        persistKey="test-counter" 
        showHistory={true} 
      />);
      
      const historyElement = screen.getByTestId('counter-history');
      expect(historyElement).toHaveTextContent('3');
      expect(historyElement).toHaveTextContent('4');
      expect(historyElement).toHaveTextContent('5');
    });
  });

  describe('onHistoryChange Callback', () => {
    it('should call onHistoryChange when history updates', () => {
      const onHistoryChange = jest.fn();
      
      render(<Counter 
        initialValue={0} 
        showHistory={true}
        onHistoryChange={onHistoryChange}
      />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      expect(onHistoryChange).toHaveBeenCalledWith(expect.arrayContaining([1]));
    });

    it('should call onHistoryChange with correct history array', () => {
      const onHistoryChange = jest.fn();
      
      render(<Counter 
        initialValue={5} 
        onHistoryChange={onHistoryChange}
      />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      expect(onHistoryChange).toHaveBeenLastCalledWith([7, 6]);
    });

    it('should not call onHistoryChange if callback is not provided', () => {
      // Should not throw errors
      render(<Counter initialValue={0} showHistory={true} />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('1');
    });
  });

  describe('clearHistory Ref Method', () => {
    it('should expose clearHistory method via ref', () => {
      const ref = createRef<any>();
      
      render(<Counter 
        ref={ref}
        initialValue={0} 
        showHistory={true}
      />);
      
      expect(ref.current).toBeTruthy();
      expect(typeof ref.current.clearHistory).toBe('function');
    });

    it('should clear history when clearHistory is called', () => {
      const ref = createRef<any>();
      
      render(<Counter 
        ref={ref}
        initialValue={0} 
        showHistory={true}
      />);
      
      // Generate some history
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      let historyElement = screen.getByTestId('counter-history');
      expect(historyElement.querySelectorAll('li')).toHaveLength(2);
      
      // Clear history
      ref.current.clearHistory();
      
      historyElement = screen.getByTestId('counter-history');
      expect(historyElement.querySelectorAll('li')).toHaveLength(0);
    });

    it('should clear localStorage history when clearHistory is called with persistKey', () => {
      const ref = createRef<any>();
      
      render(<Counter 
        ref={ref}
        initialValue={5} 
        persistKey="test-counter"
        showHistory={true}
      />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      ref.current.clearHistory();
      
      expect(mockLocalStorage.setItem).toHaveBeenLastCalledWith(
        'test-counter',
        JSON.stringify({ count: 6, history: [] })
      );
    });

    it('should call onHistoryChange when clearHistory is called', () => {
      const onHistoryChange = jest.fn();
      const ref = createRef<any>();
      
      render(<Counter 
        ref={ref}
        initialValue={0}
        onHistoryChange={onHistoryChange}
      />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      onHistoryChange.mockClear();
      
      ref.current.clearHistory();
      
      expect(onHistoryChange).toHaveBeenCalledWith([]);
    });
  });

  describe('Integration: Persistence + History', () => {
    it('should save both count and history to localStorage', () => {
      render(<Counter 
        initialValue={0} 
        persistKey="test-counter"
        showHistory={true}
      />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      fireEvent.click(screen.getByTestId('increment-btn'));
      
      const expectedData = JSON.stringify({
        count: 2,
        history: [2, 1]
      });
      
      expect(mockLocalStorage.setItem).toHaveBeenLastCalledWith(
        'test-counter',
        expectedData
      );
    });

    it('should restore both count and history from localStorage', () => {
      mockLocalStorage.setItem('test-counter', JSON.stringify({
        count: 10,
        history: [8, 9, 10]
      }));
      
      render(<Counter 
        initialValue={0} 
        persistKey="test-counter"
        showHistory={true}
      />);
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('10');
      
      const historyElement = screen.getByTestId('counter-history');
      expect(historyElement).toHaveTextContent('8');
      expect(historyElement).toHaveTextContent('9');
      expect(historyElement).toHaveTextContent('10');
    });

    it('should work with all features combined', () => {
      const onValueChange = jest.fn();
      const onHistoryChange = jest.fn();
      const onError = jest.fn();
      const ref = createRef<any>();
      
      render(<Counter 
        ref={ref}
        initialValue={5}
        resetValue={0}
        step={2}
        minValue={0}
        maxValue={15}
        persistKey="test-counter"
        showHistory={true}
        onValueChange={onValueChange}
        onHistoryChange={onHistoryChange}
        onError={onError}
      />);
      
      // Test increment with bounds
      for (let i = 0; i < 6; i++) {
        fireEvent.click(screen.getByTestId('increment-btn'));
      }
      
      expect(screen.getByTestId('counter-display')).toHaveTextContent('15');
      expect(onError).toHaveBeenCalled(); // Should hit max bound
      
      // Test reset with history
      fireEvent.click(screen.getByTestId('reset-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('0');
      
      // Check localStorage was updated
      expect(mockLocalStorage.setItem).toHaveBeenCalled();
      
      // Check history
      const historyElement = screen.getByTestId('counter-history');
      expect(historyElement).toBeInTheDocument();
      
      // Clear history via ref
      ref.current.clearHistory();
      expect(onHistoryChange).toHaveBeenLastCalledWith([]);
    });
  });

  describe('Edge Cases', () => {
    it('should handle localStorage being unavailable', () => {
      // Mock localStorage to throw
      mockLocalStorage.setItem.mockImplementation(() => {
        throw new Error('localStorage unavailable');
      });
      
      // Should not crash
      render(<Counter initialValue={5} persistKey="test-counter" />);
      
      fireEvent.click(screen.getByTestId('increment-btn'));
      expect(screen.getByTestId('counter-display')).toHaveTextContent('6');
    });

    it('should handle ref methods called before component is mounted', () => {
      const ref = createRef<any>();
      
      render(<Counter ref={ref} initialValue={0} />);
      
      // Should not throw
      expect(() => ref.current.clearHistory()).not.toThrow();
    });

    it('should handle history with bounds correctly', () => {
      render(<Counter 
        initialValue={8} 
        minValue={0} 
        maxValue={10} 
        step={3}
        showHistory={true}
      />);
      
      fireEvent.click(screen.getByTestId('increment-btn')); // Should be clamped to 10
      fireEvent.click(screen.getByTestId('decrement-btn')); // 10 -> 7
      
      const historyElement = screen.getByTestId('counter-history');
      expect(historyElement).toHaveTextContent('10');
      expect(historyElement).toHaveTextContent('7');
    });
  });
});