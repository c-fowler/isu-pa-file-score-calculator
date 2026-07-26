"""PA Program Explorer — browse program requirements and screen for eligibility.

Unofficial, researched data. Always verify against each program's official site.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
PROGRAMS_CSV = DATA_DIR / "pa_programs.csv"
PREREQS_CSV = DATA_DIR / "pa_prereqs.csv"

# Canonical prerequisite course list (matches the research/data schema).
PREREQ_COURSES = [
    "Anatomy",
    "Physiology",
    "Biology",
    "Microbiology",
    "Chemistry",
    "Organic Chemistry",
    "Biochemistry",
    "Statistics",
    "English",
    "Genetics",
    "Social Science",
    "Developmental Psychology",
    "Cultural Competency",
]

NUMERIC_COLS = ["min_gpa", "min_sgpa", "pce_hours", "lor_count"]


@st.cache_data
def load_programs() -> pd.DataFrame:
    df = pd.read_csv(PROGRAMS_CSV, dtype=str).fillna("")
    for col in NUMERIC_COLS:
        # Coerce to numeric; blanks / "unspecified" become NaN (non-disqualifying).
        df[col + "_num"] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_prereqs() -> pd.DataFrame:
    return pd.read_csv(PREREQS_CSV, dtype=str).fillna("")


def required_courses_for(prereqs: pd.DataFrame, school: str) -> set[str]:
    rows = prereqs[(prereqs["school"] == school) & (prereqs["status"].str.lower() == "required")]
    return set(rows["course"])


def fmt(value: str) -> str:
    """Display a raw cell value, showing blanks as an explicit placeholder."""
    value = (value or "").strip()
    return value if value else "—"


st.title("🎓 PA Program Explorer")

if not PROGRAMS_CSV.exists() or not PREREQS_CSV.exists():
    st.info(
        "Program data hasn't been added yet. Once `data/pa_programs.csv` and "
        "`data/pa_prereqs.csv` are in place, this page will let you browse each program's "
        "requirements and screen for the ones you qualify for."
    )
    st.stop()

programs = load_programs()
prereqs = load_prereqs()

st.warning(
    "**Unofficial, researched data — verify before relying on it.** Requirements change "
    "frequently. Use the **Source** link on each program to confirm against the official page. "
    "Fields marked “—” or *unspecified* mean the requirement wasn't clearly published."
)

browse_tab, qualify_tab = st.tabs(["Browse a school", "Do I qualify?"])

# --------------------------------------------------------------------------- #
# Tab 1: Browse a school
# --------------------------------------------------------------------------- #
with browse_tab:
    school = st.selectbox("Choose a program", sorted(programs["name"]))
    row = programs[programs["name"] == school].iloc[0]

    st.subheader(f"{row['name']} — {fmt(row['state'])}")

    left, right = st.columns(2)
    with left:
        st.markdown(
            f"**Min. cumulative GPA:** {fmt(row['min_gpa'])}  \n"
            f"**Min. science GPA:** {fmt(row['min_sgpa'])}  \n"
            f"**Recent-GPA policy:** {fmt(row['recent_gpa_policy'])}  \n"
            f"**Patient-care hours:** {fmt(row['pce_hours'])}  \n"
            f"**CPhT hours accepted:** {fmt(row['cpht_accepted'])}"
        )
    with right:
        st.markdown(
            f"**Letters of rec:** {fmt(row['lor_count'])}  \n"
            f"**GRE:** {fmt(row['gre'])}  \n"
            f"**CASPer:** {fmt(row['casper'])}  \n"
            f"**Holistic review:** {fmt(row['holistic'])}  \n"
            f"**Tuition:** {fmt(row['tuition'])}"
        )

    if row["notes"].strip():
        st.caption(f"**Notes:** {row['notes']}")
    if row["source_url"].strip():
        st.markdown(f"[Source ↗]({row['source_url']})")

    st.divider()
    st.markdown("**Prerequisite courses**")
    school_prereqs = prereqs[prereqs["school"] == school]
    if school_prereqs.empty:
        st.caption("No prerequisite-course data recorded for this program.")
    else:
        display = school_prereqs[["course", "status", "credits", "notes"]].rename(
            columns={"course": "Course", "status": "Status", "credits": "Credits", "notes": "Notes"}
        )
        st.dataframe(
            display,
            hide_index=True,
            width="stretch",
            height=35 * (len(display) + 1) + 3,
        )

# --------------------------------------------------------------------------- #
# Tab 2: Do I qualify?
# --------------------------------------------------------------------------- #
with qualify_tab:
    st.caption(
        "Enter your stats to filter down to programs whose **published minimums you meet**. "
        "Requirements a program doesn't publish (blank / unspecified) are treated as *not* "
        "disqualifying. This is a self-guided screen, not official admissions guidance."
    )

    c1, c2 = st.columns(2)
    with c1:
        my_gpa = st.number_input("Cumulative GPA", 0.0, 4.0, 3.5, step=0.01)
        my_sgpa = st.number_input("Science GPA", 0.0, 4.0, 3.5, step=0.01)
        my_pce = st.number_input("Patient-care experience hours", 0, 20000, 1000, step=50)
    with c2:
        my_lor = st.number_input("Letters of rec you can provide", 0, 10, 3, step=1)
        gre_taken = st.checkbox("I have GRE scores")
        casper_taken = st.checkbox("I have taken CASPer")

    completed = st.multiselect(
        "Prerequisite courses I've completed (or will complete before matriculation)",
        PREREQ_COURSES,
        default=PREREQ_COURSES,
    )
    completed_set = set(completed)

    def qualifies(row: pd.Series) -> bool:
        if pd.notna(row["min_gpa_num"]) and my_gpa < row["min_gpa_num"]:
            return False
        if pd.notna(row["min_sgpa_num"]) and my_sgpa < row["min_sgpa_num"]:
            return False
        if pd.notna(row["pce_hours_num"]) and my_pce < row["pce_hours_num"]:
            return False
        if pd.notna(row["lor_count_num"]) and my_lor < row["lor_count_num"]:
            return False
        if row["gre"].strip().lower() == "required" and not gre_taken:
            return False
        if row["casper"].strip().lower() == "required" and not casper_taken:
            return False
        # All required prerequisite courses must be completed.
        needed = required_courses_for(prereqs, row["name"])
        if needed and not needed.issubset(completed_set):
            return False
        return True

    mask = programs.apply(qualifies, axis=1)
    matches = programs[mask]

    st.subheader(f"{len(matches)} of {len(programs)} programs match")
    if matches.empty:
        st.info("No programs match your current inputs. Try adjusting your stats above.")
    else:
        view = matches[
            ["name", "state", "min_gpa", "min_sgpa", "pce_hours", "gre", "casper", "tuition", "source_url"]
        ].rename(
            columns={
                "name": "Program",
                "state": "State",
                "min_gpa": "Min GPA",
                "min_sgpa": "Min sGPA",
                "pce_hours": "PCE hrs",
                "gre": "GRE",
                "casper": "CASPer",
                "tuition": "Tuition",
                "source_url": "Source",
            }
        )
        st.dataframe(
            view,
            hide_index=True,
            width="stretch",
            column_config={"Source": st.column_config.LinkColumn("Source", display_text="Open ↗")},
        )
