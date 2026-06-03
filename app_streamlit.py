"""
Solar Advisor Pro - Web Application
Chạy với: streamlit run app_streamlit.py
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
    .info-box {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'customer_phone' not in st.session_state:
    st.session_state.customer_phone = ""
if 'customer_address' not in st.session_state:
    st.session_state.customer_address = ""
if 'monthly_bill' not in st.session_state:
    st.session_state.monthly_bill = 0
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# Biểu giá điện Việt Nam
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
    """Tính kWh từ tiền điện"""
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
            breakdown.append({
                'tier': name,
                'kwh': kwh_used,
                'cost': remaining_bill,
                'price': price
            })
            break
        else:
            tier_kwh = end - start
            tier_cost = tier_kwh * price
            if remaining_bill >= tier_cost:
                total_kwh += tier_kwh
                remaining_bill -= tier_cost
                breakdown.append({
                    'tier': name,
                    'kwh': tier_kwh,
                    'cost': tier_cost,
                    'price': price
                })
            else:
                kwh_used = remaining_bill / price
                total_kwh += kwh_used
                breakdown.append({
                    'tier': name,
                    'kwh': kwh_used,
                    'cost': remaining_bill,
                    'price': price
                })
                break
    
    return round(total_kwh, 2), breakdown

def calculate_solar_system(monthly_kwh):
    """Tính toán hệ thống điện mặt trời"""
    output_per_kwp = 120  # 1 kWp tạo 120 kWh/tháng
    suggested_kwp = round(monthly_kwh / output_per_kwp, 1)
    
    # Giá tham khảo theo công suất
    if suggested_kwp <= 3:
        system_price = suggested_kwp * 11000000
        system_name = "Hệ thống cơ bản"
    elif suggested_kwp <= 5:
        system_price = suggested_kwp * 10500000
        system_name = "Hệ thống gia đình"
    elif suggested_kwp <= 8:
        system_price = suggested_kwp * 10000000
        system_name = "Hệ thống kinh doanh"
    else:
        system_price = suggested_kwp * 9500000
        system_name = "Hệ thống cao cấp"
    
    return suggested_kwp, system_price, system_name

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/solar-panel.png", width=80)
    st.title("☀️ Solar Advisor Pro")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Điều hướng",
        ["📊 Dashboard", "👤 Khách hàng", "⚡ Tính toán", "💡 Đề xuất", "📄 Báo cáo"]
    )
    
    st.markdown("---")
    st.caption("© 2024 Solar Advisor Pro")
    st.caption("Giải pháp năng lượng xanh")

# Main content
if page == "📊 Dashboard":
    # Header
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
    
    st.markdown("---")
    
    # Benefits
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Lợi ích khi lắp đặt")
        st.markdown("""
        - ✅ Giảm 80-100% hóa đơn tiền điện
        - ✅ Bảo vệ môi trường, giảm phát thải CO₂
        - ✅ Tăng giá trị bất động sản
        - ✅ Độc lập năng lượng, tránh biến động giá điện
        - ✅ Bảo hành thiết bị 10-12 năm
        """)
    
    with col2:
        st.subheader("📊 Thống kê")
        st.markdown("""
        - 🏠 Hơn 10,000+ gia đình đã lắp đặt
        - 📈 Tiết kiệm trung bình 5-8 triệu/tháng
        - 🌳 Giảm 2-3 tấn CO₂/năm mỗi hệ thống
        - ⭐ Hài lòng khách hàng: 98%
        """)
    
    # Solar radiation chart
    st.subheader("☀️ Tiềm năng năng lượng mặt trời tại Việt Nam")
    months = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']
    radiation = [3.5, 4.0, 4.5, 5.0, 5.2, 5.0, 4.8, 4.5, 4.2, 4.0, 3.8, 3.5]
    
    fig = go.Figure(data=go.Scatter(
        x=months,
        y=radiation,
        mode='lines+markers',
        line=dict(color='#10B981', width=3),
        marker=dict(size=10, color='#059669'),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))
    fig.update_layout(
        title="Bức xạ mặt trời trung bình (kWh/m²/ngày)",
        xaxis_title="Tháng",
        yaxis_title="Bức xạ",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

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
            value=st.session_state.customer_address,
            placeholder="Nhập địa chỉ lắp đặt",
            height=100
        )
    
    if st.button("💾 Lưu thông tin", type="primary", use_container_width=True):
        if st.session_state.customer_name and st.session_state.customer_phone:
            st.success(f"✅ Đã lưu thông tin khách hàng {st.session_state.customer_name}!")
            st.balloons()
        else:
            st.error("❌ Vui lòng nhập đầy đủ họ tên và số điện thoại!")

elif page == "⚡ Tính toán":
    st.title("⚡ Tính toán điện năng")
    st.markdown("---")
    
    # Input
    monthly_bill = st.number_input(
        "💰 Tiền điện hàng tháng (VNĐ)",
        min_value=0,
        value=st.session_state.monthly_bill,
        step=100000,
        help="Nhập số tiền trên hóa đơn điện hàng tháng của bạn"
    )
    
    st.caption("ℹ️ Hệ thống sẽ tính ngược số kWh dựa trên biểu giá điện lũy tiến của EVN")
    
    if st.button("🔍 Tính toán ngay", type="primary", use_container_width=True):
        if monthly_bill > 0:
            st.session_state.monthly_bill = monthly_bill
            st.session_state.calculated = True
            
            # Calculate
            monthly_kwh, breakdown = calculate_kwh_from_bill(monthly_bill)
            suggested_kwp, system_price, system_name = calculate_solar_system(monthly_kwh)
            payback_years = system_price / (monthly_bill * 12)
            
            # Store results
            st.session_state.monthly_kwh = monthly_kwh
            st.session_state.suggested_kwp = suggested_kwp
            st.session_state.system_price = system_price
            st.session_state.payback_years = payback_years
            st.session_state.breakdown = breakdown
            
            # Display results
            st.success("✅ Tính toán thành công!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("⚡ Lượng điện sử dụng", f"{monthly_kwh:,.0f} kWh/tháng")
                st.metric("💡 Công suất đề xuất", f"{suggested_kwp} kWp")
                st.metric("💰 Giá đầu tư", f"{system_price:,.0f} VNĐ")
            
            with col2:
                st.metric("📈 Tiền điện trung bình/kWh", f"{monthly_bill/monthly_kwh:,.0f} VNĐ")
                st.metric("⏱️ Thời gian hoàn vốn", f"{payback_years:.1f} năm")
                st.metric("🎯 Tuổi thọ hệ thống", "25-30 năm")
            
            # Breakdown chart
            st.subheader("📊 Phân bố điện năng theo bậc giá")
            
            df = pd.DataFrame(breakdown)
            fig = go.Figure(data=[
                go.Bar(
                    x=df['tier'],
                    y=df['kwh'],
                    text=df['kwh'].round(1),
                    textposition='auto',
                    marker_color='#10B981'
                )
            ])
            fig.update_layout(
                title="Điện năng tiêu thụ theo từng bậc",
                xaxis_title="Bậc giá",
                yaxis_title="Số kWh",
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("❌ Vui lòng nhập số tiền điện hợp lệ!")
    
    # Show current calculation
    if st.session_state.calculated:
        st.info(f"📊 Kết quả hiện tại: {st.session_state.monthly_kwh:.0f} kWh/tháng - Đề xuất {st.session_state.suggested_kwp} kWp")

elif page == "💡 Đề xuất":
    st.title("💡 Đề xuất hệ thống điện mặt trời")
    st.markdown("---")
    
    if not st.session_state.calculated:
        st.warning("⚠️ Vui lòng thực hiện tính toán trước tại trang 'Tính toán'!")
    else:
        # Main recommendation
        st.markdown(f"""
        <div class="info-box">
            <h2 style="color:#10B981; text-align:center;">✅ HỆ THỐNG ĐỀ XUẤT</h2>
            <h3 style="text-align:center;">Công suất: {st.session_state.suggested_kwp} kWp</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Thông số kỹ thuật")
            st.markdown(f"""
            - **Công suất đỉnh**: {st.session_state.suggested_kwp} kWp
            - **Số lượng tấm pin**: {int(st.session_state.suggested_kwp * 3)} tấm (450W)
            - **Diện tích lắp đặt**: {st.session_state.suggested_kwp * 5} m²
            - **Sản lượng năm**: {st.session_state.suggested_kwp * 120 * 12:,.0f} kWh
            """)
        
        with col2:
            st.subheader("💰 Phân tích tài chính")
            monthly_saving = st.session_state.monthly_bill * 0.8
            st.markdown(f"""
            - **Tiết kiệm hàng tháng**: {monthly_saving:,.0f} VNĐ
            - **Tiết kiệm năm**: {monthly_saving * 12:,.0f} VNĐ
            - **Thời gian hoàn vốn**: {st.session_state.payback_years:.1f} năm
            - **Lợi nhuận 20 năm**: {(monthly_saving * 12 * 20 - st.session_state.system_price):,.0f} VNĐ
            """)
        
        # Investment chart
        st.subheader("📈 Hiệu quả đầu tư dài hạn")
        
        years = list(range(0, 26))
        cumulative_savings = []
        cumulative_investment = [st.session_state.system_price] * len(years)
        
        for i, year in enumerate(years):
            savings = monthly_saving * 12 * year
            cumulative_savings.append(savings)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=years, y=cumulative_savings, name="Tích lũy tiết kiệm",
                      line=dict(color='#10B981', width=3)),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=years, y=cumulative_investment, name="Chi phí đầu tư",
                      line=dict(color='#EF4444', width=3, dash='dash')),
            secondary_y=False,
        )
        
        fig.update_layout(
            title="Tích lũy tiết kiệm theo thời gian",
            xaxis_title="Năm",
            yaxis_title="Số tiền (VNĐ)",
            height=400,
            template="plotly_white"
        )
        
        fig.add_hline(y=st.session_state.system_price, line_dash="dash", line_color="red")
        fig.add_vline(x=st.session_state.payback_years, line_dash="dash", line_color="green")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Environmental benefits
        st.subheader("🌱 Lợi ích môi trường")
        
        co2_saved = st.session_state.monthly_kwh * 0.5 / 1000
        trees_equivalent = co2_saved * 12 / 0.02
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌍 Giảm CO₂/năm", f"{co2_saved * 12:.1f} tấn")
        with col2:
            st.metric("🌳 Cây xanh tương đương", f"{trees_equivalent:.0f} cây")
        with col3:
            st.metric("💧 Tiết kiệm nước/năm", f"{st.session_state.monthly_kwh * 2:,.0f} lít")
        
        # Recommended combos
        st.subheader("🎯 Các gói giải pháp")
        
        combos = [
            {"name": "Gói Cơ bản", "kwp": 3, "price": 35000000, "saving": monthly_saving * 0.6},
            {"name": "Gói Gia đình", "kwp": 5, "price": 52000000, "saving": monthly_saving * 0.8},
            {"name": "Gói Tiết kiệm", "kwp": 6, "price": 60000000, "saving": monthly_saving * 0.9},
            {"name": "Gói Cao cấp", "kwp": st.session_state.suggested_kwp, "price": st.session_state.system_price, "saving": monthly_saving}
        ]
        
        combo_df = pd.DataFrame(combos)
        st.dataframe(
            combo_df,
            column_config={
                "name": "Gói giải pháp",
                "kwp": st.column_config.NumberColumn("Công suất (kWp)"),
                "price": st.column_config.NumberColumn("Giá đầu tư (VNĐ)", format="%d"),
                "saving": st.column_config.NumberColumn("Tiết kiệm/tháng (VNĐ)", format="%d")
            },
            hide_index=True,
            use_container_width=True
        )

