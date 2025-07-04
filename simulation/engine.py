# simulation/engine.py

"""
Core simulation engine for damage calculation.
This module defines the skills, the damage breakdown structure, and the
primary functions for computing damage based on a given configuration.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict

from config.constants import *

# === [1] Skill Definitions ===
# This dictionary maps a skill identifier to its metadata, including damage
# coefficients, relevant modifiers, and usage counters.
def make_skill(coef=None, bonus_coef_key=None, local_mods=None, global_mods=None, count_key=None, **kwargs):
    return {
        "coef": coef,
        "bonus_coef_key": bonus_coef_key,
        "local_mods": local_mods or [],
        "global_mods": global_mods or [],
        "count_key": count_key,
        **kwargs,
    }

DAMAGE_SKILLS = {
    "basic_attack": make_skill(coef=1.0, bonus_coef_key=Bonus_Basic_Coef, local_mods=[Basic_ATK_DMG_pct, Damage_pct], global_mods=[Global_Basic_ATK_DMG_pct, Global_DMG_pct], count_key=Num_Basic_Attacks),
    "combo_attack": make_skill(coef=1.0, bonus_coef_key=Bonus_Combo_Coef, local_mods=[Basic_ATK_DMG_pct, Combo_DMG_pct, Damage_pct], global_mods=[Global_Basic_ATK_DMG_pct, Global_Combo_DMG_pct, Global_DMG_pct], count_key=Num_Combos),
    "dagger": make_skill(coef=0.45, bonus_coef_key=Bonus_Dagger_Coef, local_mods=[Dagger_DMG_pct, Physical_DMG_pct, Skill_DMG_pct, Damage_pct], global_mods=[Global_Dagger_DMG_pct, Global_Physical_DMG_pct, Global_Skill_DMG_pct, Global_DMG_pct], count_key=Num_Daggers),
    "bolt": make_skill(coef=0.3, bonus_coef_key=[Bonus_Bolt_Coef, Bonus_Lightning_Coef], local_mods=[Bolt_DMG_pct, Lightning_DMG_pct, Skill_DMG_pct, Damage_pct], global_mods=[Global_Bolt_DMG_pct, Global_Lightning_DMG_pct, Global_Skill_DMG_pct, Global_DMG_pct], count_key=Num_Bolts),
    "death_bolt": make_skill(coef=0.9, bonus_coef_key=[Bonus_Bolt_Coef, Bonus_Lightning_Coef], local_mods=[Bolt_DMG_pct, Lightning_DMG_pct, Skill_DMG_pct, Damage_pct], global_mods=[Global_Bolt_DMG_pct, Global_Lightning_DMG_pct, Global_Skill_DMG_pct, Global_DMG_pct], count_key=Num_Death_Bolts),
    "chi": make_skill(coef=0.7, bonus_coef_key=Bonus_Chi_Coef, local_mods=[Chi_DMG_pct, Physical_DMG_pct, Skill_DMG_pct, Damage_pct], global_mods=[Global_Chi_DMG_pct, Global_Physical_DMG_pct, Global_Skill_DMG_pct, Global_DMG_pct], count_key=Num_Chi_Hits),
    "rage": make_skill(coef=2.0, bonus_coef_key=Bonus_Rage_Coef, local_mods=[Rage_DMG_pct, Skill_DMG_pct, Damage_pct], global_mods=[Global_Rage_DMG_pct, Global_Skill_DMG_pct, Global_DMG_pct], count_key=Num_Rage_Strikes),
    "icy_spike": make_skill(coef=0.3, bonus_coef_key=Bonus_Icy_Spike_Coef, local_mods=[Ice_DMG_pct, Skill_DMG_pct, Damage_pct], global_mods=[Global_Ice_DMG_pct, Global_Skill_DMG_pct, Global_DMG_pct], count_key=Num_Icy_Spikes),
    "poison_dot": make_skill(coef=0.2, bonus_coef_key=Bonus_Poison_Coef, local_mods=[Poison_DMG_pct, DoT_DMG_pct, Damage_pct], global_mods=[Global_Poison_DMG_pct, Global_DoT_DMG_pct, Global_DMG_pct], count_key=Num_Poisons, stack_param=Max_Poison_Stacks),
    "burn_dot": make_skill(coef=0.3, bonus_coef_key=Bonus_Burn_Coef, local_mods=[Burn_DMG_pct, Fire_DMG_pct, DoT_DMG_pct, Damage_pct], global_mods=[Global_Burn_DMG_pct, Global_Fire_DMG_pct, Global_DoT_DMG_pct, Global_DMG_pct], count_key=Num_Burns, stack_param=Max_Burn_Stacks),
    "light_spear": make_skill(coef=0.3, bonus_coef_key=Bonus_Light_Spear_Coef, local_mods=[Light_Spear_DMG_pct, Physical_DMG_pct, Skill_DMG_pct, Damage_pct], global_mods=[Global_Light_Spear_DMG_pct, Global_Physical_DMG_pct, Global_Skill_DMG_pct, Global_DMG_pct], count_key=Num_Light_Spears),
    "counter": make_skill(coef=1.0, bonus_coef_key=Bonus_Counter_Coef, local_mods=[Counter_DMG_pct, Damage_pct], global_mods=[Global_Counter_DMG_pct, Global_DMG_pct], count_key=Num_Counter_Attacks),
    "ninjutsu_skill": make_skill(coef=1.0, local_mods=[Skill_DMG_pct, Ninjutsu_DMG_pct, Damage_pct], global_mods=[Global_Skill_DMG_pct, Global_Ninjutsu_DMG_pct, Global_DMG_pct], count_key=Num_Ninjutsu_Skills),
    "dragon_flame_skill": make_skill(coef=None, local_mods=[Skill_DMG_pct, Dragon_Flame_DMG_pct, Damage_pct], global_mods=[Global_Skill_DMG_pct, Global_DMG_pct, Global_Dragon_Flame_DMG_pct], final_bonus_type=Final_DMG_pct, count_key=Num_Dragon_Flame_Skills)
}


# === [2] Damage Breakdown Dataclass ===

@dataclass
class DamageBreakdown:
    skill: str
    count: int
    base_coef: float
    bonus_coef: float
    total_coef: float

    final_atk: float
    local_multiplier: float
    global_multiplier: float
    final_multiplier: float
    crit_multiplier: float  # NEW

    _total_damage: Optional[float] = None

    def __post_init__(self):
        if self._total_damage is not None:
            self.total_damage = self._total_damage
        else:
            per_hit = (
                self.final_atk
                * self.total_coef
                * self.local_multiplier
                * self.global_multiplier
                * self.final_multiplier
                * self.crit_multiplier
            )
            self.total_damage = per_hit * self.count

    def as_dict(self):
        return {
            "Skill": self.skill,
            "Count": self.count,
            "BaseCoef": self.base_coef,
            "BonusCoef": self.bonus_coef,
            "TotalCoef": self.total_coef,
            "FinalATK": self.final_atk,
            "LocalMult": self.local_multiplier,
            "GlobalMult": self.global_multiplier,
            "FinalMult": self.final_multiplier,
            "CritMult": self.crit_multiplier,
            "TotalDamage": self.total_damage,
        }

# === [3] Core Calculation Functions ===
def calculate_final_atk(config: dict, strength: float = 1.15) -> float:
    """Calculates the final attack power after all multipliers."""
    return (
        config[P_ATK] * strength *
        (1 + config[P_ATK_pct] / 100) *
        (1 + config[P_Global_ATK_pct] / 100) *
        (1 + config[Final_DMG_pct] / 100)
    )

def get_expected_crit_multiplier(config: dict, skill_type: str) -> float:
    """Calculates the expected critical hit multiplier for a given skill type."""
    crit_chance = config.get(Crit_Chance_pct, 0)

    if skill_type == "basic_attack":
        crit_chance += config.get(Basic_Crit_Chance_pct, 0) + config.get(Weapon_Crit_Chance_pct, 0)
    elif skill_type in {"combo_attack", "rage", "counter"}:
        crit_chance += config.get(Weapon_Crit_Chance_pct, 0)
    elif skill_type in {"burn_dot", "poison_dot"}:
        return 1.0
    else:
        crit_chance += config.get(Skill_Crit_Chance_pct, 0)

    crit_chance = min(100, crit_chance)
    crit_dmg = config.get(Crit_DMG_pct, 0)
    return (1 - crit_chance / 100) + (crit_chance / 100) * (1 + crit_dmg / 100)


def compute_damage_breakdown(skill: str, config: dict, final_atk: float, base_coef: float = None) -> Optional[DamageBreakdown]:
    """Computes a detailed damage breakdown for a single skill type."""
    meta = DAMAGE_SKILLS.get(skill)
    if not meta:
        return None

    count_key = meta.get("count_key") or meta.get("stack_param")
    count = config.get(count_key, 0)
    if count == 0:
        return None

    if base_coef is None:
        base_coef = meta.get("coef", 1.0)

    bonus_key = meta.get("bonus_coef_key")
    if isinstance(bonus_key, list):
        bonus_coef = sum(config.get(k, 0) for k in bonus_key)
    else:
        bonus_coef = config.get(bonus_key, 0) if bonus_key else 0
    total_coef = base_coef + bonus_coef

    local_multiplier = 1 + sum(config.get(mod, 0) for mod in meta.get("local_mods", [])) / 100
    global_multiplier = 1 + sum(config.get(mod, 0) for mod in meta.get("global_mods", [])) / 100
    final_multiplier = 1 + config.get(meta.get("final_bonus_type", ""), 0) / 100
    crit_multiplier = get_expected_crit_multiplier(config, skill)

    return DamageBreakdown(
        skill=skill,
        count=count,
        base_coef=base_coef,
        bonus_coef=bonus_coef,
        total_coef=total_coef,
        final_atk=final_atk,
        local_multiplier=local_multiplier,
        global_multiplier=global_multiplier,
        final_multiplier=final_multiplier,
        crit_multiplier=crit_multiplier,
    )

def compute_damage(skill: str, config: dict, final_atk: float, base_coef: float = 1.0, extra_mods: list[str] = None) -> float:
    meta = DAMAGE_SKILLS.get(skill, {})
    local_mods = meta.get("local_mods", [])
    global_mods = meta.get("global_mods", [])

    if extra_mods:
        local_mods += [m for m in extra_mods if m not in local_mods]
        global_mods += [f"Global_{m}" for m in extra_mods if f"Global_{m}" not in global_mods]

    bonus_key = meta.get("bonus_coef_key")
    if isinstance(bonus_key, list):
        bonus_coef = sum(config.get(k, 0) for k in bonus_key)
    else:
        bonus_coef = config.get(bonus_key, 0) if bonus_key else 0

    total_coef = base_coef + bonus_coef
    local_multiplier = 1 + sum(config.get(mod, 0) for mod in local_mods) / 100
    global_multiplier = 1 + sum(config.get(mod, 0) for mod in global_mods) / 100
    final_multiplier = 1 + config.get(meta.get("final_bonus_type", ""), 0) / 100
    crit_multiplier = get_expected_crit_multiplier(config, skill)

    return (
        final_atk
        * total_coef
        * local_multiplier
        * global_multiplier
        * final_multiplier
        * crit_multiplier
    )

def compute_all_damage(config: dict, strength: float = 1.15) -> dict:
    """
    Computes total damage and breakdowns for all skills defined in DAMAGE_SKILLS.
    """
    final_atk = calculate_final_atk(config, strength)
    results = {}
    breakdowns = {}

    for skill_type, meta in DAMAGE_SKILLS.items():
        count_key = meta.get("count_key") or meta.get("stack_param")
        if not count_key:
            raw = skill_type.replace("_dot", "")
            camel = "".join(w.capitalize() for w in raw.split("_"))
            count_key = f"Num_{camel}s"

        count = config.get(count_key, 0)
        if count == 0:
            continue

        base_coef = config.get(Rage_ATK_coef) if skill_type == "rage" else None
        b = compute_damage_breakdown(skill_type, config, final_atk, base_coef)
        if b:
            results[skill_type] = b.total_damage
            breakdowns[skill_type] = b

    return {
        "total_damage": results,
        "breakdowns": breakdowns
    }

def to_bonus_key(skill: str) -> str:
    """Utility to guess a bonus coefficient key from a skill name."""
    parts = skill.replace("_dot", "").split("_")
    return "Bonus_" + "".join(p.capitalize() for p in parts) + "_Coef"
