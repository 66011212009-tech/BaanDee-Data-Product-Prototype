# เอกสารระบุการใช้งาน Generative AI, Open-Source และการตรวจสอบผล (AI Use Statement)

โปรเจกต์ **BaanDee Living: Data Product Prototype** มีการนำเครื่องมือ ปัญญาประดิษฐ์ (Generative AI) มาใช้เป็นผู้ช่วยในการพัฒนา โดยสมาชิกในทีมเป็นผู้ควบคุมและตัดสินใจในขั้นตอนสำคัญทั้งหมด เอกสารฉบับนี้จัดทำขึ้นเพื่อแสดงความโปร่งใสและระบุกระบวนการทำงานร่วมกับ AI ดังนี้:

---

### 1. เครื่องมือ AI ที่ใช้งาน (Tools Used)
* **เครื่องมือ:** Gemini / ChatGPT
* **บทบาท:** AI Coding Assistant / Co-pilot

---

### 2. ส่วนที่ใช้ AI ช่วยงาน (AI-Assisted Components)
1. **Data Cleaning Script Strategy:** ช่วยแนะนำแนวทางการเขียนโค้ดเพื่อแก้ปัญหาอ่านไฟล์ภาษาไทย (`load_csv_file` เพื่อรับมือ Encoding `utf-8`, `tis-620`, `cp874`) และโครงสร้างโค้ดสำหรับจัดการค่าว่าง (`fillna`)
2. **Debugging & Refactoring:** ช่วยวิเคราะห์สาเหตุและเสนอทางแก้ปัญหา Error ระหว่างรัน เช่น `UnicodeDecodeError` และ `KeyError` ใน Pandas DataFrame
3. **Streamlit UI Layout & Boilerplate:** ช่วยสร้างโครงสร้าง UI พื้นฐานสำหรับตัวเลือกสินค้า (Dropdown), ช่องกรอกตัวเลข (Number Input) และโครงสร้างแบบฟอร์มบันทึกสต็อก (`st.form`)

---

### 3. การตรวจสอบและยืนยันผลลัพธ์โดยทีมงาน (Verification & Validation Process)
ทีมงานไม่ได้นำโค้ดที่ AI สร้างขึ้นไปใช้งานทันทีโดยไม่มีการตรวจสอบ แต่มีกระบวนการตรวจสอบคุณภาพ ดังนี้:
1. **Code Review:** สมาชิกในทีมร่วมกันอ่านและไล่เช็ก Logic ของโค้ดทีละบรรทัด เพื่อให้มั่นใจว่าเข้าใจการทำงานจริงทุกส่วน
2. **Execution Test:** นำโค้ดมาทดสอบรันบนเครื่องจริงเพื่อดูผลลัพธ์ว่าไม่มี Runtime Error หรือข้อผิดพลาดเรื่อง Encoding
3. **5 Test Cases Validation:** นำระบบเข้าสู่การทดสอบผ่านกรณีศึกษา 5 กรณี (TC-01 ถึง TC-05) ในไฟล์ `tests/test_cases.md` ครอบคลุมทั้งการ Clean ข้อมูล, การคำนวณ `available_qty`, การทำงานของ Success Case และ Failure Case บนหน้าจอ UI

---

### 4. ส่วนที่สมาชิกในทีมเป็นผู้ตัดสินใจเอง (Human Decisions & Ownership)
1. **การเลือกโจทย์และปัญหาธุรกิจ:** ทีมงานเป็นผู้กำหนดบริบทปัญหาเรื่อง "ระบบตรวจสอบความพร้อมสินค้าแต่ละสาขา" และกำหนดกลุ่มผู้ใช้งานหลัก (พนักงานขายหน้าร้าน และ ฝ่ายจัดซื้อ)
2. **การออกแบบ Data Schema & Derivative Data:** ทีมงานเป็นผู้กำหนดโครงสร้างข้อมูลสังเคราะห์ (`branch_inventory.csv`) และคิดค้นสูตรธุรกิจ:
   `available_qty = stock_qty - reserved_qty - damaged_qty`
3. **การออกแบบ Business Logic & Human-in-the-loop:** ทีมงานเป็นผู้กำหนดกฎเงื่อนไขว่า เมื่อใดที่ระบบควรอนุมัติการสั่งซื้อ (Success Case) และเมื่อใดที่ระบบต้องหยุดเพื่อส่งเรื่องต่อให้ฝ่ายจัดซื้อ (Failure Case)
4. **การเลือกใช้ Open-Source Libraries:** ทีมงานตัดสินใจเลือกใช้ Pandas และ Streamlit โดยศึกษาเพิ่มเติมจาก Official Documentation

---

### แหล่งอ้างอิง Open-Source และ Documentation
* **Pandas Documentation:** [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/) (BSD 3-Clause License)
* **Streamlit Documentation:** [https://docs.streamlit.io/](https://docs.streamlit.io/) (Apache License 2.0)
