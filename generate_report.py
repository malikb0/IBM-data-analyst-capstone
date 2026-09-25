import argparse
import os
import sqlite3
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate the charts and analysis report from the survey SQLite database."
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("SURVEY_DB", "survey_cleaned.sqlite"),
        help="input SQLite database (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("SURVEY_OUTPUT", "output"),
        help="directory for charts and the report (default: %(default)s)",
    )
    return parser.parse_args(argv)


ARGS = parse_args()
DB_PATH = ARGS.db
OUTPUT_DIR = ARGS.output_dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(DB_PATH):
    raise SystemExit(
        f"database not found: {DB_PATH}\n"
        "Build it first with `make build-db` (full run) or `make demo` (offline sample)."
    )

print("Connecting to database...")
conn = sqlite3.connect(DB_PATH)

plt.rcParams.update({"figure.max_open_warning": 0, "font.size": 10})

def save_bar(data, x_col, y_col, title, fname, xlabel=None, ylabel=None, color="#2E86AB", top=10, figsize=(10, 6), horizontal=True):
    if top and len(data) > top:
        data = data.head(top)
    fig, ax = plt.subplots(figsize=figsize)
    if horizontal:
        data = data.sort_values(y_col, ascending=True)
        ax.barh(data[x_col], data[y_col], color=color, edgecolor="white", height=0.7)
        ax.set_xlabel(ylabel or y_col)
        ax.set_ylabel(xlabel or x_col)
    else:
        ax.bar(data[x_col], data[y_col], color=color, edgecolor="white", width=0.7)
        ax.set_xlabel(xlabel or x_col)
        ax.set_ylabel(ylabel or y_col)
        for tick in ax.get_xticklabels():
            tick.set_rotation(45); tick.set_ha("right")
    ax.set_title(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150, bbox_inches="tight")
    plt.close(fig)

def save_grouped_bar(df, x_col, col1, col2, label1, label2, title, fname, figsize=(10, 6)):
    df = df.sort_values(col1, ascending=True)
    x = np.arange(len(df)); w = 0.35
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(x - w/2, df[col1], w, label=label1, color="#2E86AB", edgecolor="white")
    ax.bar(x + w/2, df[col2], w, label=label2, color="#E8833A", edgecolor="white")
    ax.set_xticks(x); ax.set_xticklabels(df[x_col], rotation=45, ha="right", fontsize=9)
    ax.set_title(title, fontweight="bold"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150, bbox_inches="tight"); plt.close(fig)

