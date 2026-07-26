# PA Admissions Toolkit

A small multi-page Streamlit app for prospective Physician Assistant (PA) applicants.
Two tools share one deployment (switch between them in the sidebar):

1. **ISU File Score Estimator** — estimates the Idaho State University PA program
   admission "file score."
2. **PA Program Explorer** — browse admission requirements across ~40 PA programs and
   screen for the ones whose published minimums you meet.

**Everything here is unofficial and unaffiliated with any university.** Always confirm
requirements and your actual scores with each program directly.

## Pages & structure

- `streamlit_app.py` — entry point / router (`st.navigation`). This stays the
  Community Cloud "main file path."
- `pages_file_score.py` — the ISU file-score estimator.
- `pages_program_explorer.py` — the program comparison tool.
- `data/pa_programs.csv` — one row per program (GPA/sGPA minimums, PCE hours, GRE/CASPer,
  LoR, tuition, notes, and a **source URL** per school).
- `data/pa_prereqs.csv` — long format: one row per (school, prerequisite course, status).
- `pa_programs_pasteback.tsv` — the program data as tab-separated values, ready to paste
  back into the source Google Sheet (not read by the app).

### About the program data

The Program Explorer data was **researched from official program websites**, with a
source link kept for every school. Fields that a program does not clearly publish are
marked `unspecified` (and left blank for numeric fields) rather than guessed — and in the
"Do I qualify?" screen, blank/unspecified requirements are treated as **not
disqualifying**. Requirements change frequently; verify against each program's site
before relying on anything. Notable data caveats live in each row's `notes` column (e.g.
Keiser's program is closed; several schools publish only competitive averages, not
minimums).

## ISU File Score Estimator — what it computes

Max score: 6.00 points, combining:
- Prerequisite GPA (4.00 pts) — simple unweighted average across the 6 required courses
- GRE Verbal & Quantitative percentiles (0.30 pts each)
- Military/veteran status (0.25 pts) and rural background (0.25 pts)
- Overall science GPA (0.10 pts)
- Experience hours: healthcare, volunteering, shadowing, employment, leadership (0.45 pts)
- Non-English language proficiency (0.25 pts) and intercollegiate activities (0.10 pts)

It also shows how an estimated score compares to ISU's published historical admission
statistics.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io, sign in, and click "New app."
3. Pick the repository/branch and set the main file path to `streamlit_app.py`.
4. Deploy. Both pages appear in the sidebar automatically.
