# 🚨 AI Incident Response Tabletop

**Live app:** [ai-ir-tabletop.streamlit.app](https://ai-ir-tabletop.streamlit.app)

An interactive AI incident response tabletop exercise for healthcare and regulated environments. Four realistic AI incidents. You make the call under pressure — and Claude grades your decision against **NIST AI RMF**, the **HIPAA Breach Rule**, **MITRE ATLAS**, and the **OWASP LLM Top 10**.

No setup. No form. No pitch. Just practice before the real incident happens.

---

## The Four Scenarios

| # | Incident | Frameworks Tested |
|---|----------|-------------------|
| 1 | **Wrong dosage hallucination** — An AI documentation assistant generates an incorrect pediatric dose, visible in the EHR for 22 minutes | NIST AI RMF Map 5.1 · HIPAA §164.308(a)(6) |
| 2 | **Prompt injection in production** — A patient intake chatbot is manipulated via embedded instructions and gives four patients incorrect triage guidance | MITRE ATLAS AML.T0051 · NIST AI RMF Govern 1.2 |
| 3 | **Silent model drift** — A vendor pushes an unannounced model update to a prior authorization tool; approval rates jump 18% | OWASP LLM05 · NIST AI RMF Govern 1.4 |
| 4 | **Vendor data exposure disclosure** — A transcription vendor reports a possible 72-hour exposure of patient audio, 11 days late, under a 3-year-old BAA | HIPAA §164.400–414 · §164.402 · NIST AI RMF Map 5.2 |

Each scenario presents a timed incident, four response options, and expert rationale for every choice — including why the wrong answers fail. Your decisions are graded in real time and summarized in a final readiness score.

## Why This Exists

Most incident response plans were written before AI entered the workflow. Hallucinations with clinical impact, prompt injection, silent model drift, and AI vendor breaches don't map cleanly to traditional IR runbooks — and the ownership questions (Security? Clinical Ops? Compliance? Legal?) are exactly where organizations stall during a real incident.

This tabletop lets teams and individuals practice those decisions safely, with framework-grounded feedback, before the 2:14 AM page.

## How It Works

- **Streamlit** front end — single-file app, no database
- **Claude (Anthropic API)** grades each decision against the scenario's expert rationale and cites the specific compliance framework
- Session-based scoring: correct / partial / needs review, with a full decision review at the end

## Run It Locally

```bash
git clone https://github.com/jdmc-services/ai-ir-tabletop.git
cd ai-ir-tabletop
pip install -r requirements.txt
```

Add your Anthropic API key to `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Then:

```bash
streamlit run app.py
```

## Related Projects

- 🔬 [Prompt Injection Attack & Defense Lab](https://promptinjectiondemo.streamlit.app) — four live healthcare-style attack/defense scenarios
- 📊 [AI Governance Readiness Scorecard](https://ai-governance-scorecard.streamlit.app) — governance readiness assessment across four industry tracks
- 🏗️ [Enterprise AI Infrastructure Architecture](https://github.com/jdmc-services/enterprise-ai-infrastructure-architecture) — reference architecture and governance framework aligned to NIST CSF 2.0, NIST AI RMF, ISO/IEC 42001, and Zero Trust

## Disclaimer

This is an independent educational project. It is not affiliated with, sponsored by, or produced on behalf of any employer. Scenarios are fictional and for training purposes only — nothing here constitutes legal or compliance advice.

## Author

**James D. McClain, MBA · AI Security Practitioner**
Built on NIST AI RMF · HIPAA Breach Rule · MITRE ATLAS · OWASP LLM Top 10

## License

MIT — free to use for internal training, education, and governance conversations.
