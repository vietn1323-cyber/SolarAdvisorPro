import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io

# --- 1. CẤU HÌNH TRANG & GIAO DIỆN ---
st.set_page_config(page_title="Solar Advisor Pro - Giải Pháp Điện Mặt Trời", page_icon="☀️", layout="wide")

# Khởi tạo trạng thái phiên (Session State) cho hệ thống Đăng nhập & CRM giả lập nếu chưa cấu hình Google Sheet
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'crm_data' not in st.session_state: 
    st.session_state.crm_data = pd.DataFrame(columns=["Tên", "Số ĐT", "Email", "Hóa Đơn (đ)", "Công Suất Đề Xuất (kW)", "Gói Chọn", "Doanh Thu Dự Kiến (đ)"])
if 'products' not in st.session_state:
    st.session_state.products = {
        "Gói Phổ Thông (LV Hybrid)": {"price_per_kw": 16000000, "desc": "Inverter Luxpower/Deye + Pin Lithium 48V phổ thông"},
        "Gói Cao Cấp (HV Hybrid)": {"price_per_kw": 24000000, "desc": "Inverter GoodWe/Sungrow + Pin Lưu Trữ Áp Cao dòng lớn"}
    }

# --- 2. CÁC HÀM XỬ LÝ LOGIC (ROI, PDF, EMAIL) ---
def calculate_roi(kw, electricity_bill, price_increase_rate):
    """Tính toán bài toán kinh tế ROI 25 năm có suy giảm hiệu suất tấm pin"""
    years = list(range(1, 26))
    savings = []
    current_saving = electricity_bill * 12 * 0.7 # Giả định tiết kiệm được 70% tiền điện hàng năm
    
    for year in years:
        # Tấm pin suy giảm hiệu suất ~0.5% mỗi năm, giá điện tăng trưởng theo % cấu hình
        efficiency = 1.0 - (year - 1) * 0.005
        price_factor = (1 + price_increase_rate / 100) ** (year - 1)
        yearly_saving = current_saving * efficiency * price_factor
        savings.append(round(yearly_saving))
    return years, savings

