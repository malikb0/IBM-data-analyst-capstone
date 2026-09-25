# Survey Data Analysis Report

> **Generated artifact — do not edit by hand.** This report and the charts in this
> directory are produced by `generate_report.py` from the SQLite database
> `survey_cleaned.sqlite`.
>
> - **Dataset:** Stack Overflow Developer Survey 2024 (ODbL). See `NOTICE.md`.
> - **Pipeline:** `build_database.py` → `generate_report.py` (see `METHODOLOGY.md`).
> - **Regenerate:** `make demo` (offline sample) or
>   `make fetch-data && make build-db && make report` (full run).
>
> Figures labelled *Data Context* and the summary tables below are computed at run
> time, as are the percentages quoted in the narrative. The charts are the
> authoritative source; prose is descriptive, not causal.

## Executive Summary

This report analyses the Stack Overflow 2024 Developer Survey, covering 18,845 respondents from 161 countries and territories. The pipeline cleans and normalises the survey into a relational SQLite model (40 tables), then derives the charts and findings below. The analysis covers technology trends, job satisfaction, compensation, geography, age, and AI tooling. Headline patterns: JavaScript remains the most widely used language, TypeScript and Rust show the strongest forward-looking demand, PostgreSQL leads databases, remote work correlates with higher satisfaction and pay, and AI tools are already part of many developers' workflows. All findings are descriptive and correlational (see the Discussion and `LIMITATIONS.md`).

## 1. Data Overview & Database Schema

### Dataset Summary

| Metric | Value |
|--------|-------|
| **Total Respondents** | 18,845 |
| **Columns (CSV)** | 114 |
| **Normalized Tables (SQLite)** | 40 |
| **Database Size** | 115 MB |
| **Countries Represented** | 161 |

### Data Cleaning Applied

| Column | Issue | Cleaning |
|--------|-------|----------|
| `YearsCode` / `YearsCodePro` | Text values: 'Less than 1 year', 'More than 50 years' | Mapped to 0.5 and 55 respectively |
| `ConvertedCompYearly` | Extreme outliers | Capped at the 99th percentile ($378,512); values above are clipped |
| `Age` | 'Prefer not to say' and unmapped values | Mapped to NULL |
| `Employment` | Semicolon-delimited multi-values | Normalized into `respondent_employment` (de-duplicated per respondent) |
| `DevType` | Semicolon-delimited multi-values | Normalized into `respondent_devtype` (de-duplicated per respondent) |
| `LearnCode`, `CodingActivities` | Semicolon-delimited multi-values | Normalized into separate tables (de-duplicated per respondent) |
| All 33 `*HaveWorkedWith`, `*WantToWorkWith`, `*Admired` columns | 11 categories × 3 variants, semicolon-delimited | Normalized into 33 per-category tables (de-duplicated per respondent × value) |
| `Knowledge_1` through `Knowledge_9` | Likert text responses | Mapped to numeric scores (1=Strongly disagree..5=Strongly agree); unmapped → NULL + warning |
| `JobSatPoints_*` | Scattered 0-100 scores | Normalized into `job_satisfaction_points` table with aspect labels |

### Key Null Statistics

| Column | NULL Count | % Missing |
|--------|-----------|----------|
| `converted_comp_yearly` | 9,295 | 49.3% |
| `job_sat` | 6,734 | 35.7% |
| `age_group` | 24 | 0.1% |
| `remote_work` | 6 | 0.0% |
| `ed_level` | 0 | 0.0% |

### Database Entity-Relationship Diagram

