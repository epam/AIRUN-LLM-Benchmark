I have the following application code that needs to update:

<source_code>
<place_code_here repo="ReactSearchJob"/>
</source_code>

Please follow these steps:

1. Migrate the provided React application to React 19.x:
   - Update all React imports to React 19.x compatible syntax
   - Replace deprecated React lifecycle methods with modern alternatives
   - Implement React 19 features where appropriate

2. Implement state management using Redux Toolkit:
   - Replace createStore with configureStore
   - Convert reducers to createSlice pattern
   - Replace direct state mutations with immutable state updates

3. Update TypeScript implementation:
   - Ensure all components use proper TypeScript typing
   - Define interfaces for all props, state, and Redux store
   - Implement strict type checking throughout the application
   - Remove Proptypes in favor of TypeScript interfaces
   - Remove Immutable.js usage

4. Restructure the application architecture:
   - Split the monolithic components into smaller, focused components
   - Organize files by feature or functionality
   - Implement proper component composition patterns

5. Implement modern React patterns:
   - Replace class components with functional components and hooks
   - Use React performance hooks for performance optimization where appropriate

6. Update dependencies and configuration:
   - Create a package.json with all required dependencies
   - Configure Redux store with proper middleware
   - Set up Redux Provider in the application entry point
   - Upgrade React Router from v5 to v6
   - Update routing patterns and navigation methods

7. Optimize for performance:
   - Implement proper memoization strategies
   - Avoid unnecessary re-renders
   - Use React.lazy for code splitting where appropriate

8. Code quality requirements:
   - Ensure no TODOs remain in the codebase
   - Follow consistent naming conventions
   - Implement proper error handling
