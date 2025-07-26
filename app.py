import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.graph_objects as go
import json
import os
import io
from datetime import datetime

st.set_page_config(
    page_title="DecisionMate",
    layout="centered",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# === Custom Logo + Light/Dark Theme Toggle ===
with st.sidebar:
    theme_mode = st.radio("🌓 Theme Mode", ["Light", "Dark"])
st.markdown(f"""
    <style>
        .reportview-container {{
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
            color: {'#000' if theme_mode == 'Light' else '#fff'};
        }}
        .sidebar .sidebar-content {{
            background-color: #f1f3f4;
        }}
    </style>
""", unsafe_allow_html=True)
st.image("nijat_logo.png", width=200)

st.markdown("""
    <style>
        .reportview-container {
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
        }
        .sidebar .sidebar-content {
            background-color: #f1f3f4;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 DecisionMate – Smart Decision Making")

# === Language and Translation Setup ===
st.sidebar.subheader("🌐 Language")
language = st.sidebar.radio("Choose Language", ["English", "Azerbaijani"])

TRANSLATIONS = {
    "en": {
        "enter_name": "Enter your name",
        "login_warning": "Please enter your name to view or save decisions.",
        "language": "Language",
        "save_success": "✅ Decision saved!",
        "module_personal": "🧠 Personal Decision Making",
        "module_business": "🏢 Business Decision Support – CAPEX / OPEX / NPV",
        "module_saved": "📂 Saved Decisions for ",
        "option_a_label": "Option A:",
        "option_a_default": "Stay in current job",
        "option_b_label": "Option B:",
        "option_b_default": "Accept new job offer",
        "reflection_hard": "Why is this decision hard for you?",
        "reflection_regret": "What would you regret not doing?",
        "reflection_gut": "What does your gut feeling tell you?"
    },
    "az": {
        "enter_name": "Adınızı daxil edin",
        "login_warning": "Qərarları görmək və ya saxlamaq üçün adınızı daxil edin.",
        "language": "Dil",
        "save_success": "✅ Qərar yadda saxlanıldı!",
        "module_personal": "🧠 Şəxsi Qərar Qəbulu",
        "module_business": "🏢 Biznes Qərar Dəstəyi – CAPEX / OPEX / NPV",
        "module_saved": "📂 Saxlanılan Qərarlar – ",
        "option_a_label": "Variant A:",
        "option_a_default": "Cari işdə qalmaq",
        "option_b_label": "Variant B:",
        "option_b_default": "Yeni iş təklifini qəbul etmək",
        "reflection_hard": "Bu qərar niyə çətindir?",
        "reflection_regret": "Nə etmədiyiniz üçün peşman ola bilərsiniz?",
        "reflection_gut": "Daxili hissiniz sizə nə deyir?"
    }
}

def t(key):
    return TRANSLATIONS["az" if language == "Azerbaijani" else "en"].get(key, key)

# === User Login ===


username = st.sidebar.text_input(t("enter_name"))
if not username:
    st.warning(t("login_warning"))
    st.stop()


# === History Helpers ===
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def export_personal_decision_to_excel(option_a, option_b, scores, swot, reflection):
    data = {
        "Option A": [option_a],
        "Option B": [option_b],
        "Scores A": [scores["Option A"]],
        "Scores B": [scores["Option B"]],
        "SWOT": [swot],
        "Reflection": [reflection]
    }
    df_export = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"personal_decision_{username}_{timestamp}.xlsx"
    st.download_button(
        label="📥 Download Decision as Excel",
        data=excel_buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def export_personal_decision_to_pdf(option_a, option_b, scores, swot, reflection):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Personal Decision Summary", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Option A: {option_a}", ln=True)
    pdf.cell(200, 10, txt=f"Option B: {option_b}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="SWOT Analysis:", ln=True)
    for key, value in swot.items():
        pdf.multi_cell(0, 10, f"{key}: {value}")
    pdf.ln(5)
    pdf.cell(200, 10, txt="Priority Scores:", ln=True)
    for i, score in enumerate(scores["Option A"]):
        pdf.cell(200, 10, txt=f"Criterion {i+1} – A: {score}, B: {scores['Option B'][i]}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Reflections:", ln=True)
    for key, value in reflection.items():
        pdf.multi_cell(0, 10, f"{key}: {value}")
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"personal_decision_{username}_{timestamp}.pdf"
    st.download_button(
        label="📄 Download Summary as PDF",
        data=pdf_output,
        file_name=filename,
        mime="application/pdf"
    )
    data = {
        "Option A": [option_a],
        "Option B": [option_b],
        "Scores A": [scores["Option A"]],
        "Scores B": [scores["Option B"]],
        "SWOT": [swot],
        "Reflection": [reflection]
    }
    df_export = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"personal_decision_{username}_{timestamp}.xlsx"
    st.download_button(
        label="📥 Download Decision as Excel",
        data=excel_buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def export_business_decision_to_pdf(capex, opex, years, discount_rate, cash_flows, npv, irr):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Business Decision Summary", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"CAPEX: {capex}", ln=True)
    pdf.cell(200, 10, txt=f"OPEX: {opex}", ln=True)
    pdf.cell(200, 10, txt=f"Years: {years}", ln=True)
    pdf.cell(200, 10, txt=f"Discount Rate: {discount_rate:.2%}", ln=True)
    pdf.cell(200, 10, txt=f"NPV: {npv:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"IRR: {irr:.2%}" if irr else "IRR: Not computable", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Cash Flows:", ln=True)
    for i, cf in enumerate(cash_flows, 1):
        pdf.cell(200, 10, txt=f"Year {i}: {cf:.2f}", ln=True)
    pdf_output = pdf.output(dest='S').encode('latin1')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"business_decision_{username}_{timestamp}.pdf"
    st.download_button(
        label="📄 Download Summary as PDF",
        data=pdf_output,
        file_name=filename,
        mime="application/pdf"
    )

if "history" not in st.session_state:
    st.session_state["history"] = load_history()

if username not in st.session_state["history"]:
    st.session_state["history"][username] = []

# === Sidebar Menu ===
menu = st.sidebar.radio("Choose Module", ["Life & Career Decisions", "Business Decisions (CAPEX/NPV)", "View Saved Decisions", "Settings"])

# === Module 1: Life & Career Decisions ===
if menu == "Life & Career Decisions":
    st.header(t("module_personal"))

    option_a = st.text_input(t("option_a_label"), t("option_a_default"))
    option_b = st.text_input(t("option_b_label"), t("option_b_default"))

    if option_a.strip() and option_b.strip():
        st.subheader("SWOT" if language == "English" else "SWOT Təhlili")
        swot = {}
        for key in ["Strengths", "Weaknesses", "Opportunities", "Threats"]:
            swot[key] = st.text_area(f"{key} for {option_a} vs {option_b}", "")

        st.subheader("Priority Scoring" if language == "English" else "Əsas meyarların qiymətləndirilməsi")
        criteria = ["Time impact", "Financial gain", "Stress level", "Flexibility"]
        scores = {"Option A": [], "Option B": []}

        for crit in criteria:
            col1, col2 = st.columns(2)
            with col1:
                scores["Option A"].append(st.slider(f"{crit} – {option_a}", 1, 10, 5))
            with col2:
                scores["Option B"].append(st.slider(f"{crit} – {option_b}", 1, 10, 5))

        st.subheader("Radar Chart" if language == "English" else "Radar Diaqramı")
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=scores["Option A"], theta=criteria, fill='toself', name=option_a))
        fig.add_trace(go.Scatterpolar(r=scores["Option B"], theta=criteria, fill='toself', name=option_b))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=True)
        st.plotly_chart(fig)

        reflection = {
            "Why is this decision hard?": st.text_area(t("reflection_hard"), ""),
            "What would you regret?": st.text_area(t("reflection_regret"), ""),
            "Gut feeling": st.text_area(t("reflection_gut"), "")
        }

        if st.button("💾 Save This Decision"):
            summary = {
                "Module": "Personal",
                "Option A": option_a,
                "Option B": option_b,
                "Scores A": scores["Option A"],
                "Scores B": scores["Option B"],
                "SWOT": swot,
                "Reflection": reflection
            }
            st.session_state["history"][username].append(summary)
            save_history(st.session_state["history"])
            st.success(t("save_success"))

            export_personal_decision_to_excel(option_a, option_b, scores, swot, reflection)
    else:
        st.info("Please enter both options to begin analysis." if language == "English" else "Zəhmət olmasa, analizə başlamaq üçün hər iki variantı daxil edin.")

# === Module 2: Business Decisions ===
elif menu == "View Saved Decisions":
    st.header("📂 Saved Decisions for " + username)
    user_history = st.session_state["history"].get(username, [])

    if not user_history:
        st.info("You don't have any saved decisions yet.")
    else:
        for i, record in enumerate(user_history[::-1], 1):
            st.subheader(f"Decision {i} – {record['Module']}")
            if record["Module"] == "Personal":
                st.write(f"**Option A:** {record['Option A']}")
                st.write(f"**Option B:** {record['Option B']}")
                st.write("**Scores A:**", record["Scores A"])
                st.write("**Scores B:**", record["Scores B"])
                st.write("**SWOT:**", record["SWOT"])
                st.write("**Reflection:**", record["Reflection"])
            elif record["Module"] == "Business":
                st.write(f"**CAPEX:** {record['CAPEX']}")
                st.write(f"**OPEX:** {record['OPEX']}")
                st.write(f"**Years:** {record['Years']}")
                st.write(f"**Discount Rate:** {record['Discount Rate']:.2%}")
                st.write("**Cash Flows:**", record["Cash Flows"])
                st.write(f"**NPV:** {record['NPV']:.2f}")
                st.write(f"**IRR:** {record['IRR']:.2%}" if record["IRR"] else "**IRR:** Not computable")
elif menu == "Business Decisions (CAPEX/NPV)":
    st.header(t("module_business"))

    st.subheader("Enter Investment Parameters")
    capex = st.number_input("CAPEX (Initial Investment)", value=100000.0)
    opex = st.number_input("Annual OPEX", value=20000.0)
    years = st.slider("Project Duration (Years)", 1, 20, 5)
    discount_rate = st.slider("Discount Rate (%)", 0.0, 20.0, 10.0) / 100

    st.subheader("Cash Flow Setup")
    cash_inflows = []
    for i in range(1, years + 1):
        cash = st.number_input(f"Year {i} Inflow", value=40000.0, key=f"inflow_{i}")
        cash_inflows.append(cash - opex)

    npv = -capex + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_inflows, 1))
    irr = npf.irr([-capex] + cash_inflows)

    st.markdown(f"### 📈 NPV: {'{:.2f}'.format(npv)}")
    st.markdown(f"### 📉 IRR: {'{:.2%}'.format(irr) if irr else 'Not computable'}")

    st.subheader("Tornado Chart (Simple Sensitivity)")
    delta = 0.1
    params = ["CAPEX", "OPEX", "Cash Flow", "Discount Rate"]
    impacts = []

    variations = {
        "CAPEX": [-capex * (1 + delta), -capex * (1 - delta)],
        "OPEX": [opex * (1 + delta), opex * (1 - delta)],
        "Cash Flow": [cf * (1 + delta) for cf in cash_inflows],
        "Discount Rate": [discount_rate * (1 + delta), discount_rate * (1 - delta)]
    }

    for param in params:
        if param == "CAPEX":
            npv_high = variations[param][1] + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_inflows, 1))
            npv_low = variations[param][0] + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_inflows, 1))
        elif param == "OPEX":
            inflows_low = [cf + opex - variations[param][0] for cf in cash_inflows]
            inflows_high = [cf + opex - variations[param][1] for cf in cash_inflows]
            npv_high = -capex + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(inflows_high, 1))
            npv_low = -capex + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(inflows_low, 1))
        elif param == "Cash Flow":
            npv_high = -capex + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(variations[param], 1))
            npv_low = -capex + sum((cf * (1 - 2 * delta)) / (1 + discount_rate) ** i for i, cf in enumerate(variations[param], 1))
        elif param == "Discount Rate":
            npv_high = -capex + sum(cf / (1 + variations[param][1]) ** i for i, cf in enumerate(cash_inflows, 1))
            npv_low = -capex + sum(cf / (1 + variations[param][0]) ** i for i, cf in enumerate(cash_inflows, 1))
        impacts.append(npv_high - npv_low)

    tornado_fig = go.Figure(go.Bar(x=impacts, y=params, orientation='h'))
    tornado_fig.update_layout(title="Tornado Chart: Parameter Impact on NPV", xaxis_title="NPV Impact")
    st.plotly_chart(tornado_fig)

    if st.button("💾 Save Business Case"):
        export_business_decision_to_pdf(capex, opex, years, discount_rate, cash_inflows, npv, irr)
        summary = {
            "Module": "Business",
            "CAPEX": capex,
            "OPEX": opex,
            "Years": years,
            "Discount Rate": discount_rate,
            "Cash Flows": cash_inflows,
            "NPV": npv,
            "IRR": irr
        }
        st.session_state["history"][username].append(summary)
        save_history(st.session_state["history"])
        st.success("✅ Business decision saved!")

        df = pd.DataFrame({"Year": list(range(1, years + 1)), "Cash Flow": cash_inflows})
        df.loc[-1] = ["Initial", -capex]
        df.index = df.index + 1
        df = df.sort_index()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Cash Flow CSV", data=csv, file_name="business_decision.csv", mime="text/csv")
