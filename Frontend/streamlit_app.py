import streamlit as st
import requests

st.set_page_config(page_title="AI Health Assistant", layout="centered")

# --- Settings ---
BACKEND_URL = st.sidebar.text_input(
    "Backend URL",
    value="http://127.0.0.1:8000",  # change if your backend runs elsewhere
    help="FastAPI server base URL",
)

st.title("🩺 AI Health Assistant (Symptom Checker)")
st.caption("Demo only — not medical advice. In an emergency, seek urgent care.")

with st.form("symptom_form"):
    age = st.number_input("Age", min_value=0, max_value=120, value=25, step=1)
    sex = st.selectbox("Sex (optional)", ["", "male", "female", "other"], index=0)
    symptoms = st.text_input(
        "Symptoms (comma-separated)",
        placeholder="fever, cough, headache"
    )
    duration_days = st.number_input(
        "Duration (days, optional)", min_value=0, max_value=365, value=3, step=1
    )
    notes = st.text_area(
        "Notes (optional)",
        placeholder="Any extra info e.g. chest tightness, fatigue"
    )
    submitted = st.form_submit_button("Assess")

# simple status check
if st.sidebar.button("Check backend /health"):
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=10)
        st.sidebar.success(f"Backend OK: {r.json()}")
    except Exception as e:
        st.sidebar.error(f"Can't reach backend: {e}")

if submitted:
    sym_list = [s.strip() for s in symptoms.split(",") if s.strip()]
    payload = {
        "age": int(age),
        "sex": sex if sex else None,
        "symptoms": sym_list,
        "duration_days": int(duration_days),
        "notes": notes,
    }

    try:
        r = requests.post(f"{BACKEND_URL}/api/assess", json=payload, timeout=30)
        if r.status_code != 200:
            st.error(f"Backend error {r.status_code}: {r.text}")
        else:
            data = r.json()

            st.subheader("Triage")
            st.markdown(f"**Level:** `{data.get('triage_level','?')}`")
            reasons = data.get("triage_reason", [])
            if reasons:
                st.markdown("**Reasons:**")
                for reason in reasons:
                    st.markdown(f"- {reason}")

            st.subheader("Likely Conditions (heuristic ranking)")
            conds = data.get("likely_conditions", [])
            if conds:
                for item in conds:
                    st.markdown(
                        f"- **{item['condition']}** — score: `{item['score']}`"
                        + (f", likelihood: `{item.get('likelihood')}`" if 'likelihood' in item else "")
                    )
            else:
                st.info("No clear match. Consider consulting a clinician.")

            st.subheader("Advice")
            for a in data.get("advice", []):
                st.markdown(f"- {a}")

    except Exception as e:
        st.error(f"Request failed. Is the backend running at {BACKEND_URL}? \n\n{e}")
