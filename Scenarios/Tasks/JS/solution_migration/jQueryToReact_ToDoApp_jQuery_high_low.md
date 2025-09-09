I have the following application code that needs to migrate:

<source_code>
<place_code_here repo="ToDoApp_jQuery"/>
</source_code>

Please follow these steps:

1. Migrate the provided jQuery application to React 18:
   - Convert the jQuery-based implementation to React 18.x
   - Maintain all existing functionality and behavior
   - Preserve the same visual appearance and user experience

2. Use the following technology stack:
   - Create React App as the project foundation
   - TypeScript for type safety
   - Redux Toolkit with createSlice for state management
   - React Router for client-side routing (migrating from Director.js)
   - nanoid for generating unique IDs (replacing custom UUID function)

3. Project structure and architecture:
   - Split the application into separate components following React best practices
   - Implement proper component hierarchy and composition
   - Create appropriate TypeScript interfaces/types for all data structures
   - Organize code into feature-based or domain-based modules

4. State management implementation:
   - Configure Redux store properly
   - Set up Redux provider in the application entry point
   - Create appropriate slices using Redux Toolkit's createSlice
   - Implement all required reducers, actions, and selectors

5. Technical requirements:
   - Implement hash-based routing with React Router (/#/all, /#/active, /#/completed)
   - Convert Handlebars templates to JSX components
   - Migrate jQuery event delegation to React event handling
   - Preserve all keyboard shortcuts (Enter key for creating/updating, Escape for canceling)
   - Implement localStorage persistence for todos (note: original has stubbed implementation)
   - Transform direct DOM manipulation to React state management patterns

6. Code quality:
   - Optimize the code where possible
   - Follow React best practices and patterns
   - Ensure the code is production-ready with no TODOs
   - Use functional components with hooks instead of class components
   - Implement proper error handling
