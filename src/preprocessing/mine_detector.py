import os
import cv2
import numpy as np
import rasterio
from src.utils.logger import get_logger

logger = get_logger("MineDetector")

def image_process(processed_dir: str):
  """Thuật toán Viễn thám chuẩn xác sử dụng chỉ số NDVI:

  NDVI = (NIR - Red) / (NIR + Red)
  - Rừng cây: NDVI > 0.25 (Xanh mướt)
  - Mỏ than & Đất đá: NDVI <= 0.25 (Trơ trọi, đen/xám)
  """
  red_path = os.path.join(processed_dir, "red_cropped.tif")
  nir_path = os.path.join(processed_dir, "nir_cropped.tif")

  if not os.path.exists(red_path) or not os.path.exists(nir_path):
    raise FileNotFoundError(f"Không tìm thấy file băng tần tại: {processed_dir}")

  # 1. Đọc ma trận điểm ảnh Đỏ (Red) và Hồng ngoại (NIR)
  with rasterio.open(red_path) as src:
    red = src.read(1).astype(np.float32)
    meta = src.meta.copy()

  with rasterio.open(nir_path) as src:
    nir = src.read(1).astype(np.float32)

  # 2. Tính toán ma trận NDVI (cộng 1e-8 để tránh lỗi chia cho 0)
  ndvi = (nir - red) / (nir + red + 1e-8)

  # 3. Phân ngưỡng: NDVI < 0.22 là mỏ than / đất đá (Gán bằng 255 - Trắng)
  mine_mask = np.where(ndvi < 0.22, 255, 0).astype(np.uint8)

  # 4. Hình thái học (Morphology) hàn gắn các tầng mỏ
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
  
  # 🌟 THÊM DÒNG NÀY: "Gọt" bớt 1 lớp viền ngoài để cắt đứt rác dính vào mỏ
  mine_mask = cv2.erode(mine_mask, kernel, iterations=1)

  morph = cv2.morphologyEx(mine_mask, cv2.MORPH_OPEN, kernel, iterations=1)
  morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel, iterations=3)

  # 5. Lọc bỏ các đốm nhỏ và vùng ven biển sát đáy ảnh
  h_img, w_img = morph.shape
  cutoff_line = int(h_img * 0.70)  # Cứ giữ nguyên 0.70 là an toàn nhất
  morph[cutoff_line:, :] = 0

  # 5. Lọc bỏ các đốm nhỏ và vùng ven biển sát đáy ảnh
  h_img, w_img = morph.shape
  contours, _ = cv2.findContours(
      morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )

  valid_mines = []
  for c in contours:
    area = cv2.contourArea(c)
    if area < 10000:
      continue

    M = cv2.moments(c)
    if M["m00"] != 0:
      cy = int(M["m01"] / M["m00"])
      cx = int(M["m10"] / M["m00"])
    else:
      continue

    # Loại bỏ vùng sát biển (28% đáy ảnh)
    if cy > (0.72 * h_img):
      continue

    valid_mines.append((c, area, (cx, cy)))

  if not valid_mines:
    logger.warning("Không tìm thấy moong mỏ hợp lệ qua NDVI!")
    return 0.0, np.zeros_like(morph)

  # Sắp xếp lấy Top 2 moong lớn nhất
  valid_mines.sort(key=lambda x: x[1], reverse=True)
  top_mines = [item[0] for item in valid_mines[:2]]
  total_mine_area_px = sum([item[1] for item in valid_mines[:2]])

  area_km2 = (total_mine_area_px * 100.0) / 1_000_000.0
  logger.info(f"🛰️ (NDVI) Diện tích khai trường mỏ: {area_km2:.3f} km²")

  # Tạo mặt nạ nhị phân kết quả cho Change Detection
  mine_only_mask = np.zeros_like(morph)
  cv2.drawContours(mine_only_mask, top_mines, -1, 255, -1)

  return area_km2, mine_only_mask