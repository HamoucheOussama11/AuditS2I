import streamlit as st
import pandas as pd
import time
import datetime
from n8n_connector import send_to_n8n
from visualizations import create_risk_matrix
from fpdf import FPDF

# --- Helper Function for Risk Level ---
def get_risk_level(score):
    if score > 10:
        return "CRITIQUE", "🔴", (220, 53, 69) # Red
    elif score >= 6:
        return "MAJEUR", "🟠", (255, 193, 7) # Orange/Dark Yellow
    else:
        return "MINEUR", "🟢", (40, 167, 69) # Green

# --- PDF Generation Logic ---
def clean_text(text):
    """
    Replaces incompatible characters for Latin-1 encoding.
    """
    replacements = {
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2022': '*',  # Bullet
        '\u2026': '...', # Ellipsis
        '€': 'EUR',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', 'replace').decode('latin-1')

class AuditReport(FPDF):
    def header(self):
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'AuditS2I - Rapport d\'Inspection Automatisé | {datetime.date.today()}', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(audit_results):
    """
    Generates a Professional PDF report from the audit results.
    """
    pdf = AuditReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Title Page ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 60, '', 0, 1) # Spacer
    pdf.cell(0, 10, 'RAPPORT DE MISSION D\'AUDIT', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, 'Module 1 : Fondations Technologiques', 0, 1, 'C')
    pdf.ln(20)
    
    pdf.set_font('Arial', 'I', 12)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, 'Confidentiel', 0, 1, 'C')
    
    # --- Risk Pages ---
    for risk in audit_results:
        pdf.add_page()
        
        score = risk.get("risk_score", 0)
        text = risk.get("frap_text", "")
        pillar = risk.get("pillar", "Général")
        
        level_name, _, color_rgb = get_risk_level(score)
        
        # Banner Header
        pdf.set_fill_color(*color_rgb)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 16)
        # Add some padding visually by using a cell with fill
        header_text = f"  {pillar.upper()} - {level_name}"
        pdf.cell(0, 15, clean_text(header_text), 0, 1, 'L', 1)
        pdf.ln(10)
        
        # Risk Score Badge
        pdf.set_fill_color(245, 245, 245) # Light Gray
        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(50, 10, f" Score de Risque : {score} ", 1, 1, 'C', 1)
        pdf.ln(10)
        
        # Body Content
        pdf.set_text_color(0, 0, 0)
        
        # Robust Text Rendering (Markdown Stripping & Formatting)
        clean_body = clean_text(text)
        lines = clean_body.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                pdf.ln(5) # Spacing for empty lines
                continue
                
            is_header = False
            
            # 1. Detect & Clean Markdown Headers (### Title)
            if line.startswith('#'):
                is_header = True
                # Remove all leading # and spaces
                line = line.lstrip('#').strip()
            
            # 2. Detect & Clean Bold Wrappers (**Title**)
            elif line.startswith('**') and line.endswith('**'):
                is_header = True
                line = line[2:-2].strip() # Remove first and last 2 chars
            
            # 3. Detect Numbered Headers (1. Title)
            elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
                is_header = True
            
            # 4. Detect Uppercase Labels (CONTEXTE :)
            elif ':' in line and len(line.split(':')[0]) < 40 and line.split(':')[0].isupper():
                is_header = True

            # Clean up any remaining inline markdown bold markers
            line = line.replace('**', '') 
            
            if is_header:
                # Special styling for "NORME VIOLÉE"
                if "NORME" in line and "VIOLÉE" in line:
                    pdf.set_font('Arial', 'BI', 10)
                    pdf.set_text_color(100, 100, 100) # Gray
                else:
                    pdf.set_font('Arial', 'B', 11)
                    pdf.set_text_color(0, 0, 0) # Black
                
                # Add a small top margin for headers if not at top of page
                if pdf.get_y() > 40: 
                    pdf.ln(2)
                pdf.multi_cell(0, 6, line)
                
                # Reset color to black for subsequent text if it was gray
                pdf.set_text_color(0, 0, 0) 
            else:
                pdf.set_font('Arial', '', 11)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, line)
        
        # Footer Note for the risk
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, "Généré par l'Agent IA AuditS2I", 0, 1, 'L')

    return pdf.output(dest='S').encode('latin-1')

