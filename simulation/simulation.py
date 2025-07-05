import pandas as pd

from simulation.adventurers import (    run_gagarin_scenario,
    run_leo_scenario,
    run_dragon_girl_scenario
)

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
