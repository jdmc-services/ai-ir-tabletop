import streamlit as st
import anthropic

st.set_page_config(
    page_title="AI Incident Response Tabletop",
    page_icon="🚨",
    layout="centered"
)

st.markdown("""
<style>
.main { max-width: 760px; margin: 0 auto; }
.incident-box {
    background: #1a0a0a;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
}
.incident-time {
    font-size: 12px;
    color: #f87171;
    font-weight: 600;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.incident-text { color: #fca5a5; font-size: 14px; line-height: 1.7; }
.grade-box {
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
    font-size: 14px;
    line-height: 1.7;
}
.grade-correct { background: #0a1a0f; border: 1px solid #166534; color: #86efac; }
.grade-partial  { background: #1a1200; border: 1px solid #854d0e; color: #fde68a; }
.grade-wrong   { background: #1a0a0a; border: 1px solid #7f1d1d; color: #fca5a5; }
.framework-tag {
    font-size: 11px;
    color: #6b7280;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #374151;
}
.score-header {
    font-size: 48px;
    font-weight: 700;
    text-align: center;
    margin: 1rem 0 0.25rem;
}
.score-label {
    text-align: center;
    color: #9ca3af;
    font-size: 15px;
    margin-bottom: 1.5rem;
}
.brand-footer {
    text-align: center;
    font-size: 12px;
    color: #4b5563;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #1f2937;
}
</style>
""", unsafe_allow_html=True)

