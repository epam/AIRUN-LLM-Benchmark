Your task is to create a sophisticated multi-package monorepo template with advanced tooling and package management.

Please follow these requirements:

1. Monorepo Structure and Tooling:
   - Configure Nx workspace with advanced caching and task orchestration
   - Set up Lerna for package versioning and publishing workflows
   - Implement Yarn workspaces with proper dependency hoisting
   - Create shared TypeScript configuration with project references
   - Configure Turborepo for build system optimization
   - Set up Rush.js alternative configuration for enterprise scenarios

2. Package Architecture:
   - Design shared UI component library with React and Storybook
   - Create utilities package with common functions and types
   - Implement shared ESLint and TypeScript configuration packages
   - Set up shared testing utilities and mocks package
   - Create design tokens package with theme configuration
   - Develop API client library with OpenAPI code generation

3. Application Packages:
   - Configure main web application using Next.js with shared components
   - Set up admin dashboard application with role-based access
   - Create mobile application using React Native with shared business logic
   - Implement CLI tools package for development and deployment tasks
   - Set up documentation site with Docusaurus integration
   - Create demo/playground application for component testing

4. Build and Development Tooling:
   - Webpack configuration with module federation for micro-frontends
   - Vite configuration for fast development builds
   - Rollup setup for library packaging and distribution
   - SWC integration for faster TypeScript compilation
   - esbuild configuration for development server optimization
   - Custom build scripts with parallel execution and caching

5. Quality Assurance and Testing:
   - Comprehensive Jest configuration with coverage reporting across packages
   - Playwright setup for cross-browser end-to-end testing
   - Visual regression testing with Chromatic integration
   - Performance testing configuration with Lighthouse CI
   - Security scanning with npm audit and Snyk integration
   - Dependency graph analysis and circular dependency detection

6. CI/CD and Automation:
   - GitHub Actions workflow with matrix builds for all packages
   - Automated semantic versioning with conventional commits
   - Package publishing pipeline with registry configuration
   - Automated dependency updates with conflict resolution
   - Branch protection rules with required status checks
   - Deployment automation for multiple environments

7. Development Experience:
   - VSCode workspace configuration with recommended extensions
   - Development containers setup for consistent environments
   - Hot module replacement configuration across all applications
   - TypeScript project references for fast incremental builds
   - Custom CLI commands for common development tasks
   - Debugging configuration for all package types

8. Package Management and Versioning:
   - Semantic release configuration with automated changelog generation
   - Package dependency management with version constraints
   - Peer dependency handling and resolution strategies
   - Bundle size monitoring and optimization alerts
   - License compatibility checking and management
   - Security vulnerability scanning and automated patching

9. Documentation and Tooling:
   - API documentation generation from TypeScript interfaces
   - Architectural decision records with template and guidelines
   - Component documentation with interactive examples
   - Development workflow documentation with best practices
   - Troubleshooting guides for common issues
   - Onboarding documentation for new team members

10. Advanced Configuration:
    - Custom Nx plugins for specialized build tasks
    - Micro-frontend orchestration with single-spa integration
    - Advanced caching strategies with remote cache configuration
    - Package import/export optimization with tree-shaking
    - Development server federation for local cross-package development
    - Performance monitoring integration across all packages

11. Code Quality Standards:
    - Unified code formatting with Prettier across all packages
    - Consistent TypeScript configuration with strict mode enabled
    - Advanced ESLint rules with custom plugin configurations
    - Pre-commit hooks with lint-staged for selective checking
    - Commit message validation with conventional commit standards
    - Code review automation with pull request templates

12. Deliverable Requirements:
    - Complete monorepo structure with all packages configured
    - Working development environment with hot reload across packages
    - Automated build and test pipeline ready for production use
    - Comprehensive documentation covering all aspects of the monorepo
    - Package publishing configuration ready for npm registry
    - Production-ready configuration without placeholder content or TODOs