```mermaid
erDiagram
    respondents ||--o{ Language_have : references
    respondents ||--o{ Language_want : references
    respondents ||--o{ Language_admired : references
    respondents ||--o{ Database_have : references
    respondents ||--o{ Database_want : references
    respondents ||--o{ Database_admired : references
    respondents ||--o{ Platform_have : references
    respondents ||--o{ Platform_want : references
    respondents ||--o{ Platform_admired : references
    respondents ||--o{ Webframe_have : references
    respondents ||--o{ Webframe_want : references
    respondents ||--o{ Webframe_admired : references
    respondents ||--o{ Embedded_have : references
    respondents ||--o{ Embedded_want : references
    respondents ||--o{ Embedded_admired : references
    respondents ||--o{ MiscTech_have : references
    respondents ||--o{ MiscTech_want : references
    respondents ||--o{ MiscTech_admired : references
    respondents ||--o{ ToolsTech_have : references
    respondents ||--o{ ToolsTech_want : references
    respondents ||--o{ ToolsTech_admired : references
    respondents ||--o{ NEWCollabTools_have : references
    respondents ||--o{ NEWCollabTools_want : references
    respondents ||--o{ NEWCollabTools_admired : references
    respondents ||--o{ OfficeStackAsync_have : references
    respondents ||--o{ OfficeStackAsync_want : references
    respondents ||--o{ OfficeStackAsync_admired : references
    respondents ||--o{ OfficeStackSync_have : references
    respondents ||--o{ OfficeStackSync_want : references
    respondents ||--o{ OfficeStackSync_admired : references
    respondents ||--o{ AISearchDev_have : references
    respondents ||--o{ AISearchDev_want : references
    respondents ||--o{ AISearchDev_admired : references
    respondents ||--o{ respondent_employment : references
    respondents ||--o{ respondent_devtype : references
    respondents ||--o{ respondent_learn_code : references
    respondents ||--o{ respondent_coding_activities : references
    respondents ||--o{ job_satisfaction_points : references
    respondents ||--o{ knowledge_self_assessment : references

    respondents {
        int respondent_id PK
        string main_branch
        string age_group
        string remote_work
        string ed_level
        float years_code
        float years_code_pro
        string country
        float converted_comp_yearly
        float job_sat
        string icor_pm
        string industry
    }

    language_have {
        int id PK
        int respondent_id FK
        string tech_name
    }

    job_satisfaction_points {
        int id PK
        int respondent_id FK
        string aspect
        float score
    }

    knowledge_self_assessment {
        int id PK
        int respondent_id FK
        string knowledge_area
        string response
        int score
    }
```

Note: The diagram shows representative tables for brevity. The full schema includes 33 per-category technology tables (11 categories × 3 variants: have/want/admired) and 6 junction tables for employment types, developer roles, learning sources, coding activities, satisfaction points, and knowledge assessments. All per-category tech tables share the same structure as `language_have`.

### Database Schema (40 Tables)

### `respondents` (18,845 rows)
| Column | Type | Nullable |
|--------|------|----------|
| respondent_id | INTEGER | YES |
| main_branch | TEXT | YES |
| age_group | TEXT | YES |
| remote_work | TEXT | YES |
| ed_level | TEXT | YES |
| years_code | REAL | YES |
| years_code_pro | REAL | YES |
| org_size | TEXT | YES |
| country | TEXT | YES |
| converted_comp_yearly | REAL | YES |
| work_exp | REAL | YES |
| job_sat | REAL | YES |
| icor_pm | TEXT | YES |
| t_branch | TEXT | YES |
| industry | TEXT | YES |
| os_personal | TEXT | YES |
| os_professional | TEXT | YES |
| so_visit_freq | TEXT | YES |
| so_account | TEXT | YES |
| so_part_freq | TEXT | YES |
| so_comm | TEXT | YES |
| ai_select | TEXT | YES |
| ai_sent | TEXT | YES |
| ai_ben | TEXT | YES |
| ai_acc | TEXT | YES |
| ai_complex | TEXT | YES |
| ai_threat | TEXT | YES |
| ai_ethics | TEXT | YES |
| survey_length | TEXT | YES |
| survey_ease | TEXT | YES |

### `Language_have` (116,557 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Language_want` (106,356 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Language_admired` (83,523 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Database_have` (69,586 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Database_want` (65,913 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Database_admired` (49,898 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Platform_have` (50,655 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Platform_want` (48,410 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Platform_admired` (36,883 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Webframe_have` (77,803 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Webframe_want` (71,417 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Webframe_admired` (52,759 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Embedded_have` (15,629 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Embedded_want` (13,538 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `Embedded_admired` (11,486 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `MiscTech_have` (45,338 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `MiscTech_want` (47,158 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `MiscTech_admired` (30,862 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `ToolsTech_have` (99,274 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `ToolsTech_want` (87,561 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `ToolsTech_admired` (73,925 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `NEWCollabTools_have` (70,906 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `NEWCollabTools_want` (57,509 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `NEWCollabTools_admired` (51,831 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `OfficeStackAsync_have` (52,820 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `OfficeStackAsync_want` (39,934 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `OfficeStackAsync_admired` (35,419 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `OfficeStackSync_have` (68,172 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `OfficeStackSync_want` (48,988 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `OfficeStackSync_admired` (45,675 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `AISearchDev_have` (40,256 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `AISearchDev_want` (36,760 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `AISearchDev_admired` (30,736 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| tech_name | TEXT | NO |

