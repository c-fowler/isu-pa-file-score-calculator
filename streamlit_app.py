"""ISU PA Program admission file-score estimator (unofficial)."""

import io
from dataclasses import dataclass

import altair as alt
import pandas as pd
import streamlit as st

SOURCE_URL = "https://www.isu.edu/pa/admission/admission-process/file-score/"
PREREQ_URL = "https://www.isu.edu/pa/admission/admission-requirements/"
STATS_URL = "https://www.isu.edu/pa/admission/admission-statistics/"

GRADE_POINTS = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 0.7,
    "F": 0.0,
}
GRADE_OPTIONS = list(GRADE_POINTS.keys())

PREREQ_COURSES = [
    "Microbiology",
    "Biochemistry",
    "Human Anatomy",
    "Human Physiology",
    "Statistics",
    "Abnormal / Developmental Psychology",
]

MAX_PREREQ_GPA_POINTS = 4.00
MAX_GRE_VERBAL_POINTS = 0.30
MAX_GRE_QUANT_POINTS = 0.30
MAX_MILITARY_POINTS = 0.25
MAX_RURAL_POINTS = 0.25
MAX_SCIENCE_GPA_POINTS = 0.10
MAX_LANGUAGE_POINTS = 0.25
MAX_SPORTS_POINTS = 0.10

EXPERIENCE_RULES = {
    "Combined patient & healthcare experience": {"threshold": 600, "points": 0.250},
    "Volunteerism / community service": {"threshold": 120, "points": 0.100},
    "Shadowing (total hours)": {"threshold": 20, "points": 0.050},
    "Non-healthcare employment": {"threshold": 1000, "points": 0.025},
    "Leadership": {"threshold": 150, "points": 0.025},
}

CLASS_YEAR_STATS = {
    2024: {
        "threshold": 4.825,
        "avg_file_score": 5.07,
        "avg_prereq_gpa": 3.88,
        "avg_science_gpa": 3.51,
        "avg_gre_verbal_pct": 67,
        "avg_gre_quant_pct": 46,
    },
    2025: {
        "threshold": 4.70,
        "avg_file_score": 5.04,
        "avg_prereq_gpa": 3.90,
        "avg_science_gpa": 3.61,
        "avg_gre_verbal_pct": 64,
        "avg_gre_quant_pct": 42,
    },
    2026: {
        "threshold": 4.64,
        "avg_file_score": 5.00,
        "avg_prereq_gpa": 3.85,
        "avg_science_gpa": 3.59,
        "avg_gre_verbal_pct": 58,
        "avg_gre_quant_pct": 38,
    },
    2027: {
        "threshold": 4.60,
        "avg_file_score": 4.95,
        "avg_prereq_gpa": 3.86,
        "avg_science_gpa": 3.54,
        "avg_gre_verbal_pct": 57,
        "avg_gre_quant_pct": 33,
    },
    2028: {
        "threshold": 4.675,
        "avg_file_score": 4.95,
        "avg_prereq_gpa": 3.87,
        "avg_science_gpa": 3.63,
        "avg_gre_verbal_pct": 61,
        "avg_gre_quant_pct": 32,
    },
}
LATEST_CLASS_YEAR = max(CLASS_YEAR_STATS)

MAX_TOTAL_POINTS = (
    MAX_PREREQ_GPA_POINTS
    + MAX_GRE_VERBAL_POINTS
    + MAX_GRE_QUANT_POINTS
    + MAX_MILITARY_POINTS
    + MAX_RURAL_POINTS
    + MAX_SCIENCE_GPA_POINTS
    + sum(rule["points"] for rule in EXPERIENCE_RULES.values())
    + MAX_LANGUAGE_POINTS
    + MAX_SPORTS_POINTS
)


def prereq_gpa_points(grades: list[str]) -> tuple[float, float]:
    gpa = sum(GRADE_POINTS[g] for g in grades) / len(grades)
    return gpa, gpa


def gre_points(percentile: float) -> float:
    percentile = max(0.0, min(100.0, percentile))
    return round(percentile * 0.003, 4)


