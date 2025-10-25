import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO
import datetime

st.set_page_config(page_title="IE Lab Copilot MVP", page_icon="🧠", layout="wide")

st.title("🧠 IE Lab Copilot – MVP Prototype")
st.markdown("ระบบต้นแบบที่ช่วยจัดการแลบ Sand-Casting: **เก็บข้อมูล – วิเคราะห์ – สรุปรายงาน – รับ Feedback**")

# --- SECTION 1 : DATA CAPTURE FORM ---
st.header("1️⃣ Data Capture Form")

with st.form("lab_form"):
    team = st.text_input("ชื่อทีม")
    date = st.date_input("วันที่ทำการทดลอง", datetime.date.today())
    sand_moisture = st.slider("ความชื้นของทราย (%)", 2.0, 8.0, 5.0)
    melt_temp = st.slider("อุณหภูมิหลอม (°C)", 600, 900, 750)
    gating_ratio = st.selectbox("อัตราส่วน Gating : Riser", ["1:1", "2:1", "3:1", "Custom"])
    defect = st.multiselect("ประเภท Defect ที่พบ", ["Porosity", "Misrun", "Cold Shut", "Shrinkage", "None"])
    notes = st.text_area("บันทึกเพิ่มเติม")
    submitted = st.form_submit_button("📥 บันทึกข้อมูล")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Team", "Date", "Moisture", "Temp", "Ratio", "Defect", "Notes"])

if submitted:
    new_row = {
        "Team": team,
        "Date": date,
        "Moisture": sand_moisture,
        "Temp": melt_temp,
        "Ratio": gating_ratio,
        "Defect": ", ".join(defect) if defect else "None",
        "Notes": notes
    }
    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
    st.success("✅ ข้อมูลถูกบันทึกแล้ว")

# --- SECTION 2 : DASHBOARD ---
st.header("2️⃣ Dashboard & Summary")
if len(st.session_state.data) > 0:
    df = st.session_state.data
    st.dataframe(df)
    fig = px.scatter(df, x="Moisture", y="Temp", color="Defect",
                     title="Moisture vs Temperature by Defect Type",
                     hover_data=["Team", "Notes"])
    st.plotly_chart(fig, use_container_width=True)
    defect_counts = df["Defect"].value_counts()
    st.bar_chart(defect_counts)
else:
    st.info("กรอกข้อมูลการทดลองก่อนเพื่อดู Dashboard")

# --- SECTION 3 : AUTO REPORT ---
st.header("3️⃣ Auto-Generated Lab Report")
if len(st.session_state.data) > 0:
    latest = df.iloc[-1]
    report = f"""
### 🧩 Auto Summary for Team {latest['Team']}
- วันที่: {latest['Date']}
- ความชื้นของทราย: {latest['Moisture']}%
- อุณหภูมิหลอม: {latest['Temp']} °C
- อัตราส่วน Gating:Riser: {latest['Ratio']}
- Defect ที่พบ: {latest['Defect']}
- หมายเหตุ: {latest['Notes']}

**สรุปโดยระบบ:**  
ค่าความชื้น {latest['Moisture']}% และอุณหภูมิ {latest['Temp']}°C อยู่ในช่วงมาตรฐานของกระบวนการ sand-casting.  
หากพบ Defect ชนิด {latest['Defect']} อาจต้องปรับสัดส่วน Gating หรืออุณหภูมิหลอมในรอบต่อไป.
    """
    st.markdown(report)
else:
    st.info("ยังไม่มีข้อมูลให้สร้างรายงาน")

# --- SECTION 4 : FEEDBACK & CONFUSION MATRIX ---
st.header("4️⃣ Feedback & Evaluation")

with st.form("feedback_form"):
    satisfaction = st.slider("ระดับความพึงพอใจต่อระบบ (1 = แย่, 5 = ดีมาก)", 1, 5, 4)
    expect_match = st.radio("ระบบตรงกับความคาดหวังของคุณไหม?", ["ใช่", "ไม่ใช่"])
    result_good = st.radio("ผลลัพธ์ระบบตรงความต้องการจริงไหม?", ["ใช่", "ไม่ใช่"])
    fb_submit = st.form_submit_button("📤 ส่ง Feedback")

if "fb_data" not in st.session_state:
    st.session_state.fb_data = pd.DataFrame(columns=["Satisfaction", "Expect", "Result"])

if fb_submit:
    st.session_state.fb_data = pd.concat([
        st.session_state.fb_data,
        pd.DataFrame([{
            "Satisfaction": satisfaction,
            "Expect": expect_match,
            "Result": result_good
        }])
    ], ignore_index=True)
    st.success("ขอบคุณสำหรับ Feedback!")

if len(st.session_state.fb_data) > 0:
    fb = st.session_state.fb_data
    st.write("📋 ข้อมูล Feedback ล่าสุด:")
    st.dataframe(fb)

    # สร้าง Confusion Matrix
    matrix = pd.crosstab(fb["Expect"], fb["Result"],
                         rownames=["Expectation"], colnames=["Outcome"])
    st.write("### Confusion Matrix")
    st.dataframe(matrix)

    tp = len(fb[(fb["Expect"]=="ใช่") & (fb["Result"]=="ใช่")])
    tn = len(fb[(fb["Expect"]=="ไม่ใช่") & (fb["Result"]=="ไม่ใช่")])
    fp = len(fb[(fb["Expect"]=="ใช่") & (fb["Result"]=="ไม่ใช่")])
    fn = len(fb[(fb["Expect"]=="ไม่ใช่") & (fb["Result"]=="ใช่")])
    total = tp+tn+fp+fn
    acc = (tp+tn)/total if total>0 else 0
    prec = tp/(tp+fp) if (tp+fp)>0 else 0
    rec = tp/(tp+fn) if (tp+fn)>0 else 0

    st.markdown(f"""
    **📈 ผลการวิเคราะห์ Confusion Matrix**
    - True Positive (TP): {tp}
    - True Negative (TN): {tn}
    - False Positive (FP): {fp}
    - False Negative (FN): {fn}
    - Accuracy: **{acc:.2f}**
    - Precision: **{prec:.2f}**
    - Recall: **{rec:.2f}**
    """)
else:
    st.info("ยังไม่มี Feedback ให้แสดง Matrix")
