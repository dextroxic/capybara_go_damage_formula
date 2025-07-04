# config/constants.py

"""
This module contains all the named constants (keys) used for configuring
player stats, damage modifiers, and simulation parameters.
"""

# Core stats
P_ATK = "P_ATK"
P_Strength = "P_Strength"
P_ATK_pct = "P_ATK_pct"
P_Global_ATK_pct = "P_Global_ATK_pct"

# Crit
Crit_Chance_pct = "Crit_Chance_pct"
Skill_Crit_Chance_pct = "Skill_Crit_Chance_pct"
Weapon_Crit_Chance_pct = "Weapon_Crit_Chance_pct"
Basic_Crit_Chance_pct = "Basic_Crit_Chance_pct"
Crit_DMG_pct = "Crit_DMG_pct"

# Local modifiers
Skill_DMG_pct = "Skill_DMG_pct"
Physical_DMG_pct = "Physical_DMG_pct"
Dagger_DMG_pct = "Dagger_DMG_pct"
Bolt_DMG_pct = "Bolt_DMG_pct"
Chi_DMG_pct = "Chi_DMG_pct"
Dragon_Flame_DMG_pct = "Dragon_Flame_DMG_pct"
Fire_DMG_pct = "Fire_DMG_pct"
Ice_DMG_pct = "Ice_DMG_pct"
Lightning_DMG_pct = "Lightning_DMG_pct"
Basic_ATK_DMG_pct = "Basic_ATK_DMG_pct"
Combo_DMG_pct = "Combo_DMG_pct"
Rage_DMG_pct = "Rage_DMG_pct"
Counter_DMG_pct = "Counter_DMG_pct"
Poison_DMG_pct = "Poison_DMG_pct"
Burn_DMG_pct = "Burn_DMG_pct"
Light_Spear_DMG_pct = "Light_Spear_DMG_pct"
DoT_DMG_pct = "DoT_DMG_pct"
Ninjutsu_DMG_pct = "Ninjutsu_DMG_pct"
Damage_pct = "Damage_pct"

# Global modifiers
Global_Skill_DMG_pct = "Global_Skill_DMG_pct"
Global_Physical_DMG_pct = "Global_Physical_DMG_pct"
Global_Dagger_DMG_pct = "Global_Dagger_DMG_pct"
Global_Bolt_DMG_pct = "Global_Bolt_DMG_pct"
Global_Chi_DMG_pct = "Global_Chi_DMG_pct"
Global_Dragon_Flame_DMG_pct = "Global_Dragon_Flame_DMG_pct"
Global_Fire_DMG_pct = "Global_Fire_DMG_pct"
Global_Ice_DMG_pct = "Global_Ice_DMG_pct"
Global_Lightning_DMG_pct = "Global_Lightning_DMG_pct"
Global_Basic_ATK_DMG_pct = "Global_Basic_ATK_DMG_pct"
Global_Combo_DMG_pct = "Global_Combo_DMG_pct"
Global_Rage_DMG_pct = "Global_Rage_DMG_pct"
Global_Counter_DMG_pct = "Global_Counter_DMG_pct"
Global_Poison_DMG_pct = "Global_Poison_DMG_pct"
Global_Burn_DMG_pct = "Global_Burn_DMG_pct"
Global_Light_Spear_DMG_pct = "Global_Light_Spear_DMG_pct"
Global_DoT_DMG_pct = "Global_DoT_DMG_pct"
Global_Ninjutsu_DMG_pct = "Global_Ninjutsu_DMG_pct"
Global_DMG_pct = "Global_DMG_pct"

# Bonus Coef
Bonus_Dagger_Coef = "Bonus_Dagger_Coef"
Bonus_Bolt_Coef = "Bonus_Bolt_Coef"
Bonus_Chi_Coef = "Bonus_Chi_Coef"
Bonus_Rage_Coef = "Bonus_Rage_Coef"
Bonus_Light_Spear_Coef = "Bonus_Light_Spear_Coef"
Bonus_Icy_Spike_Coef = "Bonus_Icy_Spike_Coef"
Bonus_Basic_Coef = "Bonus_Basic_Coef"
Bonus_Combo_Coef = "Bonus_Combo_Coef"
Bonus_Counter_Coef = "Bonus_Counter_Coef"
Bonus_Poison_Coef = "Bonus_Poison_Coef"
Bonus_Burn_Coef = "Bonus_Burn_Coef"
Bonus_Lightning_Coef = "Bonus_Lightning_Coef"
Bonus_Fire_Coef = "Bonus_Fire_Coef"

