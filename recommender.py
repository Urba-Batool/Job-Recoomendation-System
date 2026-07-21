import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pypdf


class JobRecommender:
    """
    AI-Based Job Recommendation Engine utilizing TF-IDF Vectorization,
    Cosine Similarity matching, and Resume PDF skill extraction.
    """

    def __init__(self, dataset_path="jobs.csv"):
        self.dataset_path = dataset_path
        self.df = None
        self.vectorizer = None
        self.job_tfidf_matrix = None
        self.all_unique_skills = []
        self.load_and_prepare_data()

    def clean_text(self, text):
        """Preprocesses and normalizes text string."""
        if not isinstance(text, str):
            return ""
        text = text.lower().strip()
        return text

    def load_and_prepare_data(self):
        """Loads job dataset and fits the TF-IDF vectorizer."""
        self.df = pd.read_csv(self.dataset_path)

        # Extract all unique individual skills
        skill_set = set()
        for skills_str in self.df['required_skills'].dropna():
            for skill in skills_str.split(','):
                cleaned = skill.strip().lower()
                if cleaned:
                    skill_set.add(cleaned)
        self.all_unique_skills = sorted(list(skill_set))

        # Create combined feature string for indexing
        self.df['combined_features'] = self.df.apply(
            lambda row: f"{self.clean_text(str(row['required_skills']))} "
                        f"{self.clean_text(str(row['required_skills']))} "
                        f"{self.clean_text(str(row['job_title']))} "
                        f"{self.clean_text(str(row['job_description']))}",
            axis=1
        )

        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            token_pattern=r'(?u)\b[\w\+\.#]+\b'
        )
        self.job_tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

    def extract_skills_from_pdf(self, pdf_file):
        """Extracts text from uploaded PDF resume and identifies matched skills."""
        try:
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
            
            clean_resume_text = text.lower()
            found_skills = set()
            
            for skill in self.all_unique_skills:
                # Regex word boundary check for exact skill match
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, clean_resume_text):
                    found_skills.add(skill)

            return text, sorted(list(found_skills))
        except Exception as e:
            return "", []

    def analyze_skills(self, user_skills_list, job_required_skills_str):
        """Compares user skills against job required skills."""
        if isinstance(job_required_skills_str, str):
            req_skills = [s.strip().lower() for s in job_required_skills_str.split(',') if s.strip()]
        else:
            req_skills = []

        user_skills_clean = [s.strip().lower() for s in user_skills_list if s.strip()]
        user_skills_blob = " ".join(user_skills_clean)

        matched = []
        missing = []

        for req in req_skills:
            is_matched = False
            for user_skill in user_skills_clean:
                if user_skill in req or req in user_skill:
                    is_matched = True
                    break
            
            if is_matched or req in user_skills_blob:
                matched.append(req.title())
            else:
                missing.append(req.title())

        return matched, missing

    def recommend(self, user_skills, top_n=5, category_filter=None, exp_filter=None, location_filter=None, min_score=0.0):
        """Generates job recommendations based on skills and filters."""
        if not user_skills or not user_skills.strip():
            return pd.DataFrame()

        clean_user_input = self.clean_text(user_skills)
        user_skills_list = [s.strip() for s in clean_user_input.replace('\n', ',').split(',') if s.strip()]

        user_vector = self.vectorizer.transform([clean_user_input])
        similarities = cosine_similarity(user_vector, self.job_tfidf_matrix).flatten()

        results = self.df.copy()
        results['similarity_score'] = similarities
        results['match_percentage'] = (results['similarity_score'] * 100).round(1)

        # Filters
        if category_filter and category_filter != "All Categories":
            results = results[results['category'] == category_filter]

        if exp_filter and exp_filter != "All Experience Levels":
            results = results[results['experience_level'] == exp_filter]

        if location_filter and location_filter != "All Locations":
            results = results[results['location'].str.contains(location_filter, case=False, na=False)]

        results = results[results['match_percentage'] >= min_score]
        results = results.sort_values(by='similarity_score', ascending=False)
        results = results.head(top_n)

        matched_skills_list = []
        missing_skills_list = []

        for _, row in results.iterrows():
            matched, missing = self.analyze_skills(user_skills_list, row['required_skills'])
            matched_skills_list.append(matched)
            missing_skills_list.append(missing)

        results['matched_skills'] = matched_skills_list
        results['missing_skills'] = missing_skills_list

        return results

    def get_categories(self):
        return ["All Categories"] + sorted(self.df['category'].dropna().unique().tolist())

    def get_experience_levels(self):
        return ["All Experience Levels", "Entry Level", "Mid Level", "Senior Level"]

    def get_locations(self):
        locations = set()
        for loc_str in self.df['location'].dropna():
            for loc in loc_str.split(','):
                cleaned = loc.strip()
                if cleaned:
                    locations.add(cleaned)
        return ["All Locations"] + sorted(list(locations))
