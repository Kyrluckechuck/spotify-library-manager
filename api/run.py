import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        workers=1,  # Single worker for development
        loop="asyncio",  # Use asyncio event loop
        http="httptools",  # Faster HTTP parser
        ws="websockets",  # WebSocket support
        log_level="info",
        access_log=True,
        # Optimize for async operations
        limit_concurrency=1000,  # Higher concurrency limit
        limit_max_requests=10000,  # More requests per worker
        timeout_keep_alive=30,  # Keep connections alive longer
        timeout_graceful_shutdown=30,  # Graceful shutdown timeout
    )