### `respondent_employment` (23,267 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| employment_type | TEXT | NO |

### `respondent_devtype` (18,801 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| dev_type | TEXT | NO |

### `respondent_learn_code` (65,255 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| learning_source | TEXT | NO |

### `respondent_coding_activities` (40,948 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| activity | TEXT | NO |

### `job_satisfaction_points` (109,584 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| aspect | TEXT | NO |
| score | REAL | YES |

### `knowledge_self_assessment` (105,015 rows)
| Column | Type | Nullable |
|--------|------|----------|
| id | INTEGER | YES |
| respondent_id | INTEGER | NO |
| knowledge_area | TEXT | NO |
| response | TEXT | YES |
| score | INTEGER | YES |

## 2. Current vs Future Technology Trends

### 2.1 Programming Languages

#### Currently Used Languages

![Languages Currently Used](chart_lang_current.png)

**Data Context:** Based on 116,557 responses from 18,845 total respondents. Each respondent could select multiple languages. Chart shows the top 10 languages by raw count of respondents who reported using them. No outlier removal applied — all valid responses included.

**This chart shows the top 10 programming languages respondents currently use.** JavaScript leads with 14,943 respondents, followed by SQL and HTML/CSS — reflecting the web-centric nature of the developer population.

**Key Findings:**
- **JavaScript** dominates with ~79% adoption — it is the baseline requirement for modern web development.
- **SQL** ranks second (~67%), confirming that data manipulation skills are almost as universal as front-end skills.
- **HTML/CSS** ranks third (~66%), consistent with the high proportion of front-end and full-stack developers.
- **TypeScript** (~57%) has already surpassed Java and C# in current usage, marking its rapid rise.
- **Python** (~51%) rounds out the top 5, driven by data science and automation use cases.
- **Bash/Shell** and **C#** follow, reflecting systems and enterprise development respectively.

**Implications:**
- **JavaScript and TypeScript are the safest skill investments** for developers seeking broad employability.
- **SQL remains undervalued** by many junior developers but is essential across all data roles.
- **Python's position in the top 5 validates the data science career path** as mainstream, not niche.

#### Wanted Languages

![Languages Desired](chart_lang_wanted.png)

**Data Context:** Based on 106,356 responses from 18,845 total respondents. Chart shows the top 10 languages respondents expressed desire to work with. Want/have ratios are calculated as: (respondents who want the language) / (respondents who currently use it). Percentages shown are of all respondents.

**This chart shows the top 10 languages respondents want to work with — a forward-looking indicator of where developers are investing their learning time.**

**Key Findings:**
- **JavaScript** is the most-wanted language (~61%), followed by SQL and TypeScript. Raw desire is dominated by the established leaders that most respondents already use.
- **TypeScript** (~55% want vs ~57% current use) is close to parity with its current adoption, reflecting its continued growth.
- **Rust** has the strongest want/have ratio among major languages (~2.45x: 2,284 use it, 5,597 want to), a clear growth signal.
- **Go** (~30%) and **Kotlin** (~0%) show solid desire, reflecting cloud-native and Android ecosystem trends.
- **JavaScript** and **HTML/CSS** have lower want/have ratios (<1) relative to current usage — they are mature, 'solved' skills for many respondents.

**Implications:**
- **TypeScript combines high current usage (57%) with strong, sustained desire (55%)** — a stable skill investment.
- **Rust and Go represent the biggest 'gap' opportunities** — fewer developers know them but many want to learn.
- **Python demand is sustained by AI/ML growth**, not just current data science roles.

### 2.2 Databases

#### Currently Used Databases

![Databases Currently Used](chart_db_current.png)

