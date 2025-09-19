Your task is to create a real-time collaborative text editor on React 18.x with operational transforms, conflict resolution, and advanced editing features.

Please follow these instructions:

1. Technology Requirements:
   - Implement using React 18.x with TypeScript
   - Use Draft.js or Slate.js for rich text editing foundation
   - Implement WebSocket client for real-time collaboration
   - Use Operational Transform (OT) or Conflict-free Replicated Data Types (CRDT) for synchronization
   - Include Immutable.js for efficient state management

2. Core Editor Features:
   - Rich text editing with formatting (bold, italic, underline, strikethrough)
   - Block-level formatting (headers, lists, quotes, code blocks)
   - Inline elements (links, mentions, hashtags)
   - Real-time collaborative editing with multiple cursors
   - Undo/redo functionality that respects collaborative changes
   - Document versioning with branching and merging capabilities

3. Real-time Collaboration System:
   - WebSocket connection for real-time operation synchronization
   - Operational Transform implementation for conflict resolution
   - User presence awareness with cursor positions and selections
   - Real-time user avatars and activity indicators
   - Collaborative conflict resolution with automatic merging
   - Session management with user authentication integration

4. Advanced Editing Capabilities:
   - Inline comments with threading and resolution
   - Suggestion mode for tracked changes and reviews
   - Document outline/navigation with automatic heading detection
   - Find and replace functionality with regex support
   - Smart auto-complete for mentions and hashtags
   - Markdown shortcuts for rapid formatting

5. Document Management:
   - Auto-save with optimistic updates and conflict handling
   - Document locking mechanisms for exclusive editing sections
   - Export functionality (PDF, HTML, Markdown, Word)
   - Import from various formats with content preservation
   - Document sharing with permission levels (view, comment, edit)
   - Revision history with diff visualization

6. User Interface and Experience:
   - Floating toolbar that appears on text selection
   - Customizable editor themes and layout options
   - Responsive design for mobile and tablet devices
   - Keyboard shortcuts for all major operations
   - Accessibility support with screen reader compatibility
   - Split-screen mode for comparing document versions

7. Performance Optimization:
   - Efficient text rendering for large documents (>100KB)
   - Debounced operation transmission to reduce network traffic
   - Delta compression for operation serialization
   - Virtual scrolling for documents with thousands of lines
   - Incremental parsing and syntax highlighting
   - Memory-efficient history management with cleanup

8. Conflict Resolution and Data Consistency:
   - Implement operational transform algorithms (Jupiter or Wave)
   - Handle network partitions and reconnection scenarios
   - Resolve conflicting simultaneous edits gracefully
   - Maintain document integrity across all connected clients
   - Support for offline editing with sync on reconnection
   - Data validation and corruption recovery mechanisms

9. Advanced Collaboration Features:
   - Live cursor tracking with smooth position interpolation
   - User-specific color coding for changes and cursors
   - Collaborative selection sharing for group editing
   - Voice/video integration for real-time communication
   - Activity feed showing recent document changes
   - Permission-based editing with role management

10. Integration and Extensibility:
    - Plugin architecture for custom editor extensions
    - API integration for external content sources
    - Webhook support for document change notifications
    - Integration with version control systems (Git-like workflow)
    - Custom block types for specialized content (tables, charts, embeds)
    - Third-party service integration (Grammarly, spell-check)

11. Code Quality Standards:
    - Comprehensive TypeScript typing for all operations and states
    - Robust error handling with graceful degradation
    - Unit tests for operational transform algorithms
    - Integration tests for real-time collaboration scenarios
    - Performance testing for large documents and multiple users
    - Clean architecture with separation of editor, collaboration, and persistence layers
    - Extensive documentation for the operational transform implementation
    - No TODO comments or placeholder implementations in production code