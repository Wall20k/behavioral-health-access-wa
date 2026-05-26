# Behavioral Health Treatment Gap Analysis — Washington State

**Tools:** Python 3 · SQLite · pandas · matplotlib  
**Data:** SAMHSA NSDUH 2021–2022 · HRSA Health Professional Shortage Areas  
**Author:** Waleed Adawi · 2026

---

## Problem

Millions of Americans who meet clinical criteria for a mental health condition never receive treatment. For state agencies and federally-funded behavioral health clinics — particularly Certified Community Behavioral Health Clinics (CCBHCs), which are required to document treatment access and unmet need for grant compliance — quantifying this gap at the state and county level is a core data quality function.

This project builds a SQLite database from two federal datasets, runs SQL-based audit and analysis queries across all 50 states and DC, and produces clean outputs suited to the kind of summary reporting a CCBHC Data Quality Analyst prepares. The Yakima, Washington service area context is deliberate: Yakima County ranks among Washington's highest-severity mental health provider shortage areas, making the statewide treatment gap directly relevant to local CCBHC operations.

---

## Data Sources

| Dataset | Source | Access Date |
|---|---|---|
| NSDUH 2021–2022 Model-Based State Prevalence Estimates (50 States + DC) | [SAMHSA](https://www.samhsa.gov/data/report/2021-2022-nsduh-state-prevalence-estimates) | May 2026 |
| Washington State NSDUH Tables 106A/106B (exact SAE figures) | [NSDUHsaeWashington2022.pdf](https://www.samhsa.gov/data/sites/default/files/reports/rpt42728/NSDUHsaeWashington2022.pdf) | May 2026 |
| Mental Health HPSA Designations — Washington County-Level | [HRSA BCD_HPSA_FCT_DET_MH](https://data.hrsa.gov/data/download?data=SHORT) | May 2026 |

Washington State AMI and treatment values (27.14% prevalence, 23.88% received treatment) are sourced directly from the official SAMHSA state-specific PDF using the Small Area Estimation (SAE) hierarchical Bayes methodology. All 51 records (50 states + DC) were loaded into SQLite and validated before analysis.

---

## Key Findings

- **Washington's mental health treatment gap is 3.3 percentage points** — ranking 17th of 51 (where rank 1 = largest gap). That means 16 states and DC have a larger unmet need rate than Washington, but WA's gap still exceeds the national average.
- **Washington's gap exceeds the national average by 1.1 pp** (3.3% vs. 2.2%). With 27.14% AMI prevalence — one of the highest rates in the country — the absolute number of people not receiving care is large even if the gap percentage is mid-tier.
- **Washington's substance use disorder treatment gap is 15.6%**, more than four times the mental health gap. CCBHC programs treat both MH and SUD, making the SUD gap directly relevant to capacity planning.
- **Yakima County HPSA score: 19 out of 25**, ranking 2nd in Washington for mental health provider shortage severity. Six WA counties meet or exceed the federal high-priority threshold (score ≥ 16).
- **Data quality audit: zero integrity violations** across all 51 records — no null AMI values, no null treatment values, no out-of-bounds percentages.

---

## Visualizations

### Treatment Gap by State — Top 20 (Washington highlighted)

![Top 20 States by Treatment Gap](outputs/FIG1_T~1.PNG)

Nevada, Wyoming, and Idaho top the ranking with gaps above 7%. Washington sits at 17th — meaningfully above the national midpoint, and above its regional neighbors Oregon (10th) and Idaho (3rd).

---

### Washington State vs. National Average

![WA vs National Average](outputs/fig2_wa_vs_national.png)

Washington's higher AMI prevalence (27.14% vs. 23.00% nationally) is not matched by a proportionally higher treatment rate, widening the gap relative to the national average. This pattern is consistent with SAMHSA's finding that high-prevalence states do not necessarily achieve higher treatment penetration.

---

### Washington County HPSA Scores — Top 10 (Yakima highlighted)

![WA County HPSA Scores](outputs/fig3_yakima_hpsa_rank.png)

Yakima County's HPSA score of 19 places it second in Washington, trailing only Ferry County (score 20). Scores above 16 qualify for federal designation as high-priority shortage areas, triggering eligibility for NHSC loan repayment and J-1 visa waivers — both relevant to CCBHC provider recruitment context.

---

## Methodology

```
bh_analysis.py
│
├── build_database()
│   ├── CREATE TABLE nsduh_state     — 51 rows (states + DC), NSDUH SAE estimates
│   └── CREATE TABLE hrsa_shortage   — 30 rows (WA counties), HPSA designations
│
├── Query 1: Treatment gap rank      — ORDER BY gap DESC, RANK() OVER WINDOW
├── Query 2: WA vs national          — GROUP BY aggregate, single-row JOIN
├── Query 3: MH + SUD combined gaps  — dual-column gap for top-10 worst states
├── Query 4: Data quality audit      — COUNT(*), SUM(CASE...) null/bounds checks
└── Query 5: WA county HPSA rank     — RANK() OVER, hpsa_score DESC
```

**Treatment gap** is calculated as `ami_prevalence_pct − ami_received_treatment_pct`. A positive value means more people have AMI than are receiving treatment; a negative value (seen in DC, NJ, MA, CT) indicates that treatment utilization — counting people who seek care from outside their home state — exceeds in-state prevalence estimates.

**HPSA scores** range 0–25. Scores are assigned by HRSA based on population-to-provider ratio, poverty rate, and travel distance to nearest care. Scores ≥ 16 qualify for federal high-priority designation.

---

## Repo Structure

```
behavioral-health-access-analysis/
├── README.md
├── bh_analysis.py              ← builds DB, runs all 5 queries, prints results
├── data/
│   ├── nsduh_state_estimates.csv   ← all 51 states, all 8 metrics
│   └── hrsa_hpsa_wa.csv            ← 30 WA county HPSA designations
└── outputs/
    ├── treatment_gap_by_state.csv  ← ranked gap table, all 51 states
    ├── wa_vs_national.csv          ← 2-row comparison
    ├── yakima_shortage_rank.csv    ← WA counties ranked by HPSA score
    ├── fig1_treatment_gap_ranking.png
    ├── fig2_wa_vs_national.png
    └── fig3_yakima_hpsa_rank.png
```

---

## Running the Analysis

```bash
# Install dependencies
pip install matplotlib seaborn

# Build the database and run all queries
python bh_analysis.py
```

The script prints all query results to stdout and builds `behavioral_health.db` in the same directory. Output CSVs and charts are saved to `outputs/`.

---

## Context: Why This Matters for CCBHC Reporting

CCBHCs are required under federal certification standards to collect and report on population-level behavioral health need and treatment utilization within their service areas. The data quality checks in Query 4 mirror the kind of completeness audits required before submitting federal demonstration grant reports. The county-level HPSA analysis in Query 5 directly corresponds to the workforce shortage documentation that CCBHCs in Yakima submit to HRSA and SAMHSA as part of their planning process.

This analysis replicates the type of work a CCBHC Data Quality Analyst performs when preparing state and county context for grant applications, annual reports, and needs assessments.
