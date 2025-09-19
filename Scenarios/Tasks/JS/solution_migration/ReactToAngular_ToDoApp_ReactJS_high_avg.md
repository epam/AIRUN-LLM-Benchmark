I have the following application code that needs to migrate:

<source_code>
<place_code_here repo="ToDoApp_ReactJS"/>
</source_code>

Please follow these steps:

1. Migrate the provided React TypeScript application to Angular 14.x:
   - Maintain all existing functionality and component relationships
   - Preserve the application's state management patterns
   - Ensure all component lifecycle methods are properly translated to Angular equivalents

2. Implement state management:
   - Use Angular services with RxJS for state management
   - Convert the observer pattern (subscribe/inform) to RxJS observables
   - Implement reactive state updates using BehaviorSubject/Subject

3. Apply Angular architecture best practices:
   - Split large components into smaller, focused components
   - Create appropriate services for data handling and business logic
   - Implement proper dependency injection patterns

4. Convert React component structure:
   - Transform JSX templates to Angular HTML templates
   - Replace React event handlers with Angular event bindings
   - Convert React refs (this.refs) to Angular @ViewChild decorators
   - Replace ReactDOM.findDOMNode() calls with Angular ViewChild queries
   - Transform React lifecycle methods to Angular equivalents

5. Implement proper typing:
   - Maintain TypeScript interfaces and types
   - Ensure strong typing throughout the application
   - Use appropriate Angular decorators (@Component, @Input, @Output, etc.)

6. Handle component communication:
   - Replace React props with Angular @Input() decorators
   - Convert callback props to Angular @Output() EventEmitter
   - Implement appropriate service-based communication where needed

7. Optimize the application:
   - Apply Angular change detection strategies where appropriate
   - Ensure efficient rendering patterns

8. Ensure proper routing:
   - Convert external Router library to Angular Router
   - Maintain the same URL structure and navigation patterns

9. Code quality requirements:
   - No TODOs in the final code
   - Follow Angular style guide conventions
   - Ensure code is clean, readable, and maintainable
