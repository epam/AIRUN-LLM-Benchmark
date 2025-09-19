I have the following application code that needs to migrate:

<source_code>
<place_code_here repo="AngularMeteo"/>
</source_code>

Please follow these steps:

1. Migrate the provided Angular weather application to React 19.x:
   - Assume all non-provided code has been migrated with the same contract
   - Implement equivalent functionality while following React best practices
   - Preserve the weather data visualization and location search capabilities

2. Architecture requirements:
   - Use React Context API or state management library for weather data state
   - Convert Angular services to React custom hooks and utility functions
   - Implement proper component composition patterns for weather visualization
   - Split large files into separate components, hooks, and utilities

3. Component migration:
   - Convert all Angular components to React functional components
   - Replace Angular standalone components with React component composition
   - Convert Angular inputs/outputs to React props and callback patterns
   - Migrate Angular lifecycle hooks to React useEffect and custom hooks
   - Preserve component hierarchy and data flow patterns
   - Implement proper React lifecycle management

4. State management conversion:
   - Convert Angular services to React custom hooks for weather data management
   - Migrate async operations to React patterns with useEffect and custom hooks
   - Replace Angular dependency injection with React Context providers
   - Convert Angular observables to React state and async patterns
   - Preserve all weather data fetching and location search logic
   - Implement proper state shape and data flow

5. Service implementation:
   - Create React custom hooks for Open-Meteo API communication
   - Convert Angular HTTP client usage to fetch API or HTTP library
   - Implement proper error handling and loading states with React patterns
   - Preserve all weather data processing and geolocation integration

6. Canvas visualization migration:
   - Convert Angular canvas rendering to React refs and useEffect patterns
   - Migrate waterfall chart implementation to React canvas patterns
   - Preserve all visualization logic for weather data display
   - Implement proper cleanup and performance optimization

7. Form and interaction functionality:
   - Convert Angular form controls to React controlled components
   - Preserve all autocomplete and location search logic
   - Implement equivalent user input handling and validation
   - Maintain search state and user interaction patterns

8. UI and styling:
   - Preserve the same visual appearance and layout
   - Convert Angular component styles to React styling approach
   - Maintain responsive design and weather data visualization elements
   - Preserve accessibility features and user interface components

9. Code quality and optimization:
   - Follow React best practices and modern patterns
   - Implement proper TypeScript typing throughout
   - Optimize performance with React.memo and useMemo where appropriate
   - Resolve any existing TODOs found in the source code during migration

10. Deliverable format:
    - Return translated code as markdown code snippets
    - Provide complete implementation without additional comments or explanations
    - Include proper React project structure and component organization