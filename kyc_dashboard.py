import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import json
import sys
import os
from datetime import datetime


# ========== HIDE ALL PRINT OUTPUT ==========
class HidePrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout



# ========== ENHANCED CSS STYLING ==========
def load_custom_css():
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
        }
        
        /* Header Styles */
        .app-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .app-title {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            text-align: center;
        }
        
        .app-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            text-align: center;
            margin-top: 0.5rem;
        }
        
        /* Profile Header */
        .profile-header {
            background: white;
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border-left: 6px solid #667eea;
        }
        
        .profile-name {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }
        
        .profile-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-top: 1rem;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #4a5568;
            font-size: 0.95rem;
        }
        
        .meta-label {
            font-weight: 600;
            color: #2d3748;
        }
        
        /* Risk Circle Enhanced */
        .risk-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .risk-circle {
            position: relative;
            width: 160px;
            height: 160px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        }
        
        .risk-inner {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            background: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .risk-level-text {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        
        .risk-label {
            font-size: 14px;
            color: #718096;
            font-weight: 500;
        }
        
        .match-rate-display {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-top: 0.5rem;
        }
        
        /* Section Cards */
        .section-card {
            background: white;
            border-radius: 15px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .section-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .section-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 1.2rem;
            padding-bottom: 0.8rem;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Badges Enhanced */
        .badge {
            display: inline-block;
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0.3rem;
            transition: transform 0.2s;
        }
        
        .badge:hover {
            transform: scale(1.05);
        }
        
        .badge-alias {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .badge-pep {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .badge-sanction {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: #fff;
        }
        
        .badge-role {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        /* Risk Status Cards */
        .risk-status-high {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(238, 90, 111, 0.3);
        }
        
        .risk-status-medium {
            background: linear-gradient(135deg, #ffa502 0%, #ff6348 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(255, 165, 2, 0.3);
        }
        
        .risk-status-low {
            background: linear-gradient(135deg, #26de81 0%, #20bf6b 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(38, 222, 129, 0.3);
        }
        
        .risk-status-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        /* Contact Info Boxes */
        .contact-box {
            background: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.8rem;
        }
        
        .contact-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #718096;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        
        .contact-value {
            font-size: 1rem;
            color: #2d3748;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        
        /* Metrics Cards */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            font-weight: 500;
        }
        
        /* Social Links Enhanced */
        .social-link {
            display: inline-flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.8rem 1.5rem;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            text-decoration: none;
            color: #2d3748;
            margin: 0.4rem;
            transition: all 0.3s;
            font-weight: 500;
        }
        
        .social-link:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* List Styles */
        .custom-list {
            background: #f7fafc;
            border-radius: 10px;
            padding: 1.2rem;
        }
        
        .list-item {
            padding: 0.7rem;
            border-bottom: 1px solid #e2e8f0;
            color: #2d3748;
        }
        
        .list-item:last-child {
            border-bottom: none;
        }
        
        /* Alert Box */
        .alert-box {
            background: #fff5f5;
            border: 2px solid #fc8181;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 2rem 0;
        }
        
        .alert-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .alert-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #c53030;
            margin-bottom: 0.5rem;
        }
        
        .alert-message {
            color: #742a2a;
            font-size: 1rem;
        }
        
        /* No Data Message */
        .no-data-card {
            background: white;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }
        
        .no-data-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        .no-data-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .no-data-message {
            color: #718096;
            font-size: 1rem;
        }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: white;
            border-radius: 10px;
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.8rem 1.5rem;
            font-weight: 600;
        }
        
        /* Upload Section */
        .upload-section {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin: 2rem 0;
        }
        
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        /* Profile Image Container */
        .profile-img-container {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            border: 4px solid white;
        }
        
        /* Scan ID Badge */
        .scan-id {
            background: #edf2f7;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            color: #2d3748;
            font-weight: 600;
        }
        
        /* Info Grid */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .info-item {
            background: #f7fafc;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .info-item-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #718096;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        
        .info-item-value {
            font-size: 1.1rem;
            color: #2d3748;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)


# ========== DEDUPLICATION FUNCTION ==========
def deduplicate_notes(notes_list):
    """
    Remove duplicate notes while preserving order and handling edge cases
    """
    if not notes_list:
        return []
    
    clean_notes = []
    seen_notes = set()
    
    for note in notes_list:
        # Skip empty or None values
        if not note or note == "None":
            continue
            
        # Clean the note
        cleaned = str(note).strip()
        if not cleaned:
            continue
        
        # Create a normalized version for comparison (lowercase, no extra spaces)
        normalized = ' '.join(cleaned.lower().split())
        
        # Only add if we haven't seen this note before
        if normalized not in seen_notes:
            seen_notes.add(normalized)
            clean_notes.append(cleaned)
    
    return clean_notes


# ========== ENHANCED RISK CIRCLE ==========
def display_risk_circle(risk_level, match_rate):
    """Display enhanced risk circle with proper percentage parsing."""
    # map risk levels to colors
    risk_colors = {
        'High': '#e53935',
        'Medium': '#fb8c00',
        'Low': '#43a047',
        'Unknown': '#757575'
    }
    color = risk_colors.get(risk_level, '#757575')


    # normalize match_rate into a 0–100 integer
    percentage = 0
    if isinstance(match_rate, str):
        # strip whitespace
        mr = match_rate.strip()
        if mr.endswith('%'):
            # "75%" → 75
            try:
                percentage = int(mr[:-1])
            except ValueError:
                percentage = 0
        else:
            # "0.75" or "75"
            try:
                val = float(mr)
                # if value ≤1 assume fraction, else assume whole percent
                percentage = int(val * 100) if val <= 1 else int(val)
            except ValueError:
                percentage = 0
    elif isinstance(match_rate, (int, float)):
        # numeric values
        val = float(match_rate)
        percentage = int(val * 100) if val <= 1 else int(val)


    # clamp to [0,100]
    percentage = max(0, min(100, percentage))


    angle = percentage * 3.6


    st.markdown(f"""
        <div class="risk-container">
            <div class="risk-circle"
                 style="background: conic-gradient(
                     {color} {angle}deg,
                     #e0e0e0 {angle}deg
                 );">
                <div class="risk-inner">
                    <div class="risk-level-text" style="color: {color};">
                        {risk_level}
                    </div>
                    <div class="risk-label">RISK LEVEL</div>
                </div>
            </div>
            <div class="match-rate-display">{percentage}%</div>
            <div class="risk-label">MATCH CONFIDENCE</div>
        </div>
    """, unsafe_allow_html=True)




# ========== DASHBOARD HEADER ==========
def display_app_header():
    """Display professional app header"""
    st.markdown("""
        <div class="app-header">
            <h1 class="app-title">🔍 KYC Verification Dashboard</h1>
            <p class="app-subtitle">Advanced Identity Verification & Risk Assessment Platform</p>
        </div>
    """, unsafe_allow_html=True)



# ========== NO DATA HANDLER ==========
def display_no_data(name=None):
    """Display when no external data is found"""
    display_name = name if name else "Unknown Individual"
    st.markdown(f"""
        <div class="alert-box">
            <div class="alert-icon">⚠️</div>
            <div class="alert-title">No External KYC Data Found</div>
            <div class="alert-message">
                <strong>Individual:</strong> {display_name}<br><br>
                No matching records were found in external databases. Manual verification is required to proceed with this identity check.
            </div>
        </div>
        
        <div class="no-data-card">
            <div class="no-data-icon">📋</div>
            <div class="no-data-title">Manual Verification Required</div>
            <div class="no-data-message">
                Please collect and verify identity documents manually through your organization's KYC procedures.
            </div>
        </div>
    """, unsafe_allow_html=True)



# ========== MAIN DASHBOARD ==========
def dashboard(identity_info, name=None):
    st.set_page_config(page_title="KYC Dashboard", layout="wide", page_icon="🔍")
    load_custom_css()
    display_app_header()
    
    # Handle no data case
    if name:
        display_no_data(name)
        return
    
    # ========== PROFILE HEADER ==========
    col_img, col_info = st.columns([1, 3])
    
    with col_img:
        st.markdown('<div class="profile-img-container">', unsafe_allow_html=True)
        if identity_info.get('Profile Image URL'):
            try:
                st.image(identity_info['Profile Image URL'], width=200)
            except:
                st.image("https://via.placeholder.com/200", width=200)
        else:
            st.image("https://via.placeholder.com/200", width=200)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_info:
        st.markdown(f"""
            <div class="profile-header">
                <div class="profile-name">{identity_info.get('Full Legal Name', 'Unknown Individual')}</div>
                <div class="profile-meta">
                    <div class="meta-item">
                        <span>📅</span>
                        <span><span class="meta-label">DOB:</span> {identity_info.get('Date of Birth', 'Unknown')}</span>
                    </div>
                    <div class="meta-item">
                        <span>👤</span>
                        <span><span class="meta-label">Gender:</span> {identity_info.get('Gender', 'Unknown').title()}</span>
                    </div>
                    <div class="meta-item">
                        <span>📍</span>
                        <span><span class="meta-label">Birth Place:</span> {identity_info.get('Place of Birth', 'Unknown')}</span>
                    </div>
                    <div class="meta-item">
                        <span>🌍</span>
                        <span><span class="meta-label">Nationality:</span> {identity_info.get('Nationality', 'Unknown')}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== TABS ==========
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "⚠️ Risk Assessment", 
        "👔 Positions & Roles", 
        "📞 Contact & IDs",
        "📄 Detailed Report"
    ])
    
    # ========== TAB 1: OVERVIEW ==========
    with tab1:
        col1, col2, col3 = st.columns([2, 2, 1.5])
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏷️ Known Aliases</div>', unsafe_allow_html=True)
            
            aliases = identity_info.get('Aliases', [])
            if aliases:
                # Show first 8 aliases as badges
                for alias in aliases[:8]:
                    st.markdown(f'<span class="badge badge-alias">{alias}</span>', unsafe_allow_html=True)
                
                if len(aliases) > 8:
                    with st.expander(f"View all {len(aliases)} aliases"):
                        st.markdown('<div class="custom-list">', unsafe_allow_html=True)
                        for i, alias in enumerate(aliases, 1):
                            st.markdown(f'<div class="list-item">{i}. {alias}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="no-data-message">No aliases found</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📞 Contact Information</div>', unsafe_allow_html=True)
            
            contact = identity_info.get('Contact Information', {})
            emails = [e for e in contact.get('Emails', []) if '@' in str(e)]
            phones = [p for p in contact.get('Phones', []) if p and p != 'Unknown' and str(p).strip()]
            addresses = contact.get('Addresses', [])
            
            if emails:
                st.markdown('<div class="contact-box">', unsafe_allow_html=True)
                st.markdown('<div class="contact-label">📧 Email Addresses</div>', unsafe_allow_html=True)
                for email in emails[:3]:
                    st.markdown(f'<div class="contact-value">{email}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if phones:
                st.markdown('<div class="contact-box">', unsafe_allow_html=True)
                st.markdown('<div class="contact-label">📱 Phone Numbers</div>', unsafe_allow_html=True)
                for phone in phones[:3]:
                    st.markdown(f'<div class="contact-value">{phone}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if addresses:
                st.markdown('<div class="contact-box">', unsafe_allow_html=True)
                st.markdown('<div class="contact-label">🏠 Addresses</div>', unsafe_allow_html=True)
                for addr in addresses[:2]:
                    st.markdown(f'<div class="contact-value">{addr}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if not emails and not phones and not addresses:
                st.markdown('<div class="no-data-message">No contact information available</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            display_risk_circle(
                identity_info.get('Risk Classification', 'Unknown'),
                identity_info.get('Match Rate', '0%')
            )
    
    # ========== TAB 2: RISK ASSESSMENT ==========
    with tab2:
        risk_class = identity_info.get('Risk Classification', 'Unknown')
        
        # Risk Status Banner
        risk_class_map = {
            'High': 'risk-status-high',
            'Medium': 'risk-status-medium',
            'Low': 'risk-status-low'
        }
        risk_class_css = risk_class_map.get(risk_class, 'risk-status-low')
        
        st.markdown(f"""
            <div class="{risk_class_css}">
                <div class="risk-status-title">🎯 Risk Classification: {risk_class.upper()}</div>
                <div>This individual has been classified as <strong>{risk_class} Risk</strong> based on comprehensive screening.</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">⚡ PEP & Sanctions Status</div>', unsafe_allow_html=True)
            
            pep_status = identity_info.get('PEP Status', 'Unknown')
            if pep_status == 'Yes':
                st.markdown('<span class="badge badge-pep">✓ POLITICALLY EXPOSED PERSON (PEP)</span>', unsafe_allow_html=True)
            else:
                st.success("✓ Not a Politically Exposed Person")
            
            sanctions = identity_info.get('Sanctions List', ['None'])
            st.markdown(f"**Sanctions Lists:** {', '.join(sanctions)}")
            
            watchlist = identity_info.get('Watchlist Categories', [])
            if watchlist and watchlist != ['None']:
                st.markdown("**Watchlist Categories:**")
                for item in watchlist:
                    st.markdown(f'<span class="badge badge-sanction">{item}</span>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📊 Screening Metrics</div>', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{identity_info.get('Match Rate', '0%')}</div>
                        <div class="metric-label">Match Rate</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{identity_info.get('Number of Matches', 0)}</div>
                        <div class="metric-label">Total Matches</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div style="margin-top: 1rem;">
                    <strong>Scan ID:</strong> <span class="scan-id">{identity_info.get('Scan ID', 'N/A')}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== TAB 3: POSITIONS & ROLES ==========
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏛️ Government & Military Positions</div>', unsafe_allow_html=True)
        
        gov_roles = identity_info.get('Government/Military Roles', [])
        gov_roles = [r for r in gov_roles if r and r != 'None']
        
        if gov_roles:
            for role in gov_roles[:10]:
                st.markdown(f'<span class="badge badge-role">{role}</span>', unsafe_allow_html=True)
            
            if len(gov_roles) > 10:
                with st.expander(f"View all {len(gov_roles)} government roles"):
                    st.markdown('<div class="custom-list">', unsafe_allow_html=True)
                    for i, role in enumerate(gov_roles, 1):
                        st.markdown(f'<div class="list-item">{i}. {role}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No government or military roles identified")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💼 All Positions & Occupations</div>', unsafe_allow_html=True)
        
        positions = list(dict.fromkeys(identity_info.get('Positions Held', [])))
        positions = [p for p in positions if p and p != 'None' and p.strip()]
        
        if positions:
            # Display first 15 as badges
            for pos in positions[:15]:
                st.markdown(f'<span class="badge badge-role">{pos}</span>', unsafe_allow_html=True)
            
            if len(positions) > 15:
                with st.expander(f"View all {len(positions)} positions"):
                    st.markdown('<div class="custom-list">', unsafe_allow_html=True)
                    for i, pos in enumerate(positions, 1):
                        st.markdown(f'<div class="list-item">{i}. {pos}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No position information available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== TAB 4: CONTACT & IDs ==========
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🆔 Government Identifiers</div>', unsafe_allow_html=True)
            
            gov_ids = identity_info.get('Government IDs', {})
            if gov_ids:
                st.markdown('<div class="info-grid">', unsafe_allow_html=True)
                for key, val in gov_ids.items():
                    if val and val != 'None':
                        st.markdown(f"""
                            <div class="info-item">
                                <div class="info-item-label">{key}</div>
                                <div class="info-item-value">{val}</div>
                            </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No government IDs available")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🌐 Social Media Profiles</div>', unsafe_allow_html=True)
            
            socials = identity_info.get('Social Media', {})
            has_social = False
            for platform, url in socials.items():
                if url and url != 'None' and url.startswith('http'):
                    has_social = True
                    # Determine emoji based on platform
                    emoji = '🔗'
                    if 'twitter' in url.lower(): emoji = '🐦'
                    elif 'facebook' in url.lower(): emoji = '📘'
                    elif 'instagram' in url.lower(): emoji = '📷'
                    elif 'linkedin' in url.lower(): emoji = '💼'
                    
                    st.markdown(f'<a href="{url}" target="_blank" class="social-link">{emoji} {platform}</a>', unsafe_allow_html=True)
            
            if not has_social:
                st.info("No social media profiles found")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📝 Summary Notes</div>', unsafe_allow_html=True)
            
            # ========== FIXED DEDUPLICATION LOGIC ==========
            raw_notes = identity_info.get('Summary Notes', [])
            notes = deduplicate_notes(raw_notes)
            
            if notes:
                for i, note in enumerate(notes, 1):
                    # Add numbering to distinguish multiple unique notes
                    if len(notes) > 1:
                        st.info(f"**Note {i}:** {note}")
                    else:
                        st.info(note)
            else:
                st.info("No additional notes available")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📚 Data Sources</div>', unsafe_allow_html=True)
            
            sources = identity_info.get('Data Sources', [])
            if sources:
                with st.expander(f"View all {len(sources)} data sources"):
                    st.markdown('<div class="custom-list">', unsafe_allow_html=True)
                    for src in sources:
                        st.markdown(f'<div class="list-item">• {src}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No source information available")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== TAB 5: DETAILED REPORT ==========
    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 Complete Identity Profile</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        ### Personal Information
        - **Full Legal Name:** {identity_info.get('Full Legal Name', 'Unknown')}
        - **Date of Birth:** {identity_info.get('Date of Birth', 'Unknown')}
        - **Gender:** {identity_info.get('Gender', 'Unknown').title()}
        - **Place of Birth:** {identity_info.get('Place of Birth', 'Unknown')}
        - **Nationality:** {identity_info.get('Nationality', 'Unknown')}
        - **Citizenship(s):** {', '.join(identity_info.get('Citizenship(s)', ['Unknown']))}
        
        ### Risk Profile
        - **Risk Classification:** {identity_info.get('Risk Classification', 'Unknown')}
        - **PEP Status:** {identity_info.get('PEP Status', 'Unknown')}
        - **Match Rate:** {identity_info.get('Match Rate', '0%')}
        - **Number of Matches:** {identity_info.get('Number of Matches', 0)}
        - **Scan ID:** {identity_info.get('Scan ID', 'N/A')}
        
        ### Screening Results
        - **Sanctions Lists:** {', '.join(identity_info.get('Sanctions List', ['None']))}
        - **Watchlist Categories:** {', '.join(identity_info.get('Watchlist Categories', ['None']))}
        
        ---
        
        *Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)



# ========== START APP ==========
def start_dashboard():
    st.set_page_config(page_title="KYC Verification Platform", layout="wide", page_icon="🔍")
    load_custom_css()
    display_app_header()
    
    st.markdown("""
        <div class="upload-section">
            <div class="upload-icon">📁</div>
            <h2>Upload KYC Verification Data</h2>
            <p style="color: #718096; margin-top: 0.5rem;">
                Upload a JSON file containing identity verification results to generate a comprehensive KYC dashboard.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("", type=['json'], label_visibility="collapsed")
    
    if uploaded:
        try:
            data = json.load(uploaded)
            with HidePrint():
                dashboard(data)
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)
    else:
        st.markdown("""
            <div class="section-card" style="margin-top: 2rem;">
                <h3>📋 Supported Data Format</h3>
                <p>The JSON file should contain the following structure:</p>
                <ul>
                    <li>Full Legal Name, Aliases, Date of Birth</li>
                    <li>Contact Information (Email, Phone, Address)</li>
                    <li>Government IDs and Social Media profiles</li>
                    <li>Risk Classification and PEP Status</li>
                    <li>Positions, Sanctions, and Watchlist data</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)



# ========== ENTRY POINT ==========
if __name__ == "__main__":
    start_dashboard()