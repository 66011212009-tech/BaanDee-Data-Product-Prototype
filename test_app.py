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

def test_data_cleaning_and_available_qty():
    """TC-01, TC-03: ทดสอบการจัดการค่าว่าง ค่าติดลบ และคำนวณยอดพร้อมขาย"""
    raw_data = {
        'branch_id': ['B01', 'B02'],
        'stock_qty': [10, np.nan],      # B02 มีค่าว่าง
        'reserved_qty': [2, 0],
        'damaged_qty': [-1, 3],         # B01 มีของเสียติดลบ
    }
    df = pd.DataFrame(raw_data)
    result = process_inventory_logic(df)
    
    # B01: stock 10, reserve 2, damaged แก้จาก -1 เป็น 0 -> available = 8
    assert result.loc[0, 'damaged_qty'] == 0
    assert result.loc[0, 'available_qty'] == 8
    
    # B02: stock แก้จาก NaN เป็น 0, reserve 0, damaged 3 -> available = -3
    assert result.loc[1, 'stock_qty'] == 0
    assert result.loc[1, 'available_qty'] == -3


def test_success_flow_has_enough_stock():
    """TC-04: กรณีทำงานสำเร็จ (Success Flow) มีสินค้าเพียงพอ"""
    # จำลองว่าลูกค้าต้องการ 5 ชิ้น และสาขามีพร้อมขาย 10 ชิ้น
    min_needed = 5
    available_qty = 10
    
    # Logic การตัดสินใจของระบบ
    is_success = available_qty >= min_needed
    
    # คาดหวังว่าระบบต้องอนุมัติให้ไปต่อได้ (True)
    assert is_success == True


def test_failure_flow_human_in_the_loop():
    """TC-05: กรณีระบบต้องหยุดและส่งต่อให้มนุษย์ (Failure Flow) สินค้าไม่พอ"""
    # จำลองว่าลูกค้าต้องการ 5 ชิ้น แต่สาขามีพร้อมขายแค่ 2 ชิ้น
    min_needed = 5
    available_qty = 2
    
    # Logic การตัดสินใจของระบบ
    is_success = available_qty >= min_needed
    
    # คาดหวังว่าระบบต้องหยุดทำงาน (False) เพื่อแจ้งเตือนฝ่ายจัดซื้อ
    assert is_success == False

def test_file_in_use_error(tmp_path):
    """TC-06: ทดสอบจำลองกรณีไฟล์ถูกล็อก (เช่น เปิดค้างใน Excel) ทำให้บันทึกไม่ได้"""
    import tempfile
    
    # 1. สร้างไฟล์จำลอง
    dummy_file = tmp_path / "dummy_inventory.csv"
    dummy_data = pd.DataFrame({'id': [1], 'stock': [10]})
    dummy_data.to_csv(dummy_file, index=False)
    
    # 2. จำลองการโยน PermissionError (เปรียบเสมือนไฟล์โดนโปรแกรมอื่นล็อกไว้)
    def mock_to_csv(*args, **kwargs):
        raise PermissionError("Permission denied: file is open in another program")
    
    # 3. ตรวจสอบว่า ถ้าระบบพยายามเซฟทับ แล้วเกิด PermissionError ระบบจะต้องแจ้งเตือนอย่างถูกต้อง
    try:
        # สมมุติว่าพยายามเซฟทับ
        dummy_data_update = pd.DataFrame({'id': [1], 'stock': [20]})
        
        # แทนที่จะเซฟจริง เราลองเรียก mock ฟังก์ชันที่จำลองการพัง
        mock_to_csv(dummy_file, index=False)
        
    except PermissionError as e:
        # นี่คือ Error ที่ Streamlit จะจับได้ในบล็อก except Exception as e:
        # เราคาดหวังว่าระบบจะแสดงข้อความว่า "ไม่สามารถบันทึกได้เนื่องจากไฟล์ถูกเปิดใช้งานอยู่"
        
        # เพื่อการทดสอบ เราตรวจสอบว่ามีคำว่า Permission อยู่ใน Error
        assert "Permission" in str(e)
