I have the following application code that needs to migrate:

<source_code>
<place_code_here repo="ReactAlgorithmVisualizer"/>
</source_code>

Please follow these steps:

1. Migrate the provided React algorithm visualization application to Angular 19.x:
   - Assume all non-provided code has been migrated with the same contract
   - Implement equivalent functionality while following Angular best practices
   - Preserve editor, player controls, tracers/renderers, layouts, file system, and overall UX

2. Architecture requirements:
   - Use @ngrx/store and @ngrx/effects for state management instead of Redux
   - Convert Redux actions and reducers (player, current, directory, env, toast) to NgRx feature stores/selectors/effects
   - Organize code into feature areas: viewer, editor, player, files, core (tracers/renderers/layouts), shared/ui
   - Prefer standalone components; use feature-level routing modules where appropriate

3. Component migration:
   - Convert all React components to Angular components with OnPush change detection
   - Translate JSX to Angular templates with proper input/output bindings
   - Replace React Router with Angular Router; preserve current navigation and URL structure
   - Replace react-helmet with Angular Title/Meta services for document metadata
   - Replace react-toastify with an Angular toast/snackbar service/component

4. State management conversion:
   - Map Redux store slices to NgRx feature states with strongly typed models
   - Implement selectors for derived state: playback progress, active file/visualization, directory tree, environment, toasts
   - Convert thunk/promise flows to NgRx effects using Observables
   - Preserve action semantics for play/pause/step/speed and timeline synchronization

5. Services and APIs:
   - Create Angular services for file system, code execution/visualization orchestration, and player control
   - Use HttpClient for any remote API calls; convert promise logic to Observables
   - Centralize error handling and user notifications via services and effects

6. Routing and navigation:
   - Implement Angular Router configuration mirroring existing app routes
   - Support deep-linking to files/visualizations and restoration of state from URL/query params
   - Add route guards if necessary for invalid routes/state

7. Editor integration:
   - Integrate Ace editor via an Angular-compatible wrapper component
   - Maintain controlled value updates, debouncing, and resize behavior
   - Ensure accessibility and keyboard interactions remain functional

8. Visualization and rendering layer:
   - Port tracers (Array1D/Array2D/Graph/Chart/Scatter/Log/Markdown) to Angular-friendly services or classes
   - Implement renderers as Angular components/directives that consume tracer events/data (DOM/Canvas/SVG as applicable)
   - Implement layout components (HorizontalLayout, VerticalLayout, Layout) to compose multiple renderers
   - Optimize rendering with OnPush, trackBy, and batching as appropriate

9. UI and styling:
   - Preserve the current look and feel
   - Convert shared UI components (Button, ProgressBar, TabContainer, ToastContainer, ResizableContainer, ExpandableListItem, ListItem, Ellipsis, Divider) to Angular equivalents
   - Scope styles to components; retain responsiveness

10. Code quality and deliverables:
    - Follow Angular style guide, strict TypeScript types, and best practices
    - No TODOs in the final code
    - Return translated code as markdown code snippets
    - Provide complete implementation without additional explanations
