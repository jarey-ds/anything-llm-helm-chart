# Docker Build Instructions

## Building the Docker Image

The Dockerfile requires authentication for private repositories, which is handled securely using Docker BuildKit secrets:

```bash
# CI/CD builds with BuildKit secrets (recommended)
DOCKER_BUILDKIT=1 docker build \
  --build-arg VERSION_TAG=v1.0.0 \
  --build-arg COMMIT_HASH=$(git rev-parse HEAD) \
  -f deploy/Dockerfile \
  -t cinfo/mileva/sso_anythingllm:latest .
```

For local development you can use the uv tasks:

```bash
# Build Docker image locally
task docker-build

# Run the Docker container
task docker-run
```


**Note**: Docker builds are only possible in CI/CD environments with proper credentials. For local development, use the approach below.

## Local Development (Recommended)

Since Docker builds require private repository access, local development should be done directly:

```bash
# Install dependencies locally
uv run task install

# Or use the run task:
uv run task run-local
```