**Data Context:** Based on 69,586 responses from 18,845 total respondents. Chart shows the top 10 databases by raw adoption count. No data cleaning applied beyond the standard ConvertedCompYearly cap at the 99th percentile.

**This chart shows the top 10 databases respondents currently use.** PostgreSQL leads with the highest adoption, followed by MySQL, SQLite, and MongoDB.

**Key Findings:**
- **PostgreSQL** is the most used database, reflecting its open-source nature, strong feature set, and enterprise adoption.
- **MySQL** ranks second and **SQLite** third, driven respectively by legacy web stacks and by ubiquity in mobile, embedded, and local development.
- **MongoDB** leads the NoSQL category, confirming its place as the default document database.
- **Redis** and **Elasticsearch** show strong usage in caching and search use cases respectively.
- **Microsoft SQL Server** remains relevant in enterprise .NET environments.

**Implications:**
- **PostgreSQL expertise is the most valuable database skill** for broad employability.
- **SQLite's high rank confirms that every developer needs embedded/local database skills**, regardless of role.

#### Wanted Databases

![Databases Desired](chart_db_wanted.png)

**Data Context:** Based on 65,913 responses. Percentages are of all 18,845 respondents. The 'want ratio' compares desired vs current usage to identify growth trends.

**This chart shows the top 10 databases respondents want to work with — revealing where database interest is migrating.**

**Key Findings:**
- **PostgreSQL** also tops the wanted list (12,193 respondents, ~65% of all respondents), confirming its dominance and continued growth trajectory.
- **Redis, SQLite, MySQL, and MongoDB** follow, showing desire spread across relational and non-relational stores.
- Several low-adoption databases show high want/have ratios (e.g. CockroachDB, DuckDB, Cassandra, ClickHouse) — early growth signals, though absolute counts remain small.
- **MySQL** has a lower want share (33%) than current use (45%), consistent with a gradual shift toward PostgreSQL.
- **Cloud databases** (DynamoDB, BigQuery, Supabase, Firebase) appear in the wanted list, reflecting cloud migration trends.

**Implications:**
- **PostgreSQL is the safest database skill investment** for the next 3-5 years.
- **MySQL knowledge is in relative decline** — its want share (33%) is below its current use (45%).
- **Emerging analytical/NewSQL databases (DuckDB, ClickHouse, CockroachDB) are worth watching**, but current absolute adoption is small.
- **Cloud-native databases (DynamoDB, BigQuery) are growing fast** — cloud skills complement database skills.

### 2.3 Cloud Platforms

![Platform Trends](chart_platform_trends.png)

**Data Context:** Based on 50,655 current-use responses and 48,410 desired responses. Chart shows the top 10 platforms by current usage count, overlaid with the corresponding desire counts. No data filtering applied beyond the standard cleaning pipeline.

### 2.4 Rising Stars (Want/Have Ratio > 1.5)

![Rising Stars](chart_rising_stars.png)

**Data Context:** Computed from all 18,845 respondents across all 11 technology categories. The want/have ratio is calculated as: (respondents who want the technology) / (respondents who currently use it). Only technologies with at least 30 current users are included to ensure statistical relevance. A ratio > 1.5 indicates strong demand relative to current supply — signaling growth opportunities.

### 2.5 Declining Technologies (Want/Have Ratio < 0.7)

![Declining Tech](chart_declining_tech.png)

**Data Context:** Same methodology as Rising Stars above. A ratio < 0.7 indicates weaker demand relative to current usage, suggesting the technology is losing relevance. Technologies with fewer than 30 current users are excluded.

## 3. Job Satisfaction Analysis

### 3.1 Overall Distribution

![Job Satisfaction Distribution](chart_jobsat_dist.png)

**Data Context:** Based on 12,111 respondents who provided a job satisfaction score (0-10 scale). 6,734 respondents (35.7%) did not answer this question and are excluded. No outlier removal — satisfaction scores are ordinal by design.

- Mean satisfaction: 7.15 / 10
- Median satisfaction: 8.00 / 10
- Most common rating: 8 / 10

### 3.2 What Makes Developers Satisfied?

![Satisfaction Factors](chart_jobsat_factors.png)

