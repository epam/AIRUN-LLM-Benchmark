import '@testing-library/jest-dom';
import React from 'react';

// Mock fetch for testing
global.fetch = jest.fn();

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Mock common third-party libraries that might be missing
jest.mock('react-spinners/ClipLoader', () => {
  return function MockClipLoader(props: any) {
    return <div {...props}>Spinner</div>;
  };
}, { virtual: true });

jest.mock('react-spinners/PulseLoader', () => {
  return function MockPulseLoader(props: any) {
    return <div {...props}>Spinner</div>;
  };
}, { virtual: true });

jest.mock('react-spinners/BeatLoader', () => {
  return function MockBeatLoader(props: any) {
    return <div {...props}>Spinner</div>;
  };
}, { virtual: true });

jest.mock('react-spinners/RingLoader', () => {
  return function MockRingLoader(props: any) {
    return <div data-testid="mock-ringloader" {...props}>Loading...</div>;
  };
}, { virtual: true });

// Mock other common libraries
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
}), { virtual: true });

jest.mock('lodash', () => ({
  debounce: jest.fn((fn) => fn),
  throttle: jest.fn((fn) => fn),
  get: jest.fn(),
  set: jest.fn(),
  cloneDeep: jest.fn((obj) => JSON.parse(JSON.stringify(obj))),
}), { virtual: true });

// Reset mocks after each test
afterEach(() => {
  jest.clearAllMocks();
});