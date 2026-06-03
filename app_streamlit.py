"""
Solar Advisor Pro - Web Application with Contact Info
Chạy với: streamlit run app_streamlit_final.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Cấu hình trang
st.set_page_config(
    page_title="Solar Advisor Pro",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #10B981;
    }
    .stat-label {
        color: #6B7280;
        font-size: 0.9rem;
    }
    .contact-card {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
    }
    .contact-card .phone {
        font-size: 1.3rem;
        font-weight: bold;
    }
    .contact-button {
        background-color: #0068FF;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 50px;
        font-size: 14px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
        display: inline-block;
        margin: 5px;
    }
    .contact-button:hover {
        background-color: #0052CC;
        transform: translateY(-2px);
    }
    .info-box {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .zalo-qr {
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/solar-panel.png", width=80)
    st.title("☀️ Solar Advisor Pro")
    
    # Navigation
    page = st.radio(
        "Điều hướng",
        ["📊 Dashboard", "👤 Khách hàng", "⚡ Tính toán", "💡 Đề xuất", "📄 Báo cáo"]
    )
    
    st.markdown("---")
    
    # THÔNG TIN LIÊN HỆ - PHẦN QUAN TRỌNG
    st.markdown("""
    <div class="contact-card">
        <h4>📞 TƯ VẤN MIỄN PHÍ</h4>
        <div class="phone">0329 250 056</div>
        <p>💬 Zalo: 0329250056</p>
        <p>⏰ 8h00 - 20h00 hàng ngày</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Nút Zalo
    st.markdown("""
    <div style="text-align: center;">
        <a href="https://zalo.me/0329250056" target="_blank">
            <button class="contact-button">
                💬 Chat Zalo ngay
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("© 2024 Solar Advisor Pro")

# Khởi tạo session state
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'customer_phone' not in st.session_state:
    st.session_state.customer_phone = ""
if 'monthly_bill' not in st.session_state:
    st.session_state.monthly_bill = 0
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# Biểu giá điện
PRICE_TIERS = [
    (0, 50, 1984, "Bậc 1: 0-50 kWh"),
    (50, 100, 2050, "Bậc 2: 51-100 kWh"),
    (100, 200, 2380, "Bậc 3: 101-200 kWh"),
    (200, 300, 2998, "Bậc 4: 201-300 kWh"),
    (300, 400, 3350, "Bậc 5: 301-400 kWh"),
    (400, float('inf'), 3460, "Bậc 6: Trên 400 kWh")
]
VAT_RATE = 0.08

def calculate_kwh_from_bill(total_bill):
    bill_without_vat = total_bill / (1 + VAT_RATE)
    remaining_bill = bill_without_vat
    total_kwh = 0
    breakdown = []
    
    for start, end, price, name in PRICE_TIERS:
        if remaining_bill <= 0:
            break
        if end == float('inf'):
            kwh_used = remaining_bill / price
            total_kwh += kwh_used
            breakdown.append({'tier': name, 'kwh': kwh_used, 'cost': remaining_bill, 'price': price})
            break
        else:
            tier_kwh = end - start
            tier_cost = tier_kwh * price
            if remaining_bill >= tier_cost:
                total_kwh += tier_kwh
                remaining_bill -= tier_cost
                breakdown.append({'tier': name, 'kwh': tier_kwh, 'cost': tier_cost, 'price': price})
            else:
                kwh_used = remaining_bill / price
                total_kwh += kwh_used
                breakdown.append({'tier': name, 'kwh': kwh_used, 'cost': remaining_bill, 'price': price})
                break
    
    return round(total_kwh, 2), breakdown

def calculate_solar_system(monthly_kwh):
    output_per_kwp = 120
    suggested_kwp = round(monthly_kwh / output_per_kwp, 1)
    
    if suggested_kwp <= 3:
        system_price = suggested_kwp * 11000000
    elif suggested_kwp <= 5:
        system_price = suggested_kwp * 10500000
    elif suggested_kwp <= 8:
        system_price = suggested_kwp * 10000000
    else:
        system_price = suggested_kwp * 9500000
    
    return suggested_kwp, system_price

# Main content
if page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0">🌱 Solar Advisor Pro</h1>
        <p style="margin:0">Giải pháp điện mặt trời thông minh cho gia đình bạn</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">💰</div>
            <div class="stat-value">Tiết kiệm 80%</div>
            <div class="stat-label">Hóa đơn tiền điện</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">⚡</div>
            <div class="stat-value">120 kWh/kWp</div>
            <div class="stat-label">Sản lượng mỗi tháng</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">⏱️</div>
            <div class="stat-value">4-6 năm</div>
            <div class="stat-label">Thời gian hoàn vốn</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 2rem;">🌍</div>
            <div class="stat-value">25-30 năm</div>
            <div class="stat-label">Tuổi thọ hệ thống</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Banner tư vấn
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 2rem 0;
    ">
        <h2>🎯 CẦN TƯ VẤN NGAY?</h2>
        <p style="font-size: 1.2rem">Đội ngũ chuyên gia sẵn sàng hỗ trợ bạn</p>
        <h1 style="font-size: 2.5rem; margin: 1rem 0">📞 0329 250 056</h1>
        <p>💬 Zalo: 0329250056</p>
        <a href="https://zalo.me/0329250056" target="_blank">
            <button style="
                background-color: #0068FF;
                color: white;
                padding: 15px 30px;
                font-size: 18px;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                font-weight: bold;
                margin-top: 1rem;
            ">
                💬 Nhắn tin Zalo ngay
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

elif page == "👤 Khách hàng":
    st.title("👤 Thông tin khách hàng")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.customer_name = st.text_input(
            "Họ và tên *",
            value=st.session_state.customer_name,
            placeholder="Nhập họ tên đầy đủ"
        )
        
        st.session_state.customer_phone = st.text_input(
            "Số điện thoại *",
            value=st.session_state.customer_phone,
            placeholder="Nhập số điện thoại"
        )
    
    with col2:
        st.session_state.customer_address = st.text_area(
            "Địa chỉ *",
            value=st.session_state.customer_address if hasattr(st.session_state, 'customer_address') else "",
            placeholder="Nhập địa chỉ lắp đặt",
            height=100
        )
    
    if st.button("💾 Lưu thông tin", type="primary", use_container_width=True):
        if st.session_state.customer_name and st.session_state.customer_phone:
            st.success(f"✅ Đã lưu thông tin khách hàng {st.session_state.customer_name}!")
            st.balloons()
        else:
            st.error("❌ Vui lòng nhập đầy đủ họ tên và số điện thoại!")
    
    # Thêm thông tin tư vấn
    st.markdown("---")
    st.info("📞 **Cần hỗ trợ?** Gọi ngay: **0329 250 056** hoặc chat Zalo để được tư vấn miễn phí!")

elif page == "⚡ Tính toán":
    st.title("⚡ Tính toán điện năng")
    st.markdown("---")
    
    monthly_bill = st.number_input(
        "💰 Tiền điện hàng tháng (VNĐ)",
        min_value=0,
        value=st.session_state.monthly_bill,
        step=100000,
        help="Nhập số tiền trên hóa đơn điện hàng tháng của bạn"
    )
    
    if st.button("🔍 Tính toán ngay", type="primary", use_container_width=True):
        if monthly_bill > 0:
            st.session_state.monthly_bill = monthly_bill
            st.session_state.calculated = True
            
            monthly_kwh, breakdown = calculate_kwh_from_bill(monthly_bill)
            suggested_kwp, system_price = calculate_solar_system(monthly_kwh)
            payback_years = system_price / (monthly_bill * 12)
            
            st.session_state.monthly_kwh = monthly_kwh
            st.session_state.suggested_kwp = suggested_kwp
            st.session_state.system_price = system_price
            st.session_state.payback_years = payback_years
            
            st.success("✅ Tính toán thành công!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("⚡ Lượng điện sử dụng", f"{monthly_kwh:,.0f} kWh/tháng")
                st.metric("💡 Công suất đề xuất", f"{suggested_kwp} kWp")
            with col2:
                st.metric("💰 Giá đầu tư", f"{system_price:,.0f} VNĐ")
                st.metric("⏱️ Thời gian hoàn vốn", f"{payback_years:.1f} năm")
        else:
            st.error("❌ Vui lòng nhập số tiền điện hợp lệ!")
    
    if st.session_state.calculated:
        st.info(f"📊 Kết quả hiện tại: {st.session_state.monthly_kwh:.0f} kWh/tháng")
        
        # Thêm nút tư vấn
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <p>🤔 Chưa chắc chắn về kết quả?</p>
            <a href="https://zalo.me/0329250056" target="_blank">
                <button class="contact-button">💬 Chat với chuyên gia tư vấn</button>
            </a>
        </div>
        """, unsafe_allow_html=True)

