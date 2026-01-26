# Calorie Tracker App - Docker Setup

This document provides instructions for running the Calorie Tracker App backend using Docker.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### 1. Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 2. Verify Services are Running

```bash
# Check if backend is healthy
curl http://localhost:8000/

# Expected response: {"message":"Welcome to the Healthy Food App Backend!"}
```

### 3. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (will delete MongoDB data)
docker-compose down -v
```

## Service Details

### Backend API
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

### MongoDB
- **Host**: localhost:27017
- **Database**: healthyfoodapp
- **Container**: calorie_tracker_mongodb

## Environment Variables

The backend service uses the following environment variables:

- `MONGO_URI`: MongoDB connection string (default: mongodb://mongodb:27017/healthyfoodapp)
- `SECRET_KEY`: JWT secret key for authentication
- `ENVIRONMENT`: Environment setting (development/production)

## Development Workflow

### For Development (with hot reload)

The current setup mounts the backend code as a volume, allowing for live code changes without rebuilding the container.

1. Make changes to backend files
2. Changes are automatically reflected in the running container
3. No need to restart the container for Python code changes

### For Production

1. Remove the volume mount from docker-compose.yml
2. Rebuild the image: `docker-compose build`
3. Deploy the new image

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Check what's using port 27017
   lsof -i :27017
   ```

2. **MongoDB connection issues**
   ```bash
   # Check MongoDB logs
   docker-compose logs mongodb
   
   # Check if MongoDB is healthy
   docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
   ```

3. **Backend startup issues**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Check if backend is responding
   curl http://localhost:8000/
   ```

### Reset Everything

```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean up unused Docker resources
docker system prune -af

# Start fresh
docker-compose up -d
```

## Security Notes

1. **Change the SECRET_KEY**: Update the `SECRET_KEY` in docker-compose.yml before deploying to production
2. **MongoDB Authentication**: Consider adding authentication to MongoDB for production use
3. **Network Security**: The current setup exposes MongoDB on localhost only. For production, consider using internal networking only

## File Structure

```
.
├── docker-compose.yml          # Main compose file
├── backend/
│   ├── Dockerfile             # Backend container definition
│   ├── requirements.txt       # Python dependencies
│   ├── .dockerignore          # Files to exclude from build
│   └── main.py               # FastAPI application
└── README_DOCKER.md          # This file
```

## Next Steps

1. Set up the frontend application
2. Configure reverse proxy (nginx) for production
3. Add monitoring and logging
4. Set up CI/CD pipeline