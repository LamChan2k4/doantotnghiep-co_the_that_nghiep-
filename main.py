import os
import yaml
from src.analytics.change_detector import generate_change_map
from src.analytics.economic_valuation import calculate_mining_economics
from src.ingestion.sentinel_collector import download_satellite_data
from src.preprocessing.crop_aoi import crop_bands_folder
from src.preprocessing.mine_detector import image_process
from src.utils.logger import get_logger

logger = get_logger("MainPipeline")


def load_config():
  with open("configs/data_config.yaml", "r", encoding="utf-8") as f:
    return yaml.safe_load(f)


def process_year(config, year: str):
  logger.info(f"--- ĐANG XỬ LÝ DỮ LIỆU VỆ TINH NĂM {year} (NDVI) ---")
  raw_band_dir = download_satellite_data(config, target_year=year)

  year_config = config.copy()
  year_config["satellite"] = config["satellite"].copy()

  # Nhận về cả thư mục processed lẫn file ảnh preview.png
  processed_dir, preview_path = crop_bands_folder(
      raw_band_dir, year_config, year
  )

  area_km2, mask = image_process(processed_dir)
  return area_km2, mask, preview_path


def main():
  logger.info("==========================================================")
  logger.info(
      "🚀 KHỞI ĐỘNG HỆ THỐNG GIÁM SÁT MỎ VÀ ĐỊNH GIÁ KINH TẾ (2020 - 2024)"
  )
  logger.info("==========================================================")

  config = load_config()

  # 1. Xử lý tự động năm 2020
  area_2020, mask_2020, preview_2020 = process_year(config, "2020")

  # 2. Xử lý tự động năm 2024
  area_2024, mask_2024, preview_2024 = process_year(config, "2024")

  # 3. Tạo Bản đồ biến động Change Map (So sánh 2020 và 2024)
  change_map_path = generate_change_map(
      preview_2024, mask_2020, mask_2024
  )

  # 4. Phân tích kinh tế lượng & Thuế tài nguyên
  economics = calculate_mining_economics(area_2020, area_2024)

  logger.info("🎉 HOÀN TẤT TOÀN DIỆN DỰ ÁN GIÁM SÁT MỎ VÀ KINH TẾ!")
  logger.info(f"   • Bản đồ biến động mỏ    : {change_map_path}")
  logger.info(
      f"   • Sản lượng than ước tính: {economics['coal_tonnage']/1_000_000:.2f}"
      " triệu tấn"
  )
  logger.info(
      f"   • Thuế tài nguyên dự thu :"
      f" {economics['resource_tax_vnd']/1_000_000_000:.1f} tỷ VNĐ"
  )


if __name__ == "__main__":
  main()