else:  # Báo cáo
    st.title("📄 Xuất báo cáo PDF")
    st.markdown("---")
    
    if not st.session_state.calculated:
        st.warning("⚠️ Vui lòng thực hiện tính toán trước khi xuất báo cáo!")
    else:
        st.info("""
        📋 **Nội dung báo cáo bao gồm:**
        - Thông tin khách hàng
        - Kết quả phân tích điện năng
        - Đề xuất hệ thống điện mặt trời
        - Phân tích tài chính và thời gian hoàn vốn
        - Lợi ích môi trường
        - Khuyến nghị và chính sách bảo hành
        """)
        
        if st.button("📑 Xuất báo cáo PDF", type="primary", use_container_width=True):
            try:
                # Generate HTML report
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Báo cáo Solar Advisor Pro</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .header {{ text-align: center; background: #10B981; color: white; padding: 20px; border-radius: 10px; }}
                        .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                        .title {{ color: #10B981; }}
                        table {{ width: 100%; border-collapse: collapse; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #10B981; color: white; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>SOLAR ADVISOR PRO</h1>
                        <p>Báo cáo tư vấn hệ thống điện mặt trời</p>
                        <p>Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    
                    <div class="section">
                        <h2 class="title">👤 Thông tin khách hàng</h2>
                        <p><strong>Họ tên:</strong> {st.session_state.customer_name or 'Chưa cập nhật'}</p>
                        <p><strong>Số điện thoại:</strong> {st.session_state.customer_phone or 'Chưa cập nhật'}</p>
                        <p><strong>Địa chỉ:</strong> {st.session_state.customer_address or 'Chưa cập nhật'}</p>
                    </div>
                    
                    <div class="section">
                        <h2 class="title">⚡ Kết quả phân tích</h2>
                        <table>
                            <tr><th>Chỉ số</th><th>Giá trị</th></tr>
                            <tr><td>Tiền điện hàng tháng</td><td>{st.session_state.monthly_bill:,.0f} VNĐ</td></tr>
                            <tr><td>Lượng điện sử dụng</td><td>{st.session_state.monthly_kwh:.0f} kWh/tháng</td></tr>
                            <tr><td>Công suất đề xuất</td><td>{st.session_state.suggested_kwp} kWp</td></tr>
                            <tr><td>Giá đầu tư</td><td>{st.session_state.system_price:,.0f} VNĐ</td></tr>
                            <tr><td>Thời gian hoàn vốn</td><td>{st.session_state.payback_years:.1f} năm</td></tr>
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2 class="title">💰 Phân tích tài chính</h2>
                        <p>Tiết kiệm hàng tháng: {st.session_state.monthly_bill * 0.8:,.0f} VNĐ</p>
                        <p>Tiết kiệm năm: {st.session_state.monthly_bill * 0.8 * 12:,.0f} VNĐ</p>
                        <p>Lợi nhuận 20 năm: {(st.session_state.monthly_bill * 0.8 * 12 * 20 - st.session_state.system_price):,.0f} VNĐ</p>
                    </div>
                    
                    <div class="section">
                        <h2 class="title">🌱 Lợi ích môi trường</h2>
                        <p>Giảm phát thải CO₂: {st.session_state.monthly_kwh * 0.5 / 1000:.1f} tấn/năm</p>
                        <p>Tương đương trồng: {st.session_state.monthly_kwh * 0.5 / 1000 / 0.02:.0f} cây xanh/năm</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px; color: #999;">
                        <p>Báo cáo được tạo bởi Solar Advisor Pro - Giải pháp năng lượng xanh</p>
                        <p>Hotline: 1900 1234 | Email: info@solaradvisor.vn</p>
                    </div>
                </body>
                </html>
                """
                
                # Save as PDF
                import pdfkit
                from pathlib import Path
                
                output_path = Path.home() / "Desktop" / f"SolarAdvisor_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                html_path = Path.home() / "Desktop" / "report_temp.html"
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Try to use weasyprint or reportlab
                try:
                    from weasyprint import HTML
                    HTML(str(html_path)).write_pdf(str(output_path))
                    st.success(f"✅ Đã xuất báo cáo thành công!\nLưu tại: {output_path}")
                    st.balloons()
                    
                    # Provide download link
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Tải xuống báo cáo PDF",
                            data=f,
                            file_name=output_path.name,
                            mime="application/pdf"
                        )
                except:
                    # Fallback: Provide HTML download
                    st.warning("⚠️ Chưa cài đặt weasyprint. Bạn có thể tải báo cáo dạng HTML.")
                    st.download_button(
                        label="📥 Tải xuống báo cáo HTML",
                        data=html_content,
                        file_name=f"SolarAdvisor_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                
                # Cleanup
                if html_path.exists():
                    html_path.unlink()
                    
            except Exception as e:
                st.error(f"❌ Lỗi khi xuất báo cáo: {str(e)}")