**Data Context:** Based on 109,584 individual satisfaction-aspect ratings across 9 aspects (career satisfaction, coworkers, work-life balance, compensation, resources, autonomy, growth, management, retention). Each aspect is scored 0-100. Chart shows the average score per aspect. Respondents could rate multiple aspects.

### 3.3 Satisfaction by Work Arrangement

![Satisfaction by Remote](chart_jobsat_remote.png)

**Data Context:** Based on 12,108 respondents who reported both job satisfaction and remote work status. Chart shows the average satisfaction (0-10) for each work arrangement category. Remote workers, hybrid workers, and in-person workers are compared directly — no filtering or normalization applied.

### 3.4 Satisfaction by Developer Role

![Satisfaction by Dev Type](chart_jobsat_devtype.png)

**Data Context:** Based on 18,801 developer role assignments across 18,845 respondents (multi-select). Only roles with 50+ respondents are included to ensure statistical significance. Chart shows the top 10 roles by average satisfaction.

### 3.5 Satisfaction by Country

![Satisfaction by Country](chart_jobsat_country.png)

**Data Context:** Based on respondents with both country and satisfaction data. Only countries with 50+ respondents are included. Chart shows the top 10 countries by average job satisfaction. Smaller countries are excluded to avoid sampling bias.

### 3.6 Satisfaction by Age Group

![Satisfaction by Age](chart_jobsat_age.png)

**Data Context:** Based on 12,095 respondents. Age groups follow the standard Stack Overflow survey categories. The 'Prefer not to say' group is excluded. Chart shows the line trend across age brackets — no smoothing applied.

### 3.7 Individual Contributor vs Manager

![IC vs Manager](chart_jobsat_icpm.png)

**Data Context:** Based on respondents who identified as either Individual Contributor (IC) or People Manager. Chart compares average satisfaction between the two groups. All valid responses included — no minimum count threshold.

## 4. Compensation Distribution & Analysis

### 4.1 Overall Distribution

![Compensation Distribution](chart_comp_dist.png)

**Data Context:** Based on 9,550 respondents (9,295 missing, 49.3% of total). Compensation is capped at the 99th percentile ($378,512) to handle extreme outliers; values above the cap are clipped to it.

- **Mean**: $80,912
- **Median**: $65,858
- **Range**: $1 – $378,512

### 4.2 Median Compensation by Country

![Compensation by Country](chart_comp_country.png)

**Data Context:** Based on respondents with non-null compensation and country. Only countries with 30+ respondents are included. Chart shows the top 10 countries by median compensation. Compensation is capped at the 99th percentile as described above.

### 4.3 Median Compensation by Developer Role

![Compensation by Dev Type](chart_comp_devtype.png)

**Data Context:** Based on 18,801 developer role assignments with non-null compensation. Only roles with 50+ respondents are included. Chart shows the top 10 roles by median compensation. Multi-role respondents are counted in each role they selected.

### 4.4 Median Compensation by Education Level

![Compensation by Education](chart_comp_edlevel.png)

**Data Context:** Based on respondents with non-null compensation and education level. All education levels meeting the minimum threshold are shown, sorted by median compensation descending. No minimum count filter applied due to the smaller number of distinct categories.

### 4.5 Median Compensation by Age Group

![Compensation by Age](chart_comp_age.png)

**Data Context:** Based on respondents with non-null compensation and age group. Age groups sorted in natural order. The 'Prefer not to say' group excluded. Compensation shown as median to reduce skew effects within each age bracket.

### 4.6 Median Compensation by Work Arrangement

![Compensation by Remote](chart_comp_remote.png)

**Data Context:** Based on respondents with non-null compensation and remote work status. Chart shows median compensation (not mean) to reduce the impact of compensation outliers within each work arrangement category.

### 4.7 Experience vs Compensation by Age Group

![Experience vs Comp](chart_comp_exp_age.png)

**Data Context:** Based on respondents with non-null professional years of coding and compensation. Compensation filtered to exclude values above $500K for visual clarity (extreme outliers removed). Each point represents one respondent. Color-coded by age group to reveal age-related experience-compensation patterns. Alpha blending (0.3) used to show density. Total points shown: 9,528.

### 4.8 Dev Role: Compensation vs Satisfaction