# --- Page Configuration ---
st.set_page_config(
    page_title="AuditS2I | Plateforme d'Audit Intelligente",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Cyber/Dark Theme ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff; /* Neon Blue */
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #238636;
        color: white;
        border: 1px solid #2ea043;
        border-radius: 6px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        border-color: #3fb950;
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background-color: #0d1117;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(46, 160, 67, 0.15);
        border: 1px solid #2ea043;
        color: #3fb950;
    }
    .stError {
        background-color: rgba(248, 81, 73, 0.15);
        border: 1px solid #f85149;
        color: #ff7b72;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #58a6ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("🛡 AuditS2I")
    st.markdown("---")
    
    st.header("📂 Import des Données")
    infra_file = st.file_uploader("CSV Infrastructure", type=["csv"])
    mlops_file = st.file_uploader("CSV MLOps", type=["csv"])
    api_file = st.file_uploader("CSV Logs API", type=["csv"])
    
    st.markdown("---")
    st.header("⚙ Paramètres")
    webhook_url = st.text_input("URL Webhook n8n", placeholder="https://your-n8n-instance/webhook/...", type="password")
    
    st.markdown("---")
    st.caption("v1.5.0 | Propulsé par n8n & Streamlit")

# --- Main Stage ---
st.title("Console d'Audit en Temps Réel")
st.markdown("Bienvenue sur **AuditS2I**. Importez vos journaux d'audit pour générer un rapport FRAP en temps réel.")

# Check if files are uploaded
if infra_file and mlops_file and api_file:
    st.success("✅ Toutes les sources de données sont connectées.")
    
    if st.button("🚀 Lancer l'Audit Intelligent"):
        # 1. Prepare Data
        with st.spinner("Chiffrement et préparation des données..."):
            # Read CSVs into DataFrames (mock processing)
            try:
                infra_df = pd.read_csv(infra_file)
                mlops_df = pd.read_csv(mlops_file)
                api_df = pd.read_csv(api_file)
                
                # Sanitize DataFrames (replace NaN with empty string for JSON compatibility)
                infra_df = infra_df.fillna("")
                mlops_df = mlops_df.fillna("")
                api_df = api_df.fillna("")

                # Convert to dict for JSON payload
                payload = {
                    "infrastructure": infra_df.to_dict(orient="records"),
                    "mlops": mlops_df.to_dict(orient="records"),
                    "api_logs": api_df.to_dict(orient="records")
                }
                time.sleep(1) # UX pause
            except Exception as e:
                st.error(f"Erreur lors du traitement des fichiers : {e}")
                st.stop()

        # 2. Send to n8n
        with st.spinner("📡 Transmission à l'Agent IA (n8n)..."):
            response = send_to_n8n(payload, webhook_url)
            time.sleep(1.5) # UX pause to show spinner

        # 3. Process Response
        if isinstance(response, dict) and "error" in response:
            st.error(response["message"])
        elif isinstance(response, list):
            # --- Results Area ---
            st.markdown("---")
            st.subheader("📊 Résultats de l'Audit")
            
            # Calculate Aggregate Metrics
            total_risks = len(response)
            max_risk_score = max([r.get("risk_score", 0) for r in response]) if response else 0
            # Count Critical based on score > 10
            critical_count = len([r for r in response if r.get("risk_score", 0) > 10])
            
            # Metrics Row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total des Risques", total_risks)
            with col2:
                st.metric("Score de Risque Max", max_risk_score)
            with col3:
                st.metric("Problèmes Critiques", critical_count)
            
            # Risk Matrix & Detailed Risks
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### 🕸 Matrice des Risques")
                # Visualization now handles the new schema (pillar, frequency, gravity)
                fig = create_risk_matrix(response)
                st.plotly_chart(fig, use_container_width=True)
                
            with col_right:
                st.markdown("### 📝 Résultats Détaillés")
                with st.container(height=400, border=True):
                    for i, risk in enumerate(response):
                        score = risk.get("risk_score", 0)
                        text = risk.get("frap_text", "")
                        pillar = risk.get("pillar", "Général")
                        
                        # Get Dynamic Level and Color
                        level_name, icon, _ = get_risk_level(score)
                        
                        # Expander Title: "🟠 Infrastructure (Majeur - Score: 9)"
                        expander_title = f"{icon} {pillar} ({level_name.title()} - Score: {score})"
                        
                        with st.expander(expander_title):
                            st.markdown(f"**Statut :** {level_name}")
                            st.markdown(text)
            
            # --- PDF Download ---
            st.markdown("---")
            st.subheader("📄 Génération de Rapport")
            
            pdf_bytes = generate_pdf(response)
            st.download_button(
                label="Télécharger le Rapport PDF Complet",
                data=pdf_bytes,
                file_name="Rapport_AuditS2I.pdf",
                mime="application/pdf"
            )

        else:
             st.error("⚠ Format de réponse inattendu de l'Agent IA.")

else:
    st.info("👋 Veuillez importer les 3 fichiers CSV requis dans la barre latérale pour commencer.")
    
    # Placeholder for empty state
    st.markdown("### En attente d'entrée...")
    st.markdown("""
    - **Logs Infrastructure** : Configurations serveur, règles pare-feu.
    - **Logs MLOps** : Métadonnées d'entraînement, logs de pipeline.
    - **Logs API** : En-têtes Requête/Réponse, codes d'erreur.
    """)
