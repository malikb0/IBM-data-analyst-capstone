# Results

Headline findings from the Stack Overflow 2024 Developer Survey analysis. **Every number
below was produced by a command run against the generated database** (`18,845`
respondents). Reproduce any query with:

```bash
python src/query.py "<SQL>"
```

Charts are generated into `reports/charts/` by `make report` (or `build/demo/` by `make demo`).
See [methodology.md](methodology.md) for cleaning rules and [limitations.md](limitations.md)
before drawing conclusions — all relationships are descriptive and correlational.

## Findings

1. [JavaScript is both the most-used and most-wanted language](#finding-1--javascript-is-both-the-most-used-and-most-wanted-language)
2. [Rust has the strongest forward-looking demand](#finding-2--rust-has-the-strongest-forward-looking-demand)
3. [PostgreSQL leads databases on both current use and desire](#finding-3--postgresql-leads-databases-on-both-current-use-and-desire)
4. [Remote work is associated with higher pay and higher satisfaction](#finding-4--remote-work-is-associated-with-higher-pay-and-higher-satisfaction)
5. [AI tools are already mainstream, and sentiment is broadly favourable](#finding-5--ai-tools-are-already-mainstream-and-sentiment-is-broadly-favourable)
6. [Global median pay is $65,858; the US tops large-country medians](#finding-6--global-median-pay-is-65858-the-us-tops-large-country-medians)
7. [Satisfaction factors: compensation and resources score highest](#finding-7--satisfaction-factors-compensation-and-resources-score-highest)
8. [AWS and Node.js lead their categories](#finding-8--aws-and-nodejs-lead-their-categories)

---

### Finding 1 — JavaScript is both the most-used and most-wanted language

JavaScript is used by **14,943 respondents (79.3%)** and is named first among wanted
languages (**11,541, 61.2%**). TypeScript sits close to parity: **10,709 (56.8%)** currently
use it, **10,437 (55.4%)** want to.

- Chart: [`reports/charts/chart_lang_current.png`](reports/charts/chart_lang_current.png),
  [`reports/charts/chart_lang_wanted.png`](reports/charts/chart_lang_wanted.png)
- Query:
  ```sql
  SELECT tech_name, COUNT(*) n FROM Language_have GROUP BY 1 ORDER BY n DESC LIMIT 5;
  SELECT tech_name, COUNT(*) n FROM Language_want GROUP BY 1 ORDER BY n DESC LIMIT 5;
  ```

### Finding 2 — Rust has the strongest forward-looking demand

Rust shows the largest want/have ratio of any major language: **2,284** respondents use it
and **5,597** want to — a **2.45×** ratio, far above JavaScript (**0.77×**) and TypeScript
(**0.97×**). Go (**1.71×**) and Kotlin (**1.40×**) show similar, smaller gaps.

- Chart: [`reports/charts/chart_rising_stars.png`](reports/charts/chart_rising_stars.png)
- Query:
  ```sql
  SELECT
    (SELECT COUNT(*) FROM Language_have WHERE tech_name='Rust') AS rust_have,
    (SELECT COUNT(*) FROM Language_want WHERE tech_name='Rust') AS rust_want;
  ```

### Finding 3 — PostgreSQL leads databases on both current use and desire

**11,514 (61.1%)** use PostgreSQL vs **8,556 (45.4%)** MySQL and **7,021 (37.3%)** SQLite.
PostgreSQL is the most-wanted database too (**12,193, 64.7%**). MySQL's want share
(**32.9%**) is below its current use, whereas Redis/SQLite are wanted by roughly a third.

- Chart: [`reports/charts/chart_db_current.png`](reports/charts/chart_db_current.png),
  [`reports/charts/chart_db_wanted.png`](reports/charts/chart_db_wanted.png)
- Query:
  ```sql
  SELECT tech_name, COUNT(*) n FROM Database_have GROUP BY 1 ORDER BY n DESC LIMIT 5;
  SELECT tech_name, COUNT(*) n FROM Database_want GROUP BY 1 ORDER BY n DESC LIMIT 5;
  ```

### Finding 4 — Remote work is associated with higher pay and higher satisfaction

Remote respondents report mean satisfaction **7.27/10** (n=5,091) vs **6.75/10** for
in-person (n=1,867), with hybrid in between (**7.16**). The same ordering holds for pay:
remote median **$90,712** vs in-person **$55,850**.

- Chart: [`reports/charts/chart_jobsat_remote.png`](reports/charts/chart_jobsat_remote.png),
  [`reports/charts/chart_comp_remote.png`](reports/charts/chart_comp_remote.png)
- Query:
  ```sql
  SELECT remote_work, AVG(job_sat), COUNT(*)
  FROM respondents WHERE job_sat IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
  SELECT remote_work, AVG(converted_comp_yearly), COUNT(*)
  FROM respondents WHERE converted_comp_yearly IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
  ```

### Finding 5 — AI tools are already mainstream, and sentiment is broadly favourable

**13,000 respondents (69.0%)** say they currently use AI tools; **2,424** plan to start
soon and **3,363** do not plan to. Sentiment (where given) is favourable far more often than
not: **7,458 "favorable" + 3,962 "very favorable"** vs **734 "unfavorable" + 167 "very
unfavorable"**.

- Chart: [`reports/charts/chart_ai_sentiment.png`](reports/charts/chart_ai_sentiment.png)
- Query:
  ```sql
  SELECT ai_select, COUNT(*) FROM respondents WHERE ai_select IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
  SELECT ai_sent, COUNT(*) FROM respondents WHERE ai_sent IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
  ```

### Finding 6 — Global median pay is $65,858; the US tops large-country medians

Across the **9,550** respondents who reported compensation, the median is **$65,858** and
the mean **$80,912** (capped at the 99th percentile, **$378,512**). Among countries with
30+ respondents, the highest median is the United States (**$148,000**, n=1,849).

- Chart: [`reports/charts/chart_comp_dist.png`](reports/charts/chart_comp_dist.png),
  [`reports/charts/chart_comp_country.png`](reports/charts/chart_comp_country.png)
- Query:
  ```sql
  SELECT AVG(converted_comp_yearly), MAX(converted_comp_yearly)
  FROM respondents WHERE converted_comp_yearly IS NOT NULL;
  SELECT country, AVG(converted_comp_yearly), COUNT(*)
  FROM respondents WHERE converted_comp_yearly IS NOT NULL
  GROUP BY 1 HAVING COUNT(*) >= 30 ORDER BY 2 DESC LIMIT 5;
  ```

### Finding 7 — Satisfaction factors: compensation and resources score highest

Mean overall satisfaction is **7.15/10** (median 8). Among the nine `JobSatPoints_*`
factors, **compensation (25.3)** and **resources (24.6)** score highest, while **coworkers
(8.0)** scores lowest. (These are raw item scores — see methodology.md §6 for the scale
caveat.)

- Chart: [`reports/charts/chart_jobsat_factors.png`](reports/charts/chart_jobsat_factors.png)
- Query:
  ```sql
  SELECT aspect, ROUND(AVG(score),1) avg_score, COUNT(*)
  FROM job_satisfaction_points GROUP BY 1 ORDER BY 2 DESC;
  ```

### Finding 8 — AWS and Node.js lead their categories

**AWS** is the most-used cloud platform (**10,871, 57.7%**), ahead of Azure (**6,681**) and
Google Cloud (**5,537**). **Node.js (9,230, 49.0%)** and **React (8,999)** lead web
frameworks.

- Chart: [`reports/charts/chart_platform_trends.png`](reports/charts/chart_platform_trends.png)
- Query:
  ```sql
  SELECT tech_name, COUNT(*) n FROM Platform_have GROUP BY 1 ORDER BY n DESC LIMIT 5;
  SELECT tech_name, COUNT(*) n FROM Webframe_have GROUP BY 1 ORDER BY n DESC LIMIT 5;
  ```

---

## Reproduce

```bash
make setup && make demo        # offline, on the committed sample
# or the full run:
make fetch-data && make build-db && make report
python src/query.py "SELECT COUNT(*) FROM respondents"
```

## How to read a chart

- **Denominator:** percentages are of all `18,845` respondents unless a *Data Context* line
  says otherwise. A respondent can select several values, so technology counts sum to more
  than the respondent count.
- **Capping:** `converted_comp_yearly` is clipped at the 99th percentile ($378,512); the
  top tail is truncated.
- **Descriptive, not causal:** no significance testing is claimed. "Remote work is
  associated with higher pay" does not mean remote work *causes* higher pay.
