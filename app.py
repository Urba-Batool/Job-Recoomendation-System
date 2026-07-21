import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import json
from recommender import JobRecommender

# Page Configuration
st.set_page_config(
    page_title="CareerAI — AI Job Recommendation System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Glassmorphism CSS aligned with the FastAPI Web App
DISCIPLINE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        background-color: #080c14 !important;
        color: #f8fafc !important;
    }

    /* Ambient Background Mesh & Grid */
    .stApp {
        background-image: 
            radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 85% 65%, rgba(139, 92, 246, 0.12) 0%, transparent 45%),
            radial-gradient(circle at 50% 90%, rgba(236, 72, 153, 0.08) 0%, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin-bottom: 1.25rem;
    }

    .brand-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        font-size: 1.3rem;
    }

    .brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }

    .brand-caption {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
    }

    /* Title Banner Card */
    .title-banner {
        position: relative;
        background: rgba(18, 24, 38, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 2.25rem 2.5rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        overflow: hidden;
    }

    .title-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #818cf8;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.85rem;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #818cf8;
        box-shadow: 0 0 8px #818cf8;
    }

    .title-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }

    .title-subtext {
        font-size: 1rem;
        color: #cbd5e1;
        max-width: 800px;
    }

    /* Search Container Card */
    .search-hub-card {
        background: rgba(18, 24, 38, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.8rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .hub-icon {
        width: 52px;
        height: 52px;
        border-radius: 12px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }

    .hub-heading {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.25rem;
    }

    .hub-sub {
        font-size: 0.9rem;
        color: #cbd5e1;
    }

    /* Card Box for Columns */
    .card-box {
        background: rgba(18, 24, 38, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 1.5rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
        min-height: 520px;
    }

    .card-header-flex {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 0.85rem;
        margin-bottom: 1.2rem;
    }

    .step-badge {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        color: #ffffff;
        font-weight: 800;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.4);
        flex-shrink: 0;
    }

    .step-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }

    /* Value Propositions */
    .value-props {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.15rem;
        margin-bottom: 1.5rem;
    }

    .value-prop-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.88rem;
        font-weight: 500;
        color: #cbd5e1;
    }

    .value-prop-check {
        color: #10b981;
        font-weight: bold;
    }

    /* Result Card Styling */
    .job-result-card {
        background: rgba(18, 24, 38, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        transition: border-color 0.25s, transform 0.25s;
    }

    .job-result-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }

    .score-pill {
        font-size: 0.85rem;
        font-weight: 800;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        letter-spacing: 0.02em;
    }

    .score-high {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
    }

    .score-med {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
    }

    .score-low {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #a5b4fc;
    }

    .score-bar-bg {
        width: 100%;
        height: 8px;
        background: rgba(30, 41, 59, 0.8);
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 0.5rem;
        margin-bottom: 0.85rem;
    }

    .score-bar-fill {
        height: 100%;
        border-radius: 9999px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    }

    .meta-tag {
        display: inline-block;
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #cbd5e1;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 0.2rem 0.65rem;
        border-radius: 6px;
        margin-right: 0.5rem;
    }

    .skill-matched-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        margin: 0.2rem;
    }

    .skill-missing-pill {
        display: inline-block;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: #fbbf24;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        margin: 0.2rem;
    }

    /* Custom Streamlit Widget Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.25s ease !important;
    }

</style>
"""

st.markdown(DISCIPLINE_CSS, unsafe_allow_html=True)


def load_engine():
    return JobRecommender(dataset_path="jobs.csv")



def initialize_state():
    if "user_skills" not in st.session_state:
        st.session_state.user_skills = set()
    if "saved_jobs" not in st.session_state:
        st.session_state.saved_jobs = set()


def main():
    initialize_state()
    engine = load_engine()

    # Sidebar Navigation & Settings
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-brand">
                <div class="brand-icon">💼</div>
                <div>
                    <div class="brand-title">CareerAI</div>
                    <div class="brand-caption">Intelligent Skill Matcher</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        st.markdown(f"**🔖 Saved Jobs ({len(st.session_state.saved_jobs)}):**")
        if st.session_state.saved_jobs:
            saved_df = engine.df[engine.df['job_id'].isin(st.session_state.saved_jobs)]
            for _, srow in saved_df.iterrows():
                st.write(f"- **{srow['job_title']}**")
            if st.button("Clear Saved Jobs", use_container_width=True):
                st.session_state.saved_jobs = set()
                st.rerun()
        else:
            st.caption("No saved jobs yet")

        st.divider()
        st.markdown("### ⚡ Quick Presets")
        presets = {
            "Select Preset Profile...": [],
            "Data Science & AI Engineer": ["python", "sql", "machine learning", "pandas", "numpy", "scikit-learn", "statistics"],
            "Frontend Web Developer": ["javascript", "react", "html", "css", "typescript", "git"],
            "DevOps & Cloud Engineer": ["docker", "kubernetes", "aws", "linux", "terraform", "ci/cd"],
            "Cybersecurity Specialist": ["network security", "linux", "python", "wireshark", "siem", "incident response"]
        }
        selected_preset = st.selectbox("Apply Preset Profile:", list(presets.keys()))
        if selected_preset != "Select Preset Profile...":
            st.session_state.user_skills = set(presets[selected_preset])

        st.divider()
        if st.button("Reset Skill Profile", use_container_width=True):
            st.session_state.user_skills = set()
            st.rerun()

    # 1. Main Header Title
    st.markdown("""
        <div class="title-banner">
            <div class="title-badge">
                <span class="pulse-dot"></span>
                AI Skill Matching Engine v2.0
            </div>
            <div class="title-text">AI-Based Job Recommendation System</div>
            <div class="title-subtext">Discover personalized career opportunities using TF-IDF vector analysis, cosine similarity matching, and real-time missing skill gap detection.</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Main Search Hub Container
    st.markdown("""
        <div class="search-hub-card">
            <div class="hub-icon">🔍</div>
            <div>
                <div class="hub-heading">Match Your Skill Profile</div>
                <div class="hub-sub">Upload your PDF resume, pick skills from our cloud, or enter custom technologies to get instant ranked matches.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Structured 3-Column Input Layout
    col_step1, col_step2, col_step3 = st.columns([1.3, 1.3, 1.1])

    # Step 1: Input Profile / Resume
    with col_step1:
        st.markdown("""
            <div class="card-header-flex">
                <span class="step-badge">01</span>
                <span class="step-title">Profile &amp; Skill Input</span>
            </div>
        """, unsafe_allow_html=True)

        input_mode = st.radio(
            "Choose Input Method:",
            ["📄 Upload Resume (PDF)", "🏷️ Select / Enter Skills"],
            horizontal=True
        )

        if input_mode == "📄 Upload Resume (PDF)":
            uploaded_pdf = st.file_uploader("Upload PDF Resume:", type=["pdf"])
            if uploaded_pdf is not None:
                _, extracted = engine.extract_skills_from_pdf(uploaded_pdf)
                if extracted:
                    st.session_state.user_skills.update([s.lower() for s in extracted])
                    st.success(f"✓ Extracted {len(extracted)} skills from PDF!")
        else:
            skills_dropdown = st.multiselect(
                "Select Skills from Dataset:",
                options=engine.all_unique_skills,
                default=[s for s in st.session_state.user_skills if s in engine.all_unique_skills]
            )
            st.session_state.user_skills.update([s.lower() for s in skills_dropdown])

        custom_text = st.text_input("Add custom skill tag (Press Enter):", placeholder="e.g. PyTorch, Docker, FastAPI...")
        if custom_text:
            for item in custom_text.split(','):
                cleaned = item.strip().lower()
                if cleaned:
                    st.session_state.user_skills.add(cleaned)

        # Quick Popular Skill Buttons
        st.markdown("**Quick Skill Picker (Click to add):**")
        popular = ["python", "sql", "javascript", "react", "machine learning", "docker", "aws", "pandas"]
        pop_cols = st.columns(4)
        for i, sk in enumerate(popular):
            with pop_cols[i % 4]:
                if st.button(f"+ {sk}", key=f"quick_{sk}"):
                    st.session_state.user_skills.add(sk)
                    st.rerun()

        active_skills_list = sorted(list(st.session_state.user_skills))
        st.markdown(f"**Active Skill Profile (`{len(active_skills_list)} skills`):**")
        if active_skills_list:
            st.caption(", ".join(active_skills_list))
        else:
            st.warning("No skills selected yet.")

    # Step 2: Location & Preferences
    with col_step2:
        st.markdown("""
            <div class="card-header-flex">
                <span class="step-badge">02</span>
                <span class="step-title">Preferences &amp; Thresholds</span>
            </div>
        """, unsafe_allow_html=True)
        
        selected_location = st.selectbox("Preferred Location:", engine.get_locations())
        selected_category = st.selectbox("Job Category:", engine.get_categories())
        selected_exp = st.selectbox("Experience Level:", engine.get_experience_levels())

        st.markdown("""
            <div class="card-header-flex" style="margin-top:1rem;">
                <span class="step-badge" style="width:26px; height:26px; font-size:0.75rem;">03</span>
                <span class="step-title">Match Sensitivity</span>
            </div>
        """, unsafe_allow_html=True)
        top_n = st.slider("Max Recommendations:", 1, 10, 5)
        min_score = st.slider("Min Match Cutoff (%):", 0, 50, 0, step=5)

    # Step 3: Action Card
    with col_step3:
        st.markdown("""
            <div class="card-header-flex">
                <span class="step-badge">04</span>
                <span class="step-title">Generate AI Matches</span>
            </div>
            <div class="value-props">
                <div class="value-prop-item"><span class="value-prop-check">✔</span> Automated Skill Extraction</div>
                <div class="value-prop-item"><span class="value-prop-check">✔</span> TF-IDF Vector Representation</div>
                <div class="value-prop-item"><span class="value-prop-check">✔</span> Cosine Similarity Scoring</div>
                <div class="value-prop-item"><span class="value-prop-check">✔</span> Missing Skill Gap Analysis</div>
                <div class="value-prop-item"><span class="value-prop-check">✔</span> Real-Time Job Matching</div>
            </div>
        """, unsafe_allow_html=True)
        
        generate_btn = st.button("🪄 Generate Recommendations", type="primary", use_container_width=True)

    st.divider()

    # 3. RECOMMENDATION RESULTS & ANALYTICS
    user_skills_blob = ", ".join(sorted(list(st.session_state.user_skills)))

    if generate_btn or user_skills_blob:
        results = engine.recommend(
            user_skills=user_skills_blob if user_skills_blob else "python, sql, machine learning",
            top_n=top_n,
            category_filter=selected_category,
            exp_filter=selected_exp,
            location_filter=selected_location if selected_location != "All Locations" else None,
            min_score=min_score
        )

        st.markdown("## Recommendation Results & Gap Analytics")
        st.caption("Ranked job roles matched against your skill matrix")

        if results.empty:
            st.warning("No job roles matched your exact filter criteria. Relax your filters or lower the minimum match threshold.")
        else:
            # Summary Metrics Row
            col_m1, col_m2, col_m3 = st.columns(3)
            top_row = results.iloc[0]
            
            with col_m1:
                st.metric("Top Recommended Job", top_row['job_title'])
            with col_m2:
                st.metric("Highest Match Score", f"{top_row['match_percentage']}%")
            with col_m3:
                st.metric("Total Roles Evaluated", len(results))

            st.markdown("<br>", unsafe_allow_html=True)

            # Output Tabs
            tab1, tab2, tab3 = st.tabs([
                "🎯 Recommended Jobs", 
                "📈 Skill Gap Analytics & Charts", 
                "🔍 Explore Full Dataset"
            ])

            # TAB 1: RECOMMENDED JOBS
            with tab1:
                for idx, row in results.reset_index(drop=True).iterrows():
                    score = row['match_percentage']
                    score_class = "score-high" if score >= 65 else ("score-med" if score >= 40 else "score-low")
                    job_id = row['job_id']
                    is_saved = job_id in st.session_state.saved_jobs

                    st.markdown(f"""
                        <div class="job-result-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                                <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff;">#{idx+1} {row['job_title']}</div>
                                <span class="score-pill {score_class}">{score}% Match</span>
                            </div>
                            <div class="score-bar-bg">
                                <div class="score-bar-fill" style="width: {min(100, max(5, score))}%;"></div>
                            </div>
                            <div style="margin-bottom: 0.8rem;">
                                <span class="meta-tag">📍 {row['location']}</span>
                                <span class="meta-tag">💼 {row['category']}</span>
                                <span class="meta-tag">🎯 {row['experience_level']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    c_l, c_r = st.columns(2)
                    with c_l:
                        st.markdown("**Matched Skills:**")
                        if row['matched_skills']:
                            st.markdown("".join([f'<span class="skill-matched-pill">✓ {s}</span>' for s in row['matched_skills']]), unsafe_allow_html=True)
                        else:
                            st.caption("No direct skill match.")

                    with c_r:
                        st.markdown("**Missing Skill Gap:**")
                        if row['missing_skills']:
                            st.markdown("".join([f'<span class="skill-missing-pill">+ {s}</span>' for s in row['missing_skills']]), unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="skill-matched-pill">🎉 100% Skills Matched!</span>', unsafe_allow_html=True)

                    # Action buttons
                    col_b1, col_b2 = st.columns([1, 4])
                    with col_b1:
                        save_txt = "★ Bookmarked" if is_saved else "☆ Save Job"
                        if st.button(save_txt, key=f"s_{job_id}"):
                            if is_saved:
                                st.session_state.saved_jobs.remove(job_id)
                            else:
                                st.session_state.saved_jobs.add(job_id)
                            st.rerun()

                    with col_b2:
                        with st.expander(f"📄 View Job Description & Requirements for {row['job_title']}"):
                            st.write(row['job_description'])
                            st.markdown(f"**Required Skills:** `{row['required_skills']}`")

                    st.markdown("<br>", unsafe_allow_html=True)

            # TAB 2: ANALYTICS
            with tab2:
                st.subheader("📈 Match Score Distribution")
                chart_df = results[['job_title', 'match_percentage']].copy()
                bar_chart = alt.Chart(chart_df).mark_bar(cornerRadius=6, color="#6366f1").encode(
                    x=alt.X('match_percentage:Q', title='Match Score (%)', scale=alt.Scale(domain=[0, 100])),
                    y=alt.Y('job_title:N', title='Job Title', sort='-x'),
                    tooltip=['job_title', 'match_percentage']
                ).properties(height=300)
                st.altair_chart(bar_chart, use_container_width=True)

                st.divider()

                st.subheader("⚠️ Missing Skill Gap Frequency")
                st.caption("Top skills missing across recommended job profiles.")
                
                flat_missing = []
                for ms in results['missing_skills']:
                    flat_missing.extend(ms)
                
                if flat_missing:
                    freq_df = pd.Series(flat_missing).value_counts().reset_index()
                    freq_df.columns = ['Skill', 'Count']
                    freq_chart = alt.Chart(freq_df.head(8)).mark_bar(cornerRadius=6, color="#f59e0b").encode(
                        x=alt.X('Count:Q', title='Occurrence Count'),
                        y=alt.Y('Skill:N', title='Missing Skill', sort='-x'),
                        tooltip=['Skill', 'Count']
                    ).properties(height=280)
                    st.altair_chart(freq_chart, use_container_width=True)

            # TAB 3: DATASET
            with tab3:
                st.subheader("📂 Comprehensive Job Profile Dataset")
                st.dataframe(engine.df[['job_id', 'job_title', 'category', 'experience_level', 'location', 'required_skills']], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
