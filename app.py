# app.py

"""
Main application file. This runs the simulation, prepares the data,
and will eventually house the Gradio interface for interactive analysis.
"""

import pandas as pd
import gradio as gr

# Import all the necessary components from your new modules
from config.constants import *
from config.scenarios import BASE_CONFIG, apply_scenario_config, generate_scenario_name
from simulation.adventurers import (
    run_gagarin_scenario, run_leo_scenario, run_dragon_girl_scenario
)
from utils.analysis import (
    plot_damage_analysis, plot_total_cumulative_damage,
    plot_normalized_total_damage, plot_damage_per_use,
    plot_normalized_damage_per_use
)

from copy import deepcopy

def run_full_simulation(scenario1_config, scenario2_config):
    """
    Runs the entire simulation for all adventurers and both scenarios,
    and returns the resulting dataframes.
    """

    # Apply scenario configurations
    df_gaga_skill_1, df_gaga_rounds_1, _ = run_gagarin_scenario(scenario1_config, "Scenario 1")
    df_gaga_skill_2, df_gaga_rounds_2, _ = run_gagarin_scenario(scenario2_config, "Scenario 2")

    df_leo_skill_1, df_leo_rounds_1, _ = run_leo_scenario(scenario1_config, "Scenario 1")
    df_leo_skill_2, df_leo_rounds_2, _ = run_leo_scenario(scenario2_config, "Scenario 2")

    df_dg_skill_1, df_dg_rounds_1, _ = run_dragon_girl_scenario(scenario1_config, "Scenario 1")
    df_dg_skill_2, df_dg_rounds_2, _ = run_dragon_girl_scenario(scenario2_config, "Scenario 2")


    # Combine results
    df_gaga_skill = pd.concat([df_gaga_skill_1, df_gaga_skill_2], ignore_index=True)
    df_gaga_rounds = pd.concat([df_gaga_rounds_1, df_gaga_rounds_2], ignore_index=True)
    
    df_leo_skill = pd.concat([df_leo_skill_1, df_leo_skill_2], ignore_index=True)
    df_leo_rounds = pd.concat([df_leo_rounds_1, df_leo_rounds_2], ignore_index=True)

    df_dg_skill = pd.concat([df_dg_skill_1, df_dg_skill_2], ignore_index=True)
    df_dg_rounds = pd.concat([df_dg_rounds_1, df_dg_rounds_2], ignore_index=True)

    df_all_skills = pd.concat([df_leo_skill, df_gaga_skill, df_dg_skill], ignore_index=True)
    df_all_rounds = pd.concat([df_leo_rounds, df_gaga_rounds, df_dg_rounds], ignore_index=True)
    
    # --- Post-processing ---
    df_all_skills["total"] = df_all_skills[["total_dragon_girl", "total_gagarin", "total_leonardo"]].max(axis=1)
    
    # Ensure numeric columns are correct
    excluded_cols = {"source", "scenario", "level", "total", "breakdowns"}
    damage_types = [
        col for col in df_all_skills.columns 
        if col not in excluded_cols and not col.startswith("Unnamed") and col != 'cooldown'
    ]
    df_all_skills[damage_types] = df_all_skills[damage_types].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_all_rounds["total_damage"] = pd.to_numeric(df_all_rounds["total_damage"], errors="coerce").fillna(0)
    
    # Standardize level column
    df_all_skills["level"] = df_all_skills["level"].astype(int)
    df_all_rounds["level"] = df_all_rounds["level"].astype(int)

    return df_all_skills, df_all_rounds


if __name__ == "__main__":
    SCENARIO_1 = {
        "name": "Stat Sheet 1",
        Num_Rage_Strikes: 1,
        Num_Combos: 1,
        Global_Skill_DMG_pct: 0,
        Global_DMG_pct: 0,
        Skill_DMG_pct: 0,
    }

    SCENARIO_2 = {
        "name": "Stat Sheet 2",
        Num_Daggers: 21,
        Bonus_Dagger_Coef: 0.09,
        Dagger_DMG_pct: 85,
        Physical_DMG_pct: 90,
        Num_Rage_Strikes: 3,
        Damage_pct: 25,
        Global_Skill_DMG_pct: 40,
        Global_DMG_pct: 30,
        Skill_DMG_pct: 200,
    }
    SCENARIO_1["name"] = generate_scenario_name({}, SCENARIO_1)
    SCENARIO_2["name"] = generate_scenario_name(SCENARIO_1, SCENARIO_2)

    cfg1 = apply_scenario_config(BASE_CONFIG, SCENARIO_1)
    cfg2 = apply_scenario_config(BASE_CONFIG, SCENARIO_2)
    
    # Run the full simulation with the predefined scenarios
    df_all_skills, df_all_rounds = run_full_simulation(cfg1, cfg2)
    
    print("--- Simulation Complete ---")
    print("\n--- All Skills DataFrame (Sample) ---")
    print(df_all_skills.head())
    
    print("\n--- All Rounds DataFrame (Sample) ---")
    print(df_all_rounds.head())

    # Generate and display the plots for each adventurer
    SCENARIO_NAME_MAP = {
    "Scenario 1": SCENARIO_1["name"],
    "Scenario 2": SCENARIO_2["name"],
}
    
    print("\n--- Generating Plots ---")
    
    
    plot_damage_analysis(
        df_all_skills,
        df_all_rounds,
        source="gagarin",
        scenario_name_map=SCENARIO_NAME_MAP,
        title_override="Gagarin Damage Analysis"
    )

    plot_damage_analysis(
        df_all_skills,
        df_all_rounds,
        source="leonardo",
        scenario_name_map=SCENARIO_NAME_MAP,
        title_override="Leonardo Damage Analysis"
    )

    plot_damage_analysis(
        df_all_skills,
        df_all_rounds,
        source="dragon_girl",
        scenario_name_map=SCENARIO_NAME_MAP,
        title_override="Dragon Girl Damage Analysis",
    )

    plot_total_cumulative_damage(df_all_rounds, scenario_name_map=SCENARIO_NAME_MAP)
    plot_normalized_total_damage(df_all_rounds, scenario_name_map=SCENARIO_NAME_MAP)
    plot_damage_per_use(df_all_skills, scenario_name_map=SCENARIO_NAME_MAP)
    plot_normalized_damage_per_use(df_all_skills, scenario_name_map=SCENARIO_NAME_MAP)