# Skill usage counts
Num_Combos = "Num_Combos"
Num_Basic_Attacks = "Num_Basic_Attacks"
Num_Daggers = "Num_Daggers"
Num_Rage_Strikes = "Num_Rage_Strikes"
Num_Bolts = "Num_Bolts"
Num_Death_Bolts = "Num_Death_Bolts"
Num_Chi_Hits = "Num_Chi_Hits"
Num_Burns = "Num_Burns"
Num_Poisons = "Num_Poisons"
Num_Light_Spears = "Num_Light_Spears"
Num_Icy_Spikes = "Num_Icy_Spikes"
Num_Counter_Attacks = "Num_Counter_Attacks"
Num_Ninjutsu_Skills = "Num_Ninjutsu_Skills"
Num_Dragon_Flame_Skills = "Num_Dragon_Flame_Skills"

# DoT
Max_Poison_Stacks = "Max_Poison_Stacks"
Max_Burn_Stacks = "Max_Burn_Stacks"

# Final Modifiers
Final_DMG_pct = "Final_DMG_pct"

# Env
Rage_ATK_coef = "Rage_ATK_coef"
ENEMY_HP = "ENEMY_HP"
MAX_HP = "MAX_HP"

# --- Grouped Lists of Keys ---
PLAYER_STAT_KEYS = [P_ATK, P_Strength, P_ATK_pct, P_Global_ATK_pct]
CRIT_KEYS = [Crit_Chance_pct, Skill_Crit_Chance_pct, Weapon_Crit_Chance_pct, Basic_Crit_Chance_pct, Crit_DMG_pct]
LOCAL_MOD_KEYS = [
    Skill_DMG_pct, Physical_DMG_pct, Dagger_DMG_pct, Bolt_DMG_pct, Chi_DMG_pct, Dragon_Flame_DMG_pct,
    Fire_DMG_pct, Ice_DMG_pct, Lightning_DMG_pct, Basic_ATK_DMG_pct, Combo_DMG_pct, Rage_DMG_pct,
    Counter_DMG_pct, Poison_DMG_pct, Burn_DMG_pct, Light_Spear_DMG_pct, DoT_DMG_pct, Damage_pct, Ninjutsu_DMG_pct
]
GLOBAL_MOD_KEYS = [
    Global_Skill_DMG_pct, Global_Physical_DMG_pct, Global_Dagger_DMG_pct, Global_Bolt_DMG_pct, Global_Chi_DMG_pct,
    Global_Dragon_Flame_DMG_pct, Global_Fire_DMG_pct, Global_Ice_DMG_pct, Global_Lightning_DMG_pct,
    Global_Basic_ATK_DMG_pct, Global_Combo_DMG_pct, Global_Rage_DMG_pct, Global_Counter_DMG_pct,
    Global_Poison_DMG_pct, Global_Burn_DMG_pct, Global_Light_Spear_DMG_pct, Global_DoT_DMG_pct,
    Global_Ninjutsu_DMG_pct, Global_DMG_pct
]
BONUS_COEF_KEYS = [
    Bonus_Dagger_Coef, Bonus_Bolt_Coef, Bonus_Chi_Coef, Bonus_Rage_Coef, Bonus_Light_Spear_Coef,
    Bonus_Icy_Spike_Coef, Bonus_Basic_Coef, Bonus_Combo_Coef, Bonus_Counter_Coef, Bonus_Poison_Coef,
    Bonus_Burn_Coef, Bonus_Lightning_Coef, Bonus_Fire_Coef
]
SKILL_COUNT_KEYS = [
    Num_Combos, Num_Basic_Attacks, Num_Daggers, Num_Rage_Strikes, Num_Bolts, Num_Death_Bolts, Num_Chi_Hits,
    Num_Burns, Num_Poisons, Num_Light_Spears, Num_Icy_Spikes, Num_Counter_Attacks, Num_Ninjutsu_Skills,
    Num_Dragon_Flame_Skills
]
DOT_STACK_KEYS = [Max_Poison_Stacks, Max_Burn_Stacks]
ENVIRONMENT_KEYS = [ENEMY_HP, MAX_HP]

ALL_KEYS = (
    PLAYER_STAT_KEYS + CRIT_KEYS + LOCAL_MOD_KEYS + GLOBAL_MOD_KEYS +
    BONUS_COEF_KEYS + SKILL_COUNT_KEYS + DOT_STACK_KEYS + ENVIRONMENT_KEYS +
    [Final_DMG_pct]
)