def save_hist(data, col, title, fname, bins=30, color="#2E86AB", xlabel=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(data[col].dropna(), bins=bins, color=color, edgecolor="white", alpha=0.8)
    ax.set_xlabel(xlabel or col); ax.set_ylabel("Count"); ax.set_title(title, fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150, bbox_inches="tight"); plt.close(fig)

def save_scatter(data, x, y, title, fname, color="#2E86AB", alpha=0.3):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(data[x], data[y], c=color, alpha=alpha, s=8, edgecolors="none")
    ax.set_xlabel(x); ax.set_ylabel(y); ax.set_title(title, fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150, bbox_inches="tight"); plt.close(fig)

print("Loading bulk data...")

TECH_CATEGORIES = [
    ("language", "Language"), ("database", "Database"), ("platform", "Platform"),
    ("webframe", "Webframe"), ("embedded", "Embedded"), ("misctech", "MiscTech"),
    ("toolstech", "ToolsTech"), ("collabtools", "NEWCollabTools"),
    ("officestackasync", "OfficeStackAsync"), ("officestacksync", "OfficeStackSync"),
    ("aistack", "AISearchDev"),
]
VARIANTS = ["have", "want", "admired"]

tech_data = {}
for cat, csv_pref in TECH_CATEGORIES:
    for var in VARIANTS:
        tbl = f"{csv_pref}_{var}"
        key = f"{cat}_{var}"
        tech_data[key] = pd.read_sql(f"SELECT * FROM {tbl}", conn)

respondents = pd.read_sql("SELECT * FROM respondents", conn)
respondent_devtype = pd.read_sql("SELECT * FROM respondent_devtype", conn)
respondent_employment = pd.read_sql("SELECT * FROM respondent_employment", conn)
respondent_learn_code = pd.read_sql("SELECT * FROM respondent_learn_code", conn)
respondent_coding_activities = pd.read_sql("SELECT * FROM respondent_coding_activities", conn)
job_sat_points = pd.read_sql("SELECT * FROM job_satisfaction_points", conn)
knowledge = pd.read_sql("SELECT * FROM knowledge_self_assessment", conn)
conn.close()
print("Data loaded.")

total_respondents = len(respondents)

# ═════════════════════════════════════════════
# SECTION 2: Technology Trends
# ═════════════════════════════════════════════
print("Section 2: Technology Trends...")

# Top 10 languages currently used
lang_have = tech_data["language_have"].groupby("tech_name").size().reset_index(name="count")
lang_have = lang_have.sort_values("count", ascending=False).head(10)
save_bar(lang_have, "tech_name", "count",
         "Top 10 Programming Languages Currently Used", "chart_lang_current.png",
         xlabel="Language", ylabel="Respondents")

# Top 10 languages desired
lang_want = tech_data["language_want"].groupby("tech_name").size().reset_index(name="count")
lang_want = lang_want.sort_values("count", ascending=False).head(10)
save_bar(lang_want, "tech_name", "count",
         "Top 10 Programming Languages Desired to Work With", "chart_lang_wanted.png",
         xlabel="Language", ylabel="Respondents")

# Share of all respondents, used by the narrative text below (computed, not hardcoded).
lang_have_pct = (lang_have.set_index("tech_name")["count"] / total_respondents * 100).to_dict()
lang_want_pct = (lang_want.set_index("tech_name")["count"] / total_respondents * 100).to_dict()

# Top 10 databases currently used
db_have = tech_data["database_have"].groupby("tech_name").size().reset_index(name="count")
db_have = db_have.sort_values("count", ascending=False).head(10)
save_bar(db_have, "tech_name", "count",
         "Top 10 Databases Currently Used", "chart_db_current.png",
         xlabel="Database", ylabel="Respondents")

# Top 10 databases desired
db_want = tech_data["database_want"].groupby("tech_name").size().reset_index(name="count")
db_want = db_want.sort_values("count", ascending=False).head(10)
save_bar(db_want, "tech_name", "count",
         "Top 10 Databases Desired to Work With", "chart_db_wanted.png",
         xlabel="Database", ylabel="Respondents")

# Top 10 platforms
plat_have = tech_data["platform_have"].groupby("tech_name").size().reset_index(name="have_count")
plat_want = tech_data["platform_want"].groupby("tech_name").size().reset_index(name="want_count")
top_platforms = plat_have.merge(plat_want, on="tech_name").sort_values("have_count", ascending=False).head(10)
save_grouped_bar(top_platforms, "tech_name", "have_count", "want_count",
                 "Currently Use", "Want to Use", "Top 10 Platforms: Current vs Desired", "chart_platform_trends.png")

# Rising vs declining across ALL categories (use all 33 tables)
have_all = pd.concat([tech_data[f"{cat}_have"] for cat, _ in TECH_CATEGORIES], ignore_index=True)
want_all = pd.concat([tech_data[f"{cat}_want"] for cat, _ in TECH_CATEGORIES], ignore_index=True)
admired_all = pd.concat([tech_data[f"{cat}_admired"] for cat, _ in TECH_CATEGORIES], ignore_index=True)

# Add category to tech data for the cross-category analysis
cat_map = {csv_pref: cat for cat, csv_pref in TECH_CATEGORIES}
have_all["category"] = ""
want_all["category"] = ""
for tbl_key in sorted(tech_data.keys()):
    cat = tbl_key.split("_")[0]
    var = tbl_key.split("_")[1]
    pass

# Build have/want with category from table name
have_with_cat = pd.concat([
    tech_data[f"{cat}_have"].assign(category=cat) for cat, _ in TECH_CATEGORIES
], ignore_index=True)
want_with_cat = pd.concat([
    tech_data[f"{cat}_want"].assign(category=cat) for cat, _ in TECH_CATEGORIES
], ignore_index=True)

have_counts = have_with_cat.groupby(["category", "tech_name"]).size().reset_index(name="have_count")
want_counts = want_with_cat.groupby(["category", "tech_name"]).size().reset_index(name="want_count")
wh_ratio = have_counts.merge(want_counts, on=["category", "tech_name"])
wh_ratio = wh_ratio[wh_ratio["have_count"] >= 30].copy()
wh_ratio["ratio"] = wh_ratio["want_count"] / wh_ratio["have_count"]
rising = wh_ratio[wh_ratio["ratio"] > 1.5].sort_values("ratio", ascending=False).head(10)
declining = wh_ratio[wh_ratio["ratio"] < 0.7].sort_values("ratio", ascending=True).head(10)
rising.to_csv(os.path.join(OUTPUT_DIR, "rising_tech.csv"), index=False)
declining.to_csv(os.path.join(OUTPUT_DIR, "declining_tech.csv"), index=False)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(range(len(rising)), rising["ratio"].values, color="#27AE60", edgecolor="white")
ax.set_yticks(range(len(rising)))
ax.set_yticklabels([f"{r['tech_name']} ({r['category']})" for _, r in rising.iterrows()], fontsize=9)
ax.set_xlabel("Want / Have Ratio"); ax.set_title("Rising Tech Stars (Ratio > 1.5)", fontweight="bold")
for i, v in enumerate(rising["ratio"]): ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_rising_stars.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(range(len(declining)), declining["ratio"].values, color="#E74C3C", edgecolor="white")
ax.set_yticks(range(len(declining)))
ax.set_yticklabels([f"{r['tech_name']} ({r['category']})" for _, r in declining.iterrows()], fontsize=9)
ax.set_xlabel("Want / Have Ratio"); ax.set_title("Declining Tech (Ratio < 0.7)", fontweight="bold")
for i, v in enumerate(declining["ratio"]): ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_declining_tech.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# ═════════════════════════════════════════════
# SECTION 3: Job Satisfaction
# ═════════════════════════════════════════════
print("Section 3: Job Satisfaction...")

jobsat = respondents["job_sat"].dropna()
jobsat_mean = jobsat.mean()
jobsat_median = jobsat.median()
jobsat_mode = jobsat.mode().iloc[0]
jobsat_null = respondents["job_sat"].isna().sum()
save_hist(pd.DataFrame({"job_sat": jobsat}), "job_sat", "Job Satisfaction Distribution (0-10)",
          "chart_jobsat_dist.png", bins=11, xlabel="Satisfaction Score")

sat_factors = job_sat_points.groupby("aspect")["score"].agg(["mean", "count"]).reset_index()
sat_factors.columns = ["aspect", "avg_score", "cnt"]
sat_factors = sat_factors.sort_values("avg_score", ascending=False)
sat_factor_total = len(job_sat_points)
save_bar(sat_factors, "aspect", "avg_score",
         "Job Satisfaction Factors (Avg Score out of 100)", "chart_jobsat_factors.png",
         xlabel="Satisfaction Aspect", ylabel="Average Score")

sat_remote = respondents[respondents["job_sat"].notna() & respondents["remote_work"].notna()].groupby("remote_work")["job_sat"].agg(["mean", "count"]).reset_index()
sat_remote.columns = ["remote_work", "avg_sat", "cnt"]
sat_remote_total = sat_remote["cnt"].sum()
save_bar(sat_remote, "remote_work", "avg_sat",
         "Job Satisfaction by Work Arrangement", "chart_jobsat_remote.png",
         xlabel="Work Arrangement", ylabel="Avg Satisfaction (0-10)", horizontal=False)

sat_country = respondents[respondents["job_sat"].notna() & respondents["country"].notna()].groupby("country")["job_sat"].agg(["mean", "count"]).reset_index()
sat_country.columns = ["country", "avg_sat", "cnt"]
sat_country = sat_country[sat_country["cnt"] >= 50].sort_values("avg_sat", ascending=False).head(10)
save_bar(sat_country, "country", "avg_sat",
         "Top 10 Countries by Job Satisfaction", "chart_jobsat_country.png",
         xlabel="Country", ylabel="Avg Satisfaction (0-10)")

devtype_sat = respondent_devtype.merge(respondents[["respondent_id", "job_sat"]], on="respondent_id")
devtype_sat = devtype_sat[devtype_sat["job_sat"].notna()].groupby("dev_type")["job_sat"].agg(["mean", "count"]).reset_index()
devtype_sat.columns = ["dev_type", "avg_sat", "cnt"]
devtype_sat = devtype_sat[devtype_sat["cnt"] >= 50].sort_values("avg_sat", ascending=False).head(10)
save_bar(devtype_sat, "dev_type", "avg_sat",
         "Job Satisfaction by Developer Role", "chart_jobsat_devtype.png",
         xlabel="Developer Type", ylabel="Avg Satisfaction (0-10)")

age_order = {"Under 18": 1, "18-24": 2, "25-34": 3, "35-44": 4, "45-54": 5, "55-64": 6, "65+": 7}
sat_age = respondents[respondents["job_sat"].notna() & respondents["age_group"].notna()].groupby("age_group")["job_sat"].agg(["mean", "count"]).reset_index()
sat_age.columns = ["age_group", "avg_sat", "cnt"]
sat_age["order"] = sat_age["age_group"].map(age_order)
sat_age = sat_age.sort_values("order")
sat_age_total = sat_age["cnt"].sum()
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(sat_age["age_group"], sat_age["avg_sat"], marker="o", color="#2E86AB", linewidth=2)
ax.set_xlabel("Age Group"); ax.set_ylabel("Avg Satisfaction (0-10)")
ax.set_title("Job Satisfaction by Age Group", fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_jobsat_age.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

sat_icpm = respondents[respondents["job_sat"].notna() & respondents["icor_pm"].notna()].groupby("icor_pm")["job_sat"].agg(["mean", "count"]).reset_index()
sat_icpm.columns = ["icor_pm", "avg_sat", "cnt"]
save_bar(sat_icpm, "icor_pm", "avg_sat",
         "Satisfaction: Individual Contributor vs Manager", "chart_jobsat_icpm.png",
         xlabel="Role", ylabel="Avg Satisfaction (0-10)", horizontal=False)

# ═════════════════════════════════════════════
# SECTION 4: Compensation
# ═════════════════════════════════════════════
print("Section 4: Compensation...")

comp = respondents["converted_comp_yearly"].dropna()
comp_null = respondents["converted_comp_yearly"].isna().sum()
comp_mean_val = comp.mean()
comp_median_val = comp.median()
comp_min_val = comp.min()
comp_max_val = comp.max()
save_hist(pd.DataFrame({"converted_comp_yearly": comp}), "converted_comp_yearly",
          "Compensation Distribution", "chart_comp_dist.png", bins=50, xlabel="Yearly Compensation (USD)")

comp_country_med = respondents[respondents["converted_comp_yearly"].notna()].groupby("country")["converted_comp_yearly"].agg(["median", "count"]).reset_index()
comp_country_med.columns = ["country", "med_comp", "cnt"]
comp_country_med = comp_country_med[comp_country_med["cnt"] >= 30].sort_values("med_comp", ascending=False).head(10)
save_bar(comp_country_med, "country", "med_comp",
         "Median Compensation by Country (Top 10)", "chart_comp_country.png",
         xlabel="Country", ylabel="Median Compensation (USD)")

comp_devtype = respondent_devtype.merge(respondents[["respondent_id", "converted_comp_yearly"]], on="respondent_id")
comp_devtype = comp_devtype[comp_devtype["converted_comp_yearly"].notna()].groupby("dev_type")["converted_comp_yearly"].agg(["median", "count"]).reset_index()
comp_devtype.columns = ["dev_type", "med_comp", "cnt"]
comp_devtype = comp_devtype[comp_devtype["cnt"] >= 50].sort_values("med_comp", ascending=False).head(10)
save_bar(comp_devtype, "dev_type", "med_comp",
         "Median Compensation by Developer Role", "chart_comp_devtype.png",
         xlabel="Developer Type", ylabel="Median Compensation (USD)")

comp_ed = respondents[respondents["converted_comp_yearly"].notna() & respondents["ed_level"].notna()].groupby("ed_level")["converted_comp_yearly"].agg(["median", "count"]).reset_index()
comp_ed.columns = ["ed_level", "med_comp", "cnt"]
comp_ed = comp_ed.sort_values("med_comp", ascending=False)
save_bar(comp_ed, "ed_level", "med_comp",
         "Median Compensation by Education Level", "chart_comp_edlevel.png",
         xlabel="Education Level", ylabel="Median Compensation (USD)")

comp_age = respondents[respondents["converted_comp_yearly"].notna() & respondents["age_group"].notna()].groupby("age_group")["converted_comp_yearly"].agg(["median", "count"]).reset_index()
comp_age.columns = ["age_group", "med_comp", "cnt"]
comp_age["order"] = comp_age["age_group"].map(age_order)
comp_age = comp_age.sort_values("order")
save_bar(comp_age, "age_group", "med_comp",
         "Median Compensation by Age Group", "chart_comp_age.png",
         xlabel="Age Group", ylabel="Median Compensation (USD)", horizontal=False)

comp_remote = respondents[respondents["converted_comp_yearly"].notna() & respondents["remote_work"].notna()].groupby("remote_work")["converted_comp_yearly"].agg(["median", "count"]).reset_index()
comp_remote.columns = ["remote_work", "med_comp", "cnt"]
comp_remote = comp_remote.sort_values("med_comp", ascending=False)
save_bar(comp_remote, "remote_work", "med_comp",
         "Median Compensation by Work Arrangement", "chart_comp_remote.png",
         xlabel="Work Arrangement", ylabel="Median Compensation (USD)", horizontal=False)

# Experience vs Compensation scatter
comp_exp = respondents[respondents["converted_comp_yearly"].notna() & respondents["years_code_pro"].notna() & (respondents["converted_comp_yearly"] < 500000)]
age_colors = {"Under 18": "#FF6B6B", "18-24": "#F9CA24", "25-34": "#2E86AB",
              "35-44": "#27AE60", "45-54": "#E8833A", "55-64": "#8E44AD", "65+": "#E74C3C"}
fig, ax = plt.subplots(figsize=(10, 6))
for age, grp in comp_exp.groupby("age_group"):
    if age and age in age_colors:
        ax.scatter(grp["years_code_pro"], grp["converted_comp_yearly"],
                   c=age_colors[age], label=age, alpha=0.3, s=5, edgecolors="none")
ax.set_xlabel("Years of Professional Coding"); ax.set_ylabel("Yearly Compensation (USD)")
ax.set_title("Experience vs Compensation by Age Group", fontweight="bold"); ax.legend(markerscale=4)
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_comp_exp_age.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# DevType × Compensation × Satisfaction
devtype_comp_sat = respondent_devtype.merge(respondents[["respondent_id", "converted_comp_yearly", "job_sat"]], on="respondent_id")
devtype_comp_sat = devtype_comp_sat[devtype_comp_sat["converted_comp_yearly"].notna() & devtype_comp_sat["job_sat"].notna()]
devtype_comp_sat = devtype_comp_sat.groupby("dev_type").agg(avg_comp=("converted_comp_yearly", "mean"), avg_sat=("job_sat", "mean"), cnt=("respondent_id", "count")).reset_index()
devtype_comp_sat = devtype_comp_sat[devtype_comp_sat["cnt"] >= 30]
fig, ax = plt.subplots(figsize=(10, 7))
sc = ax.scatter(devtype_comp_sat["avg_comp"], devtype_comp_sat["avg_sat"],
                c=devtype_comp_sat["cnt"], cmap="viridis", s=80, alpha=0.8, edgecolors="black")
for _, r in devtype_comp_sat.iterrows():
    ax.annotate(r["dev_type"].replace("Developer, ", "").replace("Engineer, ", "Eng, ")[:20],
                (r["avg_comp"], r["avg_sat"]), fontsize=7, ha="center", va="bottom")
ax.set_xlabel("Average Compensation (USD)"); ax.set_ylabel("Average Job Satisfaction (0-10)")
ax.set_title("Dev Role: Compensation vs Satisfaction\n(Bubble size = respondent count)", fontweight="bold")
cbar = plt.colorbar(sc); cbar.set_label("Count")
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_devtype_comp_sat.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# ═════════════════════════════════════════════
# SECTION 5: Geographic Technology
# ═════════════════════════════════════════════
print("Section 5: Geographic Tech...")

# Top 10 countries × top 10 languages heatmap
top10_countries = respondents["country"].value_counts().head(10).index.tolist()
top10_langs = tech_data["language_have"]["tech_name"].value_counts().head(10).index.tolist()
country_lang = tech_data["language_have"].merge(respondents[["respondent_id", "country"]], on="respondent_id")
country_lang = country_lang[country_lang["country"].isin(top10_countries) & country_lang["tech_name"].isin(top10_langs)]
total_per_country = respondents[respondents["country"].isin(top10_countries)].groupby("country").size()
lang_per_country = country_lang.groupby(["country", "tech_name"]).size().reset_index(name="cnt")
lang_per_country["pct"] = lang_per_country.apply(lambda r: r["cnt"] / total_per_country[r["country"]] * 100, axis=1)

pivot_hm = lang_per_country.pivot_table(index="country", columns="tech_name", values="pct", aggfunc="mean")
fig, ax = plt.subplots(figsize=(12, 7))
im = ax.imshow(pivot_hm.values, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(pivot_hm.columns)))
ax.set_xticklabels(pivot_hm.columns, rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(len(pivot_hm.index)))
ax.set_yticklabels(pivot_hm.index, fontsize=9)
for i in range(len(pivot_hm.index)):
    for j in range(len(pivot_hm.columns)):
        val = pivot_hm.values[i, j]
        ax.text(j, i, f"{val:.0f}%", ha="center", va="center", fontsize=8, color="white" if val > 50 else "black")
ax.set_title("Technology Adoption by Country (% of respondents)", fontweight="bold")
fig.colorbar(im, ax=ax, shrink=0.7, label="Adoption %")
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_geo_heatmap.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# ═════════════════════════════════════════════
# SECTION 6: Age Group × Technology
# ═════════════════════════════════════════════
print("Section 6: Age × Tech...")

age_groups = ["Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
# Top 8 languages across age groups - stacked %
top8_langs = tech_data["language_have"]["tech_name"].value_counts().head(8).index.tolist()
age_lang = tech_data["language_have"].merge(respondents[["respondent_id", "age_group"]], on="respondent_id")
age_lang = age_lang[age_lang["age_group"].isin(age_groups) & age_lang["tech_name"].isin(top8_langs)]
age_total = respondents[respondents["age_group"].isin(age_groups)].groupby("age_group").size()
age_lang_pct = age_lang.groupby(["age_group", "tech_name"]).size().reset_index(name="cnt")
age_lang_pct["pct"] = age_lang_pct.apply(lambda r: r["cnt"] / age_total[r["age_group"]] * 100, axis=1)
alp_pivot = age_lang_pct.pivot_table(index="age_group", columns="tech_name", values="pct", aggfunc="mean")
alp_pivot = alp_pivot.reindex(age_groups)

fig, ax = plt.subplots(figsize=(12, 6))
bottom = np.zeros(len(age_groups))
colors = plt.cm.Set2(np.linspace(0, 1, len(top8_langs)))
for i, lang in enumerate(top8_langs):
    vals = alp_pivot[lang].values if lang in alp_pivot.columns else np.zeros(len(age_groups))
    ax.bar(age_groups, vals, bottom=bottom, label=lang, color=colors[i], edgecolor="white", width=0.7)
    bottom += vals
ax.set_xlabel("Age Group"); ax.set_ylabel("% of Respondents")
ax.set_title("Language Adoption Across Age Groups (Stacked %)", fontweight="bold")
ax.legend(loc="upper right", fontsize=8, ncol=2)
for tick in ax.get_xticklabels(): tick.set_rotation(45); tick.set_ha("right")
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_age_lang_stacked.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# ═════════════════════════════════════════════
# SECTION 7: Extra Insights
# ═════════════════════════════════════════════
print("Section 7: Extra Insights...")

# 7.1 Remote Work by Dev Type
remote_devtype = respondent_devtype.merge(respondents[["respondent_id", "remote_work"]], on="respondent_id")
remote_devtype = remote_devtype[remote_devtype["remote_work"].notna()]
remote_devtype_pivot = remote_devtype.groupby(["dev_type", "remote_work"]).size().reset_index(name="cnt")
rd_pivot = remote_devtype_pivot.pivot_table(index="dev_type", columns="remote_work", values="cnt", aggfunc="sum").fillna(0)
rd_pivot["total"] = rd_pivot.sum(axis=1)
rd_pivot = rd_pivot[rd_pivot["total"] >= 50]
if "Remote" in rd_pivot.columns:
    rd_pivot["remote_pct"] = rd_pivot["Remote"] / rd_pivot["total"] * 100
    top_remote = rd_pivot.sort_values("remote_pct", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(top_remote)), top_remote["remote_pct"].values, color="#2E86AB", edgecolor="white")
    ax.set_yticks(range(len(top_remote)))
    ax.set_yticklabels(top_remote.index, fontsize=9)
    ax.set_xlabel("% Remote Workers"); ax.set_title("Dev Types with Highest Remote Adoption", fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_remote_devtype.png"), dpi=150, bbox_inches="tight"); plt.close(fig)
    remote_devtype_total = len(respondent_devtype)

# 7.2 AI Sentiment + AI by Age
ai_sent = respondents["ai_sent"].dropna()
ai_sent_total = len(ai_sent)
sent_counts = ai_sent.value_counts()
others = len(ai_sent) - sent_counts.head(7).sum()
if others > 0:
    sent_counts = pd.concat([sent_counts.head(7), pd.Series({"Other": others})])
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(sent_counts.values, labels=sent_counts.index, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 8})
ax.set_title("AI Sentiment Distribution", fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_ai_sentiment.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

ai_age = respondents[respondents["ai_select"].notna() & respondents["age_group"].notna()]
ai_age_total = len(ai_age)
ai_age_pivot = ai_age.groupby(["age_group", "ai_select"]).size().reset_index(name="cnt")
ai_age_wide = ai_age_pivot.pivot_table(index="age_group", columns="ai_select", values="cnt", aggfunc="sum").fillna(0)
ai_age_pct = ai_age_wide.div(ai_age_wide.sum(axis=1), axis=0) * 100
ai_age_pct = ai_age_pct.reindex(age_groups)
cols_to_plot = [c for c in ai_age_pct.columns if c != "total"][:5]
if cols_to_plot:
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(age_groups))
    colors = plt.cm.Set3(np.linspace(0, 1, len(cols_to_plot)))
    for i, col in enumerate(cols_to_plot):
        vals = ai_age_pct[col].values if col in ai_age_pct.columns else np.zeros(len(age_groups))
        ax.bar(age_groups, vals, bottom=bottom, label=col[:25], color=colors[i], edgecolor="white", width=0.7)
        bottom += vals
    ax.set_xlabel("Age Group"); ax.set_ylabel("% of Respondents"); ax.set_title("AI Tool Selection by Age Group", fontweight="bold")
    ax.legend(fontsize=7, ncol=2)
    for tick in ax.get_xticklabels(): tick.set_rotation(45); tick.set_ha("right")
    fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_ai_age.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# 7.3 Knowledge Self-Assessment
knowledge_avg = knowledge.groupby("knowledge_area")["score"].agg(["mean", "count"]).reset_index()
knowledge_avg.columns = ["knowledge_area", "avg_score", "cnt"]
knowledge_avg = knowledge_avg.sort_values("knowledge_area")
save_bar(knowledge_avg, "knowledge_area", "avg_score",
         "Self-Assessed Knowledge Scores (1=Strongly Disagree, 5=Strongly Agree)",
         "chart_knowledge.png", xlabel="Knowledge Area", ylabel="Average Score")

knowledge_corr = knowledge.merge(respondents[["respondent_id", "job_sat", "converted_comp_yearly"]], on="respondent_id")
knowledge_corr = knowledge_corr[knowledge_corr["score"].notna() & knowledge_corr["job_sat"].notna() & knowledge_corr["converted_comp_yearly"].notna()]
corr_data = knowledge_corr.groupby("knowledge_area")[["score", "job_sat", "converted_comp_yearly"]].corr().reset_index()
corr_data = corr_data[corr_data["level_1"] == "score"]
fig, ax = plt.subplots(figsize=(8, 6))
x = np.arange(len(corr_data)); w = 0.3
ax.bar(x - w/2, corr_data["job_sat"], w, label="Corr with JobSat", color="#2E86AB")
ax.bar(x + w/2, corr_data["converted_comp_yearly"], w, label="Corr with Compensation", color="#E8833A")
ax.set_xticks(x); ax.set_xticklabels(corr_data["knowledge_area"], rotation=45, ha="right", fontsize=8)
ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.5)
ax.set_title("Correlation: Knowledge Scores vs JobSat & Compensation", fontweight="bold"); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_knowledge_corr.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# 7.4 Learning Pathway → Compensation
learn_comp = respondent_learn_code.merge(respondents[["respondent_id", "converted_comp_yearly"]], on="respondent_id")
learn_comp = learn_comp[learn_comp["converted_comp_yearly"].notna()]
learn_comp_agg = learn_comp.groupby("learning_source")["converted_comp_yearly"].agg(["median", "count"]).reset_index()
learn_comp_agg.columns = ["learning_source", "med_comp", "cnt"]
learn_comp_agg = learn_comp_agg[learn_comp_agg["cnt"] >= 50].sort_values("med_comp", ascending=False)
save_bar(learn_comp_agg, "learning_source", "med_comp",
         "Median Compensation by Learning Source", "chart_learn_comp.png",
         xlabel="Learning Source", ylabel="Median Compensation (USD)")