![Dev Role Comp vs Sat](chart_devtype_comp_sat.png)

**Data Context:** Based on 18,801 developer role assignments with both non-null compensation and satisfaction. Roles with fewer than 30 respondents are excluded. Bubble size reflects the number of respondents in each role. Axes show average compensation and average satisfaction per role.

## 5. Geographic Technology Distribution

### 5.1 Top 10 Countries × Top 10 Languages (Adoption %)

![Geographic Heatmap](chart_geo_heatmap.png)

**Data Context:** Based on 18,845 respondents across the top 10 countries by respondent count. Shows the adoption rate (%) of the top 10 programming languages within each country. Percentages are calculated as: (respondents in country C who use language L) / (total respondents in country C). Values range from 0% to 100% across the heatmap. Darker red indicates higher adoption.

## 6. Age Group Technology Preferences

### 6.1 Language Adoption Across Age Groups

![Age Language Stacked](chart_age_lang_stacked.png)

**Data Context:** Based on 18,845 respondents across 7 age brackets. Shows the stacked percentage of the top 8 programming languages used within each age group. Percentages are stacked within each age group to sum to 100% (representing the proportion of all language mentions). The 'Prefer not to say' age group is excluded. Each age bar represents the distribution of language mentions by respondents in that bracket.

## 7. Extra Insights & Relationship Analysis

### 7.1 Remote Work Adoption by Developer Role

![Remote by Dev Type](chart_remote_devtype.png)

**Data Context:** Based on 18,801 developer role assignments with non-null remote work status. Chart shows the top 10 developer roles by remote work adoption percentage. Only roles with 50+ total respondents are included. Percentage = (respondents in role who work remotely) / (total respondents in role).

### 7.2 AI Sentiment & Age Group Patterns

![AI Sentiment](chart_ai_sentiment.png)

**Data Context:** Based on 15,396 respondents who provided AI sentiment data. Pie chart shows the distribution of self-reported attitudes toward AI tools. The top 7 sentiment categories are shown individually; all remaining categories are grouped into 'Other'. Percentages sum to 100%.

![AI by Age Group](chart_ai_age.png)

**Data Context:** Based on 18,763 respondents who reported both AI tool selection and age group. Stacked bar chart shows the distribution of the top 5 AI tools selected within each age bracket. Percentages sum to 100% per age group. The 'Prefer not to say' age group is excluded.

### 7.3 Knowledge Self-Assessment

![Knowledge Scores](chart_knowledge.png)

**Data Context:** Based on 105,015 self-assessment ratings across 9 knowledge areas. Scores use a Likert scale: 1 (Strongly disagree) to 5 (Strongly agree). Chart shows the average score per knowledge area. All valid responses included — no filtering applied.

![Knowledge Correlations](chart_knowledge_corr.png)

**Data Context:** Based on the subset of respondents with non-null knowledge scores, job satisfaction, and compensation. Bar chart shows the Pearson correlation between each knowledge area score and (a) job satisfaction, (b) compensation. Positive values indicate that higher self-assessed knowledge correlates with higher satisfaction/compensation.

### 7.4 Learning Pathways and Compensation

![Learning Compensation](chart_learn_comp.png)

**Data Context:** Based on 65,255 learning source responses from respondents with non-null compensation. Only learning sources with 50+ respondents are included. Chart shows median compensation (not mean) to reduce skew from high earners within each learning pathway. Respondents could select multiple learning sources.

### 7.5 Compensation by Employment Type

![Employment Compensation](chart_emp_comp.png)

**Data Context:** Based on respondents with non-null compensation and employment type. Only employment types with 100+ respondents are included. Chart shows the top 10 employment types by average compensation. Respondents could select multiple employment types.

### 7.6 Technology Migration: What Python Devs Want Next

![Python Migration](chart_python_migration.png)

**Data Context:** Based on 9,590 respondents who currently use Python. Chart shows the top 10 languages these Python developers want to learn next. Python itself is excluded from the results. Raw counts represent the number of Python users who also expressed desire for each target language.

### 7.7 Work Arrangement × Compensation × Satisfaction Matrix

![Remote Comp Sat Matrix](chart_remote_comp_sat_matrix.png)

