I have the following application code that needs to provide the business requirements:

<source_code>
<place_code_here repo="ReactAlgorithmVisualizer"/>
</source_code>

Please follow these steps:

1. Analyze the provided React algorithm visualization platform code:
   - Identify the main functionality and features of the visualization workspace
   - Examine the component architecture (Editor, Player, Viewer, Navigator, Header)
   - Review Redux-based state management (current, player, env, directory)
   - Document API usage for algorithms, visualizations, tracers, and GitHub gists

2. Document the user interaction patterns:
   - Describe the code editing experience and file management workflow
   - Outline how users build, run, and step through visualizations using the Player
   - Identify how users select categories/algorithms or open scratch papers (gists)
   - Document keyboard/mouse interactions, progress control, and speed adjustment

3. Extract the business requirements and objectives:
   - Determine the core business functionality: authoring and playing algorithm visualizations
   - Identify key entities (algorithms, visualizations, tracers, files, gists, users)
   - Document business rules for build, play/pause, step, cursor handling, and line indicators
   - Analyze goals around learning, sharing, and reusability of visualization content

4. Identify technical constraints and assumptions:
   - Note React + Redux architecture and 3rd-party dependencies (Ace, FontAwesome, InputRange)
   - Document assumptions about supported languages (md, json, js, cpp, java)
   - Identify worker/HTTP tracer execution paths and cancellation behavior
   - Describe authentication via GitHub token cookies and gist rate limits

5. Evaluate performance considerations:
   - Analyze build pipeline (TracerApi for md/json/js/cpp/java) and worker usage for JS
   - Review chunking of tracer commands, cursor navigation, and timer-driven playback
   - Identify potential bottlenecks in rendering tracers and large command streams
   - Document loading states, error handling, and responsiveness in the workspace

6. Document the data management approach:
   - Describe how files are created, modified, deleted, and selected as editing targets
   - Identify how algorithms and visualizations are fetched and set in state
   - Analyze GitHub gist CRUD flows (auth, list, get, create, edit, delete, fork)
   - Document persistence assumptions (unsaved state warning, URL-driven loading)

7. Analyze tracer and renderer functionality:
   - Document available tracer types (Markdown, Log, Array1D/2D, Chart, Graph, Scatter)
   - Describe how commands are grouped into chunks with optional line numbers
   - Explain how renderers visualize tracer state and synchronize with the Player
   - Identify visualization layout options (Horizontal/Vertical) and viewer composition

8. Summarize the user experience design:
   - Document the three-pane workspace layout and resizable weights/visibility
   - Identify accessibility and usability aspects (line highlighting, progress bar)
   - Describe visual hierarchy (Header, Navigator, Viewer, Editor, Toasts)
   - Analyze the workflow from selecting/opening content to building and playing


