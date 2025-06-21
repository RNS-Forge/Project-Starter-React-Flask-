# ProjectApp Frontend

A modern React application built with Vite and styled with Tailwind CSS.

## Features

- ⚡ **Vite** - Fast build tool and development server
- ⚛️ **React 18** - Latest React with concurrent features
- 🎨 **Tailwind CSS** - Utility-first CSS framework
- 🧭 **React Router** - Client-side routing
- 📱 **Responsive Design** - Mobile-first approach
- 🔧 **ESLint** - Code linting and formatting

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
  ├── pages/          # Page components
  │   ├── Landing.jsx # Landing page
  │   ├── Login.jsx   # Login page
  │   ├── SignUp.jsx  # Sign up page
  │   └── Home.jsx    # Dashboard/Home page
  ├── App.jsx         # Main app component with routing
  ├── main.jsx        # App entry point
  └── index.css       # Global styles with Tailwind
```

## Tailwind CSS Configuration

The project is configured with:
- Custom color palette (primary/secondary)
- Inter font family
- Custom animations and keyframes
- Responsive breakpoints
- Custom utility classes

## Deployment

Build the project for production:

```bash
npm run build
```

The `dist` folder will contain the production-ready files.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting: `npm run lint`
5. Submit a pull request