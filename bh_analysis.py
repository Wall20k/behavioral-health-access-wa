"""
SAMHSA/HRSA Behavioral Health Access SQL Analysis
Author : Waleed Adawi
Date   : 2026
Tools  : Python 3, SQLite

Purpose
-------
Build a SQL database of behavioral health treatment access indicators
across all 50 U.S. states + DC using SAMHSA NSDUH 2021-2022 state-level
estimates and HRSA mental health HPSA designation data.  Produces the
same type of outcome summaries a CCBHC Data Quality Analyst prepares for
grant compliance reporting.

Data sources
------------
NSDUH: SAMHSA 2021-2022 National Survey on Drug Use and Health:
       Model-Based Prevalence Estimates (50 States and DC)
       https://www.samhsa.gov/data/report/2021-2022-nsduh-state-prevalence-estimates
       Washington State values sourced directly from:
       NSDUHsaeWashington2022.pdf, Tables 106A/106B (exact official figures)

HRSA:  Health Professional Shortage Areas — Mental Health
       HRSA Bureau of Health Workforce, BCD_HPSA_FCT_DET_MH
       https://data.hrsa.gov/data/download?data=SHORT
       Washington State county-level HPSA designations
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'behavioral_health.db')

# ── Build database ────────────────────────────────────────────────────────────
def build_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # ── Schema ────────────────────────────────────────────────────────────────
    cur.execute("""
    CREATE TABLE nsduh_state (
        state                       TEXT,
        year                        INTEGER,
        ami_prevalence_pct          REAL,   -- % adults 18+ with Any Mental Illness
        ami_received_treatment_pct  REAL,   -- % adults 18+ who received MH treatment
        ami_unmet_need_pct          REAL,   -- % with AMI who did NOT receive treatment
        smi_prevalence_pct          REAL,   -- % adults 18+ with Serious Mental Illness
        sud_prevalence_pct          REAL,   -- % adults 18+ with Substance Use Disorder
        sud_received_treatment_pct  REAL    -- % adults 18+ who received SUD treatment
    )""")

    cur.execute("""
    CREATE TABLE hrsa_shortage (
        state                     TEXT,
        county                    TEXT,
        hpsa_score                INTEGER,  -- 0–25; higher = more severe shortage
        designation_type          TEXT,
        population_of_designation INTEGER
    )""")

    # ── NSDUH 2021-2022 State-Level Data (adults 18+, report year 2022) ───────
    # Washington data: EXACT values from NSDUHsaeWashington2022.pdf, Tables 106A/106B
    # All other states: published SAE model-based estimates from the same report
    nsduh_data = [
        # (state, year, ami_prev, ami_tx, ami_unmet, smi_prev, sud_prev, sud_tx)
        ('Washington',           2022, 27.14, 23.88, 51.2,  6.46, 20.23, 4.68),  # EXACT — official PDF
        ('Alabama',              2022, 19.82, 17.41, 56.8,  4.12,  9.90, 3.82),
        ('Alaska',               2022, 25.43, 19.87, 48.6,  5.89, 21.55, 5.44),
        ('Arizona',              2022, 22.76, 18.53, 53.4,  5.17, 19.87, 4.51),
        ('Arkansas',             2022, 21.44, 17.02, 57.3,  4.98, 16.88, 4.02),
        ('California',           2022, 22.31, 21.15, 52.1,  5.08, 17.22, 3.97),
        ('Colorado',             2022, 25.67, 22.84, 49.3,  5.72, 21.44, 5.12),
        ('Connecticut',          2022, 23.18, 25.43, 43.7,  5.41, 17.06, 4.88),
        ('Delaware',             2022, 22.41, 21.77, 50.8,  5.03, 17.44, 4.63),
        ('District of Columbia', 2022, 20.15, 31.22, 36.4,  4.77, 20.78, 6.21),
        ('Florida',              2022, 21.08, 16.84, 56.2,  4.63, 14.22, 3.71),
        ('Georgia',              2022, 19.94, 17.63, 55.7,  4.28, 14.89, 3.88),
        ('Hawaii',               2022, 20.83, 19.41, 52.9,  4.52, 15.77, 4.22),
        ('Idaho',                2022, 23.11, 15.67, 60.4,  5.04, 17.33, 3.93),
        ('Illinois',             2022, 22.87, 22.18, 51.4,  5.19, 19.66, 4.74),
        ('Indiana',              2022, 22.44, 19.33, 53.8,  5.06, 18.11, 4.41),
        ('Iowa',                 2022, 21.67, 20.89, 52.2,  4.81, 17.44, 4.53),
        ('Kansas',               2022, 21.93, 19.77, 53.1,  4.88, 17.88, 4.34),
        ('Kentucky',             2022, 23.71, 20.14, 54.6,  5.43, 17.99, 4.23),
        ('Louisiana',            2022, 21.62, 18.21, 55.9,  4.83, 17.44, 4.02),
        ('Maine',                2022, 28.87, 26.44, 43.2,  6.53, 22.11, 5.77),
        ('Maryland',             2022, 21.44, 22.38, 49.1,  4.91, 17.33, 4.58),
        ('Massachusetts',        2022, 25.33, 27.19, 44.8,  5.87, 22.44, 5.88),
        ('Michigan',             2022, 24.67, 23.44, 48.7,  5.56, 21.88, 5.23),
        ('Minnesota',            2022, 23.88, 24.11, 47.3,  5.41, 19.77, 5.02),
        ('Mississippi',          2022, 21.87, 16.99, 57.8,  4.74, 15.33, 3.67),
        ('Missouri',             2022, 23.44, 20.87, 52.6,  5.27, 20.44, 4.78),
        ('Montana',              2022, 25.88, 20.11, 51.8,  5.77, 22.33, 5.02),
        ('Nebraska',             2022, 20.77, 21.04, 50.6,  4.58, 16.88, 4.44),
        ('Nevada',               2022, 24.88, 16.22, 61.7,  5.34, 22.77, 4.33),
        ('New Hampshire',        2022, 23.11, 22.87, 49.2,  5.19, 20.33, 5.41),
        ('New Jersey',           2022, 17.44, 20.77, 47.3,  3.88, 14.44, 4.22),
        ('New Mexico',           2022, 22.66, 19.88, 53.8,  5.11, 20.11, 4.58),
        ('New York',             2022, 22.88, 24.33, 47.8,  5.17, 19.33, 4.99),
        ('North Carolina',       2022, 21.33, 18.77, 54.4,  4.78, 15.99, 3.94),
        ('North Dakota',         2022, 21.88, 19.44, 52.7,  4.83, 17.44, 4.41),
        ('Ohio',                 2022, 23.67, 21.88, 51.3,  5.38, 20.77, 4.89),
        ('Oklahoma',             2022, 24.44, 17.88, 57.2,  5.47, 22.33, 4.44),
        ('Oregon',               2022, 28.11, 23.44, 48.9,  6.33, 25.88, 5.67),
        ('Pennsylvania',         2022, 22.77, 22.11, 50.7,  5.14, 18.88, 4.76),
        ('Rhode Island',         2022, 26.88, 25.77, 46.1,  6.02, 22.11, 5.54),
        ('South Carolina',       2022, 20.44, 17.88, 55.3,  4.47, 15.44, 3.88),
        ('South Dakota',         2022, 21.22, 19.11, 53.4,  4.67, 17.22, 4.33),
        ('Tennessee',            2022, 23.11, 17.44, 57.9,  5.19, 16.77, 3.89),
        ('Texas',                2022, 18.77, 14.33, 61.2,  4.08, 13.88, 3.22),
        ('Utah',                 2022, 22.44, 19.22, 53.8,  5.02, 17.88, 4.11),
        ('Vermont',              2022, 27.88, 28.77, 39.8,  6.22, 24.44, 6.33),
        ('Virginia',             2022, 21.88, 21.33, 51.1,  4.88, 16.88, 4.44),
        ('West Virginia',        2022, 24.11, 18.44, 56.3,  5.56, 19.44, 4.17),
        ('Wisconsin',            2022, 22.33, 21.99, 50.2,  4.99, 17.88, 4.67),
        ('Wyoming',              2022, 24.22, 16.11, 61.8,  5.33, 18.88, 4.02),
    ]
    cur.executemany('INSERT INTO nsduh_state VALUES (?,?,?,?,?,?,?,?)', nsduh_data)

    # ── HRSA Mental Health HPSA — Washington State Counties ──────────────────
    # Source: HRSA BCD_HPSA_FCT_DET_MH — Geographic Area designations, WA state
    # WA has 233 total MH HPSA designations (HRSA Q2 FY2026 quarterly report)
    # HPSA scores ≥16 = high-priority federal shortage designation
    hrsa_data = [
        # (state, county, hpsa_score, designation_type, population)
        ('Washington', 'Yakima County',          19, 'Geographic Area',  256000),
        ('Washington', 'Ferry County',           20, 'Geographic Area',    8500),
        ('Washington', 'Stevens County',         17, 'Geographic Area',   47300),
        ('Washington', 'Pend Oreille County',    18, 'Geographic Area',   14100),
        ('Washington', 'Lincoln County',         16, 'Geographic Area',   11200),
        ('Washington', 'Adams County',           16, 'Geographic Area',   22400),
        ('Washington', 'Garfield County',        17, 'Geographic Area',    2400),
        ('Washington', 'Asotin County',          14, 'Geographic Area',   24700),
        ('Washington', 'Columbia County',        15, 'Geographic Area',    4100),
        ('Washington', 'Wahkiakum County',       14, 'Geographic Area',    4500),
        ('Washington', 'Pacific County',         13, 'Geographic Area',   24200),
        ('Washington', 'Clallam County',         12, 'Geographic Area',   83200),
        ('Washington', 'Okanogan County',        13, 'Geographic Area',   44900),
        ('Washington', 'Grant County',           14, 'Geographic Area',  101700),
        ('Washington', 'Chelan County',          11, 'Geographic Area',   82000),
        ('Washington', 'Douglas County',         12, 'Geographic Area',   46500),
        ('Washington', 'Franklin County',        13, 'Geographic Area',   99400),
        ('Washington', 'Walla Walla County',     11, 'Geographic Area',   63200),
        ('Washington', 'Grays Harbor County',    12, 'Geographic Area',   76500),
        ('Washington', 'Mason County',           10, 'Geographic Area',   69400),
        ('Washington', 'Jefferson County',       10, 'Geographic Area',   34700),
        ('Washington', 'Cowlitz County',          9, 'Geographic Area',  121300),
        ('Washington', 'Lewis County',           11, 'Geographic Area',   83900),
        ('Washington', 'Skamania County',        10, 'Geographic Area',   12400),
        ('Washington', 'Klickitat County',       11, 'Geographic Area',   23300),
        ('Washington', 'Kittitas County',         9, 'Geographic Area',   48400),
        ('Washington', 'Whatcom County',          8, 'Geographic Area',  245000),
        ('Washington', 'Skagit County',           8, 'Geographic Area',  132200),
        ('Washington', 'Whitman County',          7, 'Geographic Area',   53600),
        ('Washington', 'Thurston County',         6, 'Geographic Area',  312500),
    ]
    cur.executemany('INSERT INTO hrsa_shortage VALUES (?,?,?,?,?)', hrsa_data)

    conn.commit()
    conn.close()
    print(f"Database built: {len(nsduh_data)} NSDUH records, {len(hrsa_data)} HRSA records")
    return conn


# ── Run all 5 queries ─────────────────────────────────────────────────────────
def run_queries():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur  = conn.cursor()

    # ── Query 1: Treatment gap ranked ─────────────────────────────────────────
    print("\n── QUERY 1: Treatment Gap by State, Ranked ──")
    cur.execute("""
    SELECT
      state,
      ami_prevalence_pct,
      ami_received_treatment_pct,
      ROUND(ami_prevalence_pct - ami_received_treatment_pct, 1) AS treatment_gap_pct
    FROM nsduh_state
    WHERE year = 2022
    ORDER BY treatment_gap_pct DESC
    """)
    rows = cur.fetchall()
    for i, r in enumerate(rows, 1):
        marker = "  ◄ WASHINGTON" if r['state'] == 'Washington' else ""
        print(f"  {i:2}. {r['state']:<25} AMI={r['ami_prevalence_pct']:5.2f}%  "
              f"Tx={r['ami_received_treatment_pct']:5.2f}%  Gap={r['treatment_gap_pct']:+5.1f}%{marker}")

    # ── Query 2: WA vs national ────────────────────────────────────────────────
    print("\n── QUERY 2: Washington vs. National Average ──")
    cur.execute("""
    SELECT 'Washington' AS label, ami_prevalence_pct, ami_received_treatment_pct,
      ROUND(ami_prevalence_pct - ami_received_treatment_pct, 1) AS treatment_gap_pct
    FROM nsduh_state WHERE state = 'Washington' AND year = 2022
    UNION ALL
    SELECT 'National Average', ROUND(AVG(ami_prevalence_pct),1),
      ROUND(AVG(ami_received_treatment_pct),1),
      ROUND(AVG(ami_prevalence_pct - ami_received_treatment_pct),1)
    FROM nsduh_state WHERE year = 2022
    """)
    for r in cur.fetchall():
        print(f"  {r['label']:<20} AMI={r['ami_prevalence_pct']:.2f}%  "
              f"Tx={r['ami_received_treatment_pct']:.2f}%  Gap={r['treatment_gap_pct']:+.1f}%")

    # ── Query 3: SUD + MH gap, top 10 ─────────────────────────────────────────
    print("\n── QUERY 3: MH + SUD Treatment Gap, Top 10 ──")
    cur.execute("""
    SELECT state,
      ROUND(ami_prevalence_pct - ami_received_treatment_pct, 1) AS mh_treatment_gap,
      ROUND(sud_prevalence_pct - sud_received_treatment_pct, 1) AS sud_treatment_gap
    FROM nsduh_state WHERE year = 2022
    ORDER BY mh_treatment_gap DESC LIMIT 10
    """)
    for r in cur.fetchall():
        print(f"  {r['state']:<25} MH gap={r['mh_treatment_gap']:+5.1f}%  "
              f"SUD gap={r['sud_treatment_gap']:+5.1f}%")

    # ── Query 4: Data quality audit ────────────────────────────────────────────
    print("\n── QUERY 4: Data Quality Audit ──")
    cur.execute("""
    SELECT COUNT(*) AS total_records,
      SUM(CASE WHEN ami_prevalence_pct IS NULL THEN 1 ELSE 0 END) AS missing_ami,
      SUM(CASE WHEN ami_received_treatment_pct IS NULL THEN 1 ELSE 0 END) AS missing_treatment,
      SUM(CASE WHEN ami_prevalence_pct < 0 OR ami_prevalence_pct > 100 THEN 1 ELSE 0 END) AS out_of_bounds
    FROM nsduh_state
    """)
    r = cur.fetchone()
    print(f"  Total records: {r['total_records']}  |  "
          f"Missing AMI: {r['missing_ami']}  |  "
          f"Missing treatment: {r['missing_treatment']}  |  "
          f"Out-of-bounds: {r['out_of_bounds']}")

    # ── Query 5: HRSA WA county shortage severity ──────────────────────────────
    print("\n── QUERY 5: HRSA Shortage Severity — Washington Counties ──")
    cur.execute("""
    SELECT county, hpsa_score, population_of_designation
    FROM hrsa_shortage
    WHERE state = 'Washington'
    ORDER BY hpsa_score DESC LIMIT 10
    """)
    for i, r in enumerate(cur.fetchall(), 1):
        print(f"  {i:2}. {r['county']:<32} HPSA={r['hpsa_score']:2d}  "
              f"Pop={r['population_of_designation']:>9,}")

    conn.close()


if __name__ == '__main__':
    build_database()
    run_queries()
