import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import json
from recommender import JobRecommender

# Page Configuration
st.set_page_config(
    page_title="AI Job Recommendation System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Corporate UI CSS
DISCIPLINE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }

    /* Main Title Card */
    .title-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.8rem;
    }

    .title-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.4);
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin-bottom: 0.6rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .title-text {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin-bottom: 0.3rem;
    }

    .title-subtext {
        font-size: 1rem;
        color: #94a3b8;
    }

    /* Search Container Card */
    .search-hub-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
    }

    .hub-heading {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }

    .hub-sub {
        font-size: 0.92rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    /* Value Proposition Bullets */
    .value-prop-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.75rem;
    }

    .value-prop-check {
        color: #6366f1;
        font-weight: 800;
    }

    /* Result Card Styling */
    .job-result-card {
        background: rgba(30, 41, 59, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
    }

    .job-result-card:hover {
        border-color: #6366f1;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }

    .score-pill {
        font-size: 0.88rem;
        font-weight: 800;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
    }

    .score-high { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .score-med { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .score-low { background-color: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); }

    .skill-matched-pill {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    .skill-missing-pill {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    .meta-tag {
        display: inline-block;
        background-color: #0f172a;
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-right: 0.4rem;
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

    # Sidebar Dashboard & Settings
    with st.sidebar:
        st.markdown("### 💼 CareerAI Control Panel")
        st.caption("AI-Powered Job Recommendation System")
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
            st.caption("No jobs saved yet.")

        st.divider()
        st.markdown("### ⚡ Quick Presets")
        presets = {
            "Select Preset...": [],
            "Data Science & AI": ["python", "sql", "machine learning", "pandas", "numpy", "scikit-learn", "statistics"],
            "Frontend Developer": ["javascript", "react", "html", "css", "typescript", "git"],
            "DevOps Engineer": ["docker", "kubernetes", "aws", "linux", "terraform", "ci/cd"],
            "Cybersecurity Analyst": ["network security", "linux", "python", "wireshark", "siem", "incident response"]
        }
        selected_preset = st.selectbox("Apply Preset Profile:", list(presets.keys()))
        if selected_preset != "Select Preset...":
            st.session_state.user_skills = set(presets[selected_preset])

        st.divider()
        if st.button("🧹 Reset Skill Profile", use_container_width=True):
            st.session_state.user_skills = set()
            st.rerun()

    # 1. Main Header Title
    st.markdown("""
        <div class="title-banner">
            <div class="title-badge">AI Skill Matching Engine</div>
            <div class="title-text">AI-Based Job Recommendation System</div>
            <div class="title-subtext">Intelligent job profile matching using TF-IDF Vectorization, Cosine Similarity, and Missing Skill Gap Analysis.</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Main Search Hub Container
    st.markdown("""
        <div class="search-hub-card">
            <div class="hub-heading">Let AI Match Your Profile</div>
            <div class="hub-sub">Upload your resume (PDF) or select your skill profile to generate instant personalized job recommendations.</div>
        </div>
    """, unsafe_allow_html=True)

    # Structured 3-Column Input Layout
    col_step1, col_step2, col_step3 = st.columns([1.4, 1.4, 1.2])

    # Step 1: Input Profile / Resume
    with col_step1:
        st.markdown("#### Step 1: Profile & Skills Input")
        
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
                    st.session_state.user_skills.update(extracted)
                    st.success(f"✓ Extracted {len(extracted)} skills from PDF!")
        else:
            skills_dropdown = st.multiselect(
                "Select Skills from Dataset:",
                options=engine.all_unique_skills,
                default=[s for s in st.session_state.user_skills if s in engine.all_unique_skills]
            )
            st.session_state.user_skills = set(skills_dropdown)

        custom_text = st.text_input("Or add custom skills (comma separated):", placeholder="e.g. PyTorch, Docker")
        if custom_text:
            for item in custom_text.split(','):
                cleaned = item.strip().lower()
                if cleaned:
                    st.session_state.user_skills.add(cleaned)

        active_skills_list = sorted(list(st.session_state.user_skills))
        st.markdown(f"**Active Skills Profile (`{len(active_skills_list)} skills`):**")
        if active_skills_list:
            st.caption(", ".join(active_skills_list))
        else:
            st.warning("No skills entered yet.")

    # Step 2: Location & Preferences
    with col_step2:
        st.markdown("#### Step 2: Location & Track Preferences")
        
        selected_location = st.selectbox("Preferred Location:", engine.get_locations())
        selected_category = st.selectbox("Job Category Track:", engine.get_categories())
        selected_exp = st.selectbox("Experience Level:", engine.get_experience_levels())

        st.markdown("#### Step 3: Match Sensitivity")
        top_n = st.slider("Top Recommendations Count:", 1, 10, 5)
        min_score = st.slider("Minimum Match Score (%):", 0, 50, 0, step=5)

    # Step 3: System Discipline & Action
    with col_step3:
        st.markdown("#### System Value Delivery")
        st.markdown("""
            <div class="value-prop-item"><span class="value-prop-check">✔</span> Automated Skill Extraction</div>
            <div class="value-prop-item"><span class="value-prop-check">✔</span> TF-IDF Vector Representation</div>
            <div class="value-prop-item"><span class="value-prop-check">✔</span> Cosine Similarity Scoring</div>
            <div class="value-prop-item"><span class="value-prop-check">✔</span> Missing Skill Gap Analysis</div>
            <div class="value-prop-item"><span class="value-prop-check">✔</span> Real-Time Job Matching</div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🪄 Generate AI Recommendations", type="primary", use_container_width=True)

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

        st.markdown("### 📊 Recommendation Results & Analytics")

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
                st.metric("Total Jobs Evaluated", len(results))

            st.markdown("<br>", unsafe_allow_html=True)

            # Output Tabs
            tab1, tab2, tab3 = st.tabs([
                "🎯 Recommended Jobs", 
                "📈 Skill Gap Analytics & Charts", 
                "🔍 Browse Full Job Dataset"
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
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                                <div style="font-size: 1.3rem; font-weight: 700; color: #ffffff;">#{idx+1} {row['job_title']}</div>
                                <span class="score-pill {score_class}">{score}% Match</span>
                            </div>
                            <div style="margin-bottom: 0.8rem;">
                                <span class="meta-tag">📍 {row['location']}</span>
                                <span class="meta-tag">📁 {row['category']}</span>
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
                        st.markdown("**Missing Skills to Learn:**")
                        if row['missing_skills']:
                            st.markdown("".join([f'<span class="skill-missing-pill">+ {s}</span>' for s in row['missing_skills']]), unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="skill-matched-pill">🎉 100% Skills Matched!</span>', unsafe_allow_html=True)

                    # Action buttons
                    col_b1, col_b2 = st.columns([1, 4])
                    with col_b1:
                        save_txt = "★ Saved" if is_saved else "☆ Save Job"
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
