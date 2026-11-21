"""
SnapDiet - UI Theme & Visual Styling Module
Provides modern glassmorphic CSS, cards, badges, and Plotly visualization charts.
"""

import streamlit as st
import plotly.graph_objects as go

# Custom CSS for modern, premium glassmorphism
def get_theme_css():
    is_light = st.session_state.get("light_theme", False)
    is_logged_in = 'user_profile' in st.session_state and st.session_state.user_profile is not None
    
    if is_logged_in:
        # Hide the 'app' entry from sidebar navigation when user is logged in
        nav_display_css = """
        [data-testid="stSidebarNav"] ul li:first-child,
        [data-testid="stSidebarNav"] li:has(a[href="/"]),
        [data-testid="stSidebarNav"] li:has(a[href="./"]),
        [data-testid="stSidebarNav"] li:has(a[href$="/app"]),
        [data-testid="stSidebarNav"] a[href="/"],
        [data-testid="stSidebarNav"] a[href="./"],
        [data-testid="stSidebarNav"] a[href$="/app"] {
            display: none !important;
        }
        """
    else:
        # Hide internal protected pages from sidebar navigation when not logged in
        nav_display_css = """
        [data-testid="stSidebarNav"] ul li:not(:first-child) {
            display: none !important;
        }
        """
    
    if is_light:
        bg_gradient = "linear-gradient(135deg, #f8fafc, #e2e8f0, #f8fafc)"
        text_color = "#1e293b"
        card_bg = "rgba(255, 255, 255, 0.7)"
        card_border = "rgba(0, 0, 0, 0.1)"
        header_color = "#0f172a"
        input_bg = "rgba(255, 255, 255, 0.8)"
        sidebar_bg = "rgba(255, 255, 255, 0.8)"
        hero_bg = "linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)"
        hero_title = "linear-gradient(90deg, #0f172a, #334155)"
        hr_color = "rgba(0,0,0,0.1)"
    else:
        bg_gradient = "linear-gradient(135deg, #0f172a, #1e293b, #0f172a)"
        text_color = "#f8fafc"
        card_bg = "rgba(30, 41, 59, 0.6)"
        card_border = "rgba(255, 255, 255, 0.1)"
        header_color = "#f8fafc"
        input_bg = "rgba(15, 23, 42, 0.5)"
        sidebar_bg = "rgba(15, 23, 42, 0.8)"
        hero_bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
        hero_title = "linear-gradient(90deg, #ffffff, #94a3b8)"
        hr_color = "rgba(255,255,255,0.1)"

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Navigation visibility control */
    {nav_display_css}

    /* Base Styles */
    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }}

    /* Dynamic background gradient for the whole app */
    .stApp {{
        background: {bg_gradient};
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: {text_color};
    }}

    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}

    .snap-card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: {text_color};
    }}

    .snap-card:hover {{
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.15);
        border-color: rgba(16, 185, 129, 0.3);
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {header_color} !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }}
    
    hr {{
        border-color: {hr_color} !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s ease !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
    }}

    [data-testid="stMetricValue"] {{
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #34d399, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .stTextInput > div > div > input, .stSelectbox > div > div > select, .stNumberInput > div > div > input {{
        background: {input_bg} !important;
        border: 1px solid {card_border} !important;
        color: {text_color} !important;
        border-radius: 8px !important;
    }}

    .stTextInput > div > div > input:focus, .stSelectbox > div > div > select:focus, .stNumberInput > div > div > input:focus {{
        border-color: #10b981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
    }}

    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid {card_border} !important;
    }}

    .hero-header {{
        background: {hero_bg};
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 20px;
        padding: 2.5rem 2.5rem;
        color: {text_color};
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 40px -5px rgba(0, 0, 0, 0.1);
        animation: slideDown 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    }}

    .hero-header::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #10b981, #3b82f6, #8b5cf6);
    }}

    @keyframes slideDown {{
        from {{ opacity: 0; transform: translateY(-20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .hero-title {{
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        background: {hero_title};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .hero-subtitle {{
        font-size: 1.1rem;
        color: #94a3b8;
        margin-top: 0.8rem;
        font-weight: 500;
    }}

    .alert-card {{
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
        font-size: 0.9rem;
        color: #fcd34d;
    }}

    .stProgress > div > div > div > div {{
        background-image: linear-gradient(90deg, #10b981, #34d399) !important;
    }}
    </style>
    """

def inject_theme():
    """Inject custom CSS rules into Streamlit app."""
    st.markdown(get_theme_css(), unsafe_allow_html=True)

def render_hero(title: str, subtitle: str):
    """Render a bold hero banner."""
    html = f"""
    <div class="hero-header">
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, subtext: str = "", border_color: str = "#10B981", icon: str = "📊"):
    """Render a styled metric card."""
    html = f"""
    <div class="snap-card" style="border-top: 3px solid {border_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase;">{title}</span>
            <span style="font-size: 1.5rem;">{icon}</span>
        </div>
        <div style="font-size: 2rem; font-weight: 800; color: white; margin: 8px 0 4px 0;">{value}</div>
        <div style="font-size: 0.85rem; color: #cbd5e1;">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_nutrition_score_card(score_data: dict):
    """Render the Universal Nutrition Score display."""
    score = score_data.get("score", 85)
    grade = score_data.get("grade", "A")
    verdict = score_data.get("verdict", "")
    badge_color = score_data.get("badge_color", "#10B981")
    
    html = f"""
    <div class="snap-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.6) 100%); border: 1px solid rgba(16, 185, 129, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 0.85rem; font-weight: 700; color: #34D399; letter-spacing: 1px; text-transform: uppercase;">Universal Nutrition Score</span>
                <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 8px;">
                    <span style="font-size: 3.5rem; font-weight: 900; color: white; line-height: 1; text-shadow: 0 0 20px rgba(52, 211, 153, 0.4);">{score}</span>
                    <span style="font-size: 1.3rem; color: #94a3b8; font-weight: 600;">/ 100</span>
                    <span style="background: {badge_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.9rem; font-weight: 700; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">{grade}</span>
                </div>
                <p style="font-size: 1rem; color: #cbd5e1; margin-top: 12px; max-width: 500px;">{verdict}</p>
            </div>
            <div style="text-align: right; background: rgba(255,255,255,0.05); padding: 16px 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(5px);">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;">ICMR Guideline Match</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #fcd34d; margin-top: 4px;">Optimal Balance</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def create_macro_donut_chart(calories_consumed: float, target_calories: float,
                             protein_g: float, target_protein: float,
                             carbs_g: float, target_carbs: float,
                             fats_g: float, target_fats: float) -> go.Figure:
    """Create a Plotly multi-ring donut visualization with dark theme."""
    fig = go.Figure()
    
    # Outer ring: Calories
    fig.add_trace(go.Pie(
        values=[calories_consumed, max(0, target_calories - calories_consumed)],
        labels=['Calories Logged', 'Remaining'],
        hole=0.85,
        domain={'x': [0, 1], 'y': [0, 1]},
        marker=dict(colors=['#10B981', 'rgba(255,255,255,0.05)']),
        hoverinfo='label+value', textinfo='none', sort=False
    ))
    
    # Middle ring: Protein
    fig.add_trace(go.Pie(
        values=[protein_g, max(0, target_protein - protein_g)],
        labels=['Protein Logged (g)', 'Remaining (g)'],
        hole=0.72,
        domain={'x': [0.12, 0.88], 'y': [0.12, 0.88]},
        marker=dict(colors=['#3B82F6', 'rgba(255,255,255,0.05)']),
        hoverinfo='label+value', textinfo='none', sort=False
    ))

    # Inner ring: Carbs & Fats split
    fig.add_trace(go.Pie(
        values=[carbs_g, fats_g, max(0, (target_carbs + target_fats) - (carbs_g + fats_g))],
        labels=['Carbs (g)', 'Fats (g)', 'Remaining (g)'],
        hole=0.55,
        domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]},
        marker=dict(colors=['#F59E0B', '#EC4899', 'rgba(255,255,255,0.05)']),
        hoverinfo='label+value', textinfo='none', sort=False
    ))
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[
            dict(
                text=f"<b>{int(calories_consumed)}</b><br><span style='font-size:12px;color:#94a3b8;'>/ {int(target_calories)} kcal</span>",
                x=0.5, y=0.5,
                font_size=24,
                font_color='white',
                font_family='Plus Jakarta Sans',
                showarrow=False
            )
        ]
    )
    return fig

def create_weight_trajectory_chart(weight_history: list, target_weight: float) -> go.Figure:
    """Create a Plotly weight tracking line chart with dark theme."""
    days = [item["date"] for item in weight_history]
    weights = [item["weight"] for item in weight_history]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=days, y=[target_weight] * len(days),
        mode='lines', name='Goal Target',
        line=dict(color='#34d399', width=2, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=days, y=weights,
        mode='lines+markers', name='Current Weight',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8, color='#10b981', line=dict(color='#1e293b', width=2)),
        fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='white')),
        yaxis=dict(title='Weight (kg)', gridcolor='rgba(255,255,255,0.05)', color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='white')
    )
    return fig
