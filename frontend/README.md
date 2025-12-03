# Frontend (TypeScript + React + Next.js)

AI-powered interview interface with video, code editor, and voice interaction.

## Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── VideoCall.tsx
│   │   ├── CodeEditor.tsx
│   │   └── TranscriptPanel.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── useVoice.ts          # STT/TTS
│   │   └── useIntegrityDetection.ts
│   ├── lib/               # Utilities
│   │   └── api.ts               # API client
│   ├── pages/             # Next.js pages
│   │   ├── index.tsx            # Home/Start page
│   │   └── interview/[sessionId].tsx
│   └── types/             # TypeScript types
│       └── index.ts
├── package.json
├── tsconfig.json
└── .env.example
```

## Setup

1. Install Node.js 18+

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local`:
```bash
cp .env.example .env.local
```

4. Run development server:
```bash
npm run dev
```

Frontend will start on `http://localhost:3000`

## Features

### Browser APIs (Free!)
- **Speech Recognition**: Real-time STT using Web Speech API
- **Speech Synthesis**: TTS for AI responses
- **Video**: WebRTC for camera access
- **Integrity Detection**: Tab switch, window blur detection

### Components
- **VideoCall**: Displays candidate camera and AI avatar
- **CodeEditor**: Monaco editor with paste detection
- **TranscriptPanel**: Real-time conversation transcript

### Hooks
- `useVoice`: Speech recognition and synthesis
- `useIntegrityDetection`: Monitors integrity events

## Key Pages

- `/` - Start interview (candidate info, topic selection)
- `/interview/[sessionId]` - Main interview interface
- `/report/[sessionId]` - Interview report (TODO)

## Dependencies

- **Next.js**: React framework
- **Monaco Editor**: Code editor
- **Axios**: HTTP client
- **Tailwind CSS**: Styling (optional)
