# Treasury Management System - Frontend

A modern Next.js frontend for the Treasury Management System.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Icons**: Lucide React

## Features

- 🎨 Modern UI with dark mode support
- 📊 Real-time dashboard with key metrics
- 💹 Bond trading interface
- 🏦 Interbank deal management
- 🔄 Repo/Reverse Repo with margin calls
- 💳 BAHTNET & TSD settlement tracking
- 📅 Thai business day calendar
- 👥 Role-based access control

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

### API Configuration

By default, the frontend proxies API requests to `http://localhost:8000`. 

To change this, set the environment variable:

```bash
NEXT_PUBLIC_API_URL=http://your-api-server:8000
```

Or create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
src/frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home/Dashboard
│   │   ├── globals.css         # Global styles
│   │   ├── bonds/              # Bond trading pages
│   │   ├── interbank/          # Interbank pages
│   │   ├── repo/               # Repo pages
│   │   ├── settlement/         # Settlement pages
│   │   └── ...
│   ├── components/
│   │   ├── layout/             # Layout components
│   │   │   └── MainLayout.tsx  # Sidebar layout
│   │   └── ui/                 # Reusable UI components
│   ├── lib/
│   │   └── api.ts              # API client
│   ├── hooks/                  # Custom React hooks
│   ├── store/                  # Zustand stores
│   └── types/
│       └── index.ts            # TypeScript types
├── public/                     # Static assets
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
└── package.json
```

## Available Scripts

```bash
# Development
npm run dev          # Start dev server

# Production
npm run build        # Build for production
npm run start        # Start production server

# Linting
npm run lint         # Run ESLint
```

## API Integration

The frontend communicates with the FastAPI backend through the API client (`src/lib/api.ts`).

### Authentication

```typescript
import { api } from '@/lib/api';

// Login
const token = await api.login({ username: 'admin', password: 'admin123' });

// Get current user
const user = await api.getCurrentUser();

// Logout
await api.logout();
```

### Example: Fetching Securities

```typescript
import { api } from '@/lib/api';

const securities = await api.getSecurities({
  security_type: 'GOVERNMENT_BOND',
  page: 1,
  size: 20,
});

console.log(securities.items);
```

## Styling

The project uses TailwindCSS with a custom configuration:

- **Primary color**: Sky blue (#0ea5e9)
- **Secondary (Treasury) color**: Green (#22c55e)
- **Custom components**: Card, Button, Badge, etc.

### Utility Classes

```css
/* Cards */
.card              /* Basic card */
.card-hover        /* Card with hover effect */

/* Buttons */
.btn-primary       /* Primary action */
.btn-secondary     /* Secondary action */
.btn-success       /* Success/approve */
.btn-danger        /* Danger/cancel */

/* Badges */
.badge-success     /* Green badge */
.badge-warning     /* Yellow badge */
.badge-danger      /* Red badge */
.badge-info        /* Blue badge */
```

## License

Internal use only - Virtual Bank Thailand
