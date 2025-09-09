I have the following application code that needs to migrate:

<source_code>
<place_code_here repo="ReactSearchJob"/>
</source_code>

Please follow these steps:

1. Migrate the provided React job search application to Angular 16.x:
   - Assume all non-provided code has been migrated with the same contract
   - Implement equivalent functionality while following Angular best practices
   - Preserve the job search and filtering capabilities

2. Architecture requirements:
   - Use @ngrx/store and @ngrx/effects for state management instead of Redux
   - Convert Redux actions and reducers to NgRx equivalents
   - Implement proper feature module structure for job search functionality
   - Split large files into separate components, services, and modules

3. Component migration:
   - Convert all React functional components to Angular components
   - Replace react-select with Angular Material Select or equivalent with proper two-way binding
   - Convert dangerouslySetInnerHTML to Angular [innerHTML] with proper sanitization
   - Migrate PureComponent optimizations to OnPush change detection strategy
   - Migrate React Router navigation to Angular Router
   - Preserve component hierarchy and data flow patterns
   - Implement proper Angular lifecycle hooks

4. State management conversion:
   - Convert Redux store to NgRx store with proper selectors
   - Migrate async actions to NgRx effects  
   - Replace Immutable.js patterns with native TypeScript immutability or Immer
   - Convert START/SUCCESS/FAIL action patterns to proper NgRx effect patterns
   - Preserve all state management logic for job data and search filters
   - Implement proper state shape and reducers

5. Service implementation:
   - Create Angular services for API communication using HttpClient
   - Convert promise-based logic to Observable patterns
   - Implement proper error handling and loading states
   - Preserve all job search API integration

6. Routing and navigation:
   - Convert HashRouter to standard Angular Router with equivalent behavior
   - Convert React Router configuration to Angular Router
   - Preserve all route paths (/vacancies, /vacancy/:id)
   - Implement proper route guards if needed
   - Maintain navigation behavior and URL structure

7. Form and search functionality:
   - Convert search components to Angular Reactive Forms
   - Preserve all search and filtering logic
   - Implement equivalent form validation and user input handling
   - Maintain search state persistence

8. UI and styling:
   - Preserve the same visual appearance and layout
   - Convert CSS classes and styling to Angular component styles
   - Maintain responsive design and user interface elements
   - Preserve pagination and job listing display

9. Code quality and optimization:
   - Follow Angular style guide and best practices
   - Implement proper TypeScript typing throughout
   - Optimize performance with OnPush change detection where appropriate
   - Do not include any TODOs in the final code

10. Deliverable format:
    - Return translated code as markdown code snippets
    - Provide complete implementation without additional comments or explanations
    - Include proper module structure and dependency injection