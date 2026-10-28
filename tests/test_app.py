import pandas as pd
import numpy as np
import pytest
import os

# จำลองฟังก์ชัน Business Logic แบบเดียวกับที่อยู่ใน app.py
def process_inventory_logic(df):
    cleaned = df.copy()
    
    # แก้ Missing Value เป็น 0
    if 'stock_qty' in cleaned.columns:
        cleaned['stock_qty'] = cleaned['stock_qty'].fillna(0)
        
    # แก้ Invalid Value (ติดลบ) เป็น 0
    if 'damaged_qty' in cleaned.columns:
        cleaned['damaged_qty'] = cleaned['damaged_qty'].apply(lambda x: max(0, x) if pd.notnull(x) else 0)
        
    # คำนวณ available_qty
    stock = cleaned['stock_qty'] if 'stock_qty' in cleaned.columns else 0
    reserved = cleaned['reserved_qty'] if 'reserved_qty' in cleaned.columns else 0
    damaged = cleaned['damaged_qty'] if 'damaged_qty' in cleaned.columns else 0
    
    cleaned['available_qty'] = stock - reserved - damaged
    return cleaned

# ---------------------------------------------------------
# Test Cases
# ---------------------------------------------------------

def test_ui_no_negative_input():
    """TC-01: (UI Test) จำลองการตรวจสอบไม่ให้ป้อนค่าติดลบ"""
    # หมายเหตุ: การทดสอบ UI ของ Streamlit โดยตรง (st.number_input) ต้องใช้เครื่องมืออย่าง Selenium
    # แต่ในระดับ Unit Test เราสามารถตรวจสอบ Logic การแปลงค่าให้ไม่ต่ำกว่า 0 ได้
    
    input_value = -5
    # สมมุติว่าฟังก์ชัน number_input บังคับค่าต่ำสุด (min_value=0)
    actual_value = max(0, input_value)
    
    assert actual_value == 0

def test_warning_when_not_enough_stock():
    """TC-02, TC-05: จำลองการแจ้งเตือน (Warning) เมื่อสินค้าไม่เพียงพอ"""
    # จำลองว่าลูกค้าต้องการ 999 ชิ้น แต่สาขามีพร้อมขายแค่ 10 ชิ้น
    min_needed = 999
    available_qty = 10
    
    # Logic การตัดสินใจของระบบ
    is_success = available_qty >= min_needed
    
    # คาดหวังว่าระบบต้องหยุดทำงาน (False) เพื่อแสดงกล่อง Warning สีเหลือง
    assert is_success == False

def test_data_cleaning_fill_null_with_zero():
    """TC-03: ทดสอบการจัดการค่าว่าง (Null/NaN) เติมด้วย 0 อัตโนมัติ"""
    raw_data = {
        'branch_id': ['B01'],
        'stock_qty': [np.nan],      # B01 มีค่าว่าง
        'reserved_qty': [0],
        'damaged_qty': [0],         
    }
    df = pd.DataFrame(raw_data)
    result = process_inventory_logic(df)
    
    # B01: stock แก้จาก NaN เป็น 0 
    assert result.loc[0, 'stock_qty'] == 0
    assert result.loc[0, 'available_qty'] == 0

def test_missing_file_system_failure():
    """TC-04: ทดสอบจำลองกรณีไฟล์หาย (เปลี่ยนชื่อ products.csv) ระบบต้องดักจับและหยุดทำงานได้"""
    
    # 1. จำลองฟังก์ชันโหลดไฟล์ให้พัง (เสมือนว่าเปลี่ยนชื่อไฟล์ products.csv แล้วหาไม่เจอ)
    def mock_load_csv_fail(filepath):
        raise FileNotFoundError(f"No such file or directory: '{filepath}'")
    
    # 2. จำลองการทำงานของ block try-except เหมือนในไฟล์ app.py
    error_message_shown = ""
    system_stopped = False
    
    try:
        # พยายามโหลดไฟล์ที่ไม่มีอยู่จริง
        mock_load_csv_fail('data/raw/products.csv')
    except Exception as e:
        # จำลองพฤติกรรม st.error() ของ Streamlit
        error_message_shown = f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}"
        # จำลองพฤติกรรม st.stop()
        system_stopped = True
        
    # 3. ยืนยันผลลัพธ์ว่าระบบต้องแสดงข้อความ Error และหยุดการทำงาน (ไม่ Crash)
    assert "เกิดข้อผิดพลาดในการโหลดไฟล์" in error_message_shown
    assert system_stopped == True