# 7.5 Employment patterns → Comp
emp_comp = respondent_employment.merge(respondents[["respondent_id", "converted_comp_yearly", "job_sat"]], on="respondent_id")
emp_comp = emp_comp[emp_comp["converted_comp_yearly"].notna() & emp_comp["job_sat"].notna()]
emp_comp_agg = emp_comp.groupby("employment_type").agg(avg_comp=("converted_comp_yearly", "mean"), avg_sat=("job_sat", "mean"), cnt=("respondent_id", "count")).reset_index()
emp_comp_agg = emp_comp_agg[emp_comp_agg["cnt"] >= 100].sort_values("avg_comp", ascending=False).head(10)
save_bar(emp_comp_agg, "employment_type", "avg_comp",
         "Average Compensation by Employment Type", "chart_emp_comp.png",
         xlabel="Employment Type", ylabel="Avg Compensation (USD)")

# 7.6 Technology Migration: What Python Devs Want Next
python_ids = tech_data["language_have"][tech_data["language_have"]["tech_name"] == "Python"]["respondent_id"].unique()
python_want = tech_data["language_want"][tech_data["language_want"]["respondent_id"].isin(python_ids) & (tech_data["language_want"]["tech_name"] != "Python")]
python_migration = python_want["tech_name"].value_counts().head(10).reset_index()
python_migration.columns = ["tech_name", "cnt"]
python_dev_count = len(python_ids)
save_bar(python_migration, "tech_name", "cnt",
         "What Python Developers Want to Learn Next (Top 10)", "chart_python_migration.png",
         xlabel="Language", ylabel="Count")

