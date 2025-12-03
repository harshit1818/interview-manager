# Backend (Go)

REST API server for interview management.

## Structure

```
backend/
├── cmd/
│   └── server/
│       └── main.go          # Entry point
├── internal/
│   ├── handlers/            # HTTP handlers
│   │   ├── interview.go
│   │   ├── integrity.go
│   │   ├── admin.go
│   │   └── websocket.go
│   ├── models/              # Data models
│   │   └── models.go
│   ├── services/            # Business logic
│   │   ├── session.go
│   │   └── llm_client.go
│   └── middleware/          # HTTP middleware
│       └── middleware.go
├── go.mod
└── .env.example
```

## Setup

1. Install Go 1.21+

2. Install dependencies:
```bash
go mod download
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Run server:
```bash
go run cmd/server/main.go
```

Server will start on `http://localhost:8080`

## API Endpoints

### Interview
- `POST /api/interview/start` - Start new interview
- `POST /api/interview/respond` - Submit answer
- `POST /api/interview/end` - End interview
- `GET /api/interview/status/:sessionId` - Get status

### Integrity
- `POST /api/integrity/event` - Log integrity event
- `GET /api/integrity/events/:sessionId` - Get events

### Admin
- `POST /api/admin/session` - Create session
- `GET /api/admin/sessions` - List sessions
- `GET /api/admin/report/:sessionId` - Get report

### WebSocket
- `GET /ws/:sessionId` - WebSocket connection

## Testing

```bash
# Health check
curl http://localhost:8080/health
```
