# LCIF - Last Conversation Information File

## Project Overview
This is an AIRUN-LLM-Benchmark project focused on testing LLM capabilities in iterative React component development using SDLC (Software Development Life Cycle) experiments.

## Current Task Status
We are working on **Task 4** - developing and improving an SDLC benchmark for todo list components to test model consistency and prompt interpretation.

## Key Problem Identified
Different LLM models produce incompatible React components when given the same prompts, making it impossible to test them with shared test suites. This indicates the benchmark is measuring prompt interpretation differences rather than actual coding ability.

## What We've Done

### 1. Analysis Phase
- Analyzed task4 results from two models (model1 and model2)
- Model1 produced test-compatible code (proper form structure, error handling)
- Model2 produced incompatible code (missing form structure, added unauthorized features like completion toggles)

### 2. Solution: Stricter Prompts
Created `Utils/task4_improved.py` with much more prescriptive prompts:
- Removed iteration hints and application type hints
- Changed from "Todo/TodoListProps" to neutral "Item/ComponentProps" 
- Added exact structural requirements with code examples
- Made data-testid requirements explicit
- Specified forbidden features

### 3. API Simplification
Modified `Utils/sdlc_experiment.py`:
- Simplified `main()` function from multiple string parameters to single `initial_task`
- Removed complex prompt construction

## Current Files Structure

### Core Files
- `Utils/task4.py` - Original task with problematic prompts
- `Utils/task4_improved.py` - Improved version with stricter, neutral prompts
- `Utils/sdlc_experiment.py` - Main SDLC experiment runner
- `Utils/sdlc_test/src/todo_component/` - Test suites for all 4 iterations

### Test Results Analysis
- `Utils/task4/model1/` - Model1 results (4 steps, test-compatible)
- `Utils/task4/model2/` - Model2 results (4 steps, test-incompatible)

## Key Technical Details

### Prompt Improvements Made
1. **Neutrality**: Removed "todo list" references, use generic "component"
2. **Structure**: Exact form structure requirements with `<form onSubmit={handleAddItem}>`
3. **Validation**: Specific error handling with `role="alert"`
4. **Data-testids**: Exact attribute names required
5. **Examples**: Provided exact JSX structure template

### Test Strategy
- Props-based testing for maximum flexibility
- 4 iterations: basic → delete/validation → filters/search → persistence/bulk
- Backward compatibility testing across iterations

## Next Steps
1. Test `task4_improved.py` with both models to verify reduced variability
2. Compare results with original task4 to measure improvement
3. Apply improved prompt patterns to other benchmark tasks

## How to Run
```bash
# Run improved task
python -m Utils.task4_improved

# Run tests
cd Utils/sdlc_test
npm test
```

## File Paths Reference
- Project root: `/Users/ilia_korol/genai/AIRUN-LLM-Benchmark/`
- Utils: `Utils/`
- Tests: `Utils/sdlc_test/src/todo_component/`
- Results: Check for directories matching experiment names in output path

## Key Interfaces (Current)
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
  // ... additional props per iteration
}
```

This project demonstrates LLM benchmark design challenges and solutions for consistent code generation testing.