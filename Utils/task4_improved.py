# Improved Todo List Component with Stricter Prompts - Based on Analysis
from Utils.llm.config import Model
from Utils.sdlc_experiment import main

INITIAL_TASK = """
Create a React component with configurable props and TypeScript support.

REQUIREMENTS:
1. ALWAYS use <form> element with onSubmit event for adding items
2. ALWAYS render item-list container (data-testid="todo-list"), even when empty
3. Use modern React hooks (useState) - NO class components
4. Component must be exported as default
5. Include comprehensive TypeScript types

VALIDATION:
- Show error message with role="alert" when validation fails
- Clear error when user starts typing valid input
- Display error with data-testid="validation-error"

REQUIRED data-testid attributes (EXACT names):
- Add item input: data-testid="todo-input"
- Add item button: data-testid="add-btn"  
- Item list container: data-testid="todo-list"
- Individual items: data-testid="todo-item-{id}"
- Error message: data-testid="validation-error"

Create a TypeScript React component with these EXACT interfaces:

```typescript
interface Item {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
}

interface ComponentProps {
  initialItems?: Item[];
  onItemAdd?: (item: Item) => void;
}
```

IMPLEMENTATION REQUIREMENTS:
1. FORM STRUCTURE: Use <form onSubmit={handleAddItem}>
2. INPUT VALIDATION: Show role="alert" error for empty items
3. ITEM DISPLAY: Simple text display only
4. ALWAYS RENDER: <ul data-testid="todo-list"> must always be in DOM, even when empty
5. ID GENERATION: Use any unique ID generation (Date.now(), uuid, etc.)
6. ERROR CLEARING: Clear error when user types in input

STRUCTURE EXAMPLE:
```jsx
<section>
  <form onSubmit={handleAddItem}>
    <input data-testid="todo-input" />
    <button data-testid="add-btn">Add</button>
    {error && <span role="alert" data-testid="validation-error">{error}</span>}
  </form>
  <ul data-testid="todo-list">
    {items.map(item => (
      <li data-testid={`todo-item-${item.id}`}>{item.text}</li>
    ))}
  </ul>
</section>
```

Create the implementation and submit it using submit_solution tool.
"""

ENHANCED_TODO_STEPS = [
    """Add delete functionality and validation:

REQUIRED ADDITIONS:
- Add delete buttons: data-testid="todo-delete-{id}" for each todo
- Add confirmDelete prop (boolean, default: true) for window.confirm dialog
- Add onError callback: (error: string) => void for validation errors
- Add maxLength prop (number, default: 100) for text length validation
- Show validation errors with data-testid="validation-error" and role="alert"

IMPLEMENTATION REQUIREMENTS:
- Use window.confirm() when confirmDelete=true
- Validate text length: min 1, max {maxLength} characters
- Call onError callback when validation fails
- Set maxLength attribute on input element
- MAINTAIN all existing functionality and props

EXACT new data-testids required:
- data-testid="todo-delete-{id}" for delete buttons
- data-testid="validation-error" for validation messages""",
    """Add completion toggle, filtering and search:

REQUIRED ADDITIONS:
- Add completion toggle: checkbox for each todo to mark complete/incomplete
- Add filter prop: "all" | "active" | "completed" (default: "all")
- Add searchTerm prop (string) for filtering by text
- Add onFilterChange callback: (filter: string, searchTerm: string) => void
- Filter buttons: data-testid="filter-all", "filter-active", "filter-completed"
- Search input: data-testid="search-input"
- Filtered count display: data-testid="filtered-count"

IMPLEMENTATION REQUIREMENTS:
- Add checkbox input in each todo item for completion toggle
- Apply completed styling (text-decoration: line-through) for completed todos
- Filter todos based on completion status and search term (case-insensitive)
- Show count of filtered results: "X shown" format
- Call onFilterChange when filter or search changes
- Update todo.completed when checkbox is toggled
- MAINTAIN all existing functionality and props

EXACT new data-testids required:
- data-testid="filter-all", "filter-active", "filter-completed"
- data-testid="search-input"
- data-testid="filtered-count" """,
    """Add persistence and bulk operations:

REQUIRED ADDITIONS:
- Add persistKey prop (string) for localStorage persistence
- Add showBulkActions prop (boolean, default: false)
- Add "Select All" checkbox: data-testid="select-all-checkbox"
- Add "Clear Completed" button: data-testid="clear-completed-btn" 
- Add "Delete Selected" button: data-testid="delete-selected-btn"
- Add onBulkAction callback: (action: string, todoIds: string[]) => void

IMPLEMENTATION REQUIREMENTS:
- Auto-save to localStorage when persistKey provided (JSON serialization with Date handling)
- Load from localStorage on component mount
- Select all checkbox selects only filtered todos
- Clear completed removes all completed todos
- Delete selected removes all selected todos
- Add individual selection checkboxes when showBulkActions=true
- Disable buttons when no items to act on
- Call onBulkAction with action name and affected todo IDs
- MAINTAIN all existing functionality and props

EXACT new data-testids required:
- data-testid="select-all-checkbox"
- data-testid="clear-completed-btn"
- data-testid="delete-selected-btn" """,
]

# Run the improved todo test
main(
    model=Model.Sonnet_4,  # Change this to your preferred model
    initial_task=INITIAL_TASK,
    experiment_name="enhanced_todo_component_v2",
    steps=ENHANCED_TODO_STEPS,
    max_steps=4,
)
