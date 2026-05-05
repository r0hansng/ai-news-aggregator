# Frontend Architecture

## Overview

The AI News Aggregator frontend is a modern Next.js 14 application built with TypeScript, React 18, and a comprehensive state management strategy. It provides a responsive, accessible interface for users to manage news subscriptions and consume curated digests.

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Framework** | Next.js | 14+ | Server-side rendering and API routes |
| **Runtime** | React | 18+ | Component library and UI rendering |
| **Language** | TypeScript | 5.4+ | Type safety and developer experience |
| **Styling** | Tailwind CSS | Latest | Utility-first CSS framework |
| **Server State** | React Query | 4+ | Data fetching and caching |
| **Client State** | Zustand | Latest | Lightweight global state |
| **HTTP Client** | Axios | Latest | Request management with interceptors |
| **Animation** | Framer Motion | Latest | Smooth transitions and interactions |
| **Forms** | react-hook-form | Latest | Form state and validation |

## Project Structure

```
frontend/src/
├── app/                          # Next.js app router
│   ├── layout.tsx               # Root layout with providers
│   ├── page.tsx                 # Home/onboarding page
│   ├── feed/
│   │   └── page.tsx             # Feed page (protected)
│   └── globals.css              # Global styles
│
├── core/                        # Infrastructure layer
│   ├── api/
│   │   └── client.ts            # Axios instance with interceptors
│   ├── providers/
│   │   └── QueryProvider.tsx    # React Query setup
│   └── store/
│       └── use-global-store.ts  # Zustand global state
│
├── features/                    # Feature modules
│   ├── auth/
│   │   ├── api.ts               # Login/onboarding endpoints
│   │   ├── hooks/
│   │   │   └── use-auth.ts      # Identity and session orchestrator
│   │   └── components/          # Auth-related components
│   │
│   ├── feed/
│   │   ├── api.ts               # Signal digestion endpoints
│   │   ├── hooks/
│   │   │   └── use-feed.ts      # Feed data orchestration
│   │   └── components/
│   │       ├── DigestCard.tsx   # Signal rendering with animations
│   │       ├── EmailToggle.tsx  # Email subscription toggle
│   │       └── EmptyState.tsx   # Empty state UI
│   │
│   ├── signals/
│   │   ├── api.ts               # YouTube resolution endpoints
│   │   ├── hooks/
│   │   │   └── use-signals.ts   # Channel discovery orchestrator
│   │   └── components/          # Signal components
│   │
│   ├── onboarding/
│   │   ├── hooks/
│   │   │   └── use-onboarding-form.ts  # Multi-step form orchestrator
│   │   └── components/
│   │       ├── OnboardingForm.tsx      # Main form container
│   │       ├── AuthToggle.tsx          # Login/register toggle
│   │       ├── Navigation.tsx          # Step navigation
│   │       ├── LoginForm.tsx           # Login form
│   │       └── steps/                  # Individual step components
│   │
│   └── settings/
│       └── components/
│           └── SettingsDrawer.tsx  # User preferences
│
└── shared/                      # Shared utilities and components
    ├── components/
    │   ├── layout/
    │   │   └── Navbar.tsx        # Global navigation
    │   └── ui/
    │       ├── Button.tsx        # Reusable button
    │       ├── Input.tsx         # Accessible form input
    │       ├── Select.tsx        # Dropdown component
    │       ├── Textarea.tsx      # Text area component
    │       └── Loader.tsx        # Loading spinner
    ├── hooks/                   # Custom React hooks
    └── utils/
        └── utils.ts             # Helper functions (cn, etc)
```

## State Management Architecture

### Layered State Pattern

```
┌─────────────────────────────────────────────┐
│          User Interface (Components)        │
├─────────────────────────────────────────────┤
│  Zustand (Client State)  │  React Query      │
│  • UI toggles            │  • Server data    │
│  • Session metadata      │  • Caching       │
│  • Cross-feature state   │  • Background jobs│
├─────────────────────────────────────────────┤
│  Cookies (Persistent Session)               │
│  • Auth tokens                              │
└─────────────────────────────────────────────┘
```

### State Mapping

| State Type | Storage | Purpose | Scope |
|-----------|---------|---------|-------|
| **Server Data** | React Query | Signals, users, digests | Global |
| **UI Toggles** | Zustand | Drawer open/close, modals | Global |
| **Session** | Cookies | Auth tokens, user ID | Persistent |
| **Form State** | react-hook-form | Input values, errors | Local |

## Key Patterns

### 1. Server-to-Client Sync

**Problem**: Navbar needs instant access to user name without waiting for React Query.

**Solution**: useEffect bridge in useAuth hook:

```typescript
useEffect(() => {
  if (user) {
    setSession({
      id: user.id,
      name: user.name,
      email: user.email
    });
  }
}, [user]);
```

**Result**: Navbar renders with user name immediately after login.

### 2. Pub/Sub Token Refresh

**Problem**: Multiple requests fail on 401 simultaneously, causing thundering herd.

**Solution**: Axios response interceptor with Pub/Sub pattern:

```typescript
// First 401 triggers token refresh
// Subsequent requests queue and wait
// All resume when token arrives
```

**Performance**: O(n) for n queued requests (linear complexity).

### 3. Optimistic Updates

**Problem**: Feedback submission shows loading spinner (slow UX).

