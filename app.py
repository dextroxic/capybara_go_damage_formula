# app.py

"""
Main application file. This runs the simulation, prepares the data,
and houses the Gradio interface for interactive analysis.
"""

import pandas as pd
import gradio as gr

# Import all the necessary components from your new modules
from config.constants import *
from config.scenarios import BASE_CONFIG
from simulation.adventurers import (
    run_gagarin_scenario, run_leo_scenario, run_dragon_girl_scenario
)
from utils.analysis import (
    plot_damage_analysis,
    plot_normalized_total_damage, plot_total_cumulative_damage
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


# Grouped input sections
group_sections = [
    ("Core Stats", [
        P_ATK, P_Strength, P_ATK_pct, P_Global_ATK_pct, Rage_ATK_coef,
        Num_Combos, Num_Basic_Attacks
    ]),
    ("Crit Stats", [
        Crit_Chance_pct, Skill_Crit_Chance_pct, Weapon_Crit_Chance_pct,
        Basic_Crit_Chance_pct, Crit_DMG_pct
    ]),
    ("Local Dmg Mods", [
        Skill_DMG_pct, Physical_DMG_pct, Dagger_DMG_pct, Bolt_DMG_pct, Chi_DMG_pct,
        Fire_DMG_pct, Ice_DMG_pct, Lightning_DMG_pct, Basic_ATK_DMG_pct, Combo_DMG_pct,
        Rage_DMG_pct, Counter_DMG_pct, Poison_DMG_pct, Burn_DMG_pct, Light_Spear_DMG_pct,
        DoT_DMG_pct, Damage_pct
    ]),
    ("Global Dmg Mods", [
        Global_Skill_DMG_pct, Global_Physical_DMG_pct, Global_Dagger_DMG_pct,
        Global_Bolt_DMG_pct, Global_Chi_DMG_pct, Global_Fire_DMG_pct, Global_Ice_DMG_pct,
        Global_Lightning_DMG_pct, Global_Basic_ATK_DMG_pct, Global_Combo_DMG_pct,
        Global_Rage_DMG_pct, Global_Counter_DMG_pct, Global_Poison_DMG_pct,
        Global_Burn_DMG_pct, Global_Light_Spear_DMG_pct, Global_DoT_DMG_pct,
        Global_DMG_pct, Global_Dragon_Flame_DMG_pct 
    ]),
    ("Weapon Coef Mods", BONUS_COEF_KEYS),
    ("Skill Usage Counts", [
        Num_Daggers, Num_Rage_Strikes, Num_Bolts, Num_Death_Bolts, Num_Chi_Hits,
        Num_Burns, Num_Poisons, Num_Light_Spears, Num_Icy_Spikes, Num_Counter_Attacks
    ]),
    ("Other", [
        Max_Poison_Stacks, Max_Burn_Stacks, Final_DMG_pct, ENEMY_HP, MAX_HP
    ])
]

# Create tabs for one scenario and return list of input components
def create_scenario_tabs(scenario: dict):
    components = []
    for group_name, keys in group_sections:
        with gr.Tab(label=group_name):
            # Group inputs two at a time to make two columns
            for i in range(0, len(keys), 2):
                key1 = keys[i]
                default1 = scenario.get(key1, 0)

                # Optional second key
                key2 = keys[i+1] if i + 1 < len(keys) else None
                default2 = scenario.get(key2, 0) if key2 else None

                with gr.Row(equal_height=True):
                    with gr.Column():
                        comp1 = gr.Number(label=f"{key1}:", value=default1)
                        components.append(comp1)
                    if key2:
                        with gr.Column():
                            comp2 = gr.Number(label=f"{key2}:", value=default2)
                            components.append(comp2)
    return components


def run_analysis_with_inputs(*args):
    num_keys = len([k for _, keys in group_sections for k in keys])
    s1_values = dict(zip([k for _, keys in group_sections for k in keys], args[:num_keys]))
    s2_values = dict(zip([k for _, keys in group_sections for k in keys], args[num_keys:]))

    df_skills, df_rounds = run_full_simulation(s1_values, s2_values)

    SCENARIO_NAME_MAP = {
        "Scenario 1": "Scenario 1",
        "Scenario 2": "Scenario 2",
    }

    # === Plots ===
    fig1 = plot_damage_analysis(df_skills, df_rounds, "gagarin", SCENARIO_NAME_MAP, "Gagarin Damage")
    fig2 = plot_damage_analysis(df_skills, df_rounds, "leonardo", SCENARIO_NAME_MAP, "Leonardo Damage")
    fig3 = plot_damage_analysis(df_skills, df_rounds, "dragon_girl", SCENARIO_NAME_MAP, "Dragon Girl Damage")
    fig4 = plot_total_cumulative_damage(df_rounds, scenario_name_map=SCENARIO_NAME_MAP)
    fig5 = plot_normalized_total_damage(df_rounds, scenario_name_map=SCENARIO_NAME_MAP)

    # === DataTables ===
    df_skills_clean = df_skills.drop(columns=["breakdowns"], errors="ignore")

    breakdown_rows = []
    for _, row in df_skills.iterrows():
        if isinstance(row.get("breakdowns"), dict):
            for skill, breakdown in row["breakdowns"].items():
                if breakdown:
                    breakdown_dict = breakdown.as_dict()
                    breakdown_dict.update({
                        "Source": row["source"],
                        "Scenario": row["scenario"],
                        "Level": row["level"]
                    })
                    breakdown_rows.append(breakdown_dict)

    df_breakdowns = pd.DataFrame(breakdown_rows)

    return fig1, fig2, fig3, fig4, fig5, df_skills_clean, df_breakdowns

def clean_config(config):
    return {k: v for k, v in config.items() if isinstance(v, (int, float)) and v != 0}

def format_config_dict(name: str, config: dict) -> str:
    lines = [f"{name} = {{"]
    for k, v in config.items():
        if isinstance(v, (int, float)) and v != 0:
            lines.append(f"    {k!r}: {v},")
    lines.append("}")
    return "\n".join(lines)

def format_config_diff(s1: dict, s2: dict) -> str:
    diff = {}
    for k in s1:
        if s1.get(k, 0) != s2.get(k, 0):
            if s1.get(k, 0) != 0 or s2.get(k, 0) != 0:
                diff[k] = (s1.get(k, 0), s2.get(k, 0))
    lines = ["DIFF = {"]
    for k, (v1, v2) in diff.items():
        lines.append(f"    {k!r}: ({v1}, {v2}),")
    lines.append("}")
    return "\n".join(lines)

def update_config_preview(*args):
    keys = [k for _, group in group_sections for k in group]
    half = len(args) // 2
    s1 = dict(zip(keys, args[:half]))
    s2 = dict(zip(keys, args[half:]))

    s1_clean = format_config_dict("SCENARIO_1", s1)
    s2_clean = format_config_dict("SCENARIO_2", s2)
    diff_clean = format_config_diff(s1, s2)

    return s1_clean, s2_clean, diff_clean


with gr.Blocks() as demo:
    # Gradio UI setup
    gr.Markdown("""
    # 🧮 Capybara Damage Simulator

    ## Welcome to the **Capybara Go Damage Simulator**, a tool designed to help you simulate and compare skill-based damage across different adventurers, skill levels, and configurations.
    ---
    ### 🔧 How to Use

    1. **Input your base stats** from your in-game character sheet. These include:
    - `P_ATK`, `P_Crit_DMG_pct`, `P_Rel_DMG_pct`, etc.
    - Use the raw values shown on your **stats screen**.

    2. ⚠️ **Important Note:**
    Stats displayed in-game do **not** include additional modifiers from:
    - Skill trees
    - Brands and inheritance trees
    - In-battle effects (buffs, skill passives, etc.)

    Be sure to **add those extra values manually** for an accurate simulation.

    3. **Skill Usage**:
    - Set how many times a skill is used per round using fields like `Num_Daggers`, `Num_Rage_Strikes`, `Num_Bolts`, etc.
    - You can simulate different skill rotations by adjusting these counts.

    4. **Run the Simulation**:
    - Configure two scenarios side by side (left and right).
    - Click **Run Damage Analysis** to visualize total and per-round damage.
    - Switch to the **Breakdowns** tab to inspect the full damage calculation behind each skill.
    ---
    """)

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Scenario 1 Configuration")
            s1_inputs = create_scenario_tabs(BASE_CONFIG)
        with gr.Column():
            gr.Markdown("### Scenario 2 Configuration")
            s2_inputs = create_scenario_tabs(BASE_CONFIG)

    with gr.Accordion("🧩 View Current Scenario Configurations", open=False):
        with gr.Row():
            scenario1_code = gr.Code(label="Scenario 1 Config", language="python", interactive=False)
            scenario2_code = gr.Code(label="Scenario 2 Config", language="python", interactive=False)
            scenario_diff_code = gr.Code(label="Scenario Differences", language="python", interactive=False)

    # Attach change listeners to all inputs
    for comp in s1_inputs + s2_inputs:
        comp.change(
            fn=update_config_preview,
            inputs=s1_inputs + s2_inputs,
            outputs=[scenario1_code, scenario2_code, scenario_diff_code],
            show_progress=False
        )

    run_btn = gr.Button("Run Damage Analysis")

    with gr.Tab("Damage Plots"):
        fig1 = gr.Plot(label="Gagarin Damage")
        fig2 = gr.Plot(label="Leonardo Damage")
        fig3 = gr.Plot(label="Dragon Girl Damage")
        fig4 = gr.Plot(label="Total Cumulative Damage")
        fig5 = gr.Plot(label="Normalized Total Damage")

    with gr.Tab("Skill Damage Breakdown Table"):
        df_skills_view = gr.Dataframe(label="Total Damage by Skill", interactive=False)

    with gr.Tab("Detailed Coefficient Breakdown"):
        df_breakdown_view = gr.Dataframe(label="Per-Skill Breakdown", interactive=False)


    run_btn.click(
        fn=run_analysis_with_inputs,
        inputs=s1_inputs + s2_inputs,
        outputs=[fig1, fig2, fig3, fig4, fig5, df_skills_view, df_breakdown_view]
    )


if __name__ == "__main__":
    demo.launch()
