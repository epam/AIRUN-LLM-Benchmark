I have the following application code that needs to migrate:

<source_code>
<place_code_here repo="AngularJSCosmoPage"/>
</source_code>

Please follow these steps:

1. Migrate the codebase from Angular to React 18.x:
   - Use TypeScript for all components and services
   - Implement strict typing for all variables, functions, and props
   - Maintain the same functionality as the original Angular application

2. State Management Requirements:
   - Implement Redux Toolkit with createSlice for global state management
   - Create appropriate slices for each data domain
   - Use Redux selectors for accessing state
   - Implement proper action creators for state mutations

3. Component Architecture:
   - Split monolithic controllers into separate functional components
   - Create reusable UI components where patterns are identified
   - Implement proper prop typing with TypeScript interfaces
   - Use React hooks (useState, useEffect, useCallback, useMemo) appropriately

4. API Communication:
   - Replace Angular's $resource with appropriate React/Redux API handling
   - Implement API services using modern fetch or axios
   - Handle API responses and errors consistently
   - Maintain the same API endpoints structure

5. Form Handling:
   - Replace Angular form bindings with React controlled components
   - Implement form validation equivalent to the original
   - Use React hooks for form state management
   - Maintain the same validation rules and error handling

6. Routing:
   - Replace Angular routing with React Router
   - Maintain the same URL structure and parameters
   - Implement route guards where necessary
   - Handle route transitions properly

7. Internationalization:
   - Replace Angular's $translate with appropriate React i18n library
   - Maintain all translation keys and functionality
   - Implement language switching if present in original code

8. Optimization Requirements:
   - Implement code splitting for better performance
   - Use React.memo for expensive renders
   - Implement proper dependency arrays in useEffect and other hooks
   - Optimize re-renders with proper component structure

9. Local Storage Handling:
   - Maintain the same local storage functionality for draft management
   - Implement proper hooks for local storage access
   - Handle version comparison and restoration features
   - Migrate localStorage-based draft detection and recovery logic

10. File Upload Integration:
    - Replace Angular's $upload with appropriate React file upload solution
    - Implement file handling for featured image functionality
    - Maintain the same upload workflow and error handling

11. Event Communication:
    - Replace $rootScope.$broadcast with appropriate React patterns
    - Implement custom hooks or context for cross-component communication
    - Maintain notification system functionality using React state management

12. Promise Chain Migration:
    - Convert complex AngularJS promise chains to modern async/await patterns
    - Implement proper error handling for nested API operations
    - Maintain the same operation sequencing for save/update workflows

13. Code Structure:
    - Organize code into feature folders
    - Separate business logic from UI components
    - Create proper TypeScript interfaces for all data models
    - Implement consistent naming conventions