def science_gpa_points(gpa: float) -> float:
    gpa = max(0.0, min(4.0, gpa))
    return round(gpa * 0.025, 4)


@dataclass
class FileScoreInputs:
    prereq_grades: list[str]
    gre_verbal_percentile: float
    gre_quant_percentile: float
    military: bool
    rural: bool
    science_gpa: float
    healthcare_met: bool
    volunteer_met: bool
    shadowing_met: bool
    employment_met: bool
    leadership_met: bool
    language_proficient: bool
    intercollegiate_sports: bool


def compute_file_score(inputs: FileScoreInputs) -> dict:
    prereq_gpa, prereq_pts = prereq_gpa_points(inputs.prereq_grades)

    breakdown = {
        "Prerequisite GPA": (prereq_pts, MAX_PREREQ_GPA_POINTS),
        "GRE Verbal percentile": (
            gre_points(inputs.gre_verbal_percentile),
            MAX_GRE_VERBAL_POINTS,
        ),
        "GRE Quantitative percentile": (
            gre_points(inputs.gre_quant_percentile),
            MAX_GRE_QUANT_POINTS,
        ),
        "Military service": (
            MAX_MILITARY_POINTS if inputs.military else 0.0,
            MAX_MILITARY_POINTS,
        ),
        "Rural background": (
            MAX_RURAL_POINTS if inputs.rural else 0.0,
            MAX_RURAL_POINTS,
        ),
        "Overall science GPA": (
            science_gpa_points(inputs.science_gpa),
            MAX_SCIENCE_GPA_POINTS,
        ),
        "Combined patient & healthcare experience": (
            EXPERIENCE_RULES["Combined patient & healthcare experience"]["points"]
            if inputs.healthcare_met
            else 0.0,
            EXPERIENCE_RULES["Combined patient & healthcare experience"]["points"],
        ),
        "Volunteerism / community service": (
            EXPERIENCE_RULES["Volunteerism / community service"]["points"]
            if inputs.volunteer_met
            else 0.0,
            EXPERIENCE_RULES["Volunteerism / community service"]["points"],
        ),
        "Shadowing (≥20 hrs total, ≥10 PA-specific)": (
            EXPERIENCE_RULES["Shadowing (total hours)"]["points"] if inputs.shadowing_met else 0.0,
            EXPERIENCE_RULES["Shadowing (total hours)"]["points"],
        ),
        "Non-healthcare employment": (
            EXPERIENCE_RULES["Non-healthcare employment"]["points"] if inputs.employment_met else 0.0,
            EXPERIENCE_RULES["Non-healthcare employment"]["points"],
        ),
        "Leadership": (
            EXPERIENCE_RULES["Leadership"]["points"] if inputs.leadership_met else 0.0,
            EXPERIENCE_RULES["Leadership"]["points"],
        ),
        "Non-English language proficiency": (
            MAX_LANGUAGE_POINTS if inputs.language_proficient else 0.0,
            MAX_LANGUAGE_POINTS,
        ),
        "Intercollegiate activities / sports": (
            MAX_SPORTS_POINTS if inputs.intercollegiate_sports else 0.0,
            MAX_SPORTS_POINTS,
        ),
    }

    total = sum(earned for earned, _ in breakdown.values())
    return {"prereq_gpa": prereq_gpa, "breakdown": breakdown, "total": total}


st.set_page_config(page_title="ISU PA File Score Estimator", page_icon="🩺", layout="centered")

st.title("ISU PA Program File Score Estimator")
st.warning(
    "**Unofficial estimator, not affiliated with or endorsed by Idaho State University.** "
    f"Scoring rules are drawn from the [official ISU PA file score page]({SOURCE_URL}). "
    "Verify your actual file score with the ISU PA program directly before relying on this."
)

