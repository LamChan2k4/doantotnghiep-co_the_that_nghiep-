import cv2
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("ChangeDetector")

def generate_change_map(img_2024_path: str, mask_2020: np.ndarray, mask_2024: np.ndarray, output_path: str = "data/processed/cocsau_change_map.png"):
    """
    So sánh mặt nạ moong mỏ giữa 2 thời điểm 2020 và 2024:
    - Vùng mỏ cũ (2020): Phủ màu ĐỎ BẦM (semi-transparent red).
    - Vùng mới mở rộng đào lấn thêm (2020 - 2024): Tô màu VÀNG NEON RỰC RỠ.
    """
    logger.info("Đang xử lý tạo Bản đồ biến động khai trường mỏ than (Change Detection Map)...")
    
    img_2024 = cv2.imread(img_2024_path)
    h, w = img_2024.shape[:2]

    # Đảm bảo kích thước 2 mặt nạ khớp nhau
    mask_2020_resized = cv2.resize(mask_2020, (w, h), interpolation=cv2.INTER_NEAREST)
    mask_2024_resized = cv2.resize(mask_2024, (w, h), interpolation=cv2.INTER_NEAREST)

    # 1. Bóc tách logic không gian:
    # - Vùng mỏ cũ: có ở cả 2020 và 2024
    old_mine = cv2.bitwise_and(mask_2020_resized, mask_2024_resized)
    # - Vùng đào lấn mới trong 4 năm: có ở 2024 nhưng CHƯA CÓ ở 2020
    new_expansion = cv2.bitwise_and(mask_2024_resized, cv2.bitwise_not(mask_2020_resized))

    overlay = img_2024.copy()

    # 2. Phủ màu nhận diện:
    # Vùng mỏ cũ -> Tô màu đỏ cam (B=0, G=100, R=255)
    overlay[old_mine > 0] = [0, 80, 220]
    # Vùng đào mới mở rộng -> Tô màu vàng neon rực rỡ (B=0, G=255, R=255)
    overlay[new_expansion > 0] = [0, 240, 255]

    # Trộn màu trong suốt (Alpha blending: 60% ảnh gốc + 40% màu phủ) để vẫn nhìn rõ bậc tầng mỏ
    result = cv2.addWeighted(overlay, 0.45, img_2024, 0.55, 0)

    # 3. Vẽ chú thích (Legend) trực tiếp lên góc ảnh cho chuyên nghiệp
    cv2.rectangle(result, (20, 20), (450, 120), (0, 0, 0), -1) # Khung nền đen
    cv2.rectangle(result, (20, 20), (450, 120), (255, 255, 255), 2)

    # Chú thích vùng cũ
    cv2.circle(result, (45, 50), 12, (0, 80, 220), -1)
    cv2.putText(result, "Khai truong mo cu (2020)", (70, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    # Chú thích vùng đào mới
    cv2.circle(result, (45, 90), 12, (0, 240, 255), -1)
    cv2.putText(result, "Vung dao mo rong moi (2020-2024)", (70, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 240, 255), 2)

    cv2.imwrite(output_path, result)
    logger.info(f"✅ Đã xuất Bản đồ biến động không gian thành công tại: {output_path}")
    return output_path