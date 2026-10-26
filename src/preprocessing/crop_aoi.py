import os
import matplotlib.pyplot as plt
import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from src.utils.logger import get_logger

logger = get_logger("SpatialClipper")


def crop_bands_folder(band_dir: str, config: dict, year: str):
  """Cắt cúp đồng thời cả 2 băng tần (Red và NIR) và xuất ảnh preview PNG."""
  bbox = config.get("satellite", {}).get("bbox")
  out_dir = f"data/processed/{year}"
  os.makedirs(out_dir, exist_ok=True)

  cropped_red = os.path.join(out_dir, "red_cropped.tif")
  cropped_nir = os.path.join(out_dir, "nir_cropped.tif")
  preview_path = os.path.join(out_dir, f"cocsau_{year}_preview.png")

  # 1. Cắt băng tần Red (B04)
  with rasterio.open(os.path.join(band_dir, "red_path.tif")) as src:
    left, bottom, right, top = transform_bounds("EPSG:4326", src.crs, *bbox)
    window = from_bounds(left, bottom, right, top, transform=src.transform)
    data = src.read(window=window)

    meta = src.meta.copy()
    meta.update({
        "height": data.shape[1],
        "width": data.shape[2],
        "transform": src.window_transform(window),
    })

    with rasterio.open(cropped_red, "w", **meta) as dst:
      dst.write(data)

    # Xuất ảnh preview PNG từ kênh Red để làm nền bản đồ biến động
    plt.imsave(preview_path, data[0], cmap="gray")

  # 2. Cắt băng tần NIR (B08)
  with rasterio.open(os.path.join(band_dir, "nir_path.tif")) as src:
    left, bottom, right, top = transform_bounds("EPSG:4326", src.crs, *bbox)
    window = from_bounds(left, bottom, right, top, transform=src.transform)
    data = src.read(window=window)

    meta = src.meta.copy()
    meta.update({
        "height": data.shape[1],
        "width": data.shape[2],
        "transform": src.window_transform(window),
    })

    with rasterio.open(cropped_nir, "w", **meta) as dst:
      dst.write(data)

  logger.info(
      f"✂️ Đã cắt cúp băng tần thành công cho năm {year} tại: {out_dir}"
  )
  return out_dir, preview_path