**Solution**: Update local state before API call:

```typescript
const feedbackMutation = useMutation({
  mutationFn: submitFeedback,
  onMutate: (newFeedback) => {
    // Immediately update UI
    setLocalFeedback(newFeedback);
  },
  onError: (err, newFeedback, context) => {
    // Rollback on failure
    setLocalFeedback(context.previousFeedback);
  }
});
```

**Result**: 0ms perceived latency with automatic rollback.

### 4. Staggered Entry Animations

**Problem**: All digest cards animate simultaneously (jarring).

**Solution**: Framer Motion with index-based delays:

```typescript
<motion.div
  delay={index * 0.05}  // Stagger by 50ms
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
/>
```

**Result**: Smooth, professional entrance effect.

## HTTP Transport

### Axios Configuration

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Base URL** | `/api` | Proxy to backend in dev |
| **Timeout** | 30s | Prevent hanging requests |
| **withCredentials** | true | Include cookies in CORS |
| **Retry Logic** | 1 attempt | Exponential backoff on 5xx |

### Request/Response Interceptors

```typescript
// Request: Inject bearer token from cookie
// Response: Handle 401 with token refresh
// Error: Log and propagate
```

## Accessibility (WCAG AA)

### Input Component

```typescript
interface InputProps {
  label: string;           // Required label
  error?: string;          // Error message
  ...HTMLAttributes;       // Standard HTML attrs
}
```

**Features**:
- Label association for screen readers
- Error state with color contrast (4.5:1)
- Focus states for keyboard navigation
- Semantic HTML structure

### Navbar Component

- ARIA landmarks (navigation)
- Button with aria-label for mobile menu
- Focus management on dropdown

## Form Management

### react-hook-form Integration

| Feature | Implementation | Benefit |
|---------|-----------------|---------|
| **Validation** | Built-in rules | Zero dependencies |
| **Error States** | Object mapping | Type-safe errors |
| **Submission** | handleSubmit wrapper | Prevents invalid sends |
| **Dynamic Fields** | useFieldArray | Extensible forms |

### Multi-Step Onboarding

**4 Steps**:
1. **Identity**: Email, password (quick validation)
2. **Profile**: Title, background (context setting)
3. **Interests**: Topics, YouTube (source discovery)
4. **Preferences**: Frequency, format (fine-tuning)

**Pattern**: Sequential validation with back navigation.

## Performance Metrics

| Metric | Target | Method |
|--------|--------|--------|
| **FCP** (First Contentful Paint) | <1.5s | Next.js Image optimization |
| **LCP** (Largest Contentful Paint) | <2.5s | Lazy loading + code splitting |
| **CLS** (Cumulative Layout Shift) | <0.1 | Fixed dimensions, animations |
| **TTI** (Time to Interactive) | <3.5s | Tree shaking, minification |

### Optimizations Applied

- Code splitting by route
- Image optimization with Next.js Image
- CSS class merging (cn utility)
- Memoization for expensive renders

## Styling Strategy

### Tailwind CSS

**Approach**: Utility-first with glass-morphism design

```css
/* Example classes */
bg-white/3          /* 3% opacity for subtle depth */
border-white/5      /* Border with opacity */
backdrop-blur-xl    /* Frosted glass effect */
rounded-xl          /* Modern rounded corners */
```

### Color System

| Token | Value | Usage |
|-------|-------|-------|
| **Background** | #000000 | Dark theme foundation |
| **Surface** | #1a1a1a | Cards and containers |
| **Primary** | #ffffff | Text and accents |
| **Muted** | #666666 | Secondary text |

## Development Workflow

### Running Locally

```bash
cd frontend
npm install
npm run dev          # Development server on :3000
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint check
npm run type-check   # TypeScript check
```

### Environment Variables

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Best Practices

1. **Component Composition**: Keep components small and focused
2. **Hook Dependencies**: Always specify dependencies arrays
3. **Error Boundaries**: Wrap feature sections in boundaries
4. **Accessibility**: Run WAVE extension regularly
5. **Performance**: Use React DevTools Profiler
6. **Types**: Avoid `any` type, use `unknown` with type guards

## Common Patterns

### Data Fetching Hook

```typescript
export function useFeed(limit: number = 10) {
  return useQuery({
    queryKey: ['feed', limit],
    queryFn: () => feedApi.getLatest(limit),
    staleTime: 30_000,        // 30s before stale
    refetchInterval: 60_000,  // Poll every 60s
  });
}
```

### Mutation with Optimistic Update

```typescript
useMutation({
  mutationFn: (data) => api.update(data),
  onMutate: (newData) => {
    // Update cache immediately
    queryClient.setQueryData(['key'], newData);
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(['key'], context.previousData);
  },
});
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Hydration Mismatch** | SSR/CSR data diff | Add suppressHydrationWarning |
| **401 Loop** | Token refresh fails | Check refresh endpoint |
| **Stale Cache** | Query not invalidated | Call invalidateQueries |
| **Memory Leak** | Missing cleanup | Return cleanup from useEffect |

## Contributing

1. Follow TypeScript strict mode
2. Add JSDoc comments to functions
3. Test accessibility with keyboard navigation
4. Keep components under 300 lines
5. Use feature-based file organization

---

**For API integration details, see [Backend Architecture](BACKEND.md)**
