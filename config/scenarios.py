# config/scenarios.py

"""
This module defines the default configuration, the specific scenarios for
comparison, and utility functions for managing these configurations.
"""

import copy
from .constants import *

# === [0] Short Name Map ===

def build_short_name_map():
    short_names = {}

    # Count keys → N_<Skill>
    for key in SKILL_COUNT_KEYS:
        base = key.replace("Num_", "")
        short_names[key] = f"N_{base}"

    # Bonus Coefficients → C_<Skill>
    for key in BONUS_COEF_KEYS:
        base = key.replace("Bonus_", "").replace("_Coef", "")
        short_names[key] = f"C_{base}"

    # Global Modifiers → G_<Skill>
    for key in GLOBAL_MOD_KEYS:
        base = key.replace("Global_", "").replace("_pct", "")
        short_names[key] = f"G_{base}"

    # Local Modifiers → D_<Skill>
    for key in LOCAL_MOD_KEYS:
        base = key.replace("_pct", "")
        short_names[key] = f"D_{base}"

    # Other singleton keys
    short_names[Final_DMG_pct] = "Final"
    short_names[Damage_pct] = "D_All"
    short_names[Crit_DMG_pct] = "CritD"
    short_names[Crit_Chance_pct] = "Crit%"
    short_names[Skill_Crit_Chance_pct] = "SkillCrit%"
    short_names[Weapon_Crit_Chance_pct] = "WpnCrit%"
    short_names[Basic_Crit_Chance_pct] = "BasicCrit%"

    return short_names

SHORT_NAME_MAP = build_short_name_map()

# === [1] DEFAULT_VALUES using Constants ===
DEFAULT_VALUES = {
    # Core stats
    P_ATK: 10_000_000,
    P_Strength: 1.15,
    P_ATK_pct: 3000,
    P_Global_ATK_pct: 250,

    # Crit
    Crit_Chance_pct: 100,
    Skill_Crit_Chance_pct: 100,
    Weapon_Crit_Chance_pct: 100,
    Basic_Crit_Chance_pct: 100,
    Crit_DMG_pct: 500,

    # Skill Counts
    Num_Basic_Attacks: 1,
    Num_Combos: 4,
    Num_Rage_Strikes: 1,

    # Damage Modifiers
    Skill_DMG_pct: 100,

    # Final
    Final_DMG_pct: 0,

    # DoT Stack Settings
    Max_Poison_Stacks: 5,
    Max_Burn_Stacks: 5,

    # Environment
    Rage_ATK_coef: 2.6,
    ENEMY_HP: 3_500_000_000,
    MAX_HP: 3_500_000_000,
}

# All remaining keys default to 0
for key in ALL_KEYS:
    if key not in DEFAULT_VALUES:
        DEFAULT_VALUES[key] = 0

# === [2] BASE_CONFIG constructed from defaults ===
BASE_CONFIG = dict(DEFAULT_VALUES)

# === [3] Utility Functions ===
def generate_scenario_name(base_scenario: dict, compare_scenario: dict) -> str:
    """
    Generate a short scenario name showing what config values changed.
    """
    diffs = []
    for key, val in compare_scenario.items():
        if key == "name":
            continue
        base_val = base_scenario.get(key, None)
        if val != base_val:
            short = SHORT_NAME_MAP.get(key, key)
            val_str = f"{val:.2f}" if isinstance(val, float) and abs(val) < 1 else f"{val:.0f}"
            diffs.append(f"{short}={val_str}")
    return "Δ: " + ", ".join(diffs) if diffs else "Same"

def apply_scenario_config(base_config: dict, scenario_overrides: dict) -> dict:
    cfg = copy.deepcopy(base_config)
    overrides = {k: v for k, v in scenario_overrides.items() if k != "name"}
    cfg.update(overrides)
    return cfg