I have the following application code that needs to document:

<source_code>
<place_code_here repo="ReactAlgorithmVisualizer"/>
</source_code>

Please follow these steps:

1. Create comprehensive technical documentation for the provided React algorithm visualization application:
   - Begin with a concise overview of the application's purpose and functionality
   - Document all key features and capabilities (editor, player controls, tracers/renderers, layouts, file system)
   - Maintain clear, professional technical language throughout

2. Document application architecture:
   - Explain the overall folder structure and modular organization (`components`, `core` with `tracers`/`renderers`/`layouts`, `reducers`, `files`, `apis`, `common`)
   - Detail the Redux state management implementation (reducers: `player`, `current`, `directory`, `env`, `toast`)
   - Describe component hierarchy and responsibilities (e.g., `App`, `Header`, `Navigator`, `CodeEditor`, `Player`, `VisualizationViewer`)
   - Outline how tracers and renderers interact and how layouts compose visualizations

3. Detail component specifications:
   - Document main containers and their responsibilities
   - List reusable UI components with their props and usage (`Button`, `ProgressBar`, `TabContainer`, `ToastContainer`, `ResizableContainer`, `ExpandableListItem`, `ListItem`, `Ellipsis`, `Divider`)
   - Explain state management and data flow for each major component
   - Describe accessibility considerations for interactive controls and visualization regions

4. Document Redux implementation:
   - List key actions/state for `player` (play/pause/step/speed, timeline), `current` (active file/visualization), `directory` (tree/files), `env` (language/runtime), `toast` (notifications)
   - Explain reducer logic, state shape, and how components subscribe/select state
   - Describe async handling patterns if present and integration points with `apis`

5. Provide API and file integration documentation:
   - Document file system abstraction in `files` (skeletons, loaders) and how code execution/visualization is wired
   - Explain editor integration (Ace) including controlled/uncontrolled value, debouncing, and resize behavior
   - Detail error handling and user feedback patterns (toasts)

6. Visualization and rendering layer:
   - Document tracer contracts (`Array1DTracer`, `Array2DTracer`, `GraphTracer`, `ChartTracer`, `ScatterTracer`, `LogTracer`, `MarkdownTracer`) and how they emit events/data
   - Explain renderer responsibilities and how they translate tracer events/data into DOM/Canvas/SVG output
   - Describe layout components (`HorizontalLayout`, `VerticalLayout`, `Layout`) and how multiple renderers are composed
   - Include performance considerations (batching, memoization, avoiding unnecessary re-renders)

7. Player and timeline mechanics:
   - Document player controls, playback loop, stepping, speed control, and synchronization with tracer events
   - Explain progress reporting (`ProgressBar`) and keyboard interaction if present

8. Provide usage documentation:
   - Include example code showing how to define a simple visualization using a tracer and renderer
   - Show how to load/edit code in the editor, run, and visualize
   - Document initialization requirements and configuration options (`common/config`)

9. Accessibility and performance considerations:
   - List ARIA roles/attributes for buttons, progress bar, and visualization regions
   - Explain keyboard navigation and focus management for player controls and editor
   - Document performance optimizations (memoization, virtualization, canvas batching) where applicable

10. Conclude with implementation summary:
   - Highlight key architectural decisions and separation of concerns
   - Emphasize scalability and extensibility (adding new tracers/renderers)
   - Note best practices and potential areas for future enhancement