st.divider()
st.subheader("1. Prerequisite GPA")
st.caption(
    "Enter your grade in each of the 6 required prerequisite courses "
    f"([full requirements]({PREREQ_URL})). ISU requires a minimum grade of C in each course "
    "and a minimum cumulative prerequisite GPA of 3.0."
)
st.caption(
    "**Assumption:** ISU's page does not state whether this GPA is credit-hour weighted. "
    "This tool computes a **simple unweighted average** across the 6 courses, which may differ "
    "slightly from ISU's actual internal calculation if your course credit hours are uneven."
)

prereq_grades = []
cols = st.columns(2)
default_grade_index = GRADE_OPTIONS.index("C")
for i, course in enumerate(PREREQ_COURSES):
    with cols[i % 2]:
        grade = st.selectbox(course, GRADE_OPTIONS, index=default_grade_index, key=f"prereq_{i}")
        prereq_grades.append(grade)

live_gpa = sum(GRADE_POINTS[g] for g in prereq_grades) / len(prereq_grades)
st.metric("Computed prerequisite GPA", f"{live_gpa:.2f} / 4.00")

st.divider()
st.subheader("2. GRE Scores")
st.caption("Enter percentile scores (not raw scores). Analytical writing is not used.")
gre_col1, gre_col2 = st.columns(2)
with gre_col1:
    gre_verbal = st.number_input("GRE Verbal percentile", 0.0, 100.0, 50.0, step=1.0)
with gre_col2:
    gre_quant = st.number_input("GRE Quantitative percentile", 0.0, 100.0, 50.0, step=1.0)
with st.expander("How this is scored"):
    st.write("Each percentile is multiplied by 0.003, up to 0.30 points per section (max 0.60 combined).")

st.divider()
st.subheader("3. Overall Science GPA")
science_gpa = st.number_input(
    "CASPA-calculated overall science GPA", 0.0, 4.0, 3.5, step=0.01
)
with st.expander("How this is scored"):
    st.write("Science GPA is multiplied by 0.025, up to 0.10 points.")

st.divider()
st.subheader("4. Military Service & Background")
military = st.checkbox("Active duty, reservist, or veteran status (as indicated on CASPA)")
rural = st.checkbox("Childhood residence in a rural area (population ≤ 49,999)")
with st.expander("How this is scored"):
    st.write("Each is worth a flat 0.25 points if applicable, 0 otherwise.")

st.divider()
st.subheader("5. Experience Hours")
st.caption("Check each box only if you meet the minimum hours for that category.")
healthcare_met = st.checkbox("I have ≥ 600 hours of combined patient & healthcare experience")
volunteer_met = st.checkbox("I have ≥ 120 hours of volunteerism / community service")
shadowing_met = st.checkbox("I have ≥ 20 hours of shadowing, including ≥ 10 PA-specific hours")
employment_met = st.checkbox("I have ≥ 1,000 hours of non-healthcare employment")
leadership_met = st.checkbox("I have ≥ 150 hours of leadership experience")
with st.expander("How this is scored"):
    st.table(
        {
            "Category": list(EXPERIENCE_RULES.keys()),
            "Minimum hours": [
                f"{r['threshold']:,.0f}" + (" (≥10 PA-specific)" if "Shadowing" in name else "")
                for name, r in EXPERIENCE_RULES.items()
            ],
            "Points": [f"{r['points']:.3f}" for r in EXPERIENCE_RULES.values()],
        }
    )

st.divider()
st.subheader("6. Other Factors")
language_proficient = st.checkbox(
    "At least intermediate proficiency in a non-English language"
)
intercollegiate_sports = st.checkbox(
    "Documented intercollegiate activities/sports participation (excludes intramural/club)"
)
with st.expander("How this is scored"):
    st.write(
        "Language proficiency (intermediate or higher) is worth a flat 0.25 points. "
        "Intercollegiate activities are worth a flat 0.10 points."
    )

