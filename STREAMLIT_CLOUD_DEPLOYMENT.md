# ☁️ Streamlit Cloud Deployment Guide

This guide covers how to deploy the **Zomato AI Recommender** to Streamlit Cloud.

## 1. Prerequisites
- A GitHub account.
- A [Streamlit Cloud](https://share.streamlit.io/) account (linked to GitHub).
- Your **Groq API Key**.

## 2. Prepare the Repository
I have already made the following changes to make the project "Cloud Ready":
- ✅ Updated `.gitignore` to protect your `secrets.toml`.
- ✅ Configured `.streamlit/config.toml` with Zomato branding.
- ✅ Set up `requirements.txt` with all necessary dependencies.
- ✅ Updated `data/restaurants.py` to load data from a public HTTPS URL.

### Final Check: Push to GitHub
Ensure all your local changes are pushed to your GitHub repository:
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

## 3. Deploy on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your repository (`first_project`), branch (`main`), and main file path (`app.py`).
4.  **CRITICAL — Add Secrets**:
    - Before clicking "Deploy", click on **"Advanced settings..."**.
    - In the **Secrets** section, paste your Groq API key:
      ```toml
      GROQ_API_KEY = "your_actual_groq_api_key_here"
      ```
5.  Click **"Deploy"**.

## 4. Why Streamlit Cloud?
- **Ease of Use**: No need to manage Docker containers or Cloud Run services.
- **Auto-Update**: Every `git push` will automatically trigger a re-deploy.
- **Free Tier**: Perfect for personal projects and demos.

---
*Note: If you still wish to use Google Cloud Run, refer to [DEPLOYMENT.md](DEPLOYMENT.md).*
