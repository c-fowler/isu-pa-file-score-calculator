# ISU PA File Score Estimator

A small Streamlit app that estimates the Idaho State University Physician Assistant
program admission "file score," based on the methodology published at
https://www.isu.edu/pa/admission/admission-process/file-score/

**This is an unofficial, unaffiliated estimate.** It is not endorsed by or connected
to Idaho State University. Always confirm your actual file score with the ISU PA
program.

## What it computes

Max score: 6.00 points, combining:
- Prerequisite GPA (4.00 pts) — average of your grades in the 6 required prerequisite
  courses (see https://www.isu.edu/pa/admission/admission-requirements/). This app uses
  a simple unweighted average since ISU's page doesn't specify credit-hour weighting.
- GRE Verbal & Quantitative percentiles (0.30 pts each)
- Military/veteran status (0.25 pts)
- Rural background (0.25 pts)
- Overall science GPA (0.10 pts)
- Experience hours: healthcare, volunteering, shadowing, non-healthcare employment,
  leadership (0.45 pts combined, threshold-based)
- Non-English language proficiency (0.25 pts)
- Intercollegiate activities/sports (0.10 pts)

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a new GitHub repository.
2. Go to https://share.streamlit.io, sign in, and click "New app."
3. Pick the repository/branch and set the main file path to `streamlit_app.py`.
4. Deploy.
