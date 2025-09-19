Your task is to create a comprehensive full-stack enterprise application template with microservices architecture.

Please follow these requirements:

1. Frontend Application Setup:
   - Configure Next.js 14+ with App Router for the main frontend application
   - Implement TypeScript with strict configuration throughout
   - Set up TailwindCSS with custom design system configuration
   - Configure React Query for server state management
   - Integrate NextAuth.js for authentication with multiple providers
   - Set up Storybook for component documentation and testing

2. Backend Services Architecture:
   - Create API Gateway service using Express.js with TypeScript
   - Design User Management microservice with authentication endpoints
   - Implement Product/Content Management microservice
   - Set up Notification Service with email and push notification support
   - Configure Redis for caching and session management
   - Implement PostgreSQL database with Prisma ORM integration

3. Infrastructure and DevOps Configuration:
   - Docker Compose setup for local development environment
   - Kubernetes manifests for production deployment
   - GitHub Actions CI/CD pipeline configuration
   - Environment configuration management for development, staging, and production
   - Health check endpoints for all services
   - Logging configuration with structured logging format

4. Security and Monitoring:
   - JWT token management with refresh token rotation
   - Rate limiting configuration for API endpoints
   - CORS configuration with environment-specific origins
   - Helmet.js security headers configuration
   - Error tracking integration with Sentry
   - Performance monitoring with application metrics collection

5. Testing Infrastructure:
   - Jest configuration for unit testing across all services
   - Cypress setup for end-to-end testing
   - Supertest configuration for API integration testing
   - Test database setup with data seeding
   - Code coverage reporting configuration
   - Mock service setup for external API dependencies

6. Development Tools and Quality:
   - ESLint and Prettier configuration with custom rules
   - Husky pre-commit hooks for code quality enforcement
   - TypeScript path mapping for clean imports
   - API documentation generation with OpenAPI/Swagger
   - Database migration system with rollback capabilities
   - Development environment setup scripts and documentation

7. Package Management and Dependencies:
   - Comprehensive package.json files for each service
   - Dependency management with exact version pinning
   - Security vulnerability scanning configuration
   - Automated dependency updates with Renovate configuration
   - Bundle analysis and optimization settings
   - Node.js version management with .nvmrc files

8. Configuration Files and Documentation:
   - Environment variable templates for all services
   - Database schema documentation with ERD diagrams
   - API endpoint documentation with request/response examples
   - Deployment guide for different environments
   - Development setup instructions with troubleshooting guide
   - Architecture decision records (ADR) templates

9. Code Quality Standards:
   - Production-ready configuration without placeholder content
   - Consistent naming conventions across all services
   - Error handling patterns with proper HTTP status codes
   - Logging standards with correlation IDs for request tracing
   - Performance optimization settings for production deployment
   - Security best practices implementation throughout the stack

10. Deliverable Structure:
    - Complete project template with all configuration files
    - Ready-to-use Docker development environment
    - Automated setup scripts for quick project initialization
    - Comprehensive documentation for onboarding new developers
    - Production deployment checklist and monitoring setup
    - Scalable architecture supporting horizontal scaling requirements