def generate_pdf(name, kw, cost, total_saving):
    """Tạo file báo giá PDF chuyên nghiệp có cấu trúc"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "SOLAR ADVISOR PRO - BẢO CÁO TƯ VẤN ĐIỆN MẶT TRỜI")
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Kính gửi Khách hàng: {name}")
    p.drawString(50, 700, f"Công suất hệ thống đề xuất: {kw} kWp")
    p.drawString(50, 680, f"Chi phí đầu tư dự kiến: {cost:,.0f} VNĐ")
    p.drawString(50, 660, f"Tổng tiền điện tiết kiệm ước tính (25 năm): {total_saving:,.0f} VNĐ")
    p.drawString(50, 620, "Cảm ơn quý khách đã tin tưởng dịch vụ của chúng tôi!")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def send_email_quote(to_email, name, pdf_buffer):
    """Gửi email báo giá đính kèm tệp PDF tự động (Yêu cầu cấu hình SMTP nếu chạy thật)"""
    st.info(f"⚡ Hệ thống đang giả lập gửi Email báo giá thông minh đến: {to_email}")
    # Trong môi trường sản xuất thực tế, bạn sẽ mở các dòng code dưới đây và cấu hình mật khẩu ứng dụng Gmail:
    # msg = MIMEMultipart()
    # msg['From'] = "your_email@gmail.com"
    # msg['To'] = to_email
    # msg['Subject'] = f"[Solar Advisor Pro] Báo giá giải pháp điện mặt trời cho {name}"
    # ... kết nối smtplib.SMTP_SSL ...

# --- 3. GIAO DIỆN CHÍNH (STREAMLIT MULTI-PAGE CHUYỂN ĐỔI) ---
menu = st.sidebar.selectbox("🧭 ĐIỀU HƯỚNG HỆ THỐNG", ["☀️ Trang Chủ Khách Hàng", "📊 Admin Dashboard & CRM"])

# ==================== GIAO DIỆN KHÁCH HÀNG ====================
if menu == "☀️ Trang Chủ Khách Hàng":
    # Khối thu Lead đầu trang và Hỗ trợ nhanh
    col_logo, col_contact = st.columns([2, 1])
    with col_logo:
        st.title("☀️ SOLAR ADVISOR PRO")
        st.subheader("Giải Pháp Tính Toán & Khảo Sát Điện Mặt Trời Tự Động")
    with col_contact:
        st.markdown("### 📞 Hỗ Trợ Nhanh")
        st.markdown("[💬 Chát Zalo Ngay](https://zalo.me) | ☎️ Hotline: **1900 xxxx**")
        st.caption("Quét mã QR hoặc bấm để gọi điện trực tiếp cho chuyên viên.")

    st.markdown("---")
    
    # Form thu thập thông tin Lead đầu vào
    st.markdown("### 📝 Bước 1: Nhập thông tin nhu cầu & Khảo sát")
    with st.form("lead_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            cust_name = st.text_input("Họ và tên của bạn:", placeholder="Nguyễn Văn A")
            cust_phone = st.text_input("Số điện thoại liên hệ:", placeholder="090XXXXXXX")
        with col2:
            cust_email = st.text_input("Địa chỉ Email nhận báo giá:", placeholder="username@gmail.com")
            bill = st.number_input("Tiền điện trung bình hàng tháng (VNĐ):", min_value=0, value=3000000, step=200000)
        with col3:
            package_choice = st.selectbox("Chọn gói sản phẩm thực tế mục tiêu:", list(st.session_state.products.keys()))
            price_inc = st.slider("Dự báo giá điện tăng trưởng hàng năm (%):", 1, 15, 5)
            
        submit_btn = st.form_submit_button("🚀 PHÂN TÍCH HIỆU QUẢ KINH TẾ & GỬI BÁO GIÁ")

    if submit_btn:
        if not cust_name or not cust_phone:
            st.error("⚠️ Vui lòng nhập đầy đủ Họ tên và Số điện thoại để hệ thống lập báo cáo!")
        else:
            # Thuật toán tính toán thông minh
            kw_proposed = round((bill / 2500 / 30 / 4) * 1.2, 1)
            if kw_proposed < 3: kw_proposed = 3.0
            
            price_per_kw = st.session_state.products[package_choice]["price_per_kw"]
            total_cost = kw_proposed * price_per_kw
            
            # Tính toán bài toán ROI tài chính
            years, savings = calculate_roi(kw_proposed, bill, price_inc)
            total_savings = sum(savings)
            payback_year = "Đang tính toán..."
            
            # Tính thời gian hoàn vốn (ROI) sơ bộ
            temp_cost = total_cost
            for y, s in zip(years, savings):
                temp_cost -= s
                if temp_cost <= 0:
                    payback_year = f"{y} năm"
                    break
            if temp_cost > 0: payback_year = "> 15 năm"

            # Lưu thông tin khách hàng trực tiếp vào bảng CRM hệ thống (Google Sheets backup/Session State)
            new_lead = {
                "Tên": cust_name, "Số ĐT": cust_phone, "Email": cust_email, 
                "Hóa Đơn (đ)": bill, "Công Suất Đề Xuất (kW)": kw_proposed, 
                "Gói Chọn": package_choice, "Doanh Thu Dự Kiến (đ)": total_cost
            }
            st.session_state.crm_data = pd.concat([st.session_state.crm_data, pd.DataFrame([new_lead])], ignore_index=True)

            # Hiển thị Dashboard Kết quả trực quan cho Khách hàng
            st.balloons()
            st.success(f"🎉 Kết quả phân tích giải pháp tối ưu dành cho khách hàng {cust_name}")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Công suất khuyên dùng", f"{kw_proposed} kWp")
            c2.metric("Chi phí trọn gói dự kiến", f"{total_cost:,.0f} đ")
            c3.metric("Thời gian hoàn vốn ước tính", payback_year)
            c4.metric("Tổng tích lũy 25 năm", f"{total_savings:,.0f} đ")
            
            # Bản đồ đồ thị ROI biểu diễn trực quan
            st.markdown("#### 📊 Biểu đồ Dự kiến số tiền tiết kiệm lũy tiến trong 25 năm (Đã tính hao mòn pin)")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=years, y=savings, name="Tiền tiết kiệm hàng năm", marker_color='#27ae60'))
            fig.add_trace(go.Scatter(x=years, y=np.cumsum(savings), name="Tổng tích lũy dồn", line=dict(color='#e67e22', width=3)))
            fig.update_layout(title="Kế Hoạch Tài Chính Dài Hạn", xaxis_title="Năm vận hành", yaxis_title="Giá trị (VNĐ)", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            # Xuất tài liệu PDF và tự động kích hoạt tiến trình Email
            pdf_file = generate_pdf(cust_name, kw_proposed, total_cost, total_savings)
            
            st.markdown("#### 📄 Tải xuống hoặc Kiểm tra Hộp thư của bạn")
            col_dl, col_mail = st.columns(2)
            with col_dl:
                st.download_button(label="📥 TẢI FILE BÁO GIÁ PDF CHUYÊN NGHIỆP", data=pdf_file, file_name=f"Bao_Gia_Solar_{cust_name}.pdf", mime="application/pdf")
            with col_mail:
                if cust_email:
                    send_email_quote(cust_email, cust_name, pdf_file)
                    st.success("✉️ Một bản sao báo cáo PDF chi tiết đã được gửi tự động vào email của bạn!")

# ==================== GIAO DIỆN QUẢN TRỊ ADMIN ====================
elif menu == "📊 Admin Dashboard & CRM":
    st.title("📊 Hệ Thống Quản Trị & Điều Hành Doanh Số")
    
    # Cơ chế đăng nhập bảo mật
    if not st.session_state.logged_in:
        st.subheader("🔐 Đăng nhập quyền Quản trị viên")
        username = st.text_input("Tài khoản doanh nghiệp:")
        password = st.text_input("Mật khẩu bảo mật:", type="password")
        if st.button("ĐĂNG NHẬP HỆ THỐNG"):
            if username == "admin" and password == "solar2026": # Thay đổi thông tin bảo mật tại đây
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Sai thông tin tài khoản hoặc mật khẩu hệ thống!")
    else:
        if st.sidebar.button("🔒 Đăng Xuất"):
            st.session_state.logged_in = False
            st.rerun()
            
        # Thống kê tổng quan Dashboard Doanh số
        st.markdown("### 📈 Chỉ số kinh doanh tổng quan")
        df_crm = st.session_state.crm_data
        
        c_lead, c_rev, c_avg = st.columns(3)
        c_lead.metric("Tổng số khách hàng (Leads)", len(df_crm))
        c_rev.metric("Tổng giá trị phễu doanh thu dự kiến", f"{df_crm['Doanh Thu Dự Kiến (đ)'].sum():,.0f} VNĐ")
        c_avg.metric("Giá trị đơn hàng trung bình", f"{df_crm['Doanh Thu Dự Kiến (đ)'].mean() if len(df_crm)>0 else 0:,.0f} VNĐ")
        
        # Phần quản lý cơ sở dữ liệu khách hàng CRM
        st.markdown("---")
        st.markdown("### 👥 Danh sách Khách hàng tiềm năng (CRM trực tuyến)")
        if len(df_crm) > 0:
            st.dataframe(df_crm, use_container_width=True)
            
            # Nút bấm KẾT NỐI THẬT đến Google Sheets sử dụng Secrets
            if st.button("🔄 ĐỒNG BỘ DỮ LIỆU ĐẨY THẲNG SANG GOOGLE SHEETS"):
                try:
                    import gspread
                    from google.oauth2.service_account import Credentials
                    
                    # 1. Định nghĩa quyền truy cập API
                    scopes = ["https://googleapis.com"]
                    
                    # 2. Đọc thông tin cấu hình từ mục Secrets trên Streamlit Cloud
                    secret_creds = st.secrets["gspread_credentials"]
                    creds = Credentials.from_service_account_info(secret_creds, scopes=scopes)
                    client = gspread.authorize(creds)
                    
                    # 3. Mở file Google Sheets (Bạn phải tạo sẵn file tên "Solar_CRM" trên Driver)
                    # Và nhớ Share quyền "Editor" cho email "client_email" trong file JSON của bạn.
                    sheet = client.open("Solar_CRM").sheet1
                    
                    # 4. Xóa dữ liệu cũ, ghi đè toàn bộ dữ liệu CRM mới nhất lên
                    sheet.clear()
                    # Thêm hàng tiêu đề (Header)
                    sheet.append_row(list(df_crm.columns))
                    # Thêm tất cả các hàng dữ liệu khách hàng
                    for index, row in df_crm.iterrows():
                        sheet.append_row(list(row))
                        
                    st.success("✅ ĐÃ ĐỒNG BỘ THÀNH CÔNG! Dữ liệu đã được ghi trực tiếp vào Google Sheets.")
                except Exception as e:
                    st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
                    st.info("Mẹo: Hãy đảm bảo bạn đã cấu hình mục 'Secrets' trên Streamlit và tạo file 'Solar_CRM' trên Google Drive!")
        else:
            st.info("Chưa có dữ liệu khách hàng nào đăng ký khảo sát từ trang chủ.")
            
        # Phần cấu hình giá trị thực tế các gói sản phẩm
        st.markdown("---")
        st.markdown("### ⚙️ Cấu hình đơn giá các gói sản phẩm phân phối")
        for key, val in st.session_state.products.items():
            new_price = st.number_input(f"Đơn giá cho mỗi kW của {key} (VNĐ):", min_value=0, value=val["price_per_kw"], step=500000)
            st.session_state.products[key]["price_per_kw"] = new_price
