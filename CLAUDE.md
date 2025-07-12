# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Taiwan Navigation System (台灣導航系統) - a Docker-based geolocation and real-time communication platform that combines map navigation with WebSocket chat functionality. The system provides user geolocation, nearby user search, A-to-B navigation, and real-time messaging.

## Architecture

- **Frontend**: Vanilla HTML/CSS/JavaScript served by Nginx (no frameworks)
- **Backend**: Django with Django REST Framework + Channels for WebSocket support
- **Database**: PostgreSQL with PostGIS for geospatial data, Redis for chat pub/sub
- **Services**: OSRM for route planning, OpenStreetMap tile server for map tiles
- **Load Balancing**: Nginx with 3 Django instances (django-1, django-2, django-3)

## Development Commands

### System Setup
```bash
# Initial setup (downloads Taiwan OSM data, processes OSRM files, generates SSL certs)
chmod +x setup.sh
./setup.sh

# After containers are running, apply Django migrations
docker compose exec django-1 python manage.py migrate
```

### Container Management
```bash
# Start all services
docker compose up -d --build

# View logs for specific service
docker compose logs django-1
docker compose logs nginx
docker compose logs osrm

# Execute Django commands in container
docker compose exec django-1 python manage.py [command]
docker compose exec django-1 python manage.py shell
docker compose exec django-1 python manage.py createsuperuser
```

### Testing
```bash
# Run Django tests
docker compose exec django-1 python manage.py test
docker compose exec django-1 python manage.py test geouser
docker compose exec django-1 python manage.py test chat
```

## Key Services & Ports

- **Nginx**: 80 (HTTP), 443 (HTTPS) - Frontend + reverse proxy
- **Django instances**: 8001, 8002, 8003 - API endpoints
- **PostgreSQL**: 5432 - Main database with PostGIS
- **Redis**: 6379 - WebSocket channel layer
- **OSRM**: 5000 - Route planning service
- **Tile Server**: 8080 - OpenStreetMap tiles

## Important Paths

- `backend/` - Django application code
- `frontend/` - Static HTML/CSS/JS files  
- `nginx/nginx.conf` - Nginx configuration with load balancing
- `osm_data/` - Taiwan OSM data and OSRM processed files
- `certbot/conf/selfsigned/` - Self-signed SSL certificates
- `.env` - Environment variables (created from .env.sample)

## Django Apps Structure

- `geouser/` - User location management and nearby search
- `chat/` - WebSocket real-time messaging functionality
- `taxi_backend/` - Main Django project settings and configuration

## Environment Setup

The system requires environment variables defined in `.env` file. The `setup.sh` script automatically creates this from `.env.sample`.

## API Documentation

The system includes Swagger/OpenAPI documentation via drf-spectacular:
- Swagger UI: Available after deployment
- ReDoc: Available after deployment

## Development Notes

- Frontend API endpoints need IP address configuration in `frontend/app.js`
- System designed for Taiwan map data specifically
- Self-signed certificates generated for HTTPS development
- Load balancer distributes requests across 3 Django instances
- WebSocket connections handled by Django Channels with Redis backend