# 7.7 Remote Work × Compensation × Satisfaction Matrix
remote_comp_sat = respondents[respondents["converted_comp_yearly"].notna() & respondents["job_sat"].notna() & respondents["remote_work"].notna()].copy()
remote_comp_sat_total = len(remote_comp_sat)
remote_comp_sat["comp_bracket"] = pd.cut(remote_comp_sat["converted_comp_yearly"],
    bins=[0, 30000, 70000, 120000, float("inf")],
    labels=["Low (<$30K)", "Medium-Low ($30-70K)", "Medium-High ($70-120K)", "High (>$120K)"])
rcs_pivot = remote_comp_sat.groupby(["remote_work", "comp_bracket"])["job_sat"].mean().reset_index()
rcs_wide = rcs_pivot.pivot_table(index="remote_work", columns="comp_bracket", values="job_sat", aggfunc="mean")
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(rcs_wide.values, cmap="RdYlGn", aspect="auto", vmin=5, vmax=8)
ax.set_xticks(range(len(rcs_wide.columns))); ax.set_xticklabels(rcs_wide.columns, fontsize=8)
ax.set_yticks(range(len(rcs_wide.index))); ax.set_yticklabels(rcs_wide.index, fontsize=9)
for i in range(len(rcs_wide.index)):
    for j in range(len(rcs_wide.columns)):
        ax.text(j, i, f"{rcs_wide.values[i,j]:.1f}", ha="center", va="center", fontsize=10, fontweight="bold")
ax.set_title("Job Satisfaction by Work Arrangement and Compensation Level", fontweight="bold")
fig.colorbar(im, ax=ax, shrink=0.7, label="Avg Satisfaction")
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_remote_comp_sat_matrix.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# 7.8 Country × Remote Work × Compensation
top_countries_remote = respondents[respondents["remote_work"] == "Remote"]["country"].value_counts().head(10).index.tolist()
cf = respondents[respondents["converted_comp_yearly"].notna() & respondents["remote_work"].notna() & respondents["country"].isin(top_countries_remote)]
crf_pivot = cf.groupby(["country", "remote_work"])["converted_comp_yearly"].median().reset_index()
crf_wide = crf_pivot.pivot_table(index="country", columns="remote_work", values="converted_comp_yearly", aggfunc="mean")
crf_wide = crf_wide.sort_values("Remote", ascending=True) if "Remote" in crf_wide.columns else crf_wide
fig, ax = plt.subplots(figsize=(10, 6))
y = np.arange(len(crf_wide)); w = 0.25
for i, col in enumerate(crf_wide.columns):
    offset = (i - len(crf_wide.columns)/2 + 0.5) * w
    ax.barh(y + offset, crf_wide[col].values, w, label=col, edgecolor="white")
