# Spotify Migration Tool - Docker Setup

This document provides instructions for running the Spotify Migration Tool using Docker.

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository and navigate to the project directory**
2. **Create your environment file**:
   ```bash
   cp .env.example .env
   ```
   
3. **Edit `.env` with your credentials**:
   ```env
   CLIENT_ID="your_spotify_client_id"
   CLIENT_SECRET="your_spotify_client_secret"
   REDIRECT_URI="http://localhost:8888/callback"
   LIDARR_URL="http://your_lidarr_server:8686/api/v1"
   API_KEY="your_lidarr_api_key"
   ```

4. **Create data directory and copy your Navidrome database**:
   ```bash
   mkdir -p data
   cp /path/to/your/navidrome.db data/
   ```

5. **Start the application**:
   ```bash
   docker-compose up --build
   ```

6. **Access the application**: Open http://localhost:8888 in your browser

### Using Docker Run

```bash
# Build the image
docker build -t spotify-migration .

# Run the container
docker run -d \
  --name spotify-migration \
  -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  spotify-migration
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLIENT_ID` | Spotify Client ID | Required |
| `CLIENT_SECRET` | Spotify Client Secret | Required |
| `REDIRECT_URI` | OAuth redirect URI | `http://localhost:8888/callback` |
| `LIDARR_URL` | Lidarr API URL | Optional |
| `API_KEY` | Lidarr API Key | Optional |
| `DATABASE_PATH` | Path to Navidrome database | `/app/data/navidrome.db` |
| `OUTPUT_DIR` | Output directory for generated files | `/app/output` |
| `DATA_DIR` | Data directory mount point | `/app/data` |

### Volume Mounts

- **`./data:/app/data`**: Mount your local data directory containing the Navidrome database
- **`./output:/app/output`** (optional): Mount for persistent output files

## Docker Hub Image

The image is available on Docker Hub with multi-architecture support:

```bash
# Pull and run from Docker Hub (latest version)
docker pull ethanbarclay/spotify-migration:latest

docker run -d \
  --name spotify-migration \
  -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  ethanbarclay/spotify-migration:latest
```

### Available Tags:
- `latest` - Latest stable version
- `v1.0.1` - Fixed production server compatibility
- `v1.0.0` - Initial release

## Building Multi-Architecture Images

To build for multiple architectures (AMD64, ARM64):

```bash
# Create and use a new builder
docker buildx create --name multiarch --use

# Build and push multi-architecture image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ethanbarclay/spotify-migration:latest \
  --push .
```

## Health Checks

The container includes health checks accessible at:
- **Health endpoint**: `http://localhost:8888/health`
- **Docker health check**: Automatically monitors container health

## Directory Structure

```
/app/
├── data/              # Mounted data directory
│   └── navidrome.db   # Your Navidrome database
├── output/            # Generated files (M3U playlists, etc.)
├── temp/              # Temporary files
├── app.py             # Main application
├── scripts/           # Processing scripts
├── templates/         # HTML templates
└── static/            # CSS, JS, images
```

## Usage Examples

### Local Development
```bash
# Build and run locally
docker-compose up --build

# View logs
docker-compose logs -f spotify-migration
```

### Production Deployment
```bash
# Using Docker Hub image
docker run -d \
  --name spotify-migration \
  --restart unless-stopped \
  -p 8888:8888 \
  -v /path/to/navidrome/data:/app/data \
  --env-file .env \
  ethanbarclay/spotify-migration:latest
```

### With Navidrome Stack
```yaml
version: '3.8'
services:
  navidrome:
    image: deluan/navidrome:latest
    ports:
      - "4533:4533"
    volumes:
      - ./data:/data
      - ./music:/music:ro
    environment:
      ND_SCANSCHEDULE: 1h
      ND_LOGLEVEL: info

  spotify-migration:
    image: ethanbarclay/spotify-migration:latest
    ports:
      - "8888:8888"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    depends_on:
      - navidrome
```

## Troubleshooting

### Common Issues

1. **Database not found**:
   - Ensure your Navidrome database is in the mounted `data` directory
   - Check the `DATABASE_PATH` environment variable

2. **Permission issues**:
   - Ensure the data directory is readable by the container
   - The container runs as a non-root user (`appuser`)

3. **Spotify authentication fails**:
   - Verify your Spotify app credentials in `.env`
   - Ensure the redirect URI matches your Spotify app settings

4. **Container won't start**:
   - Check logs: `docker logs spotify-migration`
   - Verify all required environment variables are set

### Debugging

```bash
# View container logs
docker logs -f spotify-migration

# Execute shell in running container
docker exec -it spotify-migration /bin/bash

# Check health status
curl http://localhost:8888/health
```

## Security Notes

- The container runs as a non-root user for security
- Environment variables should be kept secure
- Consider using Docker secrets for production deployments
- The application is intended for local/private network use

## Building from Source

```bash
# Clone repository
git clone <repository-url>
cd spotify-migration

# Build image
docker build -t spotify-migration .

# Run locally
docker-compose up
```

## Support

For issues related to:
- **Docker setup**: Check this README and container logs
- **Application features**: See the main README.md
- **Spotify integration**: Verify your Spotify app configuration
- **Navidrome integration**: Ensure database accessibility
