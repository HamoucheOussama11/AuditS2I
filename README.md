# AuditS2I - Automated intelligent Audit Agent 🛡️🤖

**Master of Excellence Project MS2I
*Mohammed Premier University, Oujda*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![n8n](https://img.shields.io/badge/Orchestration-n8n-orange.svg)](https://n8n.io/)
[![OpenAI](https://img.shields.io/badge/AI-GPT--4o-green.svg)](https://openai.com/)

---

## 📋 Project Overview

**AuditS2I** is an automated technical audit solution ("Audit-as-Code") designed to assess the compliance and performance of critical Intelligent Information Systems (IIS) infrastructures in real-time.

The tool distinguishes itself through its **Hybrid Architecture** which combines:
1.  A **Deterministic Rule Engine (n8n)** for factual filtering based on international standards (ITIL 4, ISO 27001).
2.  **Cognitive Analysis (GPT-4o)** for contextual interpretation and the drafting of expert recommendations (FRAP).

### Audited Pillars
The system analyzes three fundamental axes:
* ☁️ **Infrastructure & Cloud:** Cost optimization (FinOps) and availability.
* 🧠 **Artificial Intelligence (MLOps):** Model drift, algorithmic bias, and reproducibility.
* 🔌 **Integration & API:** Performance (Latency), Security, and Robustness.

---

## 🚀 Key Features

* **Multi-Stream Ingestion:** Automatic import and validation of heterogeneous log files (CSV).
* **Dynamic Risk Matrix:** Real-time calculation and visualization of criticality (Severity x Frequency).
* **FRAP Report Generation:** Automatic drafting of full audit reports in PDF format, ready for management review.
* **Low-Code Orchestration:** Flexible business logic, modifiable via n8n without redeploying code.

---

## 🛠️ Tech Stack

* **Frontend / UI:** Python (Streamlit), Plotly (Visualization), Pandas (Data Processing).
* **Backend / Orchestration:** n8n (Workflow Automation).
* **AI Engine:** OpenAI API (GPT-4o Model) via n8n.
* **Document Generation:** FPDF.

---

## 📂 Project Structure

```bash
AuditS21/
├── app.py                  # Streamlit application entry point
├── n8n_connector.py        # n8n Webhook connection module
├── visualizations.py       # Graph generation (Risk Matrix, KPIs)
├── workflow_audits21.json  # n8n Workflow Export (Agent Brain)
├── requirements.txt        # Python dependencies list
├── .gitignore              # Sensitive files exclusion
├── data/                   # Mock Data for simulation
│   ├── infra.csv
│   ├── mlops.csv
│   └── api.csv
└── README.md               # Project documentation