inputs = FileScoreInputs(
    prereq_grades=prereq_grades,
    gre_verbal_percentile=gre_verbal,
    gre_quant_percentile=gre_quant,
    military=military,
    rural=rural,
    science_gpa=science_gpa,
    healthcare_met=healthcare_met,
    volunteer_met=volunteer_met,
    shadowing_met=shadowing_met,
    employment_met=employment_met,
    leadership_met=leadership_met,
    language_proficient=language_proficient,
    intercollegiate_sports=intercollegiate_sports,
)
result = compute_file_score(inputs)

st.divider()
st.header("Estimated File Score")
total = result["total"]
st.metric("Total", f"{total:.3f} / {MAX_TOTAL_POINTS:.2f}")
st.progress(min(total / MAX_TOTAL_POINTS, 1.0))

breakdown_rows = [
    {"Component": name, "Points earned": round(earned, 3), "Max points": max_pts}
    for name, (earned, max_pts) in result["breakdown"].items()
]
st.dataframe(
    breakdown_rows,
    hide_index=True,
    width="stretch",
    height=35 * (len(breakdown_rows) + 1) + 3,
)

st.divider()
st.subheader("7. How You Compare")
st.caption(
    "Historical context from ISU's published "
    f"[admission statistics]({STATS_URL}), for Class of {LATEST_CLASS_YEAR} (the most recent "
    "cycle shown). This is context only, not a guarantee — actual thresholds vary year to year."
)

latest_stats = CLASS_YEAR_STATS[LATEST_CLASS_YEAR]
gap_to_avg = total - latest_stats["avg_file_score"]
gap_direction = "above" if gap_to_avg >= 0 else "below"

comparison_message = (
    f"Your estimated score of **{total:.3f}** is **{abs(gap_to_avg):.3f} points {gap_direction}** "
    f"the average file score of **{latest_stats['avg_file_score']:.2f}** among applicants offered a "
    f"seat for the Class of {LATEST_CLASS_YEAR}."
)
st.info(comparison_message)

stats_rows = [
    {
        "Class Year": year,
        "Interview Threshold": stats["threshold"],
        "Avg. Seat-Offer Score": stats["avg_file_score"],
        "Avg. Prereq GPA": stats["avg_prereq_gpa"],
        "Avg. Science GPA": stats["avg_science_gpa"],
        "Avg. GRE Verbal %": stats["avg_gre_verbal_pct"],
        "Avg. GRE Quant %": stats["avg_gre_quant_pct"],
    }
    for year, stats in sorted(CLASS_YEAR_STATS.items())
]
st.dataframe(stats_rows, hide_index=True, width="stretch")

trend_years = sorted(CLASS_YEAR_STATS)
trend_df = pd.DataFrame(
    {
        "Class Year": [str(y) for y in trend_years],
        "Interview threshold": [CLASS_YEAR_STATS[y]["threshold"] for y in trend_years],
        "Avg. seat-offer score": [CLASS_YEAR_STATS[y]["avg_file_score"] for y in trend_years],
        "Your score": [total] * len(trend_years),
    }
)
trend_long_df = trend_df.melt("Class Year", var_name="Series", value_name="File Score")
trend_chart = (
    alt.Chart(trend_long_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("Class Year:N", title="Class Year"),
        y=alt.Y("File Score:Q", title="File Score", scale=alt.Scale(domain=[4, 6], clamp=True)),
        color=alt.Color("Series:N", title=""),
    )
)
st.altair_chart(trend_chart, use_container_width=True)

summary_lines = [
    "ISU PA Program File Score Estimate (unofficial)",
    f"Source: {SOURCE_URL}",
    "",
    f"Computed prerequisite GPA (unweighted average): {result['prereq_gpa']:.2f}",
    "",
]
for name, (earned, max_pts) in result["breakdown"].items():
    summary_lines.append(f"{name}: {earned:.3f} / {max_pts:.2f}")
summary_lines.append("")
summary_lines.append(f"TOTAL: {total:.3f} / {MAX_TOTAL_POINTS:.2f}")
summary_text = "\n".join(summary_lines)

st.download_button(
    "Download results (.txt)",
    data=io.StringIO(summary_text).getvalue(),
    file_name="isu_pa_file_score_estimate.txt",
    mime="text/plain",
)
