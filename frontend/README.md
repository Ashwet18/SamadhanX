# SamadhanX Frontend

Next.js-based frontend application for the SamadhanX platform.

## Architecture

The frontend is built using Next.js 14 with the App Router, providing:

- **Server-Side Rendering (SSR)** for improved performance and SEO
- **Static Site Generation (SSG)** for static content
- **Client-Side Rendering (CSR)** for dynamic interactions
- **TypeScript** for type safety throughout the application
- **Tailwind CSS** for utility-first styling
- **Component-based architecture** with reusable UI components

## Project Structure

```
frontend/
├── app/                     # Next.js 14 App Router
│   ├── globals.css         # Global styles and Tailwind imports
│   ├── layout.tsx          # Root layout component
│   └── page.tsx            # Home page
├── components/             # Reusable UI components
│   ├── ui/                 # Base UI components (buttons, inputs, etc.)
│   ├── forms/              # Form-specific components
│   └── layout/             # Layout-specific components
├── lib/                    # Utility functions and configurations
│   ├── utils/              # General utility functions
│   └── api/                # API client configuration
├── types/                  # TypeScript type definitions
│   └── api/                # API-related types
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
├── tailwind.config.ts      # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
├── next.config.js         # Next.js configuration
└── README.md              # This file
```

## Key Features

### 1. **Responsive Design**
- Mobile-first approach using Tailwind CSS
- Adaptive layouts for different screen sizes
- Touch-friendly interface for mobile devices

### 2. **Type Safety**
- Full TypeScript integration
- Strict type checking enabled
- API response types for better developer experience

### 3. **Modern UI/UX**
- Clean, accessible design following modern web standards
- Consistent design system with reusable components
- Loading states, error handling, and user feedback

### 4. **Performance Optimization**
- Next.js automatic code splitting
- Image optimization with Next.js Image component
- Font optimization with Next.js Font module

### 5. **Development Experience**
- Hot reloading for fast development
- ESLint and Prettier for code quality
- TypeScript for better IDE support

## Getting Started

### Prerequisites
- Node.js 18+ and npm 9+
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
# Copy environment template
cp .env.example .env.local

# Edit environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SamadhanX
```

4. **Start development server:**
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### Development Scripts

```bash
# Development server with hot reloading
npm run dev

# Production build
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Code formatting
npm run format
npm run format:check

# Testing
npm test
npm run test:watch
npm run test:coverage

# Bundle analysis
npm run analyze
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS for styling with:

- **Custom color palette** aligned with SamadhanX branding
- **Custom components** for consistent UI patterns
- **Responsive utilities** for mobile-first design
- **Dark mode support** (configurable)

### Design System

Key design tokens:

```css
/* Primary Colors */
--primary-500: #3b82f6;
--primary-600: #2563eb;
--primary-700: #1d4ed8;

/* Success/Error/Warning */
--success: #10b981;
--warning: #f59e0b;
--error: #ef4444;

/* Typography */
--font-sans: 'Inter', system-ui, sans-serif;
```

### Component Classes

Predefined utility classes for common patterns:

```css
/* Form elements */
.form-input { @apply block w-full px-3 py-2 border rounded-md ... }
.form-label { @apply block text-sm font-medium ... }

/* Buttons */
.btn-primary { @apply bg-primary-600 text-white hover:bg-primary-700 ... }

/* Cards */
.card { @apply bg-white rounded-lg border shadow-sm ... }

/* Status badges */
.badge-success { @apply bg-green-100 text-green-800 ... }
```

## State Management

The application uses multiple approaches for state management:

### 1. **Local State (useState, useReducer)**
- Component-level state for UI interactions
- Form state management
- Toggle states, loading states

### 2. **React Query (TanStack Query)**
- Server state management
- API data caching and synchronization
- Background updates and optimistic updates

### 3. **Zustand (Planned)**
- Global client state management
- User authentication state
- Application preferences
- Notification state

## API Integration

### HTTP Client Configuration

```typescript
// lib/api/config.ts
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
}

// Endpoints are organized by domain
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    // ...
  },
  CHALLENGES: {
    BASE: '/challenges',
    CREATE: '/challenges',
    // ...
  }
}
```

### Type-Safe API Calls

```typescript
// Type definitions ensure API consistency
interface Challenge {
  id: UUID
  title: string
  status: ChallengeStatus
  // ...
}

// API responses are fully typed
const challenges: ApiResponse<Challenge[]> = await fetchChallenges()
```

## Routing

The application uses Next.js App Router with:

### File-based Routing
```
app/
├── page.tsx                    # / (home)
├── about/page.tsx             # /about
├── auth/
│   ├── login/page.tsx         # /auth/login
│   └── register/page.tsx      # /auth/register
├── dashboard/
│   ├── page.tsx               # /dashboard
│   └── challenges/
│       ├── page.tsx           # /dashboard/challenges
│       └── [id]/page.tsx      # /dashboard/challenges/[id]
└── api/                       # API routes (if needed)
```

