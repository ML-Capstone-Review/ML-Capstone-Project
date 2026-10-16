"""Streamlit presentation for AirlinePulse."""
import pandas as pd
import streamlit as st
from .prediction import predict_feedback
from .validation import validate_feedback
from .schema import CATEGORICAL_COLUMNS, LABELS, NUMERIC_COLUMNS, RATING_COLUMNS


def apply_theme():
    st.set_page_config(page_title="AirlinePulse | Passenger feedback", page_icon="✈️", layout="wide")
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      :root { --navy:#10243c; --blue:#1265a8; --sky:#e9f4fb; --ink:#23354a; }
      html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
      .stApp { background:linear-gradient(180deg,#f4f9fc 0%,#fff 340px); }
      h1,h2,h3 { font-family:'Manrope',sans-serif; color:var(--navy); }
      .hero { padding:2.1rem 2.3rem; border-radius:22px; color:#fff; background:linear-gradient(115deg,#10243c 0%,#155c8d 67%,#4e9ac2 100%); margin:.4rem 0 1.5rem; }
      .hero h1 { color:#fff; margin:0; font-size:2.5rem; letter-spacing:-.04em; }
      .hero p { color:#e7f3fb; margin:.45rem 0 0; font-size:1.05rem; }
      .eyebrow { color:#a9dbf4; text-transform:uppercase; letter-spacing:.14em; font-size:.76rem; font-weight:700; margin-bottom:.65rem; }
      .section-card { padding:1.05rem 1.2rem .3rem; border:1px solid #dce8ef; border-radius:16px; background:#fff; margin:.7rem 0 1rem; }
      .note { font-size:.9rem; color:#546b7d; }
      div.stButton > button[kind="primaryFormSubmit"], div.stFormSubmitButton > button { background:#1265a8; color:#fff; border:0; border-radius:10px; min-height:3rem; font-weight:700; }
      div.stButton > button { border-radius:10px; }
      [data-testid="stMetric"] { background:#fff; border:1px solid #dce8ef; padding:1rem; border-radius:14px; }
      .stTabs [data-baseweb="tab-list"] { gap:1.5rem; }
      footer { visibility:hidden; }
    </style>
    """, unsafe_allow_html=True)


def _rating_widget(column, default):
    return st.slider(LABELS[column], min_value=0, max_value=5, value=int(default), step=1,
                     help="Service ratings in the project dataset use a 0–5 scale.", key=f"field_{column}")


def render_feedback(data, model, bounds, numeric, categorical):
    st.markdown('<div class="hero"><div class="eyebrow">Your journey, heard</div><h1>Tell us about your flight</h1><p>A few details help us understand the experience you had.</p></div>', unsafe_allow_html=True)
    st.markdown('<p class="note">Example values are prefilled to make the form easy to explore. Edit them to reflect your recent trip. This capstone demo does not save responses to a database or send them to an airline.</p>', unsafe_allow_html=True)
    defaults = {}
    for col in CATEGORICAL_COLUMNS:
        defaults[col] = str(data[col].mode(dropna=True).iloc[0])
    for col in NUMERIC_COLUMNS:
        if col in RATING_COLUMNS:
            defaults[col] = int(data[col].mode(dropna=True).iloc[0])
        else:
            defaults[col] = int(round(float(data[col].median())))
    for col in CATEGORICAL_COLUMNS:
        key=f"field_{col}"
        if key not in st.session_state: st.session_state[key]=defaults[col]
    for col in NUMERIC_COLUMNS:
        key=f"field_{col}"
        if key not in st.session_state: st.session_state[key]=defaults[col]

    def reset_values():
        for col, value in defaults.items(): st.session_state[f"field_{col}"]=value
        st.session_state.pop("feedback_done", None)
        st.session_state["passenger_name"] = ""
    st.button("↺ Reset to example values", on_click=reset_values, help="Restore the editable example values.")

    with st.form("passenger_feedback", clear_on_submit=False):
        passenger_name = st.text_input("Passenger name", placeholder="Enter your name", key="passenger_name")
        st.markdown('<div class="section-card"><h3>About your trip</h3></div>', unsafe_allow_html=True)
        a,b,c = st.columns(3)
        with a: values={"Gender": st.selectbox(LABELS["Gender"], sorted(data["Gender"].dropna().unique().tolist()), key="field_Gender")}
        with b: values["Customer Type"] = st.selectbox(LABELS["Customer Type"], data["Customer Type"].dropna().unique().tolist(), key="field_Customer Type")
        with c: values["Type of Travel"] = st.selectbox(LABELS["Type of Travel"], data["Type of Travel"].dropna().unique().tolist(), key="field_Type of Travel")
        with a: values["Class"] = st.selectbox(LABELS["Class"], data["Class"].dropna().unique().tolist(), key="field_Class")
        with b: values["Age"] = st.number_input(LABELS["Age"], min_value=int(data["Age"].min()), max_value=int(data["Age"].max()), step=1, key="field_Age")
        with c: values["Flight Distance"] = st.number_input(LABELS["Flight Distance"], min_value=int(data["Flight Distance"].min()), max_value=int(data["Flight Distance"].max()), step=1, key="field_Flight Distance")

        st.markdown('<div class="section-card"><h3>Travel timing</h3></div>', unsafe_allow_html=True)
        a,b=st.columns(2)
        for i,col in enumerate(["Departure Delay","Arrival Delay"]):
            with (a if i==0 else b):
                values[col]=st.number_input(LABELS[col], min_value=int(data[col].min()), max_value=int(data[col].max()), step=1, key=f"field_{col}")
        st.markdown('<div class="section-card"><h3>Onboard experience</h3><p class="note">Rate each area from 0 (lowest) to 5 (highest), following the project dataset scale.</p></div>', unsafe_allow_html=True)
        for start in range(0,len(RATING_COLUMNS),3):
            cols=st.columns(3)
            for box,col in zip(cols,RATING_COLUMNS[start:start+3]):
                with box: values[col]=_rating_widget(col,defaults[col])
        submitted=st.form_submit_button("Submit feedback", type="primary", use_container_width=True)
    if submitted:
        passenger_name = passenger_name.strip()
        errors=validate_feedback(values,data)
        if not passenger_name:
            st.error("Please enter your name before submitting.")
        elif errors:
            for message in errors: st.error(message)
        else:
            try:
                _internal_result=predict_feedback(model,values,bounds,numeric,categorical)
                st.session_state["feedback_done"]=True
                submissions = st.session_state.setdefault("passenger_submissions", {})
                submissions[passenger_name.casefold()] = {
                    "name": passenger_name,
                    "prediction": _internal_result,
                }
            except Exception as exc:
                st.error(f"We could not process this form. Please review your entries and try again. ({type(exc).__name__})")
    if st.session_state.get("feedback_done"):
        st.success("Thank you for sharing your journey with us. Your feedback has been reviewed for this demo.")
        st.caption("Your response was processed for this demo only. It was not saved to a database or sent to an airline.")


def render_evaluator(artifacts):
    st.markdown('<div class="hero"><div class="eyebrow">Project evaluator view</div><h1>Model evaluation</h1><p>Held-out results from the classification notebook workflow.</p></div>', unsafe_allow_html=True)
    st.info("Metrics below are computed on the notebook’s fixed 20% stratified test split.")
    st.subheader("Passenger prediction")
    submissions = st.session_state.get("passenger_submissions", {})
    if not submissions:
        st.caption("Submit passenger feedback with a name to see its prediction here.")
    else:
        selected_key = st.selectbox(
            "Select passenger",
            options=sorted(submissions),
            format_func=lambda key: submissions[key]["name"],
        )
        prediction = submissions[selected_key]["prediction"]
        if prediction == 1:
            st.success(f"{submissions[selected_key]['name']}: predicted satisfied.")
        else:
            st.warning(f"{submissions[selected_key]['name']}: predicted neutral or dissatisfied.")
    st.subheader("Selected classifier")
    st.write("**Random Forest Classifier** — the notebook’s top-ranked model by weighted F1-score, selected from its 10-model comparison.")
    st.code("RandomForestClassifier(n_estimators=200, min_samples_split=5, max_depth=None, random_state=42, n_jobs=1)", language="python")
    st.caption(f"Training rows: {artifacts['train_rows']:,} · Test rows: {artifacts['test_rows']:,} · Evaluation is recomputed using the notebook split and settings.")
    metric_cols=st.columns(5)
    for col,(label,value) in zip(metric_cols,artifacts["metrics"].items()): col.metric(label,f"{value:.4f}")
    st.subheader("Top feature importances")
    table=artifacts["feature_importance"].copy()
    st.dataframe(table,hide_index=True,use_container_width=True)
    st.caption("Importance values show which inputs the model relied on most; they do not establish cause and effect.")
    st.subheader("Notebook's 10-model comparison")
    st.caption("These rounded values are transcribed from the saved comparison output in notebook cell F1. The current-runtime Random Forest metrics above are recomputed from the notebook code; saved notebook outputs can differ slightly across library versions.")
    comparison_path=__import__("pathlib").Path(__file__).with_name("notebook_model_comparison.csv")
    comparison=pd.read_csv(comparison_path)
    st.dataframe(comparison.style.format({c:"{:.4f}" for c in comparison.columns if c not in {"Rank","Model"}}),hide_index=True,use_container_width=True)
