Your task is to create an application on React 18.x that can utilize the SWAPI open API to fetch characters and display them in a list.

Please follow these instructions:

1. Technology Stack:
   - React 18.x or newer
   - TypeScript
   - Create React App for project bootstrapping
   - Axios for API requests
   - Include package.json file for dependencies and versioning

2. Data Source Integration:
   - Endpoint: https://swapi.dev/api/people
   - Response structure: { results: Array<{ name: string, url: string }> }
   - Fetch character data on initial component mount
   - No search functionality required

3. UI Requirements:
   - Display character list showing all fetched entries
   - Implement loading state with visual indicator during API calls
   - No user input fields required

4. Code Quality Standards:
   - Optimize component rendering
   - Implement proper TypeScript typing
   - Handle potential API errors gracefully
   - No TODO comments in final code
   - Clean codebase with minimal comments

5. Performance Requirements:
   - Implement efficient data fetching
   - Use appropriate React patterns for optimal rendering
   - Handle loading and error states efficiently