### Route Protection
```typescript
// Authentication middleware for protected routes
export function middleware(request: NextRequest) {
  // Check authentication status
  // Redirect to login if not authenticated
}
```

## Components Architecture

### Base UI Components (`components/ui/`)
- **Button**: Variants for different actions and states
- **Input**: Form inputs with validation styling
- **Card**: Content containers with consistent styling
- **Modal**: Overlay components for dialogs
- **Loading**: Loading indicators and skeletons

### Form Components (`components/forms/`)
- **ChallengeForm**: Challenge submission form
- **LoginForm**: User authentication form
- **ProfileForm**: User profile management
- **SearchForm**: Search and filter interfaces

### Layout Components (`components/layout/`)
- **Header**: Navigation and user menu
- **Sidebar**: Dashboard navigation
- **Footer**: Site-wide footer content
- **Breadcrumbs**: Navigation context

## Performance Optimization

### Next.js Features
- **Automatic code splitting** reduces initial bundle size
- **Image optimization** with WebP/AVIF support
- **Font optimization** with preloading and display swap

### React Optimization
- **Lazy loading** for non-critical components
- **Memoization** for expensive computations
- **Virtual scrolling** for large lists (when implemented)

### Bundle Analysis
```bash
# Analyze bundle size
ANALYZE=true npm run build
```

## Accessibility

### WCAG 2.1 Compliance
- **Semantic HTML** structure throughout
- **ARIA labels** for interactive elements
- **Keyboard navigation** support
- **Focus management** for modals and forms
- **Color contrast** meeting AA standards

### Screen Reader Support
- **Alt text** for all images
- **Descriptive link text**
- **Form label associations**
- **Status announcements** for dynamic content

## Testing Strategy

### Unit Testing (Jest + Testing Library)
```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

### Component Testing
```typescript
// Example component test
import { render, screen } from '@testing-library/react'
import { Button } from '@/components/ui/button'

test('renders button with correct text', () => {
  render(<Button>Click me</Button>)
  expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
})
```

## Environment Configuration

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SamadhanX
NEXT_PUBLIC_MAPS_API_KEY=your_maps_key
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

### Build-time Configuration
- **next.config.js** for Next.js-specific settings
- **tailwind.config.ts** for styling configuration
- **tsconfig.json** for TypeScript settings

## Deployment

### Production Build
```bash
# Create optimized production build
npm run build

# Start production server
npm start
```

### Docker Support
```dockerfile
# Multi-stage build for optimized container
FROM node:18-alpine AS builder
# ... build steps

FROM node:18-alpine AS runner
# ... runtime configuration
```

### Vercel Deployment
```bash
# Deploy to Vercel (recommended)
npx vercel

# Or connect GitHub repository for automatic deployments
```

## Browser Support

### Minimum Requirements
- **Chrome**: 88+
- **Firefox**: 85+
- **Safari**: 14+
- **Edge**: 88+

### Progressive Enhancement
- **Core functionality** works without JavaScript
- **Enhanced experience** with JavaScript enabled
- **Fallbacks** for unsupported features

## Development Guidelines

### Code Style
- **ESLint**: Enforces consistent code style
- **Prettier**: Automatic code formatting
- **TypeScript strict mode**: Maximum type safety

### Commit Messages
```bash
# Follow conventional commits
git commit -m "feat(auth): add login form validation"
git commit -m "fix(ui): resolve button hover state issue"
git commit -m "docs(api): update endpoint documentation"
```

### Component Development
1. Start with TypeScript interfaces
2. Create base component with proper types
3. Add styling with Tailwind classes
4. Write unit tests
5. Update Storybook documentation (when added)

## Future Enhancements

### Short Term
- [ ] **Authentication system** integration
- [ ] **Challenge submission** forms
- [ ] **Dashboard** implementation
- [ ] **Real-time notifications**

### Medium Term
- [ ] **Progressive Web App** (PWA) features
- [ ] **Offline support** for core functionality
- [ ] **Advanced animations** with Framer Motion
- [ ] **Data visualization** with Chart.js

### Long Term
- [ ] **Mobile app** (React Native)
- [ ] **Desktop app** (Electron)
- [ ] **Micro-frontend** architecture
- [ ] **A/B testing** framework

## Contributing

### Getting Started
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit with conventional commit format
5. Submit pull request with detailed description

### Code Review Checklist
- [ ] TypeScript types are properly defined
- [ ] Components are accessible (WCAG compliant)
- [ ] Responsive design works on all breakpoints
- [ ] Tests are written and passing
- [ ] Documentation is updated

## Support

For development questions or issues:
- **GitHub Issues**: Technical problems and feature requests
- **Documentation**: Check docs/ directory for detailed guides
- **Team Chat**: Internal communication channels

---

Built with ❤️ using Next.js, TypeScript, and Tailwind CSS for SIH 2026.