"""MaaGuide AI • Group 13 • a fictional, session-only product walkthrough."""
import json
import os
from urllib.error import HTTPError
import urllib.request
from urllib.parse import quote

import streamlit as st

st.set_page_config(page_title="MaaGuide · Meera’s lunch break", page_icon="🌿")
st.markdown("""<style>
.stApp {background:#fcf9f4;color:#193e35}
[data-testid="stMainBlockContainer"] {max-width:49rem;padding-top:2.5rem}
h1,h2,h3 {color:#124e43!important}
header[data-testid="stHeader"] {background:transparent}
.scenario {background:#144c43;color:#fff;padding:1.45rem 1.7rem;border-radius:18px}
.scenario small {color:#cce8db;letter-spacing:.08em}
.scenario p {font:1.6rem/1.35 Georgia,serif;margin:.75rem 0 .25rem}
</style>""", unsafe_allow_html=True)

NHS = "https://www.nhs.uk/pregnancy/common-symptoms/indigestion-and-heartburn/"
steps = ["Meet Meera", "Choose a plan", "Reply to Amma", "Check in"]
plans = {
    "At my desk now": (
        "Sit upright after lunch", "Before the next call, settle into an upright sitting position.",
        "I’ll sit upright after lunch today.", "ఈ రోజు భోజనం తర్వాత నిటారుగా కూర్చుంటాను."),
    "At my next lunch": (
        "Try a smaller lunch", "Plan smaller, more frequent meals and see how they feel.",
        "I’ll try smaller meals more often.", "కొద్దికొద్దిగా ఎక్కువసార్లు తినడానికి ప్రయత్నిస్తాను."),
}
question = "Amma suggested ajwain water for heartburn. Is it suitable for me during pregnancy?"
state = st.session_state
state.setdefault("step", 0)

def advance():
    state.step += 1

def restart():
    for key in list(state):
        del state[key]

def setting(name, default=""):
    if os.getenv(name):
        return os.environ[name]
    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default


def ask_gemini(prompt):
    key = setting("GEMINI_API_KEY")
    if not key:
        raise ValueError("Add GEMINI_API_KEY in Streamlit Secrets.")
    model = setting("GEMINI_MODEL", "gemini-flash-latest").removeprefix("models/")
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + quote(model, safe="") + ":generateContent"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    request = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.load(response)
        candidate = result["candidates"][0]
        parts = candidate["content"]["parts"]
        answer = " ".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if candidate.get("finishReason") != "STOP" or not answer:
            raise KeyError("Incomplete response")
        return answer
    except HTTPError as error:
        hints = {400: "Check the API key and model settings.", 403: "Check API access for this key.",
                 404: "Set GEMINI_MODEL to a generateContent model available to your account.",
                 429: "Quota reached. Check the project quota or try again later.",
                 503: "Gemini is busy. Try again shortly."}
        raise ValueError(hints.get(error.code, "Gemini could not complete this request.")) from None
    except (OSError, LookupError, TypeError, AttributeError, ValueError):
        raise ValueError("No complete response from Gemini. Try again.") from None


def suggest_opener():
    try:
        choice = ask_gemini("A fictional mother packed ajwain and checked in on her daughter. "
                            "Select an opener: A thanks her for packing it; B thanks her for "
                            "checking in. Return only A or B.")
        if choice not in ("A", "B"):
            raise ValueError("Unexpected model choice")
        state.opener = choice
        state.ai_status = "Gemini selected the opening line."
    except (OSError, KeyError, ValueError, IndexError):
        state.ai_status = "Using the built-in opening line. Gemini is unavailable or unconfigured."

st.caption("MaaGuide AI   /   DPM Phase 2 · Group 13")
st.markdown("""<div class="scenario"><small>MEERA’S WORKDAY · HYDERABAD</small>
<p>A lunch break, a family remedy,<br>and a call in three minutes.</p></div>""", unsafe_allow_html=True)
st.progress((state.step + 1) / 4, text=f"Step {state.step + 1} of 4 · {steps[state.step]}")
if state.step == 0:
    st.header("Meet Meera")
    st.write("Meera is a business analyst, 22 weeks pregnant. At 1:57 pm, back at her desk after lunch, she feels mild heartburn. Her mother sends a message.")
    st.info("“I packed some ajwain for you, amma. Did you try it in warm water?”")
    st.write("Meera wants something she can do between calls and a kind way to tell Amma she’ll check before trying the remedy.")
    st.button("Help Meera decide", type="primary", on_click=advance)
    st.caption("Fictional classroom scenario. All choices refer to Meera.")
