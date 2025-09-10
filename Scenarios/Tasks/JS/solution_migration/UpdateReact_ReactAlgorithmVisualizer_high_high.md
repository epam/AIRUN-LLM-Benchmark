I have the following application code that needs to update:

<source_code>
<place_code_here repo="ReactAlgorithmVisualizer"/>
</source_code>

Please follow these steps:

1. Migrate the provided React application to React 19.x:
   - Update all React and ReactDOM imports to React 19 compatible usage
   - Replace deprecated lifecycle methods with modern alternatives
   - Update entry point to use createRoot API
   - Implement React 19 features where appropriate

2. Modernize state management with Redux Toolkit:
   - Replace legacy Redux patterns with configureStore
   - Convert reducers to createSlice pattern; remove redux-actions
   - Replace direct state mutations with immutable updates via RTK (Immer)
   - Keep existing state shape and behavior intact

3. Update routing to React Router v6:
   - Migrate from react-router v5 and react-router-redux
   - Replace Switch with Routes, component with element, and history.push with useNavigate
   - Ensure all routes continue to function

4. Update TypeScript and typing (if TypeScript is introduced):
   - Prefer TypeScript typings for components, props, and store if applicable
   - Remove PropTypes in favor of TypeScript interfaces if present

5. Restructure where helpful:
   - Split monolithic components into smaller, focused components
   - Organize files by feature or functionality
   - Implement proper component composition patterns

6. Implement modern React patterns and performance optimizations:
   - Prefer functional components with hooks over class components
   - Use React.memo, useCallback, and useMemo appropriately
   - Use React.lazy/Suspense for code splitting where appropriate

7. Update dependencies and configuration:
   - Upgrade to React 19.x and compatible react-dom
   - Upgrade react-scripts (or migrate away from CRA if necessary) to a version compatible with React 19
   - Upgrade related libraries to versions compatible with React 19 and Router v6
   - Remove deprecated packages (e.g., react-router-redux)

8. Clean up and quality requirements:
   - Ensure no TODOs remain
   - Follow consistent naming conventions
   - Implement proper error handling and error boundaries where needed

9. Verify functionality specific to Algorithm Visualizer:
   - Ensure algorithm playback/controls, charts, and editors still render and function
   - Preserve URL-based navigation to different visualizations
   - Maintain keyboard/mouse interactions and fullscreen where present