**Data Context:** Based on 6,872 respondents with non-null compensation, satisfaction, and remote work status. Compensation is bucketed into 4 tiers: Low (<$30K), Medium-Low ($30-70K), Medium-High ($70-120K), High (>$120K). Cell values show average job satisfaction (0-10 scale). Color scale: Green = higher satisfaction, Red = lower satisfaction (range 5-8).

### 7.8 Country × Remote Work × Compensation

![Country Remote Comp](chart_country_remote_comp.png)

**Data Context:** Based on respondents from the top 10 countries by remote worker count. Only respondents with non-null compensation and remote work status are included. Bars show median compensation for remote vs in-person workers within each country. Countries sorted by remote worker median compensation.

### 7.9 Stack Overflow Engagement Patterns

![SO Visit Frequency](chart_so_visit.png)

**Data Context:** Based on all 18,845 respondents with non-null Stack Overflow visit frequency. Chart shows the distribution of visit frequencies. Categories are ordered from most to least frequent. No filtering applied.

![SO Participation Compensation](chart_so_comp.png)

**Data Context:** Based on respondents with non-null compensation and SO participation frequency. Only frequency categories with 50+ respondents are included. Chart shows average compensation by participation level. Results should be interpreted as correlational, not causal.

### 7.10 Employment Type Distribution

![Employment Distribution](chart_employment_dist.png)

**Data Context:** Based on 23,267 employment type responses from 18,845 respondents (multi-select). Chart shows the top 10 most common employment types by raw count. Each respondent could select multiple employment types.

---

## Discussion

### Technology Trends
The technology landscape revealed by this survey confirms several well-known trends while surfacing emerging patterns. The JavaScript ecosystem continues to dominate current usage, while TypeScript has risen to near parity between current use and desire — a signal of the shift toward type safety at scale in large codebases. Rust shows the strongest desire relative to current adoption, a forward-looking signal rather than current dominance.

Rust and Go represent the most significant 'adoption gap' opportunities: relatively few developers currently use them, but demand is disproportionately high. For organizations hiring, prioritizing Rust or Go skills may yield access to a smaller but highly motivated talent pool.

PostgreSQL's lead over MySQL in both current and desired usage confirms a long-anticipated tipping point. MySQL, once the default open-source relational database, now has a lower want share than current use. Emerging analytical/NewSQL databases such as DuckDB show high want/have ratios from a small base — interest worth watching rather than current dominance.

### Job Satisfaction
The mean satisfaction score of approximately 7.1/10 suggests moderate-to-high overall satisfaction. Among the individual satisfaction factors, **compensation** and **resources** score highest on average, while **coworkers** scores lowest. (See METHODOLOGY.md for how the factor scores are derived.)

Remote workers report higher average satisfaction than in-person workers, with hybrid workers in between. In this dataset, average satisfaction rises with age across the reported brackets (though the oldest brackets have small sample sizes). See the satisfaction-by-age chart for the exact shape rather than assuming a mid-career peak.

### Compensation Dynamics
The compensation analysis reveals substantial geographic variation. Among countries with at least 30 respondents, the highest national median is United States of America ($148,000), against a global median of $65,858. The positive correlation between remote work and compensation is partly explained by geographic arbitrage: remote workers based in lower-cost regions can earn salaries benchmarked to higher-cost markets.

The experience-compensation chart shows a steep rise in average pay over the first ~15 years of professional coding, after which it flattens while the spread widens — suggesting that career progression (management, specialisation, or entrepreneurship) matters more than additional years of experience alone.

### AI & The Future of Development
AI sentiment in this dataset is broadly favourable: favorable and very-favorable responses substantially outnumber unfavorable ones, with an indifferent/unsure minority. The age-based analysis of AI tool selection shows that younger developers are more likely to report using AI tools, suggesting AI-assisted development will become increasingly normative as this cohort progresses in their careers.

### Methodological Considerations
Several limitations should be noted. The survey is self-selected and may over-represent certain demographics (English speakers, Stack Overflow users, web developers). Compensation data has notable missingness (49%), which may introduce bias. The technology category definitions are fixed by the survey design and may not capture all relevant tools. The cross-sectional nature of the data means all relationships are correlational — causal inferences require caution.

---

## Summary of Key Findings