SCENARIOS = [
    {
        "id": 0,
        "title": "Wrong dosage hallucination",
        "tag": "NIST AI RMF · HIPAA",
        "time": "2:14 AM — Saturday",
        "incident": (
            "Your AI clinical documentation assistant just generated a discharge summary "
            "recommending 500mg metformin twice daily for a pediatric patient. The correct "
            "dose is 500mg once daily. The attending physician caught it before signing — "
            "but the document was already visible in the EHR for 22 minutes. Three staff "
            "members opened the record during that window."
        ),
        "question": "What is your first action in the next 30 minutes?",
        "choices": [
            "A — Quarantine the AI system immediately and escalate to the CISO and CMO.",
            "B — Correct the document and log the error internally — no escalation needed since it was caught before signing.",
            "C — Notify the patient's care team, flag the document, and open a formal AI incident ticket.",
            "D — Wait until morning to assess — the physician caught it, so there is no active patient harm.",
        ],
        "best": "C",
        "rationale": {
            "A": "Quarantining the system is premature before root cause is known — and escalating to CISO/CMO without first securing the patient record inverts the priority order.",
            "B": "Logging internally misses the 22-minute exposure window and the three staff views, which create a potential HIPAA audit trail requirement.",
            "C": "Correct. Securing the clinical record and notifying the care team is the immediate patient safety action. A formal AI incident ticket triggers your investigation workflow per NIST AI RMF Map 5.1.",
            "D": "Deferring until morning is a compliance failure. The 22-minute exposure window must be documented while the record is fresh.",
        },
        "framework": "NIST AI RMF Map 5.1 · HIPAA §164.308(a)(6) — Security incident procedures",
    },
    {
        "id": 1,
        "title": "Prompt injection in production",
        "tag": "OWASP LLM01 · MITRE ATLAS",
        "time": "10:47 AM — Tuesday",
        "incident": (
            "Your AI patient intake chatbot has been returning unusual outputs for 90 minutes. "
            "Investigation reveals a patient submitted a form containing embedded override "
            "instructions. The bot ignored its clinical screening criteria and told 4 patients "
            "they did not need in-person follow-up — contradicting your triage protocol. "
            "You have no record of what the bot told them."
        ),
        "question": "Who owns this incident and what happens next?",
        "choices": [
            "A — IT Security owns it — this is a cyberattack. Lock down the chatbot and file a cybersecurity incident report.",
            "B — Clinical Operations owns it — four patients received incorrect medical guidance. Patient outreach is the only priority.",
            "C — Joint incident: Clinical Operations handles patient outreach while IT Security investigates the attack vector simultaneously.",
            "D — Legal owns it — notify the malpractice insurer and pause all actions until counsel advises.",
        ],
        "best": "C",
        "rationale": {
            "A": "Treating this as a pure cybersecurity incident misses the immediate patient safety obligation. Four patients received incorrect triage guidance and must be contacted.",
            "B": "Clinical outreach is essential — but handing the incident entirely to clinical ops means the attack vector stays open.",
            "C": "Correct. This is exactly the split-ownership scenario NIST AI RMF anticipates. Patient outreach and attack containment are parallel tracks, not sequential.",
            "D": "Pausing all action for legal counsel leaves the attack vector open and delays patient outreach. Inaction is itself a liability.",
        },
        "framework": "MITRE ATLAS AML.T0051 — Prompt injection · NIST AI RMF Govern 1.2 — Accountability · HIPAA §164.308(a)(6)",
    },
    {
        "id": 2,
        "title": "Silent model drift",
        "tag": "NIST AI RMF · OWASP LLM09",
        "time": "3:30 PM — Thursday",
        "incident": (
            "Your AI prior authorization assistant has been in production for 8 months. "
            "A physician flags that it has been approving requests it used to flag for review. "
            "No code was deployed in 6 weeks. The vendor confirms they pushed a model update "
            "3 weeks ago without notifying you. Authorization approval rates jumped 18% "
            "after the update. You don't know if clinical criteria changed."
        ),
        "question": "What is the core compliance failure and what do you do first?",
        "choices": [
            "A — Suspend the AI tool immediately and revert to manual authorization review until the vendor explains the model change.",
            "B — Request a model card and change log from the vendor. Do not suspend — suspension disrupts operations and the change may be benign.",
            "C — Notify your CMO and compliance team, request the vendor's model change documentation, and audit a sample of post-update authorizations for clinical accuracy.",
            "D — Do nothing yet — an 18% approval rate increase could reflect population changes, not a model problem. Gather more data first.",
        ],
        "best": "C",
        "rationale": {
            "A": "Immediate suspension is defensible but operationally costly and may be premature before you know if clinical harm occurred.",
            "B": "Requesting documentation without escalating internally is incomplete. Your CMO and compliance team need to know a vendor silently changed a clinical decision support tool.",
            "C": "Correct. The core compliance failure is unauthorized model modification of a clinical decision support tool — a direct NIST AI RMF Govern 1.4 and OWASP LLM05 issue. Internal escalation, vendor documentation, and a sample audit run in parallel.",
            "D": "Waiting when you have a confirmed silent model update to a clinical tool is a governance failure. The 18% shift is statistically significant and the cause is already known.",
        },
        "framework": "OWASP LLM05 — Supply chain risk · NIST AI RMF Govern 1.4 — Organizational AI risk policies",
    },
    {
        "id": 3,
        "title": "Vendor data exposure disclosure",
        "tag": "HIPAA Breach Rule · NIST AI RMF",
        "time": "9:00 AM — Monday",
        "incident": (
            "Your AI transcription vendor emails you notifying you of a security incident "
            "from 11 days ago. They believe patient audio recordings from 6 healthcare "
            "customers — possibly including yours — were accessible to an unauthorized party "
            "for approximately 72 hours. They cannot confirm whether your data was involved. "
            "Your BAA with them is 3 years old."
        ),
        "question": "Does HIPAA breach notification apply here, and what is your 24-hour action?",
        "choices": [
            "A — HIPAA does not apply yet — you need confirmation your data was involved before any notification obligation triggers.",
            "B — HIPAA notification applies now. Notify HHS and begin patient notification within 24 hours.",
            "C — Treat this as a presumed breach under HIPAA's harm standard. Escalate to your Privacy Officer, request a written incident report from the vendor, review your BAA, and begin a 60-day notification clock assessment.",
            "D — Notify patients immediately out of caution — even without confirmed exposure.",
        ],
        "best": "C",
        "rationale": {
            "A": "Waiting for confirmation is the most common and most costly compliance mistake. Under HIPAA, the burden is on the covered entity to demonstrate a breach did NOT occur. The 60-day clock starts from discovery — today.",
            "B": "Jumping to HHS notification in 24 hours without investigating scope is premature. HIPAA gives you 60 days from discovery — use that window properly.",
            "C": "Correct. HIPAA §164.402 presumes breach unless you can demonstrate low probability of compromise. Your 60-day clock starts today. Your 3-year-old BAA needs review — 11 days notice is likely a violation of that agreement.",
            "D": "Notifying patients before you have confirmed scope creates its own liability and may cause unnecessary harm.",
        },
        "framework": "HIPAA §164.400-414 — Breach notification · HIPAA §164.402 — Breach presumption standard · NIST AI RMF Map 5.2",
    },
]

def get_client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

def grade_with_claude(scenario, choice_letter, choice_text):
    is_correct = choice_letter == scenario["best"]
    rationale = scenario["rationale"][choice_letter]
    prompt = f"""You are an AI incident response expert grading a healthcare professional's decision in a tabletop exercise.

Scenario: {scenario['title']}
Incident: {scenario['incident']}
The user chose: "{choice_text}"
{"This is the correct answer." if is_correct else f"The correct answer was option {scenario['best']}."}
Expert rationale: {rationale}

Write a 2-3 sentence grading response. Be direct and specific. Start with what they got right or wrong. Reference the specific compliance framework ({scenario['framework']}). Do not use filler phrases. Keep it under 80 words. Do not use bullet points."""

    client = get_client()
    with st.spinner("Grading your decision..."):
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
    return message.content[0].text, is_correct

def init_state():
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "current" not in st.session_state:
        st.session_state.current = 0
    if "show_summary" not in st.session_state:
        st.session_state.show_summary = False

