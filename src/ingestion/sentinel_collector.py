import os
import planetary_computer
import pystac_client
import requests
from src.utils.logger import get_logger

logger = get_logger("SentinelCollector")


def download_satellite_data(config: dict, target_year: str = "2024") -> str:
  url = "https://planetarycomputer.microsoft.com/api/stac/v1"
  catalog = pystac_client.Client.open(
      url, modifier=planetary_computer.sign_inplace
  )

  sat_cfg = config.get("satellite", {})
  collection = sat_cfg.get("collection", "sentinel-2-l2a")
  bbox = sat_cfg.get("bbox")
  date_range = f"{target_year}-01-01/{target_year}-04-30"

  output_dir = f"data/raw/{target_year}"
  os.makedirs(output_dir, exist_ok=True)

  # Tìm ảnh
  search = catalog.search(
      collections=[collection],
      bbox=bbox,
      datetime=date_range,
      query={"eo:cloud_cover": {"lt": 20}},
  )
  items = list(search.items())
  if not items:
    raise RuntimeError(f"Không tìm thấy ảnh cho năm {target_year}!")

  best_item = sorted(
      items, key=lambda x: x.properties.get("eo:cloud_cover", 100)
  )[0]
  logger.info(
      f"🎯 Đã chọn ảnh tối ưu năm {target_year}: Ngày"
      f" {best_item.datetime.strftime('%Y-%m-%d')}"
  )

  # Tải 2 băng tần cốt lõi: B04 (Red) và B08 (NIR) để tính NDVI
  bands = {"B04": "red_path.tif", "B08": "nir_path.tif"}
  downloaded_paths = {}

  for band_name, filename in bands.items():
    asset = best_item.assets.get(band_name)
    if not asset:
      # Dự phòng cho tên asset khác nhau trên STAC
      asset = best_item.assets.get(band_name.lower())

    save_path = os.path.join(output_dir, filename)
    downloaded_paths[band_name] = save_path

    if not os.path.exists(save_path):
      logger.info(f"Đang tải băng tần {band_name}...")
      r = requests.get(asset.href, timeout=60)
      with open(save_path, "wb") as f:
        f.write(r.content)

  return output_dir  # Trả về thư mục chứa B04 và B08