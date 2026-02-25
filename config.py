"""
Uygulama yapılandırması: tema CSS ve sabitler.

Kurumsal card layout ve grid sistemi için tek kaynak.
"""

# Kurumsal / modern tema: koyu arka plan, okunaklı gri, vurgu renkleri
THEME_CSS = """
<style>
  :root {
    --bg-dark: #0e1117;
    --surface: #1a1d24;
    --surface-hover: #252930;
    --accent-green: #00e676;
    --accent-blue: #00b0ff;
    --text-primary: #f0f2f6;
    --text-muted: #d1d5db;
    --card-shadow: 0 4px 20px rgba(0, 230, 118, 0.08);
    --card-shadow-hover: 0 8px 32px rgba(0, 230, 118, 0.18);
    --card-radius: 12px;
    --card-border: 1px solid rgba(0, 230, 118, 0.15);
  }
  .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1d24 100%); }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1d24 0%, #0e1117 100%) !important;
  }
  [data-testid="stSidebar"] .stMarkdown { color: #f0f2f6; }
  h1, .main-title { color: var(--text-primary) !important; }
  .subtitle, p, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--text-muted) !important; }
  [data-testid="stMetricValue"] { color: #00e676 !important; }
  [data-testid="stMetricLabel"] { color: var(--text-muted) !important; }
  .stButton > button {
    background: rgba(0, 230, 118, 0.2) !important; color: #00e676 !important;
    border: var(--card-border) !important; border-radius: 8px !important;
    min-height: 2.5rem; padding: 0.5rem 1rem;
  }
  .stButton > button:hover {
    background: rgba(0, 230, 118, 0.3) !important; border-color: var(--accent-green) !important;
  }
  /* Kurumsal card layout */
  .card-container {
    background: var(--surface); border: var(--card-border);
    border-radius: var(--card-radius); padding: 1.25rem;
    box-shadow: var(--card-shadow); margin-bottom: 1rem;
    transition: all 0.25s ease;
  }
  .card-container:hover { box-shadow: var(--card-shadow-hover); }
  .card-title { color: var(--accent-green); font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem; }
  .card-metric { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }
  .nav-card { background: var(--surface); border: var(--card-border); border-radius: 16px;
    padding: 1.5rem; margin-bottom: 1rem; box-shadow: var(--card-shadow);
    transition: all 0.3s ease; min-height: 140px; }
  .nav-card:hover { border-color: rgba(0, 230, 118, 0.4); box-shadow: var(--card-shadow-hover);
    transform: translateY(-4px); background: var(--surface-hover); }
  .nav-card-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
  .nav-card-title { color: var(--accent-green); font-weight: 700; font-size: 1.15rem; margin-bottom: 0.35rem; }
  .nav-card-desc { color: var(--text-muted); font-size: 0.9rem; line-height: 1.4; }
  .nav-card-wrapper a {
    display: inline-block !important; margin-top: 0.5rem !important;
    padding: 0.5rem 1rem !important; background: rgba(0, 230, 118, 0.15) !important;
    color: var(--accent-green) !important; border-radius: 8px !important;
    text-decoration: none !important; font-weight: 600 !important; font-size: 0.9rem !important;
    border: 1px solid rgba(0, 230, 118, 0.3) !important;
  }
  .nav-card-wrapper a:hover { background: rgba(0, 230, 118, 0.25) !important; color: var(--accent-green) !important; }
  @media (max-width: 768px) {
    .nav-card { min-height: 120px; padding: 1rem; }
    .block-container { padding: 1rem !important; max-width: 100% !important; }
    .stButton > button { min-height: 3rem; font-size: 1rem; }
  }
  @media (max-width: 480px) { h1 { font-size: 1.5rem !important; } }
</style>
"""

# Varsayılan hareket listesi (program boşken)
DEFAULT_EXERCISES = ["Bench Press", "Squat", "Deadlift", "Overhead Press", "Barbell Row"]

# Haftanın günleri (program formu için)
WEEKDAYS = [
    "Pazartesi", "Salı", "Çarşamba", "Perşembe",
    "Cuma", "Cumartesi", "Pazar",
]
