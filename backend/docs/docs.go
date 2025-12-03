package docs

import "github.com/swaggo/swag"

const docTemplate = `{
    "swagger": "2.0",
    "info": {
        "title": "Interview Manager API",
        "description": "Backend API for AI-powered technical interview system",
        "version": "1.0.0",
        "contact": {
            "name": "Interview Manager Team"
        }
    },
    "host": "localhost:8080",
    "basePath": "/",
    "paths": {
        "/health": {
            "get": {
                "summary": "Health check",
                "tags": ["Health"],
                "responses": {
                    "200": {
                        "description": "Service is healthy"
                    }
                }
            }
        },
        "/api/interview/start": {
            "post": {
                "summary": "Start a new interview session",
                "tags": ["Interview"],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": true,
                    "schema": {
                        "type": "object",
                        "required": ["candidateName", "topic", "difficulty", "duration"],
                        "properties": {
                            "candidateName": {"type": "string", "example": "John Doe"},
                            "topic": {"type": "string", "example": "DSA"},
                            "difficulty": {"type": "string", "example": "Junior"},
                            "duration": {"type": "integer", "example": 30}
                        }
                    }
                }],
                "responses": {
                    "200": {
                        "description": "Interview started successfully"
                    },
                    "400": {
                        "description": "Invalid request"
                    },
                    "500": {
                        "description": "Failed to generate question"
                    }
                }
            }
        },
        "/api/interview/respond": {
            "post": {
                "summary": "Submit candidate response",
                "tags": ["Interview"],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": true,
                    "schema": {
                        "type": "object",
                        "required": ["sessionId", "transcript"],
                        "properties": {
                            "sessionId": {"type": "string"},
                            "transcript": {"type": "string", "example": "I would use a hash map..."}
                        }
                    }
                }],
                "responses": {
                    "200": {
                        "description": "Response evaluated"
                    },
                    "404": {
                        "description": "Session not found"
                    }
                }
            }
        },
        "/api/interview/end": {
            "post": {
                "summary": "End interview and generate report",
                "tags": ["Interview"],
                "consumes": ["application/x-www-form-urlencoded"],
                "produces": ["application/json"],
                "parameters": [{
                    "in": "formData",
                    "name": "sessionId",
                    "type": "string",
                    "required": true
                }],
                "responses": {
                    "200": {
                        "description": "Report generated"
                    },
                    "404": {
                        "description": "Session not found"
                    }
                }
            }
        },
        "/api/interview/status/{sessionId}": {
            "get": {
                "summary": "Get interview status",
                "tags": ["Interview"],
                "parameters": [{
                    "in": "path",
                    "name": "sessionId",
                    "type": "string",
                    "required": true
                }],
                "responses": {
                    "200": {
                        "description": "Session status"
                    },
                    "404": {
                        "description": "Session not found"
                    }
                }
            }
        },
        "/api/integrity/event": {
            "post": {
                "summary": "Log an integrity event",
                "tags": ["Integrity"],
                "consumes": ["application/json"],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": true,
                    "schema": {
                        "type": "object",
                        "required": ["sessionId", "eventType"],
                        "properties": {
                            "sessionId": {"type": "string"},
                            "eventType": {"type": "string", "example": "TAB_SWITCH"},
                            "metadata": {"type": "object"}
                        }
                    }
                }],
                "responses": {
                    "200": {
                        "description": "Event logged"
                    }
                }
            }
        },
        "/api/integrity/events/{sessionId}": {
            "get": {
                "summary": "Get integrity events for session",
                "tags": ["Integrity"],
                "parameters": [{
                    "in": "path",
                    "name": "sessionId",
                    "type": "string",
                    "required": true
                }],
                "responses": {
                    "200": {
                        "description": "List of integrity events"
                    }
                }
            }
        },
        "/api/admin/sessions": {
            "get": {
                "summary": "List all sessions",
                "tags": ["Admin"],
                "responses": {
                    "200": {
                        "description": "List of sessions"
                    }
                }
            }
        },
        "/api/admin/report/{sessionId}": {
            "get": {
                "summary": "Get session report",
                "tags": ["Admin"],
                "parameters": [{
                    "in": "path",
                    "name": "sessionId",
                    "type": "string",
                    "required": true
                }],
                "responses": {
                    "200": {
                        "description": "Session report"
                    },
                    "404": {
                        "description": "Session not found"
                    }
                }
            }
        }
    }
}`

var SwaggerInfo = &swag.Spec{
	Version:          "1.0.0",
	Host:             "localhost:8080",
	BasePath:         "/",
	Schemes:          []string{},
	Title:            "Interview Manager API",
	Description:      "Backend API for AI-powered technical interview system",
	InfoInstanceName: "swagger",
	SwaggerTemplate:  docTemplate,
}

func init() {
	swag.Register(SwaggerInfo.InstanceName(), SwaggerInfo)
}
