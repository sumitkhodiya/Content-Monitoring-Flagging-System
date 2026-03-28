# React Frontend - Content Monitoring System

Modern React dashboard for the Content Monitoring & Flagging System.

## Setup

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
cd frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

The dev server automatically proxies API calls to `http://localhost:8000/api`

## Build for Production

```bash
npm run build
```

Creates optimized production build in `dist/` directory.

## Project Structure

```
frontend/
├── package.json              # Dependencies
├── vite.config.js            # Build configuration
├── index.html                # HTML template
└── src/
    ├── main.jsx              # React entry point
    ├── App.jsx               # Main app component
    ├── App.css               # Global styles
    ├── api.js                # API client (axios)
    └── components/
        ├── Common.jsx        # Reusable components
        ├── Statistics.jsx     # Stats display
        ├── ScanPanel.jsx      # Scan trigger
        ├── KeywordsPanel.jsx  # Keyword management
        └── FlagsPanel.jsx     # Flags display & filtering
```

## Components

### Statistics
Real-time flag statistics with auto-refresh

### ScanPanel
- Trigger content scans
- View scan results (items processed, flags created, suppressed)
- Loading state feedback

### KeywordsPanel
- Add new keywords
- Display all keywords as chips
- Auto-reload on add

### FlagsPanel
- List all flags with filtering
- Status tabs (All/Pending/Relevant/Irrelevant)
- Mark pending flags as relevant/irrelevant
- Real-time flag updates

### Common Components
- `StatBox` - Statistics display
- `Alert` - Toast notifications
- `FlagCard` - Individual flag display
- `Loading` - Loading spinner
- `EmptyState` - No data message

## Features

✅ Component-based architecture  
✅ API integration with axios  
✅ Real-time statistics  
✅ Alert notifications  
✅ Responsive design  
✅ Auto-refresh on actions  
✅ Status filtering  
✅ Clean, maintainable code  

## API Integration

All API calls are handled through `src/api.js`:

```javascript
// Keywords
getKeywords()
createKeyword(name)

// Flags
getFlags(filters)
updateFlagStatus(id, status)
getFlagStats()

// Scan
runScan(source)
```

The API client uses axios with CORS automatically configured.

## Development Notes

- Uses Vite for fast development and optimized builds
- React 18+ with hooks for state management
- Simple but effective styling without external CSS frameworks
- Responsive mobile-first design
- Graceful error handling with user feedback

## Production Notes

When building for production:
1. Set `VITE_API_BASE` environment variable if API is on different domain
2. Update `vite.config.js` proxy settings if needed
3. Build output is in `dist/`

## Troubleshooting

### Cannot connect to API
```bash
# Make sure Django backend is running
python manage.py runserver 0.0.0.0:8000

# Check that CORS is enabled in Django settings
# (Should be by default with django-cors-headers)
```

### Port 3000 already in use
```bash
npm run dev -- --port 3001
```

### Build fails
```bash
# Clean and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

**Frontend ready!** Start with `npm install && npm run dev`
