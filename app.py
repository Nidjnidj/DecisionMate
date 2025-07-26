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

st.title("📊 DecisionMate - Smart Decision Making")

# === Language and Translation Setup ===
st.sidebar.subheader("🌐 Language")
language = st.sidebar.radio("Choose Language", ["English", "Azerbaijani"], key="language_radio")

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

# === Safe IRR Calculation ===
def calculate_irr(cashflows):
    try:
        irr = npf.irr(cashflows)
        if irr is None or np.isnan(irr):
            return None
        return irr
    except Exception:
        return None

# === Life & Career Decision Module ===
menu = st.sidebar.radio("Choose Module", ["Life & Career Decisions", "Business Decisions (CAPEX/NPV)", "View Saved Decisions", "Settings"], key="module_selector")

if menu == "Life & Career Decisions":
    st.header(t("module_personal"))

    option_a = st.text_input(t("option_a_label"), t("option_a_default"))
    option_b = st.text_input(t("option_b_label"), t("option_b_default"))

    if option_a.strip() and option_b.strip():
        st.subheader("SWOT" if language == "English" else "SWOT Təhlili")
        swot = {}
        for key in ["Strengths", "Weaknesses", "Opportunities", "Threats"]:
            swot[key] = st.text_area(f"{key} ({option_a} vs {option_b})", "")

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
            t("reflection_hard"): st.text_area(t("reflection_hard"), ""),
            t("reflection_regret"): st.text_area(t("reflection_regret"), ""),
            t("reflection_gut"): st.text_area(t("reflection_gut"), "")
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
            history = load_history()
            history.setdefault(username, []).append(summary)
            save_history(history)
            st.success(t("save_success"))

            # Export Excel
            df_export = pd.DataFrame({
                "Option A": [option_a],
                "Option B": [option_b],
                "Scores A": [scores["Option A"]],
                "Scores B": [scores["Option B"]],
                "SWOT": [swot],
                "Reflection": [reflection]
            })
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df_export.to_excel(writer, index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"personal_decision_{username}_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Export PDF
            from fpdf import FPDF
            pdf = FPDF()
            pdf.set_font("Arial", size=12)
            pdf.add_page()
            pdf.cell(200, 10, txt="Personal Decision Summary", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Option A: {option_a}", ln=True)
            pdf.cell(200, 10, txt=f"Option B: {option_b}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt="SWOT Analysis:", ln=True)
            for k, v in swot.items():
                pdf.multi_cell(0, 10, f"{k}: {v}")
            pdf.ln(5)
            pdf.cell(200, 10, txt="Priority Scores:", ln=True)
            for i, score in enumerate(scores["Option A"]):
                pdf.cell(200, 10, txt=f"Criterion {i+1} - A: {score}, B: {scores['Option B'][i]}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt="Reflections:", ln=True)
            for k, v in reflection.items():
                pdf.multi_cell(0, 10, f"{k}: {v}")
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=f"Exported by: {username}", ln=True)
            pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf_output = pdf.output(dest='S').encode('latin1', 'replace')

            import zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                zipf.writestr(f"personal_decision_{username}_{timestamp}.pdf", pdf_output)
                zipf.writestr(f"personal_decision_{username}_{timestamp}.xlsx", excel_buffer.getvalue())

            st.download_button(
                label="📦 Download All (PDF + Excel)",
                data=zip_buffer.getvalue(),
                file_name=f"personal_export_{timestamp}.zip",
                mime="application/zip"
            )

                

# Business Decision Calculator
elif menu == "Business Decisions (CAPEX/NPV)":
    st.header(t("module_business"))

    st.subheader("Sərmayə Parametrlərini Daxil Edin" if language == "Azerbaijani" else "Enter Investment Parameters")
    capex = st.number_input("Başlanğıc Sərmayə (CAPEX)" if language == "Azerbaijani" else "CAPEX (Initial Investment)", value=100000.0)
    opex = st.number_input("İllik Əməliyyat Xərcləri (OPEX)" if language == "Azerbaijani" else "Annual OPEX", value=20000.0)
    years = st.slider("Layihənin Müddəti (İllər)" if language == "Azerbaijani" else "Project Duration (Years)", 1, 20, 5)
    discount_rate = st.slider("Endirim Faizi \(\%\)" if language == "Azerbaijani" else "Discount Rate (%)", 0.0, 20.0, 10.0) / 100 / 100

    st.subheader("Nağd Pul Axınının Quraşdırılması" if language == "Azerbaijani" else "Cash Flow Setup")
    cash_inflows = []
    for i in range(1, years + 1):
        label = f"{i}-ci İlin Gəliri" if language == "Azerbaijani" else f"Year {i} Inflow"
        cash = st.number_input(label, value=40000.0, key=f"inflow_{i}")
        cash_inflows.append(cash - opex)

    npv = -capex + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_inflows, 1))
    irr = calculate_irr([-capex] + cash_inflows)

    st.markdown(f"### 📈 NPV: {'{:.2f}'.format(npv)}")
    st.markdown(f"### 📉 IRR: {'{:.2%}'.format(irr) if irr is not None else 'Not computable'}")

    # Extra Metrics
    cumulative_cash_flow = np.cumsum([-capex] + cash_inflows)
    payback_period = next((i for i, val in enumerate(cumulative_cash_flow) if val >= 0), None)
    roi = (sum(cash_inflows) - capex) / capex if capex != 0 else None

    if payback_period is not None:
        st.markdown(f"### ⏳ Payback Period: {payback_period} years")
    else:
        st.markdown("### ⏳ Payback Period: Not recovered within project duration")

    if roi is not None:
        st.markdown(f"### 💰 ROI: {'{:.2%}'.format(roi)}")
    else:
        st.markdown("### 💰 ROI: Not computable")

    # Cash Flow Chart
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.bar(["Initial"] + [f"Year {i+1}" for i in range(years)], [-capex] + cash_inflows)
    ax.set_title("Annual Cash Flow")
    ax.set_ylabel("Amount")
    st.pyplot(fig)

    # Tornado Diagram
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

    # Export Buttons
    from fpdf import FPDF
    if st.button("💾 Save Business Case"):
        pdf = FPDF()
        pdf.set_font("Arial", size=12)
        pdf.add_page()
        pdf.cell(200, 10, txt="Business Decision Summary", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"CAPEX: {capex}", ln=True)
        pdf.cell(200, 10, txt=f"OPEX: {opex}", ln=True)
        pdf.cell(200, 10, txt=f"Years: {years}", ln=True)
        pdf.cell(200, 10, txt=f"Discount Rate: {discount_rate:.2%}", ln=True)
        pdf.cell(200, 10, txt=f"NPV: {npv:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"IRR: {'{:.2%}'.format(irr) if irr else 'Not computable'}", ln=True)
        if payback_period is not None:
            pdf.cell(200, 10, txt=f"Payback Period: {payback_period} years", ln=True)
        if roi is not None:
            pdf.cell(200, 10, txt=f"ROI: {'{:.2%}'.format(roi)}", ln=True)
        pdf.ln(10)
        pdf.cell(200, 10, txt="Cash Flows:", ln=True)
        for i, cf in enumerate([-capex] + cash_inflows):
            label = "Initial" if i == 0 else f"Year {i}"
            pdf.cell(200, 10, txt=f"{label}: {cf:.2f}", ln=True)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"Exported by: {username}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf_output = pdf.output(dest='S').encode('latin1', 'replace')

        df = pd.DataFrame({"Year": ["Initial"] + [f"Year {i+1}" for i in range(years)], "Cash Flow": [-capex] + cash_inflows})
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

        import zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zipf.writestr(f"business_decision_{username}_{timestamp}.pdf", pdf_output)
            zipf.writestr(f"business_cashflow_{username}_{timestamp}.xlsx", excel_buffer.getvalue())

        st.download_button(
            label="📦 Download All (PDF + Excel)",
            data=zip_buffer.getvalue(),
            file_name=f"business_export_{timestamp}.zip",
            mime="application/zip"
        )

        # Removed redundant second Excel export block
