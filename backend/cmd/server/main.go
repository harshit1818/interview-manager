package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	_ "interview-manager/backend/docs"
	"interview-manager/backend/internal/handlers"
	"interview-manager/backend/internal/middleware"
	"interview-manager/backend/internal/services"
)

func main() {
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	sessionService := services.NewSessionService()
	llmClient := services.NewLLMClient(os.Getenv("LLM_SERVICE_URL"))

	router := gin.Default()

	router.Use(middleware.CORS())
	router.Use(middleware.Logger())

	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "healthy"})
	})

	router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	api := router.Group("/api")
	{
		// Interview routes
		interview := api.Group("/interview")
		{
			handler := handlers.NewInterviewHandler(sessionService, llmClient)
			interview.POST("/start", handler.StartInterview)
			interview.POST("/respond", handler.HandleResponse)
			interview.POST("/end", handler.EndInterview)
			interview.GET("/status/:sessionId", handler.GetStatus)
		}

		// Integrity routes
		integrity := api.Group("/integrity")
		{
			handler := handlers.NewIntegrityHandler(sessionService)
			integrity.POST("/event", handler.LogEvent)
			integrity.GET("/events/:sessionId", handler.GetEvents)
		}

		// Admin routes
		admin := api.Group("/admin")
		{
			handler := handlers.NewAdminHandler(sessionService)
			admin.POST("/session", handler.CreateSession)
			admin.GET("/sessions", handler.ListSessions)
			admin.GET("/report/:sessionId", handler.GetReport)
		}

		// Topics and Job Description routes (proxy to LLM service)
		topics := api.Group("/topics")
		{
			handler := handlers.NewTopicsHandler(llmClient)
			topics.GET("", handler.ListTopics)
			topics.GET("/domains", handler.ListDomains)
			topics.GET("/domain/:domain", handler.ListTopicsByDomain)
		}

		jd := api.Group("/jd")
		{
			handler := handlers.NewJDHandler(llmClient, sessionService)
			jd.POST("/upload", handler.UploadJD)
			jd.POST("/text", handler.ProcessJDText)
			jd.GET("/:sessionId", handler.GetJDContext)
			jd.DELETE("/:sessionId", handler.ClearJDContext)
		}
	}

	// WebSocket for real-time updates
	router.GET("/ws/:sessionId", handlers.HandleWebSocket)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