def main():
    init_state()

    st.markdown("# 🚨 AI Incident Response Tabletop")
    st.markdown(
        "Four healthcare AI incidents. Make the call. "
        "Claude grades your decisions against **NIST AI RMF**, **HIPAA**, and **MITRE ATLAS**."
    )
    st.divider()

    if st.session_state.show_summary:
        show_summary_page()
        return

    progress_cols = st.columns(4)
    for i, s in enumerate(SCENARIOS):
        with progress_cols[i]:
            if i in st.session_state.answers:
                correct = st.session_state.answers[i] == s["best"]
                st.markdown(f"{'✅' if correct else '❌'} **Scenario {i+1}**")
            elif i == st.session_state.current:
                st.markdown(f"▶️ **Scenario {i+1}**")
            else:
                st.markdown(f"⬜ Scenario {i+1}")

    st.divider()

    idx = st.session_state.current
    if idx >= len(SCENARIOS):
        st.session_state.show_summary = True
        st.rerun()
        return

    s = SCENARIOS[idx]

    st.markdown(f"### Scenario {idx+1} of 4 — {s['title']}")
    st.caption(s["tag"])

    st.markdown(f"""
<div class="incident-box">
  <div class="incident-time">🕐 {s['time']}</div>
  <div class="incident-text">{s['incident']}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"**{s['question']}**")

    already_answered = idx in st.session_state.answers

    choice = st.radio(
        "Select your response:",
        options=s["choices"],
        key=f"choice_{idx}",
        disabled=already_answered,
        label_visibility="collapsed"
    )

    if not already_answered:
        if st.button("Submit my decision", type="primary", use_container_width=True):
            letter = choice[0]
            feedback, is_correct = grade_with_claude(s, letter, choice)
            st.session_state.answers[idx] = letter
            st.session_state.feedback[idx] = {
                "text": feedback,
                "correct": is_correct,
                "letter": letter
            }
            st.rerun()

    if already_answered and idx in st.session_state.feedback:
        fb = st.session_state.feedback[idx]
        if fb["correct"]:
            css_class = "grade-correct"
            verdict = "✅ Correct call"
        elif fb["letter"] in ["A", "B"] and s["best"] == "C":
            css_class = "grade-partial"
            verdict = "⚠️ Partial — critical gaps"
        else:
            css_class = "grade-wrong"
            verdict = "❌ Needs review"

        st.markdown(f"""
<div class="grade-box {css_class}">
  <strong>{verdict}</strong><br><br>
  {fb['text']}
  <div class="framework-tag">📋 {s['framework']}</div>
</div>
""", unsafe_allow_html=True)

        st.divider()
        if idx < len(SCENARIOS) - 1:
            if st.button("Next scenario →", use_container_width=True):
                st.session_state.current = idx + 1
                st.rerun()
        else:
            if st.button("See my results →", use_container_width=True):
                st.session_state.show_summary = True
                st.rerun()

    st.markdown('<div class="brand-footer">James D. McClain, MBA · AI Security Practitioner<br>Built on NIST AI RMF · HIPAA Breach Rule · MITRE ATLAS · OWASP LLM Top 10</div>', unsafe_allow_html=True)


def show_summary_page():
    correct = sum(1 for i, s in enumerate(SCENARIOS) if st.session_state.answers.get(i) == s["best"])
    partial = sum(1 for i, s in enumerate(SCENARIOS)
                  if st.session_state.answers.get(i) in ["A","B"] and s["best"] == "C"
                  and st.session_state.answers.get(i) != s["best"])
    wrong = 4 - correct - partial
    pct = int((correct + partial * 0.5) / 4 * 100)

    if pct >= 75:
        label = "Strong IR foundation"
        emoji = "🟢"
    elif pct >= 50:
        label = "Developing IR capability"
        emoji = "🟡"
    else:
        label = "Significant gaps identified"
        emoji = "🔴"

    st.markdown(f'<div class="score-header">{emoji} {pct}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="score-label">{label}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Correct", correct)
    col2.metric("Partial", partial)
    col3.metric("Incorrect", wrong)

    st.divider()
    st.markdown("### Decision review")

    for i, s in enumerate(SCENARIOS):
        chosen = st.session_state.answers.get(i, "—")
        fb = st.session_state.feedback.get(i, {})
        is_correct = chosen == s["best"]
        with st.expander(f"{'✅' if is_correct else '❌'} Scenario {i+1} — {s['title']}"):
            st.markdown(f"**You chose:** {chosen} — {s['choices'][ord(chosen)-65] if chosen != '—' else '—'}")
            st.markdown(f"**Correct answer:** {s['best']} — {s['choices'][ord(s['best'])-65]}")
            if fb.get("text"):
                st.markdown(f"*{fb['text']}*")
            st.caption(s["framework"])

    st.divider()
    st.markdown("""
This tabletop covers four of the most common AI incident types in healthcare:
hallucination with clinical impact, prompt injection in production, silent model drift,
and vendor data exposure. A complete AI IR plan addresses all four before an incident occurs.
    """)

    if st.button("Run again", use_container_width=True):
        for key in ["answers", "feedback", "current", "show_summary"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown('<div class="brand-footer">James D. McClain, MBA · AI Security Practitioner<br>Built on NIST AI RMF · HIPAA Breach Rule · MITRE ATLAS · OWASP LLM Top 10</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
