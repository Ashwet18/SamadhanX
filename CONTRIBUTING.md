# Contributing to SamadhanX

Thank you for your interest in contributing to SamadhanX! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. By participating, you agree to uphold this code.

### Our Standards

- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other contributors

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and pip
- Docker and Docker Compose
- Git
- PostgreSQL 14+ (for local development)
- Redis (for caching and background jobs)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/samadhanx.git
   cd samadhanx
   ```

2. **Set Up Environment**
   ```bash
   make setup
   # Edit .env with your configuration
   ```

3. **Start Development Environment**
   ```bash
   make dev
   ```

4. **Verify Setup**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports**: Help us identify and fix issues
2. **Feature Requests**: Suggest new functionality
3. **Code Contributions**: Bug fixes, new features, improvements
4. **Documentation**: Improve or add documentation
5. **Testing**: Add or improve test coverage
6. **Performance**: Optimize existing code
7. **Security**: Identify and fix security issues

### Before Contributing

1. **Check Existing Issues**: Look for existing issues or discussions
2. **Discuss Major Changes**: Open an issue for significant changes
3. **Follow Guidelines**: Ensure your contribution follows our guidelines
4. **Test Locally**: Test your changes thoroughly

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Follow coding standards
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Your Changes

```bash
git add .
git commit -m "type(scope): description"
```

**Commit Message Format:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(auth): add JWT token refresh mechanism"
git commit -m "fix(challenge): resolve duplicate detection issue"
git commit -m "docs(api): update authentication endpoints"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots for UI changes
- Testing instructions

### 5. Address Review Feedback

- Respond to reviewer comments
- Make necessary changes
- Push updates to the same branch
- Request re-review when ready

## Coding Standards

### Backend (Python/FastAPI)

#### Code Style
- **Formatting**: Black (88 characters)
- **Import Sorting**: isort
- **Linting**: flake8
- **Type Checking**: mypy
- **Security**: bandit

#### Standards
```python
# Use type hints everywhere
def create_user(user_data: UserCreate) -> User:
    pass

# Use Pydantic for validation
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

# Use dependency injection
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    pass

# Handle errors properly
try:
    user = await create_user(user_data)
except IntegrityError:
    raise HTTPException(
        status_code=400,
        detail="User with this email already exists"
    )
```

#### Database Guidelines
- Use Alembic for migrations
- Add proper indexes for performance
- Use foreign key constraints
- Implement soft deletes where appropriate
- Add audit trails for sensitive data

### Frontend (TypeScript/React/Next.js)

#### Code Style
- **Formatting**: Prettier
- **Linting**: ESLint with TypeScript rules
- **Type Checking**: TypeScript strict mode

#### Standards
```typescript
// Use proper TypeScript types
interface User {
  id: string
  email: string
  firstName: string
  lastName: string
}

// Use React hooks properly
const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  
  useEffect(() => {
    // Effect logic
  }, [])
  
  return { user, setUser }
}

// Use proper error boundaries
const ErrorFallback = ({ error }: { error: Error }) => (
  <div role="alert">
    <h2>Something went wrong:</h2>
    <pre>{error.message}</pre>
  </div>
)
```

#### Component Guidelines
- Use functional components with hooks
- Implement proper error boundaries
- Add loading and error states
- Use semantic HTML
- Ensure accessibility (WCAG 2.1 AA)
- Implement responsive design

## Testing Requirements

### Backend Testing

#### Test Structure
```python
# test_user_service.py
import pytest
from unittest.mock import Mock
from app.services.user_service import UserService

class TestUserService:
    def test_create_user_success(self, db_session):
        # Test implementation
        pass
    
    def test_create_user_duplicate_email(self, db_session):
        # Test implementation
        pass
```

#### Coverage Requirements
- Minimum 80% code coverage
- Test all public methods
- Test error conditions
- Use pytest fixtures for setup
- Mock external dependencies

### Frontend Testing

#### Test Structure
```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })
  
  it('calls onClick when clicked', () => {
    const onClick = jest.fn()
    render(<Button onClick={onClick}>Click me</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalled()
  })
})
```

#### Testing Guidelines
- Use React Testing Library
- Test user interactions
- Test accessibility
- Mock API calls
- Test error states

### Running Tests

```bash
# Backend tests
make test-backend

# Frontend tests  
make test-frontend

# All tests
make test

# With coverage
make test-coverage
```

## Documentation

### Code Documentation

#### Python Docstrings
```python
def create_challenge(
    challenge_data: ChallengeCreate,
    user: User,
    db: Session
) -> Challenge:
    """
    Create a new challenge submission.
    
    Args:
        challenge_data: Challenge creation data
        user: User creating the challenge
        db: Database session
        
    Returns:
        Created challenge instance
        
    Raises:
        ValidationError: If challenge data is invalid
        PermissionError: If user cannot create challenges
    """
```

#### TypeScript JSDoc
```typescript
/**
 * Fetches user profile from the API
 * @param userId - The ID of the user to fetch
 * @returns Promise resolving to user data
 * @throws {ApiError} When the request fails
 */
async function fetchUser(userId: string): Promise<User> {
  // Implementation
}
```

### API Documentation

- Use OpenAPI/Swagger annotations
- Document all endpoints
- Include request/response examples
- Document error responses
- Add authentication requirements

### README Updates

When adding new features:
- Update feature list
- Add configuration options
- Include usage examples
- Update installation instructions

## Development Workflow

### Daily Workflow

1. **Pull Latest Changes**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

3. **Develop and Test**
   ```bash
   make dev
   # Make changes
   make test
   make lint
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

5. **Create Pull Request**

### Code Review Process

#### As an Author
- Ensure CI passes
- Provide clear description
- Respond to feedback promptly
- Keep changes focused

#### As a Reviewer
- Review logic and architecture
- Check for security issues
- Verify test coverage
- Ensure documentation is updated
- Test the changes locally

## Release Process

### Version Management
- Follow Semantic Versioning (SemVer)
- Update CHANGELOG.md
- Tag releases appropriately
- Update version in package files

### Deployment
- Test in staging environment
- Review security implications
- Update production documentation
- Monitor deployment metrics

## Getting Help

### Resources
- **Documentation**: Check the `docs/` directory
- **API Reference**: http://localhost:8000/docs
- **Architecture**: See `docs/architecture.md`
- **Database**: See `docs/database.md`

### Communication
- **Issues**: GitHub Issues for bugs and features
- **Discussions**: GitHub Discussions for questions
- **Security**: Email security@samadhanx.gov.in for security issues

### Development Commands

```bash
# Quick reference
make help                # Show all available commands
make dev                 # Start development environment
make test               # Run all tests
make lint               # Run code linting
make format             # Format code
make clean              # Clean up Docker resources
```

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation for major features

Thank you for contributing to SamadhanX and helping solve societal challenges through innovation!