1. **Technology Trends**: JavaScript remains dominant (79% adoption) and is also the most-wanted language (61%). TypeScript is close to parity between current use (57%) and desire (55%), and Rust has the strongest want/have ratio among major languages (~2.45x). PostgreSQL has overtaken MySQL as the leading database.

2. **Job Satisfaction**: Average satisfaction is 7.1/10. **compensation** and **resources** rank highest among the individual satisfaction factors. Remote workers are most satisfied. Individual Contributors and Managers report similar satisfaction levels.

3. **Compensation**: Global median compensation is $65,858. Among countries with at least 30 respondents, the highest national median is United States of America ($148,000). Engineering managers, DevOps specialists, and senior executives top the compensation charts. Remote work correlates with higher pay across most countries. Compensation-education correlation exists but is weaker than compensation-experience.

4. **Geography**: The country×language heatmap shows JavaScript near the top of the language mix across all large countries in the dataset, with country-level differences in the relative adoption of TypeScript and Python. Differences for smaller countries should be read cautiously (see §5.1).

5. **Age**: The language mix and AI-tool selection vary by age group (see §6.1 and §7.2). The experience-compensation chart shows pay rising steeply early in a career and flattening afterwards, with widening variance.

6. **AI & Learning**: AI sentiment in this dataset is broadly favourable — favorable and very-favorable responses far outnumber unfavorable ones. Median compensation varies by learning source; see the learning-pathway chart rather than assuming a single ranking.

7. **Work Patterns**: Remote work is associated with higher average satisfaction and higher median pay than in-person work, with hybrid work in between. These are descriptive correlations (see §4.6, §3.3, and LIMITATIONS.md).

---

## Implications & Recommendations

### For Developers
- **Invest in TypeScript** — it offers the best risk/reward ratio for career development, with both high current demand and strong growth trajectory.
- **Learn PostgreSQL** if you work with databases — it is the clear market leader with sustained growth momentum.
- **Consider Rust or Go** if you want to differentiate yourself — demand far outstrips current supply, creating premium positioning.
- **Prioritize remote-capable roles** — they correlate with higher satisfaction and compensation across nearly all comparisons.

### For Employers
- **Support TypeScript adoption** in your tech stack — it improves developer productivity and makes your company more attractive to top talent.
- **Offer remote and hybrid options** — the satisfaction and retention benefits are clear across all compensation levels.
- **Invest in mid-career retention** — the 35-44 age bracket is the satisfaction peak and represents your most productive engineers.
- **Build AI-assisted development workflows** — the next generation of developers expects AI tooling as part of their standard toolkit.

### For Educators & Training Providers
- **TypeScript and Python should be core curriculum** — they represent both current demand and future growth.
- **Emerging analytical databases (e.g. DuckDB) and cloud databases deserve curriculum attention** — they show strong want/have ratios from a small current base.
- **Bootcamps and self-directed learning are validated pathways** — the market rewards skill over credentials.

### For the Industry
- **The remote work trend is structural, not cyclical** — organizations that resist it will face talent acquisition challenges.
- **AI tools will become standard equipment**, not optional — prepare for widespread AI-assisted development within 3-5 years.
- **The MySQL→PostgreSQL migration will continue** — plan your data infrastructure investments accordingly.

---

## Conclusion

The 2024 Stack Overflow Developer Survey reveals a developer ecosystem in transition. The technology landscape is being reshaped by the continued dominance of JavaScript, the maturation of TypeScript, the PostgreSQL ascendancy, and the early but accelerating impact of AI tools. Job satisfaction is moderate-to-high on average, and its factor scores are led by **compensation** and **resources** in this dataset. Remote work has cemented its place as a structural feature of the industry, correlating positively with both satisfaction and earnings.

For developers, the message is clear: invest in TypeScript, PostgreSQL, and cloud-native skills; prioritize remote-capable roles; and prepare for AI-assisted development as the new normal. For employers, the data supports investing in developer experience, offering flexible work arrangements, and modernizing technology stacks to attract and retain top talent.

The common thread across all analyses is that the industry is becoming more specialized, more distributed, and more tool-augmented. Developers who embrace these trends — by learning modern languages, working remotely, and leveraging AI tools — position themselves for the strongest career outcomes.