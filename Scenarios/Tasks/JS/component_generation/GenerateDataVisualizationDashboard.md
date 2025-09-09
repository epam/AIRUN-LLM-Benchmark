Your task is to create a comprehensive real-time data visualization dashboard on React 18.x with WebSocket integration and advanced chart capabilities.

Please follow these instructions:

1. Technology Requirements:
   - Implement using React 18.x with TypeScript
   - Use Chart.js or D3.js for data visualization
   - Implement WebSocket client for real-time data streaming
   - Include CSS-in-JS solution (styled-components or emotion)
   - Use React Context API for global state management

2. Core Dashboard Features:
   - Display multiple chart types: line charts, bar charts, pie charts, and heatmaps
   - Real-time data streaming via WebSocket connection (simulate with mock WebSocket server)
   - Interactive chart filtering and drill-down capabilities
   - Responsive grid layout with drag-and-drop chart repositioning
   - Data export functionality (CSV, JSON, PNG formats)

3. WebSocket Integration Requirements:
   - Establish WebSocket connection on component mount
   - Handle connection states (connecting, connected, disconnected, error)
   - Implement reconnection logic with exponential backoff
   - Process real-time data updates and update charts dynamically
   - Handle graceful disconnection on component unmount

4. Advanced Interaction Features:
   - Cross-chart filtering (selecting data in one chart filters others)
   - Time range selector for historical data analysis
   - Zoom and pan capabilities for line and bar charts
   - Tooltip with detailed information on hover
   - Chart type switching (convert between line/bar/area charts)

5. Performance Optimization Requirements:
   - Implement data virtualization for large datasets (>10,000 points)
   - Use React.memo and useMemo for expensive chart calculations
   - Implement chart data aggregation for different time intervals
   - Debounce user interactions to prevent excessive re-renders
   - Lazy load chart components to improve initial load time

6. Dashboard Layout and UX:
   - Responsive grid system that adapts to different screen sizes
   - Draggable chart panels with resize handles
   - Collapsible sidebar with chart configuration options
   - Dark/light theme toggle with persistent user preference
   - Loading states and error handling for all data operations

7. Data Management:
   - Support multiple data sources with different update frequencies
   - Implement data caching with TTL (time-to-live) mechanism
   - Handle data transformation and normalization
   - Provide data validation and error recovery
   - Support real-time alerts based on data thresholds

8. Code Quality Standards:
   - Production-ready code with comprehensive TypeScript typing
   - Implement proper error boundaries for chart components
   - Include unit tests for critical data processing functions
   - Follow React best practices with proper hook usage
   - Clean code without TODO comments or placeholder implementations
   - Implement proper accessibility (ARIA labels, keyboard navigation)

9. Technical Architecture:
   - Modular component structure with clear separation of concerns
   - Custom hooks for WebSocket management and data processing
   - Efficient state management avoiding unnecessary re-renders
   - Proper cleanup of WebSocket connections and event listeners
   - Scalable folder structure supporting future chart additions