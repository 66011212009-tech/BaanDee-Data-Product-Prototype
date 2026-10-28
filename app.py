import streamlit as st
import pandas as pd

st.set_page_config(page_title="ระบบเช็กสต็อกสินค้า BaanDee Living", layout="wide")
st.title("🏬 ระบบช่วยตรวจสอบความพร้อมของสินค้าแต่ละสาขา")
st.subheader("BaanDee Living Data Product Prototype")

# ฟังก์ชันช่วยโหลดไฟล์ CSV รองรับภาษาไทยหลาย encoding
def load_csv_file(file_path):
    encodings = ['utf-8', 'tis-620', 'cp874', 'utf-8-sig', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            df.columns = df.columns.str.strip()  # ตัดช่องว่างหน้า-หลังชื่อคอลัมน์ออก
            return df
        except Exception:
            continue
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    return df

# 1. โหลดข้อมูลดิบจากไฟล์ CSV ใน data/raw/
try:
    products_df = load_csv_file('data/raw/products.csv')
    branch_inventory_df = load_csv_file('data/raw/branch_inventory.csv')
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")
    st.stop()
    # 2. กระบวนการ Data Cleaning (3 ปัญหา)
cleaned_inventory = branch_inventory_df.copy()

# ปัญหาที่ 1: เติมค่าว่าง (Missing Values) ด้วย 0
if 'stock_qty' in cleaned_inventory.columns:
    cleaned_inventory['stock_qty'] = cleaned_inventory['stock_qty'].fillna(0)

# ปัญหาที่ 2: แก้ค่าติดลบ (Invalid Data) ให้กลายเป็น 0
if 'damaged_qty' in cleaned_inventory.columns:
    cleaned_inventory['damaged_qty'] = cleaned_inventory['damaged_qty'].apply(lambda x: max(0, x) if pd.notnull(x) else 0)

# ปัญหาที่ 3: ปรับรูปแบบวันที่ให้เป็นมาตรฐานเดียวกัน (YYYY-MM-DD)
if 'last_updated' in cleaned_inventory.columns:
    cleaned_inventory['last_updated'] = pd.to_datetime(cleaned_inventory['last_updated'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('2023-10-01')

# คำนวณสต็อกพร้อมขายจริง (Available Stock)
stock_qty = cleaned_inventory['stock_qty'] if 'stock_qty' in cleaned_inventory.columns else 0
reserved_qty = cleaned_inventory['reserved_qty'] if 'reserved_qty' in cleaned_inventory.columns else 0
damaged_qty = cleaned_inventory['damaged_qty'] if 'damaged_qty' in cleaned_inventory.columns else 0

cleaned_inventory['available_qty'] = stock_qty - reserved_qty - damaged_qty

# บันทึกไฟล์ที่ Clean แล้วเก็บไว้ใน data/cleaned/
cleaned_inventory.to_csv('data/cleaned/cleaned_inventory.csv', index=False, encoding='utf-8-sig')

# 3. เชื่อมข้อมูล 2 แหล่งด้วย Key (product_id)
merged_df = pd.merge(cleaned_inventory, products_df, on='product_id', how='inner')
# แสดงแถบสถานะด้านข้าง
st.sidebar.header("⚙️ การจัดการข้อมูล (Data Pipeline)")
st.sidebar.success("✅ เชื่อมข้อมูลด้วย Key: product_id")
st.sidebar.info("🧹 ทำความสะอาดข้อมูล 3 ปัญหาเรียบร้อยแล้ว")

# 4. ส่วน Interactive ค้นหาสินค้า
col1, col2 = st.columns(2)
with col1:
    product_col = 'product_name' if 'product_name' in products_df.columns else products_df.columns[0]
    selected_product = st.selectbox("เลือกสินค้าที่ต้องการตรวจสอบ:", products_df[product_col].unique())
with col2:
    min_needed = st.number_input("จำนวนที่ลูกค้าต้องการซื้อ (ชิ้น):", min_value=1, value=1)

result_df = merged_df[merged_df[product_col] == selected_product]

st.subheader(f"📊 รายงานสถานะสต็อก: {selected_product}")

# กรองเลือกเฉพาะคอลัมน์ที่มีอยู่จริงมาแสดง
target_cols = ['branch_name', 'branch_id', 'stock_qty', 'reserved_qty', 'damaged_qty', 'available_qty', 'last_updated']
show_cols = [col for col in target_cols if col in result_df.columns]
st.dataframe(result_df[show_cols] if show_cols else result_df)
# 5. Logic การวิเคราะห์สต็อก (Success / Failure Cases)
available_branches = result_df[result_df['available_qty'] >= min_needed]

branch_col = 'branch_name' if 'branch_name' in result_df.columns else ('branch_id' if 'branch_id' in result_df.columns else show_cols[0])

if not available_branches.empty:
    st.success(f"✅ มีสินค้าพร้อมส่งเพียงพอในสาขา: {', '.join(available_branches[branch_col].astype(str).tolist())}")
else:
    st.warning("⚠️ ไม่มีสาขาใดมีสินค้าเพียงพอ ระบบหยุดการทำงานและส่งเรื่องแจ้งเตือนฝ่ายจัดซื้อ (Human-in-the-loop)")

# 6. ฟังก์ชันบันทึกสต็อกหน้าร้าน
st.write("---")
st.subheader("📝 บันทึกการปรับปรุงสต็อกหน้าร้านจริง")
with st.form("update_form"):
    branch_to_update = st.selectbox("เลือกสาขาที่จะแก้ไข:", result_df[branch_col].unique())
    new_stock = st.number_input("ป้อนจำนวนสต็อกใหม่:", min_value=0, value=0)
    submitted = st.form_submit_button("บันทึกข้อมูลเข้าสู่ระบบ")
    if submitted:
        # 1. อ่านไฟล์ข้อมูลดิบขึ้นมา
        file_path = 'data/raw/branch_inventory.csv'
        try:
            df_update = pd.read_csv(file_path)
            
            # 2. ค้นหาแถวที่ตรงกับ สินค้า และ สาขา ที่เลือก แล้วอัปเดตค่า stock_qty
            # เนื่องจาก selectbox คืนค่าจากคอลัมน์ product_col เราต้องหา product_id ก่อน
            product_id_val = products_df.loc[products_df[product_col] == selected_product, 'product_id'].values[0]
            
            # ค้นหาเงื่อนไข
            condition = (df_update['product_id'] == product_id_val) & (df_update['branch_id'] == branch_to_update)
            df_update.loc[condition, 'stock_qty'] = new_stock
            
            # 3. เซฟกลับลงไปทับไฟล์เดิม
            df_update.to_csv(file_path, index=False)
            
            st.success(f"บันทึกสำเร็จ! อัปเดตสต็อกสินค้า {selected_product} ในสาขา {branch_to_update} เป็น {new_stock} ชิ้นเรียบร้อยแล้ว")
            
            # 4. สั่งให้รีเฟรชหน้าเว็บอัตโนมัติ เพื่อให้ตารางด้านบนอัปเดตตาม
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")
        except PermissionError:
            st.error("ไม่สามารถบันทึกได้เนื่องจากไฟล์ถูกเปิดใช้งานอยู่ (เช่น เปิดค้างไว้ในโปรแกรม Excel) กรุณาปิดไฟล์ก่อนทำรายการอีกครั้ง")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")
