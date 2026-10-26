#!/bin/bash

echo "🚀 Đang khởi tạo cấu trúc thư mục dự án Mining Satellite Platform..."

# 1. Tạo các thư mục chính
mkdir -p configs data/raw data/processed docker src/ingestion src/utils log

# 2. Tạo file __init__.py cho các package Python
touch src/__init__.py
touch src/ingestion/__init__.py
touch src/utils/__init__.py

# 3. Tạo file configs/data_config.yaml
cat << 'EOF' > configs/data_config.yaml
project:
  name: "Mining_Satellite_Monitoring"
  target: "Coc_Sau_Coal_Mine"

satellite:
  collection: "sentinel-2-l2a"
  bbox: [107.30, 21.00, 107.40, 21.06] # Tọa độ mỏ than Cọc Sáu
  max_cloud_cover: 5
  date_range: "2024-01-01/2024-03-31"
EOF

# 4. Tạo file docker/docker-compose.yml (Dựng MinIO S3 Storage)
cat << 'EOF' > docker/docker-compose.yml
version: '3.8'

services:
  minio:
    image: minio/minio:latest
    container_name: minio_storage
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: "admin"
      MINIO_ROOT_PASSWORD: "adminpassword"
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

volumes:
  minio_data:
EOF

# 5. Tạo file requirements.txt
cat << 'EOF' > requirements.txt
pystac-client
planetary-computer
requests
pyyaml
rasterio
matplotlib
seaborn
EOF

# 6. Tạo file .gitignore
cat << 'EOF' > .gitignore
.venv/
data/raw/*
data/processed/*
__pycache__/
.ipynb_checkpoints/
*.log
EOF

# 7. Tạo file src/utils/logger.py (Hệ thống log chuẩn DE)
cat << 'EOF' > src/utils/logger.py
import logging
import sys

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
EOF

# 8. Tạo file src/ingestion/sentinel_collector.py
cat << 'EOF' > src/ingestion/sentinel_collector.py
from src.utils.logger import get_logger

logger = get_logger("SentinelCollector")

def download_satellite_data(config):
    logger.info("Bắt đầu kết nối STAC API để tìm kiếm ảnh vệ tinh...")
    bbox = config['satellite']['bbox']
    collection = config['satellite']['collection']
    logger.info(f"Đã nạp thành công cấu hình vùng quét BBOX: {bbox} cho collection: {collection}")
    logger.info("Mô-đun Ingestion đã sẵn sàng thực thi tải ảnh vệ tinh!")
EOF

# 9. Tạo file main.py (Điểm vào chính)
cat << 'EOF' > main.py
import yaml
from src.utils.logger import get_logger
from src.ingestion.sentinel_collector import download_satellite_data

logger = get_logger("MainPipeline")

def load_config():
    with open("configs/data_config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    logger.info("==================================================")
    logger.info("🚀 KHỞI ĐỘNG HỆ THỐNG GIÁM SÁT MỎ BẰNG ẢNH VỆ TINH")
    logger.info("==================================================")
    
    config = load_config()
    download_satellite_data(config)
    
    logger.info("✅ Quy trình Phase 1 hoàn tất thành công!")

if __name__ == "__main__":
    main()
EOF

echo "🎉 KHỞI TẠO TOÀN BỘ CẤU TRÚC DỰ ÁN THÀNH CÔNG!"