elif state.step == 1:
    st.header("What can Meera do today?")
    st.write("Ajwain is part of her family’s kitchen tradition. Meera will ask her maternity team before using it as a remedy.")
    timing = st.radio("When would she like to act?", list(plans))
    title, detail, _, _ = plans[timing]
    with st.container(border=True):
        st.subheader(title)
        st.write(detail)
        st.markdown(f"[Read the NHS guidance on heartburn in pregnancy]({NHS})")
    recommendations = state.setdefault("recommendations", {})
    if st.button("Get Gemini’s recommendation", disabled=timing in recommendations):
        prompt = (
            "Write a short educational recommendation addressed to Meera, a fictional analyst "
            "22 weeks pregnant with mild heartburn just after lunch, three minutes before a call. "
            f"Her timing choice is {timing}. Her plan is: {detail} "
            "Use only these NHS guidance notes: sitting upright during and just after meals can "
            "reduce pressure on the stomach; smaller, more frequent meals may ease heartburn. "
            "If lifestyle changes do not help, speak with a midwife or doctor. "
            "Explain the selected action and why it fits her timing in two or three sentences. "
            "Her mother suggested ajwain water. Acknowledge her mother's care and suggest "
            "asking her maternity team before trying it. Do not add remedies, doses, medicines, "
            "diagnoses, claims of safety or other clinical advice. Return plain text."
        )
        with st.spinner("Preparing Meera’s recommendation…"):
            try:
                recommendations[timing] = ask_gemini(prompt)
            except ValueError as error:
                st.warning(f"Gemini recommendation unavailable. {error} The built-in plan is shown above.")
    if timing in recommendations:
        st.subheader("Gemini’s recommendation for Meera")
        st.text(recommendations[timing])
        st.caption("AI-generated educational guidance for this fictional case. No clinician has reviewed this response.")
    st.caption("If symptoms persist despite lifestyle changes, she should speak with her midwife or doctor.")
    if st.button("Choose this plan", type="primary"):
        state.timing = timing
        advance()
        st.rerun()
elif state.step == 2:
    st.header("A reply for Amma")
    st.write("Meera can acknowledge her mother’s care, explain her plan, and leave the remedy question open.")
    language = st.radio("Family reply language", ["English", "Telugu"], horizontal=True)
    st.button("Suggest an opening line with Gemini", on_click=suggest_opener)
    st.caption(state.get("ai_status", "Optional. Gemini receives only the fictional message shown in this demo."))
    en, te = plans[state.timing][2:]
    packed = state.get("opener") == "A"
    if language == "English":
        opening = "Thanks for packing the ajwain, Amma." if packed else "Thanks for checking on me, Amma."
        note = f"{opening} {en} I’ll ask my doctor about ajwain water before trying it."
    else:
        opening = "అమ్మా, వాము పెట్టి ఇచ్చినందుకు థాంక్స్." if packed else "అమ్మా, నా గురించి అడిగినందుకు థాంక్స్."
        note = f"{opening} {te} వాము నీళ్లు తాగే ముందు నా డాక్టర్‌ని అడుగుతాను."
    st.code(note, language=None, wrap_lines=True)
    st.caption("Use the copy icon to take the reply into WhatsApp.")
    if st.button("Keep this reply and check in", type="primary"):
        state.note = note
        advance()
        st.rerun()
else:
    st.header("Before the next call")
    st.write(f"Meera’s plan is to **{plans[state.timing][0].lower()}**.")
    if "outcome" not in state:
        choice = st.radio("In Meera’s shoes, how clear is your next step?",
                          ["I know what to do next", "I would like more guidance"], index=None)
        if st.button("Finish check-in", type="primary", disabled=choice is None):
            state.outcome = choice
            st.rerun()
    else:
        st.success("Check-in complete")
        st.write("**Meera’s reflection** · " + state.outcome)
        if state.outcome == "I would like more guidance":
            st.info("Meera can take her question to her maternity team before deciding what to try.")
        st.write("**Question for her next appointment**")
        st.write(question)
        summary = "\n\n".join(["MaaGuide · Meera’s lunch break (fictional demo)", plans[state.timing][0],
                               state.note, question, "Check-in: " + state.outcome, "Source: " + NHS])
        recommendation = state.get("recommendations", {}).get(state.timing)
        if recommendation:
            summary += "\n\nGemini’s educational recommendation (AI-generated)\n" + recommendation
        st.download_button("Download Meera’s takeaway", summary, "meera-takeaway.txt", "text/plain")
if state.step:
    st.button("Restart Meera’s story", on_click=restart)