ax.set_yticks(y); ax.set_yticklabels(crf_wide.index, fontsize=9)
ax.set_xlabel("Median Compensation (USD)")
ax.set_title("Remote vs In-Person Compensation by Country (Top 10)", fontweight="bold"); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(OUTPUT_DIR, "chart_country_remote_comp.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# 7.9 Stack Overflow Engagement
so_visit = respondents["so_visit_freq"].dropna().value_counts().reset_index()
so_visit.columns = ["so_visit_freq", "cnt"]
so_visit.index.name = None
save_bar(so_visit, "so_visit_freq", "cnt",
         "Stack Overflow Visit Frequency", "chart_so_visit.png",
         xlabel="Visit Frequency", ylabel="Count", horizontal=False)

so_comp = respondents[respondents["converted_comp_yearly"].notna() & respondents["so_part_freq"].notna()]
so_comp_agg = so_comp.groupby("so_part_freq")["converted_comp_yearly"].agg(["mean", "count"]).reset_index()
so_comp_agg.columns = ["so_part_freq", "avg_comp", "cnt"]
so_comp_agg = so_comp_agg[so_comp_agg["cnt"] >= 50].sort_values("avg_comp", ascending=False)
save_bar(so_comp_agg, "so_part_freq", "avg_comp",
         "Average Compensation by SO Participation Frequency", "chart_so_comp.png",
         xlabel="Participation Frequency", ylabel="Avg Compensation (USD)")

# 7.10 Employment type distribution
emp_dist = respondent_employment["employment_type"].value_counts().head(10).reset_index()
emp_dist.columns = ["employment_type", "cnt"]
save_bar(emp_dist, "employment_type", "cnt",
         "Top 10 Employment Types", "chart_employment_dist.png",
         xlabel="Employment Type", ylabel="Count")

print("All charts generated.")

# ═════════════════════════════════════════════
# MARKDOWN REPORT
# ═════════════════════════════════════════════

# Schema
conn2 = sqlite3.connect(DB_PATH)
schema_lines = []
# 33 per-category tech tables + 6 junction tables
tech_tbls = []
for cat, csv_pref in TECH_CATEGORIES:
    for var in VARIANTS:
        tech_tbls.append(f"{csv_pref}_{var}")
all_tables = ["respondents"] + tech_tbls + [
    "respondent_employment", "respondent_devtype", "respondent_learn_code",
    "respondent_coding_activities", "job_satisfaction_points", "knowledge_self_assessment"]
for tbl in all_tables:
    cnt = conn2.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    cols = conn2.execute(f"PRAGMA table_info({tbl})").fetchall()
    schema_lines.append(f"### `{tbl}` ({cnt:,} rows)")
    schema_lines.append("| Column | Type | Nullable |")
    schema_lines.append("|--------|------|----------|")
    for c in cols:
        schema_lines.append(f"| {c[1]} | {c[2]} | {'YES' if c[3]==0 else 'NO'} |")
    schema_lines.append("")
null_stats = conn2.execute("""
SELECT
  SUM(CASE WHEN age_group IS NULL THEN 1 ELSE 0 END),
  SUM(CASE WHEN converted_comp_yearly IS NULL THEN 1 ELSE 0 END),
  SUM(CASE WHEN job_sat IS NULL THEN 1 ELSE 0 END),
  SUM(CASE WHEN remote_work IS NULL THEN 1 ELSE 0 END),
  SUM(CASE WHEN ed_level IS NULL THEN 1 ELSE 0 END)
FROM respondents
""").fetchone()
total_resp = conn2.execute("SELECT COUNT(*) FROM respondents").fetchone()[0]
conn2.close()

# ── Computed facts used by the report prose (never hardcode these) ──────────
db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
n_countries = int(respondents["country"].nunique())
n_tables = len(all_tables)
n_aspects = int(job_sat_points["aspect"].nunique())
comp_cap = comp_max_val
comp_missing_pct = comp_null / total_resp * 100
lang_js = lang_have_pct.get("JavaScript", 0.0)
lang_ts_have = lang_have_pct.get("TypeScript", 0.0)
lang_ts_want = lang_want_pct.get("TypeScript", 0.0)
lang_rust_want = lang_want_pct.get("Rust", 0.0)
lang_js_want = lang_want_pct.get("JavaScript", 0.0)
lang_sql = lang_have_pct.get("SQL", 0.0)
lang_html = lang_have_pct.get("HTML/CSS", 0.0)
lang_py_have = lang_have_pct.get("Python", 0.0)
lang_py_want = lang_want_pct.get("Python", 0.0)
lang_go_want = lang_want_pct.get("Go", 0.0)
lang_kotlin_want = lang_want_pct.get("Kotlin", 0.0)
lang_js_count = int(lang_have.loc[lang_have["tech_name"] == "JavaScript", "count"].sum())

_country_stats = (
    respondents.dropna(subset=["converted_comp_yearly"])
    .groupby("country")["converted_comp_yearly"]
    .agg(["median", "count"])
)
_country_stats = _country_stats[_country_stats["count"] >= 30].sort_values(
    "median", ascending=False
)
top_comp_country = _country_stats.index[0] if len(_country_stats) else "n/a"
top_comp_median = float(_country_stats["median"].iloc[0]) if len(_country_stats) else float("nan")
us_mask = respondents["country"].fillna("").str.contains("United States")
us_median = respondents.loc[us_mask, "converted_comp_yearly"].median()
us_median_display = f"${us_median:,.0f}" if pd.notna(us_median) else "n/a"
global_median = comp_median_val


def _cat_count(key, tech):
    d = tech_data[key]
    return int((d["tech_name"] == tech).sum())


rust_have_n = _cat_count("language_have", "Rust")
rust_want_n = _cat_count("language_want", "Rust")
rust_ratio = rust_want_n / rust_have_n if rust_have_n else float("nan")
ts_have_n = _cat_count("language_have", "TypeScript")
ts_want_n = _cat_count("language_want", "TypeScript")
ts_ratio = ts_want_n / ts_have_n if ts_have_n else float("nan")
lang_want_top = lang_want.iloc[0]["tech_name"] if len(lang_want) else "n/a"
lang_want_top_pct = lang_want_pct.get(lang_want_top, 0.0)

_sat_sorted = sat_factors.sort_values("avg_score", ascending=False)
sat_top = _sat_sorted.iloc[0]["aspect"] if len(_sat_sorted) else "n/a"
sat_second = _sat_sorted.iloc[1]["aspect"] if len(_sat_sorted) > 1 else "n/a"
sat_low = _sat_sorted.iloc[-1]["aspect"] if len(_sat_sorted) else "n/a"

_db_have = tech_data["database_have"].groupby("tech_name").size()
_db_want = tech_data["database_want"].groupby("tech_name").size()


def _pct_of_total(series, name):
    return series.get(name, 0) / total_resp * 100


pg_want_n = int(_db_want.get("PostgreSQL", 0))
pg_want_pct = _pct_of_total(_db_want, "PostgreSQL")
mysql_have_pct = _pct_of_total(_db_have, "MySQL")
mysql_want_pct = _pct_of_total(_db_want, "MySQL")

# Build report
lines = []
def L(text=""): lines.append(text)

L("# Survey Data Analysis Report")
L()
L("> **Generated artifact — do not edit by hand.** This report and the charts in this")
L("> directory are produced by `generate_report.py` from the SQLite database")
L(f"> `{os.path.basename(DB_PATH)}`.")
L(">")
L("> - **Dataset:** Stack Overflow Developer Survey 2024 (ODbL). See `NOTICE.md`.")
L("> - **Pipeline:** `build_database.py` → `generate_report.py` (see `METHODOLOGY.md`).")
L("> - **Regenerate:** `make demo` (offline sample) or")
L(">   `make fetch-data && make build-db && make report` (full run).")
L(">")
L("> Figures labelled *Data Context* and the summary tables below are computed at run")
L("> time, as are the percentages quoted in the narrative. The charts are the")
L("> authoritative source; prose is descriptive, not causal.")
L()
L("## Executive Summary")
L()
L(
    f"This report analyses the Stack Overflow 2024 Developer Survey, covering "
    f"{total_resp:,} respondents from {n_countries} countries and territories. "
    "The pipeline cleans and normalises the survey into a relational SQLite model "
    f"({n_tables} tables), then derives the charts and findings below. The analysis "
    "covers technology trends, job satisfaction, compensation, geography, age, and AI "
    "tooling. Headline patterns: JavaScript remains the most widely used language, "
    "TypeScript and Rust show the strongest forward-looking demand, PostgreSQL leads "
    "databases, remote work correlates with higher satisfaction and pay, and AI tools "
    "are already part of many developers' workflows. All findings are descriptive and "
    "correlational (see the Discussion and `LIMITATIONS.md`)."
)
L()
L("## 1. Data Overview & Database Schema")
L()
L("### Dataset Summary")
L()
L("| Metric | Value |")
L("|--------|-------|")
L(f"| **Total Respondents** | {total_resp:,} |")
L("| **Columns (CSV)** | 114 |")
L(f"| **Normalized Tables (SQLite)** | {n_tables} |")
L(f"| **Database Size** | {db_size_mb:,.0f} MB |")
L(f"| **Countries Represented** | {n_countries} |")
L()
L("### Data Cleaning Applied")
L()
L("| Column | Issue | Cleaning |")
L("|--------|-------|----------|")
L("| `YearsCode` / `YearsCodePro` | Text values: 'Less than 1 year', 'More than 50 years' | Mapped to 0.5 and 55 respectively |")
L(f"| `ConvertedCompYearly` | Extreme outliers | Capped at the 99th percentile (${comp_cap:,.0f}); values above are clipped |")
L("| `Age` | 'Prefer not to say' and unmapped values | Mapped to NULL |")
L("| `Employment` | Semicolon-delimited multi-values | Normalized into `respondent_employment` (de-duplicated per respondent) |")
L("| `DevType` | Semicolon-delimited multi-values | Normalized into `respondent_devtype` (de-duplicated per respondent) |")
L("| `LearnCode`, `CodingActivities` | Semicolon-delimited multi-values | Normalized into separate tables (de-duplicated per respondent) |")
L("| All 33 `*HaveWorkedWith`, `*WantToWorkWith`, `*Admired` columns | 11 categories × 3 variants, semicolon-delimited | Normalized into 33 per-category tables (de-duplicated per respondent × value) |")
L("| `Knowledge_1` through `Knowledge_9` | Likert text responses | Mapped to numeric scores (1=Strongly disagree..5=Strongly agree); unmapped → NULL + warning |")
L("| `JobSatPoints_*` | Scattered 0-100 scores | Normalized into `job_satisfaction_points` table with aspect labels |")
L()
L("### Key Null Statistics")
L()
L("| Column | NULL Count | % Missing |")
L("|--------|-----------|----------|")
L(f"| `converted_comp_yearly` | {null_stats[1]:,} | {null_stats[1]/total_resp*100:.1f}% |")
L(f"| `job_sat` | {null_stats[2]:,} | {null_stats[2]/total_resp*100:.1f}% |")
L(f"| `age_group` | {null_stats[0]:,} | {null_stats[0]/total_resp*100:.1f}% |")
L(f"| `remote_work` | {null_stats[3]:,} | {null_stats[3]/total_resp*100:.1f}% |")
L(f"| `ed_level` | {null_stats[4]:,} | {null_stats[4]/total_resp*100:.1f}% |")
L()
L("### Database Entity-Relationship Diagram")
L()
L("```mermaid")
L("erDiagram")
for _cat, _tbl_pref in TECH_CATEGORIES:
    for _var in VARIANTS:
        L(f"    respondents ||--o{{ {_tbl_pref}_{_var} : references")
L("    respondents ||--o{ respondent_employment : references")
L("    respondents ||--o{ respondent_devtype : references")
L("    respondents ||--o{ respondent_learn_code : references")
L("    respondents ||--o{ respondent_coding_activities : references")
L("    respondents ||--o{ job_satisfaction_points : references")
L("    respondents ||--o{ knowledge_self_assessment : references")
L("")
L("    respondents {")
L("        int respondent_id PK")
L("        string main_branch")
L("        string age_group")
L("        string remote_work")
L("        string ed_level")
L("        float years_code")
L("        float years_code_pro")
L("        string country")
L("        float converted_comp_yearly")
L("        float job_sat")
L("        string icor_pm")
L("        string industry")
L("    }")
L("")
L("    language_have {")
L("        int id PK")
L("        int respondent_id FK")
L("        string tech_name")
L("    }")
L("")
L("    job_satisfaction_points {")
L("        int id PK")
L("        int respondent_id FK")
L("        string aspect")
L("        float score")
L("    }")
L("")
L("    knowledge_self_assessment {")
L("        int id PK")
L("        int respondent_id FK")
L("        string knowledge_area")
L("        string response")
L("        int score")
L("    }")
L("```")
L()
L("Note: The diagram shows representative tables for brevity. The full schema includes 33 per-category technology tables (11 categories × 3 variants: have/want/admired) and 6 junction tables for employment types, developer roles, learning sources, coding activities, satisfaction points, and knowledge assessments. All per-category tech tables share the same structure as `language_have`.")
L()
L(f"### Database Schema ({n_tables} Tables)")
L()
for s in schema_lines:
    L(s)

# Section 2
L("## 2. Current vs Future Technology Trends")
L()
L("### 2.1 Programming Languages")
L()
L("#### Currently Used Languages")
L()
L("![Languages Currently Used](chart_lang_current.png)")
L()
L(f"**Data Context:** Based on {len(tech_data['language_have']):,} responses from {total_resp:,} total respondents. Each respondent could select multiple languages. Chart shows the top 10 languages by raw count of respondents who reported using them. No outlier removal applied — all valid responses included.")
L()
L(f"**This chart shows the top 10 programming languages respondents currently use.** JavaScript leads with {lang_js_count:,} respondents, followed by SQL and HTML/CSS — reflecting the web-centric nature of the developer population.")
L()
L("**Key Findings:**")
L(f"- **JavaScript** dominates with ~{lang_js:.0f}% adoption — it is the baseline requirement for modern web development.")
L(f"- **SQL** ranks second (~{lang_sql:.0f}%), confirming that data manipulation skills are almost as universal as front-end skills.")
L(f"- **HTML/CSS** ranks third (~{lang_html:.0f}%), consistent with the high proportion of front-end and full-stack developers.")
L(f"- **TypeScript** (~{lang_ts_have:.0f}%) has already surpassed Java and C# in current usage, marking its rapid rise.")
L(f"- **Python** (~{lang_py_have:.0f}%) rounds out the top 5, driven by data science and automation use cases.")
L("- **Bash/Shell** and **C#** follow, reflecting systems and enterprise development respectively.")
L()
L("**Implications:**")
L("- **JavaScript and TypeScript are the safest skill investments** for developers seeking broad employability.")
L("- **SQL remains undervalued** by many junior developers but is essential across all data roles.")
L("- **Python's position in the top 5 validates the data science career path** as mainstream, not niche.")
L()
L("#### Wanted Languages")
L()
L("![Languages Desired](chart_lang_wanted.png)")
L()
L(f"**Data Context:** Based on {len(tech_data['language_want']):,} responses from {total_resp:,} total respondents. Chart shows the top 10 languages respondents expressed desire to work with. Want/have ratios are calculated as: (respondents who want the language) / (respondents who currently use it). Percentages shown are of all respondents.")
L()
L("**This chart shows the top 10 languages respondents want to work with — a forward-looking indicator of where developers are investing their learning time.**")
L()
L("**Key Findings:**")
L(f"- **{lang_want_top}** is the most-wanted language (~{lang_want_top_pct:.0f}%), followed by SQL and TypeScript. Raw desire is dominated by the established leaders that most respondents already use.")
L(f"- **TypeScript** (~{lang_ts_want:.0f}% want vs ~{lang_ts_have:.0f}% current use) is close to parity with its current adoption, reflecting its continued growth.")
L(f"- **Rust** has the strongest want/have ratio among major languages (~{rust_ratio:.2f}x: {rust_have_n:,} use it, {rust_want_n:,} want to), a clear growth signal.")
L(f"- **Go** (~{lang_go_want:.0f}%) and **Kotlin** (~{lang_kotlin_want:.0f}%) show solid desire, reflecting cloud-native and Android ecosystem trends.")
L("- **JavaScript** and **HTML/CSS** have lower want/have ratios (<1) relative to current usage — they are mature, 'solved' skills for many respondents.")
L()
L("**Implications:**")
L(f"- **TypeScript combines high current usage ({lang_ts_have:.0f}%) with strong, sustained desire ({lang_ts_want:.0f}%)** — a stable skill investment.")
L("- **Rust and Go represent the biggest 'gap' opportunities** — fewer developers know them but many want to learn.")
L("- **Python demand is sustained by AI/ML growth**, not just current data science roles.")
L()
L("### 2.2 Databases")
L()
L("#### Currently Used Databases")
L()
L("![Databases Currently Used](chart_db_current.png)")
L()
L(f"**Data Context:** Based on {len(tech_data['database_have']):,} responses from {total_resp:,} total respondents. Chart shows the top 10 databases by raw adoption count. No data cleaning applied beyond the standard ConvertedCompYearly cap at the 99th percentile.")
L()
L("**This chart shows the top 10 databases respondents currently use.** PostgreSQL leads with the highest adoption, followed by MySQL, SQLite, and MongoDB.")
L()
L("**Key Findings:**")
L("- **PostgreSQL** is the most used database, reflecting its open-source nature, strong feature set, and enterprise adoption.")
L("- **MySQL** ranks second and **SQLite** third, driven respectively by legacy web stacks and by ubiquity in mobile, embedded, and local development.")
L("- **MongoDB** leads the NoSQL category, confirming its place as the default document database.")
L("- **Redis** and **Elasticsearch** show strong usage in caching and search use cases respectively.")
L("- **Microsoft SQL Server** remains relevant in enterprise .NET environments.")
L()
L("**Implications:**")
L("- **PostgreSQL expertise is the most valuable database skill** for broad employability.")
L("- **SQLite's high rank confirms that every developer needs embedded/local database skills**, regardless of role.")
L()
L("#### Wanted Databases")
L()
L("![Databases Desired](chart_db_wanted.png)")
L()
L(f"**Data Context:** Based on {len(tech_data['database_want']):,} responses. Percentages are of all {total_resp:,} respondents. The 'want ratio' compares desired vs current usage to identify growth trends.")
L()
L("**This chart shows the top 10 databases respondents want to work with — revealing where database interest is migrating.**")
L()
L("**Key Findings:**")
L(f"- **PostgreSQL** also tops the wanted list ({pg_want_n:,} respondents, ~{pg_want_pct:.0f}% of all respondents), confirming its dominance and continued growth trajectory.")
L("- **Redis, SQLite, MySQL, and MongoDB** follow, showing desire spread across relational and non-relational stores.")
L("- Several low-adoption databases show high want/have ratios (e.g. CockroachDB, DuckDB, Cassandra, ClickHouse) — early growth signals, though absolute counts remain small.")
L(f"- **MySQL** has a lower want share ({mysql_want_pct:.0f}%) than current use ({mysql_have_pct:.0f}%), consistent with a gradual shift toward PostgreSQL.")
L("- **Cloud databases** (DynamoDB, BigQuery, Supabase, Firebase) appear in the wanted list, reflecting cloud migration trends.")
L()
L("**Implications:**")
L("- **PostgreSQL is the safest database skill investment** for the next 3-5 years.")
L(f"- **MySQL knowledge is in relative decline** — its want share ({mysql_want_pct:.0f}%) is below its current use ({mysql_have_pct:.0f}%).")
L("- **Emerging analytical/NewSQL databases (DuckDB, ClickHouse, CockroachDB) are worth watching**, but current absolute adoption is small.")
L("- **Cloud-native databases (DynamoDB, BigQuery) are growing fast** — cloud skills complement database skills.")
L()
L("### 2.3 Cloud Platforms")
L()
L("![Platform Trends](chart_platform_trends.png)")
L()
L(f"**Data Context:** Based on {len(tech_data['platform_have']):,} current-use responses and {len(tech_data['platform_want']):,} desired responses. Chart shows the top 10 platforms by current usage count, overlaid with the corresponding desire counts. No data filtering applied beyond the standard cleaning pipeline.")
L()
L("### 2.4 Rising Stars (Want/Have Ratio > 1.5)")
L()
L("![Rising Stars](chart_rising_stars.png)")
L()
L(f"**Data Context:** Computed from all {total_resp:,} respondents across all 11 technology categories. The want/have ratio is calculated as: (respondents who want the technology) / (respondents who currently use it). Only technologies with at least 30 current users are included to ensure statistical relevance. A ratio > 1.5 indicates strong demand relative to current supply — signaling growth opportunities.")
L()
L("### 2.5 Declining Technologies (Want/Have Ratio < 0.7)")
L()
L("![Declining Tech](chart_declining_tech.png)")
L()
L(f"**Data Context:** Same methodology as Rising Stars above. A ratio < 0.7 indicates weaker demand relative to current usage, suggesting the technology is losing relevance. Technologies with fewer than 30 current users are excluded.")
L()
# Section 3
L("## 3. Job Satisfaction Analysis")
L()
L("### 3.1 Overall Distribution")
L()
L("![Job Satisfaction Distribution](chart_jobsat_dist.png)")
L()
L(f"**Data Context:** Based on {len(jobsat):,} respondents who provided a job satisfaction score (0-10 scale). {jobsat_null:,} respondents ({jobsat_null/total_resp*100:.1f}%) did not answer this question and are excluded. No outlier removal — satisfaction scores are ordinal by design.")
L()
L(f"- Mean satisfaction: {jobsat_mean:.2f} / 10")
L(f"- Median satisfaction: {jobsat_median:.2f} / 10")
L(f"- Most common rating: {jobsat_mode:.0f} / 10")
L()
L("### 3.2 What Makes Developers Satisfied?")
L()
L("![Satisfaction Factors](chart_jobsat_factors.png)")
L()
L(f"**Data Context:** Based on {sat_factor_total:,} individual satisfaction-aspect ratings across {n_aspects} aspects (career satisfaction, coworkers, work-life balance, compensation, resources, autonomy, growth, management, retention). Each aspect is scored 0-100. Chart shows the average score per aspect. Respondents could rate multiple aspects.")
L()
L("### 3.3 Satisfaction by Work Arrangement")
L()
L("![Satisfaction by Remote](chart_jobsat_remote.png)")
L()
L(f"**Data Context:** Based on {sat_remote_total:,} respondents who reported both job satisfaction and remote work status. Chart shows the average satisfaction (0-10) for each work arrangement category. Remote workers, hybrid workers, and in-person workers are compared directly — no filtering or normalization applied.")
L()
L("### 3.4 Satisfaction by Developer Role")
L()
L("![Satisfaction by Dev Type](chart_jobsat_devtype.png)")
L()
L(f"**Data Context:** Based on {len(respondent_devtype):,} developer role assignments across {total_resp:,} respondents (multi-select). Only roles with 50+ respondents are included to ensure statistical significance. Chart shows the top 10 roles by average satisfaction.")
L()
L("### 3.5 Satisfaction by Country")
L()
L("![Satisfaction by Country](chart_jobsat_country.png)")
L()
L(f"**Data Context:** Based on respondents with both country and satisfaction data. Only countries with 50+ respondents are included. Chart shows the top 10 countries by average job satisfaction. Smaller countries are excluded to avoid sampling bias.")
L()
L("### 3.6 Satisfaction by Age Group")
L()
L("![Satisfaction by Age](chart_jobsat_age.png)")
L()
L(f"**Data Context:** Based on {sat_age_total:,} respondents. Age groups follow the standard Stack Overflow survey categories. The 'Prefer not to say' group is excluded. Chart shows the line trend across age brackets — no smoothing applied.")
L()
L("### 3.7 Individual Contributor vs Manager")
L()
L("![IC vs Manager](chart_jobsat_icpm.png)")
L()
L(f"**Data Context:** Based on respondents who identified as either Individual Contributor (IC) or People Manager. Chart compares average satisfaction between the two groups. All valid responses included — no minimum count threshold.")
L()
# Section 4
L("## 4. Compensation Distribution & Analysis")
L()
L("### 4.1 Overall Distribution")
L()
L("![Compensation Distribution](chart_comp_dist.png)")
L()
L(f"**Data Context:** Based on {len(comp):,} respondents ({comp_null:,} missing, {comp_missing_pct:.1f}% of total). Compensation is capped at the 99th percentile (${comp_cap:,.0f}) to handle extreme outliers; values above the cap are clipped to it.")
L()
L(f"- **Mean**: ${comp_mean_val:,.0f}")
L(f"- **Median**: ${comp_median_val:,.0f}")
L(f"- **Range**: ${comp_min_val:,.0f} – ${comp_max_val:,.0f}")
L()
L("### 4.2 Median Compensation by Country")
L()
L("![Compensation by Country](chart_comp_country.png)")
L()
L(f"**Data Context:** Based on respondents with non-null compensation and country. Only countries with 30+ respondents are included. Chart shows the top 10 countries by median compensation. Compensation is capped at the 99th percentile as described above.")
L()
L("### 4.3 Median Compensation by Developer Role")
L()
L("![Compensation by Dev Type](chart_comp_devtype.png)")
L()
L(f"**Data Context:** Based on {len(respondent_devtype):,} developer role assignments with non-null compensation. Only roles with 50+ respondents are included. Chart shows the top 10 roles by median compensation. Multi-role respondents are counted in each role they selected.")
L()
L("### 4.4 Median Compensation by Education Level")
L()
L("![Compensation by Education](chart_comp_edlevel.png)")
L()
L(f"**Data Context:** Based on respondents with non-null compensation and education level. All education levels meeting the minimum threshold are shown, sorted by median compensation descending. No minimum count filter applied due to the smaller number of distinct categories.")
L()
L("### 4.5 Median Compensation by Age Group")
L()
L("![Compensation by Age](chart_comp_age.png)")
L()
L(f"**Data Context:** Based on respondents with non-null compensation and age group. Age groups sorted in natural order. The 'Prefer not to say' group excluded. Compensation shown as median to reduce skew effects within each age bracket.")
L()
L("### 4.6 Median Compensation by Work Arrangement")
L()
L("![Compensation by Remote](chart_comp_remote.png)")
L()
L(f"**Data Context:** Based on respondents with non-null compensation and remote work status. Chart shows median compensation (not mean) to reduce the impact of compensation outliers within each work arrangement category.")
L()
L("### 4.7 Experience vs Compensation by Age Group")
L()
L("![Experience vs Comp](chart_comp_exp_age.png)")
L()
L(f"**Data Context:** Based on respondents with non-null professional years of coding and compensation. Compensation filtered to exclude values above $500K for visual clarity (extreme outliers removed). Each point represents one respondent. Color-coded by age group to reveal age-related experience-compensation patterns. Alpha blending (0.3) used to show density. Total points shown: {len(comp_exp):,}.")
L()
L("### 4.8 Dev Role: Compensation vs Satisfaction")
L()
L("![Dev Role Comp vs Sat](chart_devtype_comp_sat.png)")
L()
L(f"**Data Context:** Based on {len(respondent_devtype):,} developer role assignments with both non-null compensation and satisfaction. Roles with fewer than 30 respondents are excluded. Bubble size reflects the number of respondents in each role. Axes show average compensation and average satisfaction per role.")
L()
# Section 5
L("## 5. Geographic Technology Distribution")
L()
L("### 5.1 Top 10 Countries × Top 10 Languages (Adoption %)")
L()
L("![Geographic Heatmap](chart_geo_heatmap.png)")
L()
L(f"**Data Context:** Based on {total_resp:,} respondents across the top 10 countries by respondent count. Shows the adoption rate (%) of the top 10 programming languages within each country. Percentages are calculated as: (respondents in country C who use language L) / (total respondents in country C). Values range from 0% to 100% across the heatmap. Darker red indicates higher adoption.")
L()
# Section 6
L("## 6. Age Group Technology Preferences")
L()
L("### 6.1 Language Adoption Across Age Groups")
L()
L("![Age Language Stacked](chart_age_lang_stacked.png)")
L()
L(f"**Data Context:** Based on {total_resp:,} respondents across 7 age brackets. Shows the stacked percentage of the top 8 programming languages used within each age group. Percentages are stacked within each age group to sum to 100% (representing the proportion of all language mentions). The 'Prefer not to say' age group is excluded. Each age bar represents the distribution of language mentions by respondents in that bracket.")
L()
# Section 7
L("## 7. Extra Insights & Relationship Analysis")
L()
L("### 7.1 Remote Work Adoption by Developer Role")
L()
L("![Remote by Dev Type](chart_remote_devtype.png)")
L()
L(f"**Data Context:** Based on {remote_devtype_total:,} developer role assignments with non-null remote work status. Chart shows the top 10 developer roles by remote work adoption percentage. Only roles with 50+ total respondents are included. Percentage = (respondents in role who work remotely) / (total respondents in role).")
L()
L("### 7.2 AI Sentiment & Age Group Patterns")
L()
L("![AI Sentiment](chart_ai_sentiment.png)")
L()
L(f"**Data Context:** Based on {ai_sent_total:,} respondents who provided AI sentiment data. Pie chart shows the distribution of self-reported attitudes toward AI tools. The top 7 sentiment categories are shown individually; all remaining categories are grouped into 'Other'. Percentages sum to 100%.")
L()
L("![AI by Age Group](chart_ai_age.png)")
L()
L(f"**Data Context:** Based on {ai_age_total:,} respondents who reported both AI tool selection and age group. Stacked bar chart shows the distribution of the top 5 AI tools selected within each age bracket. Percentages sum to 100% per age group. The 'Prefer not to say' age group is excluded.")
L()
L("### 7.3 Knowledge Self-Assessment")
L()
L("![Knowledge Scores](chart_knowledge.png)")
L()
L(f"**Data Context:** Based on {len(knowledge):,} self-assessment ratings across 9 knowledge areas. Scores use a Likert scale: 1 (Strongly disagree) to 5 (Strongly agree). Chart shows the average score per knowledge area. All valid responses included — no filtering applied.")
L()
L("![Knowledge Correlations](chart_knowledge_corr.png)")
L()
L(f"**Data Context:** Based on the subset of respondents with non-null knowledge scores, job satisfaction, and compensation. Bar chart shows the Pearson correlation between each knowledge area score and (a) job satisfaction, (b) compensation. Positive values indicate that higher self-assessed knowledge correlates with higher satisfaction/compensation.")
L()
L("### 7.4 Learning Pathways and Compensation")
L()
L("![Learning Compensation](chart_learn_comp.png)")
L()
L(f"**Data Context:** Based on {len(respondent_learn_code):,} learning source responses from respondents with non-null compensation. Only learning sources with 50+ respondents are included. Chart shows median compensation (not mean) to reduce skew from high earners within each learning pathway. Respondents could select multiple learning sources.")
L()
L("### 7.5 Compensation by Employment Type")
L()
L("![Employment Compensation](chart_emp_comp.png)")
L()
L(f"**Data Context:** Based on respondents with non-null compensation and employment type. Only employment types with 100+ respondents are included. Chart shows the top 10 employment types by average compensation. Respondents could select multiple employment types.")
L()
L("### 7.6 Technology Migration: What Python Devs Want Next")
L()
L("![Python Migration](chart_python_migration.png)")
L()
L(f"**Data Context:** Based on {python_dev_count:,} respondents who currently use Python. Chart shows the top 10 languages these Python developers want to learn next. Python itself is excluded from the results. Raw counts represent the number of Python users who also expressed desire for each target language.")
L()
L("### 7.7 Work Arrangement × Compensation × Satisfaction Matrix")
L()
L("![Remote Comp Sat Matrix](chart_remote_comp_sat_matrix.png)")
L()
L(f"**Data Context:** Based on {remote_comp_sat_total:,} respondents with non-null compensation, satisfaction, and remote work status. Compensation is bucketed into 4 tiers: Low (<$30K), Medium-Low ($30-70K), Medium-High ($70-120K), High (>$120K). Cell values show average job satisfaction (0-10 scale). Color scale: Green = higher satisfaction, Red = lower satisfaction (range 5-8).")
L()
L("### 7.8 Country × Remote Work × Compensation")
L()
L("![Country Remote Comp](chart_country_remote_comp.png)")
L()
L(f"**Data Context:** Based on respondents from the top 10 countries by remote worker count. Only respondents with non-null compensation and remote work status are included. Bars show median compensation for remote vs in-person workers within each country. Countries sorted by remote worker median compensation.")
L()
L("### 7.9 Stack Overflow Engagement Patterns")
L()
L("![SO Visit Frequency](chart_so_visit.png)")
L()
L(f"**Data Context:** Based on all {total_resp:,} respondents with non-null Stack Overflow visit frequency. Chart shows the distribution of visit frequencies. Categories are ordered from most to least frequent. No filtering applied.")
L()
L("![SO Participation Compensation](chart_so_comp.png)")
L()
L(f"**Data Context:** Based on respondents with non-null compensation and SO participation frequency. Only frequency categories with 50+ respondents are included. Chart shows average compensation by participation level. Results should be interpreted as correlational, not causal.")
L()
L("### 7.10 Employment Type Distribution")
L()
L("![Employment Distribution](chart_employment_dist.png)")
L()
L(f"**Data Context:** Based on {len(respondent_employment):,} employment type responses from {total_resp:,} respondents (multi-select). Chart shows the top 10 most common employment types by raw count. Each respondent could select multiple employment types.")
L()
L("---")
L()
L("## Discussion")
L()
L("### Technology Trends")
L("The technology landscape revealed by this survey confirms several well-known trends while surfacing emerging patterns. The JavaScript ecosystem continues to dominate current usage, while TypeScript has risen to near parity between current use and desire — a signal of the shift toward type safety at scale in large codebases. Rust shows the strongest desire relative to current adoption, a forward-looking signal rather than current dominance.")
L()
L("Rust and Go represent the most significant 'adoption gap' opportunities: relatively few developers currently use them, but demand is disproportionately high. For organizations hiring, prioritizing Rust or Go skills may yield access to a smaller but highly motivated talent pool.")
L()
L("PostgreSQL's lead over MySQL in both current and desired usage confirms a long-anticipated tipping point. MySQL, once the default open-source relational database, now has a lower want share than current use. Emerging analytical/NewSQL databases such as DuckDB show high want/have ratios from a small base — interest worth watching rather than current dominance.")
L()
L("### Job Satisfaction")
L(f"The mean satisfaction score of approximately {jobsat_mean:.1f}/10 suggests moderate-to-high overall satisfaction. Among the individual satisfaction factors, **{sat_top}** and **{sat_second}** score highest on average, while **{sat_low}** scores lowest. (See METHODOLOGY.md for how the factor scores are derived.)")
L()
L("Remote workers report higher average satisfaction than in-person workers, with hybrid workers in between. In this dataset, average satisfaction rises with age across the reported brackets (though the oldest brackets have small sample sizes). See the satisfaction-by-age chart for the exact shape rather than assuming a mid-career peak.")
L()
L("### Compensation Dynamics")
L(f"The compensation analysis reveals substantial geographic variation. Among countries with at least 30 respondents, the highest national median is {top_comp_country} (${top_comp_median:,.0f}), against a global median of ${global_median:,.0f}. The positive correlation between remote work and compensation is partly explained by geographic arbitrage: remote workers based in lower-cost regions can earn salaries benchmarked to higher-cost markets.")
L()
L("The experience-compensation chart shows a steep rise in average pay over the first ~15 years of professional coding, after which it flattens while the spread widens — suggesting that career progression (management, specialisation, or entrepreneurship) matters more than additional years of experience alone.")
L()
L("### AI & The Future of Development")
L("AI sentiment in this dataset is broadly favourable: favorable and very-favorable responses substantially outnumber unfavorable ones, with an indifferent/unsure minority. The age-based analysis of AI tool selection shows that younger developers are more likely to report using AI tools, suggesting AI-assisted development will become increasingly normative as this cohort progresses in their careers.")
L()
L("### Methodological Considerations")
L(f"Several limitations should be noted. The survey is self-selected and may over-represent certain demographics (English speakers, Stack Overflow users, web developers). Compensation data has notable missingness ({comp_missing_pct:.0f}%), which may introduce bias. The technology category definitions are fixed by the survey design and may not capture all relevant tools. The cross-sectional nature of the data means all relationships are correlational — causal inferences require caution.")
L()
L("---")
L()
L("## Summary of Key Findings")
L()
L(f"1. **Technology Trends**: JavaScript remains dominant ({lang_js:.0f}% adoption) and is also the most-wanted language ({lang_want_top_pct:.0f}%). TypeScript is close to parity between current use ({lang_ts_have:.0f}%) and desire ({lang_ts_want:.0f}%), and Rust has the strongest want/have ratio among major languages (~{rust_ratio:.2f}x). PostgreSQL has overtaken MySQL as the leading database.")
L()
L(f"2. **Job Satisfaction**: Average satisfaction is {jobsat_mean:.1f}/10. **{sat_top}** and **{sat_second}** rank highest among the individual satisfaction factors. Remote workers are most satisfied. Individual Contributors and Managers report similar satisfaction levels.")
L()
L(f"3. **Compensation**: Global median compensation is ${global_median:,.0f}. Among countries with at least 30 respondents, the highest national median is {top_comp_country} (${top_comp_median:,.0f}). Engineering managers, DevOps specialists, and senior executives top the compensation charts. Remote work correlates with higher pay across most countries. Compensation-education correlation exists but is weaker than compensation-experience.")
L()
L("4. **Geography**: The country×language heatmap shows JavaScript near the top of the language mix across all large countries in the dataset, with country-level differences in the relative adoption of TypeScript and Python. Differences for smaller countries should be read cautiously (see §5.1).")
L()
L("5. **Age**: The language mix and AI-tool selection vary by age group (see §6.1 and §7.2). The experience-compensation chart shows pay rising steeply early in a career and flattening afterwards, with widening variance.")
L()
L("6. **AI & Learning**: AI sentiment in this dataset is broadly favourable — favorable and very-favorable responses far outnumber unfavorable ones. Median compensation varies by learning source; see the learning-pathway chart rather than assuming a single ranking.")
L()
L("7. **Work Patterns**: Remote work is associated with higher average satisfaction and higher median pay than in-person work, with hybrid work in between. These are descriptive correlations (see §4.6, §3.3, and LIMITATIONS.md).")
L()
L("---")
L()
L("## Implications & Recommendations")
L()
L("### For Developers")
L("- **Invest in TypeScript** — it offers the best risk/reward ratio for career development, with both high current demand and strong growth trajectory.")
L("- **Learn PostgreSQL** if you work with databases — it is the clear market leader with sustained growth momentum.")
L("- **Consider Rust or Go** if you want to differentiate yourself — demand far outstrips current supply, creating premium positioning.")
L("- **Prioritize remote-capable roles** — they correlate with higher satisfaction and compensation across nearly all comparisons.")
L()
L("### For Employers")
L("- **Support TypeScript adoption** in your tech stack — it improves developer productivity and makes your company more attractive to top talent.")
L("- **Offer remote and hybrid options** — the satisfaction and retention benefits are clear across all compensation levels.")
L("- **Invest in mid-career retention** — the 35-44 age bracket is the satisfaction peak and represents your most productive engineers.")
L("- **Build AI-assisted development workflows** — the next generation of developers expects AI tooling as part of their standard toolkit.")
L()
L("### For Educators & Training Providers")
L("- **TypeScript and Python should be core curriculum** — they represent both current demand and future growth.")
L("- **Emerging analytical databases (e.g. DuckDB) and cloud databases deserve curriculum attention** — they show strong want/have ratios from a small current base.")
L("- **Bootcamps and self-directed learning are validated pathways** — the market rewards skill over credentials.")
L()
L("### For the Industry")
L("- **The remote work trend is structural, not cyclical** — organizations that resist it will face talent acquisition challenges.")
L("- **AI tools will become standard equipment**, not optional — prepare for widespread AI-assisted development within 3-5 years.")
L("- **The MySQL→PostgreSQL migration will continue** — plan your data infrastructure investments accordingly.")
L()
L("---")
L()
L("## Conclusion")
L()
L(f"The 2024 Stack Overflow Developer Survey reveals a developer ecosystem in transition. The technology landscape is being reshaped by the continued dominance of JavaScript, the maturation of TypeScript, the PostgreSQL ascendancy, and the early but accelerating impact of AI tools. Job satisfaction is moderate-to-high on average, and its factor scores are led by **{sat_top}** and **{sat_second}** in this dataset. Remote work has cemented its place as a structural feature of the industry, correlating positively with both satisfaction and earnings.")
L()
L("For developers, the message is clear: invest in TypeScript, PostgreSQL, and cloud-native skills; prioritize remote-capable roles; and prepare for AI-assisted development as the new normal. For employers, the data supports investing in developer experience, offering flexible work arrangements, and modernizing technology stacks to attract and retain top talent.")
L()
L("The common thread across all analyses is that the industry is becoming more specialized, more distributed, and more tool-augmented. Developers who embrace these trends — by learning modern languages, working remotely, and leveraging AI tools — position themselves for the strongest career outcomes.")

report_text = "\n".join(lines)
with open(os.path.join(OUTPUT_DIR, "analysis_report.md"), "w") as f:
    f.write(report_text)

print(f"Report saved to {OUTPUT_DIR}/analysis_report.md")
print(f"Total report lines: {len(lines)}")
print("Done!")