elif page == "💡 Đề xuất":
    st.title("💡 Đề xuất hệ thống điện mặt trời")
    
    if not st.session_state.calculated:
        st.warning("⚠️ Vui lòng thực hiện tính toán trước tại trang 'Tính toán'!")
    else:
        st.markdown(f"""
        <div class="info-box">
            <h2 style="color:#10B981; text-align:center;">✅ HỆ THỐNG ĐỀ XUẤT</h2>
            <h3 style="text-align:center;">Công suất: {st.session_state.suggested_kwp} kWp</h3>
        </div>
        """, unsafe_allow_html=True)
        
        monthly_saving = st.session_state.monthly_bill * 0.8
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Tiết kiệm hàng tháng", f"{monthly_saving:,.0f} VNĐ")
            st.metric("📈 Tiết kiệm năm", f"{monthly_saving * 12:,.0f} VNĐ")
        with col2:
            st.metric("⏱️ Thời gian hoàn vốn", f"{st.session_state.payback_years:.1f} năm")
            st.metric("🎯 Lợi nhuận 20 năm", f"{(monthly_saving * 12 * 20 - st.session_state.system_price):,.0f} VNĐ")

elif page == "📄 Báo cáo":
    st.title("📄 Xuất báo cáo PDF")
    
    if not st.session_state.calculated:
        st.warning("⚠️ Vui lòng thực hiện tính toán trước khi xuất báo cáo!")
    else:
        st.info("""
        📋 **Nội dung báo cáo bao gồm:**
        - Thông tin khách hàng
        - Kết quả phân tích điện năng
        - Đề xuất hệ thống điện mặt trời
        - Phân tích tài chính
        - Lợi ích môi trường
        """)
        
        if st.button("📑 Xuất báo cáo PDF", type="primary", use_container_width=True):
            st.success("✅ Chức năng đang được phát triển! Vui lòng liên hệ tư vấn để nhận báo cáo chi tiết.")
            st.info("📞 Liên hệ ngay: **0329 250 056** (Zalo) để được tư vấn miễn phí!")
