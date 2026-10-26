from src.utils.logger import get_logger

logger = get_logger("EconomicValuation")

def calculate_mining_economics(area_2020_km2: float, area_2024_km2: float):
    """
    Module Tin học Kinh tế:
    Quy đổi biến động diện tích moong mỏ than (km2) sang:
    - Thể tích đào bới (m3)
    - Sản lượng than thu hồi (Tấn)
    - Doanh thu ước tính (VNĐ)
    - Thuế tài nguyên phải nộp (12%)
    - Chi phí phục hồi môi trường rừng (VNĐ)
    """
    delta_area_km2 = max(0.0, area_2024_km2 - area_2020_km2)
    delta_area_m2 = delta_area_km2 * 1_000_000.0
    delta_area_ha = delta_area_km2 * 100.0

    # Các thông số định mức kỹ thuật mỏ Cọc Sáu - Cao Sơn
    DEPTH_DELTA_M = 40.0         # Chiều sâu khai thác trung bình tăng thêm (mét)
    STRIPPING_RATIO = 11.0       # Hệ số bóc đất đá Kboc: 11 m3 đất đá / 1 tấn than
    COAL_PRICE_VND = 1_950_000   # Đơn giá than bình quân: 1.95 triệu VNĐ/tấn
    TAX_RATE = 0.12              # Thuế tài nguyên than lộ thiên: 12%
    REFOREST_PER_HA = 70_000_000 # Chi phí hoàn nguyên rừng: 70 triệu VNĐ/ha

    # 1. Tính toán khối lượng kỹ thuật
    volume_rock_m3 = delta_area_m2 * DEPTH_DELTA_M
    coal_tonnage = volume_rock_m3 / STRIPPING_RATIO

    # 2. Tính toán tài chính kinh tế
    gross_revenue = coal_tonnage * COAL_PRICE_VND
    resource_tax = gross_revenue * TAX_RATE
    environment_fee = delta_area_ha * REFOREST_PER_HA

    print("\n" + "=" * 70)
    print("💰 BÁO CÁO KIỂM TOÁN TÀI NGUYÊN & ĐỊNH GIÁ KINH TẾ (2020 - 2024)")
    print("=" * 70)
    print(f"📊 1. BIẾN ĐỘNG HÌNH THÁI MỎ:")
    print(f"   • Diện tích mỏ năm 2020      : {area_2020_km2:.3f} km²")
    print(f"   • Diện tích mỏ năm 2024      : {area_2024_km2:.3f} km²")
    print(f"   • Khai trường mở rộng thêm   : {delta_area_km2:.3f} km² ({delta_area_ha:.1f} ha)")
    print(f"   • Thể tích đất đá đào bóc (V): {volume_rock_m3:,.0f} m³")
    print("-" * 70)
    print(f"⛏️  2. SẢN LƯỢNG KHOÁNG SẢN THU HỒI ƯỚC TÍNH:")
    print(f"   • Sản lượng than nguyên khai : {coal_tonnage:,.0f} tấn ({coal_tonnage/1_000_000:.2f} triệu tấn)")
    print("-" * 70)
    print(f"💵 3. NGHĨA VỤ TÀI CHÍNH & KINH TẾ TÀI NGUYÊN:")
    print(f"   • Tổng giá trị than ước tính : {gross_revenue:,.0f} VNĐ ({gross_revenue/1_000_000_000:,.1f} tỷ VNĐ)")
    print(f"   • THUẾ TÀI NGUYÊN PHẢI NỘP   : {resource_tax:,.0f} VNĐ ({resource_tax/1_000_000_000:,.1f} tỷ VNĐ)")
    print(f"   • Chi phí dự phòng hoàn nguyên rừng : {environment_fee:,.0f} VNĐ ({environment_fee/1_000_000_000:,.2f} tỷ VNĐ)")
    print("=" * 70 + "\n")

    return {
        "delta_area_km2": delta_area_km2,
        "coal_tonnage": coal_tonnage,
        "gross_revenue_vnd": gross_revenue,
        "resource_tax_vnd": resource_tax,
        "environment_fee_vnd": environment_fee
    }