# TaskTracker Frontend

Modern Next.js frontend for the TaskTracker API built with shadcn/ui components.

## Features

- 🔐 User authentication (login/register)
- ✅ Task management (create, read, update, delete)
- 📊 Real-time statistics
- 🎨 Beautiful UI with shadcn/ui components
- 📱 Responsive design
- ⚡ Fast and modern Next.js 15

## Prerequisites

- Node.js 18+
- npm or yarn
- TaskTracker API running on http://localhost:8000

## Quick Start

### 1. Install Dependencies

```bash
cd tasktracker-frontend
npm install
```

### 2. Configure Environment

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Run Development Server

```bash
npm run dev
```

Visit http://localhost:3000

## Project Structure

```
tasktracker-frontend/
├── app/
│   ├── layout.tsx          # Root layout with AuthProvider
│   ├── page.tsx            # Main page (routing)
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── LoginPage.tsx       # Login/Register page
│   └── Dashboard.tsx       # Main dashboard
├── contexts/
│   └── AuthContext.tsx     # Authentication context
├── lib/
│   ├── api.ts             # API client
│   └── utils.ts           # Utilities
└── .env.local             # Environment variables
```

## Features

### Authentication
- Login with username and password
- Register new account
- Automatic token management
- Protected routes

### Task Management
- Create new tasks with title, description, and priority
- View all tasks with status indicators
- Mark tasks as completed
- Delete tasks
- Filter by status and priority

### Statistics
- Total tasks count
- Completed tasks count
- Completion percentage

## Development

```bash
# Development mode
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **State Management**: React Context API

## API Integration

The frontend connects to the TaskTracker API at `http://localhost:8000/api/v1`.

Make sure the backend is running before starting the frontend:

```bash
# In tasktracker-mono directory
docker compose up
```

## Building for Production

```bash
npm run build
npm start
```

The application will be available at http://localhost:3000

## License

Educational purposes
