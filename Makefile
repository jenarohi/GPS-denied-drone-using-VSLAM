# VSLAM-UAV Makefile
# Quick commands for building, running, and managing the VSLAM stack

.PHONY: build up down logs deploy clean status attach-vslam attach-mavros calibrate

# ── Primary Commands ────────────────────────────────────────────────────────

build:
	@echo "🔨 Building VSLAM containers..."
	docker compose build

up:
	@echo "🚀 Starting VSLAM + MAVROS pipeline..."
	docker compose up -d vslam-core flight-bridge

down:
	@echo "🛑 Stopping all containers..."
	docker compose down

logs:
	docker compose logs -f

status:
	@echo "📊 Container status:"
	@docker compose ps

deploy:
	@chmod +x deploy.sh
	@./deploy.sh

# ── Container Access ────────────────────────────────────────────────────────

attach-vslam:
	docker exec -it vslam-core bash

attach-mavros:
	docker exec -it flight-bridge bash

# ── Calibration ─────────────────────────────────────────────────────────────

calibrate:
	@echo "📐 Starting IMU calibration container..."
	docker compose --profile calibration up -d imu-calibration
	docker exec -it imu-calibration bash

# ── Maintenance ─────────────────────────────────────────────────────────────

clean:
	@echo "🧹 Removing all containers and images..."
	docker compose down --rmi all --volumes
	@echo "Done."

rebuild:
	@echo "♻️  Force rebuilding (no cache)..."
	docker compose build --no-cache
