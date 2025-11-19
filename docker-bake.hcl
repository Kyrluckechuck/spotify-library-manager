# Docker Bake file for parallel multi-platform builds
# Usage: docker buildx bake [target]
#   docker buildx bake --push              # Build and push all images
#   docker buildx bake backend             # Build only backend
#   docker buildx bake frontend            # Build only frontend

# Variables that can be overridden
variable "REGISTRY" {
  default = "ghcr.io"
}

variable "REPO_OWNER" {
  default = ""
}

variable "SHA" {
  default = "dev"
}

variable "BRANCH" {
  default = "main"
}

variable "PLATFORMS" {
  default = "linux/amd64,linux/arm64"
}

# Default group - builds both backend and frontend in parallel
group "default" {
  targets = ["backend", "frontend"]
}

# Backend image target
target "backend" {
  context = "."
  dockerfile = "Dockerfile"
  target = "backend-prod"
  platforms = split(",", PLATFORMS)
  
  tags = [
    # Always tag with SHA for traceability
    "${REGISTRY}/${REPO_OWNER}/spotify-library-manager:sha-${SHA}",
    # Tag with branch name (main becomes latest)
    BRANCH == "main" 
      ? "${REGISTRY}/${REPO_OWNER}/spotify-library-manager:latest"
      : "${REGISTRY}/${REPO_OWNER}/spotify-library-manager:${BRANCH}"
  ]
  
  cache-from = [
    "type=gha,scope=backend-app"
  ]
  
  cache-to = [
    "type=gha,scope=backend-app,mode=max"
  ]
  
  labels = {
    "org.opencontainers.image.source" = "https://github.com/${REPO_OWNER}/spotify-library-manager"
    "org.opencontainers.image.revision" = "${SHA}"
    "org.opencontainers.image.created" = timestamp()
  }
}

# Frontend image target
target "frontend" {
  context = "./frontend"
  dockerfile = "Dockerfile"
  target = "production"
  platforms = split(",", PLATFORMS)
  
  tags = [
    # Always tag with SHA for traceability
    "${REGISTRY}/${REPO_OWNER}/spotify-library-manager-frontend:sha-${SHA}",
    # Tag with branch name (main becomes latest)
    BRANCH == "main"
      ? "${REGISTRY}/${REPO_OWNER}/spotify-library-manager-frontend:latest"
      : "${REGISTRY}/${REPO_OWNER}/spotify-library-manager-frontend:${BRANCH}"
  ]
  
  cache-from = [
    "type=gha,scope=frontend-app"
  ]
  
  cache-to = [
    "type=gha,scope=frontend-app,mode=max"
  ]
  
  labels = {
    "org.opencontainers.image.source" = "https://github.com/${REPO_OWNER}/spotify-library-manager"
    "org.opencontainers.image.revision" = "${SHA}"
    "org.opencontainers.image.created" = timestamp()
  }
}

# Local testing targets (single platform, loadable)
target "backend-local" {
  inherits = ["backend"]
  platforms = ["linux/amd64"]
  tags = ["local-backend:latest"]
  output = ["type=docker"]
}

target "frontend-local" {
  inherits = ["frontend"]
  platforms = ["linux/amd64"]
  tags = ["local-frontend:latest"]
  output = ["type=docker"]
}

group "local" {
  targets = ["backend-local", "frontend-local"]
}
