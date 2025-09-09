Your task is to create a sophisticated drag-and-drop form builder component on React 18.x with dynamic validation and nested field support.

Please follow these instructions:

1. Technology Requirements:
   - Implement using React 18.x with TypeScript
   - Use React DnD or @dnd-kit for drag-and-drop functionality
   - Implement React Hook Form for form state management
   - Include Yup or Zod for schema validation
   - Use styled-components or CSS modules for styling

2. Form Builder Core Features:
   - Drag-and-drop interface for form field creation
   - Field palette with multiple input types (text, email, number, select, checkbox, radio, textarea, file upload)
   - Real-time form preview with live updates
   - Nested field groups and repeatable field arrays
   - Conditional field visibility based on other field values
   - Custom field properties panel for configuration

3. Advanced Field Types:
   - Dynamic select options with API integration
   - Multi-step form sections with progress indicator
   - Date/time pickers with timezone support
   - Rich text editor fields with formatting options
   - Signature capture fields for digital signatures
   - Address autocomplete with geocoding integration

4. Dynamic Validation System:
   - Real-time validation with custom error messages
   - Cross-field validation dependencies
   - Conditional validation rules based on field values
   - Custom validation functions with JavaScript support
   - Validation rule templates for common patterns
   - Async validation for unique field checking

5. Form State Management:
   - Auto-save draft functionality with localStorage
   - Undo/redo operations for form building actions
   - Form versioning with change history tracking
   - Import/export form configurations as JSON schema
   - Form templates library with pre-built forms
   - Collaborative editing with conflict resolution

6. User Experience Features:
   - Intuitive field property editor with live preview
   - Grid-based layout system with responsive breakpoints
   - Field duplication and bulk operations
   - Search and filter functionality in field palette
   - Keyboard shortcuts for common operations
   - Accessibility compliance with ARIA labels and screen reader support

7. Form Output and Integration:
   - Generate React component code from form configuration
   - Export form schema in JSON Schema format
   - Generate HTML form with embedded validation
   - REST API integration for form submission
   - Webhook configuration for form data processing
   - PDF generation from submitted form data

8. Performance Optimization:
   - Virtual scrolling for large forms with 100+ fields
   - Debounced auto-save to prevent excessive operations
   - Memoized form components to prevent unnecessary re-renders
   - Lazy loading of field type components
   - Efficient drag-and-drop with optimized re-ordering
   - Background processing for form validation and export

9. Advanced Configuration Options:
   - Custom CSS styling injection for form theming
   - Field layout options (inline, stacked, two-column)
   - Form submission handling with success/error states
   - Integration with external validation services
   - Custom field type plugin system
   - Form analytics and completion tracking

10. Code Quality Standards:
    - Comprehensive TypeScript interfaces for all form configurations
    - Robust error handling with user-friendly error messages
    - Unit tests for form validation logic and state management
    - Integration tests for drag-and-drop functionality
    - Clean, maintainable code without TODO comments
    - Proper separation of concerns with custom hooks
    - Documentation for extending the form builder with new field types