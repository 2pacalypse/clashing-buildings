# Building Clashes Detection API

Backend service to detect 3D spatial overlaps between buildings with a 3D visualization frontend.

## Quick Start

```bash
# Build and run all services (API, Worker, Redis, Frontend)
docker-compose up --build
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | REST API for clash detection |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Frontend | http://localhost:8080 | 3D visualization |
| Redis | localhost:6379 | Cache and message broker |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/detect-clashes` | Submit buildings for clash detection |
| GET | `/api/v1/results/{job_id}` | Poll for async results |
| GET | `/health` | Health check |

## Input Format

```json
{
  "buildings": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "id": "building_0",
        "properties": {
          "height": 4,
          "elevation": 0
        },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[20, 0], [20, 60], [0, 60], [0, 0], [20, 0]]]
        }
      }
    ]
  }
}
```

## Frontend Features

- **3D Visualization** - View buildings in 3D with actual height/elevation
- **Interactive Controls** - Rotate (left drag), Pan (right drag), Zoom (scroll)
- **View Presets** - Reset Camera, Top-Down View, Side View
- **Color Coding** - Each building gets a unique color
- **Hover Info** - Click on buildings to see details

## Project Structure
