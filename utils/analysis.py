# utils/analysis.py

"""
Utility functions for data preprocessing and visualization of the
simulation results.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns


def preprocess_skill_comparison(df_all_skills, source, scenario_1="Scenario 1", scenario_2="Scenario 2"):
    df1 = df_all_skills[
        (df_all_skills["source"] == source) & (df_all_skills["scenario"] == scenario_1)
    ].copy()

    df2 = df_all_skills[
        (df_all_skills["source"] == source) & (df_all_skills["scenario"] == scenario_2)
    ].copy()

    df_merged = pd.merge(df1, df2, on="level", suffixes=("_1", "_2"))
    return df1, df2, df_merged

def build_percent_change_table(df_merged, damage_types):
    rows = []
    for _, row in df_merged.iterrows():
        level = row["level"]
        for dmg in damage_types:
            col1 = f"{dmg}_1"
            col2 = f"{dmg}_2"
            if col1 not in row or col2 not in row:
                continue

            val1 = row[col1]
            val2 = row[col2]

            if val1 == 0:
                pct_diff = None
                relative = None
            else:
                pct_diff = 100 * (val2 - val1) / val1
                relative = val2 / val1

            rows.append({
                "level": level,
                "DamageType": dmg,
                "Scenario1": val1,
                "Scenario2": val2,
                "PercentChange": pct_diff,
                "Relative": relative
            })

    return pd.DataFrame(rows)

def get_relevant_damage_types(df, threshold=0.01, exclude_cols=None):
    """
    Identifies damage types that contribute significantly to total damage.
    """
    exclude_cols = exclude_cols or {"level", "source", "scenario", "total", "total_damage", "damageperuse", "damage_per_use", "total_gagarin", "total_leonardo", "total_dragon_girl"}
    candidate_cols = [
        col for col in df.columns
        if col not in exclude_cols and df[col].dtype != "O"
    ]
    return [
        col for col in candidate_cols
        if (df[col] / df["total"]).fillna(0).gt(threshold).any()
    ]


def combine_minor_damage_types(df, damage_types, threshold=0.05):
    """
    Groups damage types that contribute less than a threshold into an 'Other' category.
    """
    combined = []
    for dt in damage_types:
        if dt not in df.columns:
            continue
        share = df[dt] / df["total"]
        if (share < threshold).all():
            combined.append(dt)

    if combined:
        label = "combined - " + ", ".join(combined)
        df[label] = df[combined].sum(axis=1)
        df = df.drop(columns=combined)
        damage_types = [d for d in damage_types if d not in combined]
        damage_types.append(label)
    return df, damage_types


def plot_damage_analysis(
    df_all_skills,
    df_all_rounds,
    source,
    scenario_name_map,
    damage_types=None,
    auto_detect=True,
    threshold_minor=0.05,
    title_override=None
):

    sns.set_theme(style="whitegrid", palette="Set2")

    df_source = df_all_skills[df_all_skills["source"] == source].copy()

    if auto_detect or damage_types is None:
        damage_types = get_relevant_damage_types(df_source)

    df1, df2, df_merged = preprocess_skill_comparison(df_all_skills, source)
    df_compare = build_percent_change_table(df_merged, damage_types=damage_types)

    title = title_override or f"{source.title()} Damage Analysis"

    # === Plot
    fig = plt.figure(figsize=(20, 18))
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1.2])
    fig.suptitle(title, fontsize=18, y=0.97)

    # Row 1
    for i, (scenario, df_plot_orig) in enumerate([("Scenario 1", df1), ("Scenario 2", df2)]):
        ax = fig.add_subplot(gs[0, i])
        df_plot = df_plot_orig.copy()
        df_plot, types_used = combine_minor_damage_types(df_plot, damage_types, threshold=threshold_minor)
        df_plot.plot(x="level", y=types_used, ax=ax, marker="o")
        ax.set_title(f"{scenario} - Per Use Damage", fontsize=13)
        if scenario in scenario_name_map:
            ax.text(0.5, 1.1, scenario_name_map[scenario], fontsize=10,
                    ha="center", transform=ax.transAxes)
        ax.set_xlabel("level")
        ax.set_ylabel("Damage")
        ax.grid(True)
        ax.legend(fontsize=8)

    # Row 2
    for i, scenario in enumerate(["Scenario 1", "Scenario 2"]):
        ax = fig.add_subplot(gs[1, i])
        df_r = df_all_rounds[
            (df_all_rounds["source"] == source) & (df_all_rounds["scenario"] == scenario)
        ]
        for lvl in df_r["level"].unique():
            sub = df_r[df_r["level"] == lvl]
            ax.plot(sub["round"], sub["total_damage"], label=f"Lvl {lvl}")
        ax.set_title(f"{scenario} - Cumulative Damage", fontsize=13)
        ax.set_xlabel("round")
        ax.set_ylabel("Damage")
        ax.grid(True)
        ax.legend(fontsize=8)

    # Row 3
    ax_full = fig.add_subplot(gs[2, :])
    sns.barplot(
        data=df_compare,
        y="DamageType",
        x="Relative",
        hue="level",
        orient="h",
        dodge=True,
        ax=ax_full
    )
    ax_full.axvline(1.0, color="black", linestyle="--", linewidth=1)

    for container in ax_full.containers:
        for bar in container:
            width = bar.get_width()
            if width == 0 or width is None:
                continue
            label = f"{abs(width - 1) * 100:.0f}% {'stronger' if width > 1 else 'weaker'}"
            x = width + 0.02 if width > 1 else width - 0.02
            ax_full.text(
                x,
                bar.get_y() + bar.get_height() / 2,
                label,
                ha="left" if width > 1 else "right",
                va="center",
                fontsize=9,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
            )

    ax_full.set_title(f"Scenario 2 vs Scenario 1 — {source.title()} Damage Categories by Level", fontsize=13)
    ax_full.set_xlabel("Relative Damage (Scenario 1 = 1.0)")
    ax_full.set_ylabel("Damage Category")
    ax_full.legend(title="level", bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig


def plot_total_cumulative_damage(df_all_rounds, scenario_name_map=None):
    df_final_round = df_all_rounds[df_all_rounds["round"] == 10].copy()
    df_final_round["level"] = pd.to_numeric(df_final_round["level"], errors="coerce")
    df_final_round["total_damage"] = pd.to_numeric(df_final_round["total_damage"], errors="coerce")

    df_final_round["stacks_label"] = ""
    if "stacks" in df_final_round.columns:
        dg_mask = df_final_round["source"].str.lower().str.contains("dragon")
        df_final_round.loc[dg_mask, "stacks_label"] = " - " + df_final_round.loc[dg_mask, "stacks"].astype(str)

    df_final_round["label"] = df_final_round["source"] + df_final_round["stacks_label"]

    scenarios = df_final_round["scenario"].unique()
    fig, axs = plt.subplots(
        nrows=1, ncols=len(scenarios), figsize=(9 * len(scenarios), 6), constrained_layout=True
    )

    axs = [axs] if len(scenarios) == 1 else axs.flatten()

    for i, scenario in enumerate(scenarios):
        df_scenario = df_final_round[df_final_round["scenario"] == scenario]
        ax = axs[i]

        sns.lineplot(
            data=df_scenario,
            x="level",
            y="total_damage",
            hue="label",
            marker="o",
            ax=ax
        )

        scenario_name = scenario_name_map.get(scenario, scenario) if scenario_name_map else scenario
        title_wrapped = f"Cumulative Damage After 10 Rounds\n{scenario_name}"
        ax.set_title(title_wrapped, fontsize=13)

        ax.set_ylabel("Total Cumulative Damage")
        ax.set_xlabel("Skill Level")
        ax.legend(title="Adventurer", fontsize=9)
        ax.grid(True)

    return (fig)


def plot_normalized_total_damage(df_all_rounds, scenario_name_map=None):
    df_all_rounds["stacks_label"] = ""
    if "stacks" in df_all_rounds.columns:
        dg_mask = df_all_rounds["source"].str.lower().str.contains("dragon")
        df_all_rounds.loc[dg_mask, "stacks_label"] = " - " + df_all_rounds.loc[dg_mask, "stacks"].astype(str)

    # Create unified label
    df_all_rounds["label"] = df_all_rounds["source"] + df_all_rounds["stacks_label"]

    df_all_rounds.columns = df_all_rounds.columns.str.lower()
    df_final_round = df_all_rounds[df_all_rounds["round"] == 10].copy()

    gaga_lvl7 = df_final_round[
        (df_final_round["source"] == "gagarin") &
        (df_final_round["level"] == 7)
    ].copy()

    gaga_lvl8 = gaga_lvl7.copy()
    gaga_lvl8["level"] = 8
    df_final_round = pd.concat([df_final_round, gaga_lvl8], ignore_index=True)

    baseline = df_final_round[df_final_round["source"] == "leonardo"][["scenario", "level", "total_damage"]]
    baseline = baseline.rename(columns={"total_damage": "leonardodamage"})

    df_norm = df_final_round.merge(baseline, on=["scenario", "level"], how="left")
    df_norm["normalized"] = df_norm["total_damage"] / df_norm["leonardodamage"]

    unique_scenarios = df_norm["scenario"].unique()
    fig, axs = plt.subplots(1, len(unique_scenarios), figsize=(9 * len(unique_scenarios), 6))
    axs = [axs] if len(unique_scenarios) == 1 else axs

    fig.suptitle(f"Normalized Total Damage After 10 Rounds: {' vs '.join(unique_scenarios)}", fontsize=16, y=1.03)

    for i, scenario in enumerate(unique_scenarios):
        df_plot = df_norm[(df_norm["scenario"] == scenario) & df_norm["normalized"].notna()]
        ax = axs[i]

        sns.barplot(
            data=df_plot,
            y="label",
            x="normalized",
            hue="level",
            orient="h",
            dodge=True,
            ax=ax
        )

        ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
        title = scenario_name_map.get(scenario, scenario) if scenario_name_map else scenario
        ax.set_title(f"Normalized Damage — {title}")
        ax.set_xlabel("Relative Damage (Leonardo = 1.0)")
        ax.set_ylabel("Adventurer")

        for container in ax.containers:
            for bar in container:
                width = bar.get_width()
                if pd.notna(width):
                    diff_pct = (width - 1) * 100
                    label = f"{abs(diff_pct):.0f}% {'stronger' if diff_pct > 0 else 'weaker' if diff_pct < 0 else 'equal'}"
                    text_x = width + 0.01 if width > 0 else width - 0.01
                    text_y = bar.get_y() + bar.get_height() / 2
                    ax.text(
                        text_x, text_y, label,
                        va="center",
                        ha="left" if width > 0 else "right",
                        fontsize=9,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
                    )

        ax.legend(title="Skill Level", bbox_to_anchor=(1.02, 1), loc="upper left")
        ax.grid(True)

    return fig


def plot_damage_per_use(df_all_skills, scenario_name_map=None):
    df_all_skills["damage_per_use"] = pd.to_numeric(df_all_skills["total"], errors="coerce")
    df_all_skills["stacks_label"] = ""

    if "stacks" in df_all_skills.columns:
        dg_mask = df_all_skills["source"].str.lower().str.contains("dragon")
        df_all_skills.loc[dg_mask, "stacks_label"] = " - " + df_all_skills.loc[dg_mask, "stacks"].astype(str)

    df_all_skills["label"] = df_all_skills["source"] + df_all_skills["stacks_label"]
    df_all_skills["level"] = pd.to_numeric(df_all_skills["level"], errors="coerce")
    df_all_skills["scenario"] = df_all_skills["scenario"].astype(str)

    sns.set(style="whitegrid")
    scenarios = df_all_skills["scenario"].unique()
    fig, axs = plt.subplots(nrows=1, ncols=len(scenarios), figsize=(9 * len(scenarios), 6))
    axs = [axs] if len(scenarios) == 1 else axs.flatten()

    for i, scenario in enumerate(scenarios):
        ax = axs[i]
        df_scenario = df_all_skills[df_all_skills["scenario"] == scenario]

        sns.lineplot(
            data=df_scenario,
            x="level",
            y="damage_per_use",
            hue="label",
            marker="o",
            ax=ax
        )

        title = scenario_name_map.get(scenario, scenario) if scenario_name_map else scenario
        ax.set_title(f"Damage Per Use by Level – \n{title}", fontsize=13)
        ax.set_ylabel("Total Damage Per Use")
        ax.set_xlabel("Skill Level")
        ax.grid(True)
        ax.legend(title="Adventurer", fontsize=9)

    return fig


def plot_normalized_damage_per_use(df_all_skills, scenario_name_map=None):
    df_all_skills.columns = df_all_skills.columns.str.lower()
    df_all_skills["damageperuse"] = pd.to_numeric(df_all_skills["total"], errors="coerce")

    gaga_lvl7 = df_all_skills[
        (df_all_skills["source"] == "gagarin") &
        (df_all_skills["level"] == 7)
    ].copy()

    gaga_lvl8 = gaga_lvl7.copy()
    gaga_lvl8["level"] = 8
    df_all_skills = pd.concat([df_all_skills, gaga_lvl8], ignore_index=True)

    df_all_skills["stackslabel"] = ""
    if "stacks" in df_all_skills.columns:
        dg_mask = df_all_skills["source"] == "dragon_girl"
        df_all_skills.loc[dg_mask, "stackslabel"] = " - " + df_all_skills.loc[dg_mask, "stacks"].astype(str)

    df_all_skills["label"] = df_all_skills["source"] + df_all_skills["stackslabel"]

    baseline = df_all_skills[df_all_skills["source"] == "leonardo"][["scenario", "level", "damageperuse"]]
    baseline = baseline.rename(columns={"damageperuse": "leonardodamage"})

    df_norm = df_all_skills.merge(baseline, on=["scenario", "level"], how="left")
    df_norm["normalized"] = df_norm["damageperuse"] / df_norm["leonardodamage"]

    unique_scenarios = df_norm["scenario"].unique()
    fig, axs = plt.subplots(1, len(unique_scenarios), figsize=(9 * len(unique_scenarios), 6))
    axs = [axs] if len(unique_scenarios) == 1 else axs

    fig.suptitle(f"Damage Comparison Across Scenarios: {' vs '.join(unique_scenarios)}", fontsize=16, y=1.03)

    for i, scenario in enumerate(unique_scenarios):
        df_plot = df_norm[(df_norm["scenario"] == scenario) & df_norm["normalized"].notna()]
        ax = axs[i]

        sns.barplot(
            data=df_plot,
            y="label",
            x="normalized",
            hue="level",
            orient="h",
            dodge=True,
            ax=ax
        )

        ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
        title = scenario_name_map.get(scenario, scenario) if scenario_name_map else scenario
        ax.set_title(f"Normalized Damage — {title}")
        ax.set_xlabel("Relative Damage (Leonardo = 1.0)")
        ax.set_ylabel("Adventurer")

        for container in ax.containers:
            for bar in container:
                width = bar.get_width()
                if pd.notna(width):
                    diff_pct = (width - 1) * 100
                    label = f"{abs(diff_pct):.0f}% {'stronger' if diff_pct > 0 else 'weaker' if diff_pct < 0 else 'equal'}"
                    text_x = width + 0.01 if width > 0 else width - 0.01
                    text_y = bar.get_y() + bar.get_height() / 2
                    ax.text(
                        text_x, text_y, label,
                        va="center",
                        ha="left" if width > 0 else "right",
                        fontsize=9,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
                    )

        ax.legend(title="Skill Level", bbox_to_anchor=(1.02, 1), loc="upper left")
        ax.grid(True)

    return fig
