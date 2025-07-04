# simulation/adventurers.py

"""
Contains the adventurer-specific logic, including passive abilities and
unique skill damage calculations. This is where the simulation comes to life
by applying adventurer-specific rules on top of the core engine.
"""

import copy
import pandas as pd

# Core engine and configuration imports
from .engine import (
    calculate_final_atk, compute_all_damage, compute_damage_breakdown,
    DamageBreakdown, DAMAGE_SKILLS, compute_damage, get_expected_crit_multiplier
)
from config.constants import *
from config.scenarios import BASE_CONFIG, apply_scenario_config

# === [1] Passive Injection per Adventurer ===
def apply_adventurer_passives(config: dict, level: int, adventurer: str) -> dict:
    """Applies passive buffs to a config based on adventurer and level."""
    cfg = copy.deepcopy(config)

    if adventurer == "Gagarin":
        cfg[P_Strength] = 1.20
        if level >= 10:
            cfg[Global_Skill_DMG_pct] += 30
            cfg[Global_Dagger_DMG_pct] += 30
    elif adventurer == "Leonardo":
        cfg[P_Strength] = 1.10
        if level >= 5:
            cfg[Ninjutsu_DMG_pct] += 100
            cfg[Fire_DMG_pct] += 100
            cfg[Lightning_DMG_pct] += 100
            cfg[Physical_DMG_pct] += 100
        if level >= 10:
            cfg[Global_Fire_DMG_pct] += 60
            cfg[Global_Lightning_DMG_pct] += 60
            cfg[Global_Physical_DMG_pct] += 60
    elif adventurer == "DragonGirl":
        cfg[P_Strength] = 1.15
        if level >= 4: cfg[Global_Dragon_Flame_DMG_pct] += 30
        if level >= 7: cfg[Global_Dragon_Flame_DMG_pct] += 30
        if level >= 5: cfg[Global_Dragon_Flame_DMG_pct] += 100
        if level >= 8: cfg[Final_DMG_pct] += 30
    return cfg

# === [2] Adventurer-Specific Damage Functions ===
def gagarin_damage(level: int, config: dict, target_hp: float = 3_500_000_000_000):
    cfg = apply_adventurer_passives(config, level, "Gagarin")

    final_atk = calculate_final_atk(cfg, strength=cfg[P_Strength])
    shared_output = compute_all_damage(cfg, strength=cfg[P_Strength])
    shared_damage = shared_output["total_damage"]
    shared_breakdowns = shared_output["breakdowns"]

    num_daggers = cfg[Num_Daggers]
    missile_chance = 0.65 if level >= 5 else 0.50
    missile_coef = 1.00 if level >= 2 else 0.80
    bonus_dagger_coef = cfg[Bonus_Dagger_Coef]

    total_dagger_hits = (1 - missile_chance) * num_daggers
    total_missile_hits = missile_chance * num_daggers
    base_dagger_coef = 0.45
    base_missile_coef = missile_coef

    def calc_damage(hits, coef, skill):
        return compute_damage(
            skill=skill,
            config=cfg,
            final_atk=final_atk,
            base_coef=(coef + bonus_dagger_coef),
        ) * hits

    dagger_dmg = calc_damage(total_dagger_hits, base_dagger_coef, "dagger")
    missile_dmg = calc_damage(total_missile_hits, base_missile_coef, "dagger")

    # === Custom breakdown overrides for dagger and missile split ===
    if "dagger" in shared_breakdowns:
        original = shared_breakdowns["dagger"]
        
        # Split damage proportionally for daggers
        shared_breakdowns["dagger"] = DamageBreakdown(
            skill="dagger",
            count=int(total_dagger_hits),
            base_coef=base_dagger_coef,
            bonus_coef=bonus_dagger_coef,
            total_coef=base_dagger_coef + bonus_dagger_coef,
            final_atk=final_atk,
            crit_multiplier=original.crit_multiplier,
            local_multiplier=original.local_multiplier,
            global_multiplier=original.global_multiplier,
            final_multiplier=original.final_multiplier,
        )

        # Create a new breakdown entry for missiles
        shared_breakdowns["missiles"] = DamageBreakdown(
            skill="missiles",
            count=int(total_missile_hits),
            base_coef=base_missile_coef,
            bonus_coef=bonus_dagger_coef,
            total_coef=base_missile_coef + bonus_dagger_coef,
            final_atk=final_atk,
            crit_multiplier=original.crit_multiplier,
            local_multiplier=original.local_multiplier,
            global_multiplier=original.global_multiplier,
            final_multiplier=original.final_multiplier,
        )


    # Bomb damage logic
    if level < 4:
        bomb = 0
    elif level >= 7:
        bomb = compute_damage("dagger", cfg, final_atk, base_coef=(18 + bonus_dagger_coef)) + min(final_atk * 100, target_hp * 0.10)
    else:
        bomb = compute_damage("dagger", cfg, final_atk, base_coef=(9 + bonus_dagger_coef))

    output = {
        "dagger": dagger_dmg,
        "missiles": missile_dmg,
        "bomb": bomb,
        "rage": shared_damage.get("rage", 0),
        "breakdowns": shared_breakdowns
    }

    # Add remaining skill damage values from shared total_damage (e.g., light_spear, basic_attack, combo_attack, etc.)
    overridden_keys = {"dagger", "missiles", "bomb", "rage", "breakdowns"}
    for k, v in shared_damage.items():
        if k not in overridden_keys and k.lower() != "total":
            output[k] = v

    # Ensure all known skills are included (with 0 if missing)
    for key in DAMAGE_SKILLS:
        if key not in output:
            output[key] = 0.0

    output["level"] = level

    # Final aggregation
    non_damage_keys = {"level", "scenario", "source", "breakdowns", "total_gagarin"}
    output["total_gagarin"] = sum(
        v for k, v in output.items()
        if isinstance(v, (int, float)) and k not in non_damage_keys
    )

    return output

def run_gagarin_scenario(scenario_dict: dict, name: str):
    skill_rows = []
    round_rows = []
    debug_rows = []

    levels = [0, 2, 4, 5, 7, 10]
    rounds = 10

    for lvl in levels:
        base_cfg = apply_scenario_config(BASE_CONFIG, scenario_dict)

        dmg = gagarin_damage(lvl, base_cfg, target_hp=base_cfg.get(ENEMY_HP, 3_500_000_000_000))
        dmg["scenario"] = name
        dmg["source"] = "gagarin"
        skill_rows.append(dmg)

        cfg_with_passives = apply_adventurer_passives(base_cfg, lvl, "Gagarin")
        debug_rows.append({
            "level": lvl,
            P_Strength: cfg_with_passives.get(P_Strength, 0),
            Global_Skill_DMG_pct: cfg_with_passives.get(Global_Skill_DMG_pct, 0),
            Global_Dagger_DMG_pct: cfg_with_passives.get(Global_Dagger_DMG_pct, 0),
            Bonus_Dagger_Coef: cfg_with_passives.get(Bonus_Dagger_Coef, 0),
            Num_Daggers: cfg_with_passives.get(Num_Daggers, 0),
            Rage_ATK_coef: cfg_with_passives.get(Rage_ATK_coef, 0),
            Global_DMG_pct: cfg_with_passives.get(Global_DMG_pct, 0),
            Dagger_DMG_pct: cfg_with_passives.get(Dagger_DMG_pct, 0),
            Num_Light_Spears: cfg_with_passives.get(Num_Light_Spears, 0),
        })

        # Only sum relevant keys
        non_damage_keys = {"level", "scenario", "source", "total_gagarin", "breakdowns"}
        cumulative_keys = [k for k in dmg if isinstance(dmg[k], (int, float)) and k not in non_damage_keys and k != "bomb"]

        running_total = 0
        for rnd in range(1, rounds + 1):
            per_round = sum(dmg[k] for k in cumulative_keys)

            # Add bomb damage only on specific rounds
            if rnd >= 3 and rnd % 2 == 1:
                per_round += dmg.get("bomb", 0)

            running_total += per_round
            round_rows.append({
                "round": rnd,
                "level": lvl,
                "scenario": name,
                "source": "gagarin",
                "total_damage": running_total
            })

    return pd.DataFrame(skill_rows), pd.DataFrame(round_rows), pd.DataFrame(debug_rows)

def leo_damage(level: int, config: dict, target_hp: float = 3_500_000_000_000):
    cfg = apply_adventurer_passives(config, level, adventurer="Leonardo")
    strength = cfg.get(P_Strength, 1.10)
    final_atk = calculate_final_atk(cfg, strength)

    def sbs_damage():
        # === Fixed 3-hit sequence ===
        base_hits = [0.3, 0.7, 1.0]
        base_total_coef = sum(base_hits)  # 2.0
        base_damage = sum([
            compute_damage("basic_attack", cfg, final_atk, base_coef=coef)
            for coef in base_hits
        ])

        # === Fixed ninjutsu cast ===
        fixed_ninjutsu = compute_damage("ninjutsu_skill", cfg, final_atk, base_coef=1.0)
        bonus_damage = fixed_ninjutsu
        bonus_coef = 1.0

        # === Conditional extra ninjutsu ===
        extra_damage = 0.0
        extra_coef = 0.0
        if level >= 2:
            ninjutsu_chance = 1 - (1 - 0.7) ** 3
            extra_damage = ninjutsu_chance * compute_damage("ninjutsu_skill", cfg, final_atk, base_coef=1.0)
            extra_coef = ninjutsu_chance * 1.0

        # === Combine totals ===
        total_coef = base_total_coef + bonus_coef + extra_coef
        total_damage = base_damage + bonus_damage + extra_damage
        effective_count = cfg.get(Num_Basic_Attacks, 1) * cfg.get(Num_Combos, 1)

        return total_damage * effective_count, total_coef, effective_count

    def hsd_damage():
        if level < 4:
            return 0
        coef = 4 if level >= 7 else 2
        base = 5 * compute_damage("ninjutsu_skill", cfg, final_atk, base_coef=coef)
        if level >= 7:
            hp_val = 0.02 * target_hp
            hp_cap = 20 * final_atk
            base += 5 * min(hp_val, hp_cap)
        return base

    def hsd_cd():
        return 2 if level >= 7 else 3

    def wts_damage():
        if level < 8:
            return 0
        coef = 5 if level >= 10 else 3
        return 3 * compute_damage("ninjutsu_skill", cfg, final_atk, base_coef=coef)

    def rage_damage():
        if level >= 8:
            return 0
        return compute_damage("rage", cfg, final_atk, base_coef=cfg[Rage_ATK_coef])

    # === Compute modular skills ===
    sbs_total, sbs_coef, sbs_count = sbs_damage()
    hsd = hsd_damage()
    wts = wts_damage() * cfg.get(Num_Rage_Strikes, 1)
    rage_atk = rage_damage() * cfg.get(Num_Rage_Strikes, 1)
    cooldown = hsd_cd()

    # === Shared breakdowns ===
    shared_output = compute_all_damage(cfg, strength)
    shared_damage = shared_output["total_damage"]
    shared_breakdowns = shared_output["breakdowns"]

    for key in ["basic_attack", "combo_attack"]:
        shared_breakdowns.pop(key, None)

    def inject_breakdown(skill, total_damage, count, coef):
        shared_breakdowns[skill] = DamageBreakdown(
            skill=skill,
            count=count,
            base_coef=coef,
            bonus_coef=0.0,
            total_coef=coef,
            final_atk=final_atk,
            crit_multiplier=get_expected_crit_multiplier(cfg, skill),
            local_multiplier=1.0,
            global_multiplier=1.0,
            final_multiplier=1.0,
            _total_damage=total_damage  # <-- explicitly set this
        )


    inject_breakdown("sbs", sbs_total, count=sbs_count, coef=sbs_coef)

    if level >= 4:
        inject_breakdown("hsd", hsd, count=1, coef=10.0)
    if level >= 8:
        inject_breakdown("wts", wts, count=cfg.get(Num_Rage_Strikes, 1), coef=3.0)
    else:
        inject_breakdown("rage", rage_atk, count=cfg.get(Num_Rage_Strikes, 1), coef=cfg[Rage_ATK_coef])

    output = {
        "sbs": sbs_total,
        "hsd": hsd,
        "wts": wts,
        "rage": rage_atk,
        "basic_attack": 0.0,
        "combo_attack": 0.0,
        "cooldown": cooldown,
        "breakdowns": shared_breakdowns,
    }

    overridden_keys = {"sbs", "hsd", "wts", "rage", "basic_attack", "combo_attack", "cooldown", "breakdowns"}
    for k, v in shared_damage.items():
        if k not in overridden_keys and k.lower() != "total":
            output[k] = v

    for skill_key in DAMAGE_SKILLS:
        if skill_key not in output:
            output[skill_key] = 0.0

    output["total_leonardo"] = sum(
        v for k, v in output.items()
        if isinstance(v, (int, float)) and k not in {"level", "scenario", "source", "breakdowns", "total_leonardo", "cooldown"}
    )

    return output




def run_leo_scenario(scenario_dict: dict, name: str):
    levels = [0, 2, 4, 5, 7, 8, 10]

    skill_rows = []
    round_rows = []
    debug_rows = []

    for lvl in levels:
        base_cfg = apply_scenario_config(BASE_CONFIG, scenario_dict)
        cfg_with_passives = apply_adventurer_passives(base_cfg, lvl, "Leonardo")

        debug_rows.append({
            "level": lvl,
            P_Strength: cfg_with_passives.get(P_Strength, 0),
            Ninjutsu_DMG_pct: cfg_with_passives.get(Ninjutsu_DMG_pct, 0),
            Rage_ATK_coef: cfg_with_passives.get(Rage_ATK_coef, 0),
            Global_DMG_pct: cfg_with_passives.get(Global_DMG_pct, 0),
            Global_Skill_DMG_pct: cfg_with_passives.get(Global_Skill_DMG_pct, 0),
            "Final_ATK": calculate_final_atk(cfg_with_passives, cfg_with_passives.get(P_Strength, 1.10)),
        })

        dmg = leo_damage(lvl, base_cfg, target_hp=base_cfg.get(ENEMY_HP, 3_500_000_000_000))
        skill_rows.append({
            "source": "leonardo",
            "scenario": name,
            "level": lvl,
            **{k: v for k, v in dmg.items() if k != "cooldown"}
        })

        # === Round-by-round damage accounting ===
        total = 0
        for rnd in range(1, 11):
            round_dmg = (
                dmg["sbs"] * base_cfg.get(Num_Combos, 1)
                + dmg["wts"]
                + dmg["rage"]
            )
            if rnd % dmg["cooldown"] == 0:
                round_dmg += dmg["hsd"]

            total += round_dmg
            round_rows.append({
                "source": "leonardo",
                "scenario": name,
                "level": lvl,
                "round": rnd,
                "total_damage": total
            })

    return pd.DataFrame(skill_rows), pd.DataFrame(round_rows), pd.DataFrame(debug_rows)

def dg_damage(level: int, config: dict, stacks: bool = True, target_hp=3_500_000_000_000):
    cfg = apply_adventurer_passives(config, level, adventurer="DragonGirl")
    strength = cfg.get(P_Strength, 1.15)
    final_atk = calculate_final_atk(cfg, strength)

    def dragon_breath():
        coef = 0.9 if level < 2 else 1.8
        return compute_damage("dragon_flame_skill", cfg, final_atk, base_coef=coef), coef

    def catastrophic_breath():
        if level < 4:
            return 0, 0
        coef = 12 if level >= 7 else 6
        return compute_damage("dragon_flame_skill", cfg, final_atk, base_coef=coef), coef

    def dragons_wrath():
        if level < 8:
            return 0
        cap = 100 * final_atk
        my_hp = cfg.get(MAX_HP, 3_500_000_000)
        return min(0.10 * my_hp, cap) + min(0.10 * target_hp, cap)

    def basic_attack_hit():
        mods = ["Basic_ATK_DMG_pct"]
        if level >= 5:
            mods.append("Global_Dragon_Flame_DMG_pct")
        return compute_damage("basic_attack", cfg, final_atk, base_coef=1.0, extra_mods=mods)

    def combo_attack_hit():
        mods = ["Basic_ATK_DMG_pct", "Combo_DMG_pct"]
        if level >= 5:
            mods.append("Global_Dragon_Flame_DMG_pct")
        return compute_damage("combo_attack", cfg, final_atk, base_coef=1.0, extra_mods=mods)

    def rage_attack_hit():
        mods = ["Rage_DMG_pct", "Skill_DMG_pct"]
        if level >= 5:
            mods.append("Global_Dragon_Flame_DMG_pct")
        return compute_damage("rage", cfg, final_atk, base_coef=cfg.get(Rage_ATK_coef, 2.0), extra_mods=mods)

    # === Calculate Core Damages ===
    basic_attack = cfg[Num_Basic_Attacks] * basic_attack_hit()
    combo_attack = cfg[Num_Combos] * combo_attack_hit()
    rage = cfg[Num_Rage_Strikes] * rage_attack_hit()

    dragon_breath_hit, dragon_breath_coef = dragon_breath()
    basic_breath = dragon_breath_hit * (cfg[Num_Basic_Attacks] + cfg[Num_Combos])
    rage_breath = dragon_breath_hit * cfg[Num_Rage_Strikes]
    breath = basic_breath + rage_breath

    catastrophic, catastrophic_coef = catastrophic_breath()
    dragon_wrath = dragons_wrath()

    # === Shared Modular Breakdown ===
    shared_output = compute_all_damage(cfg, strength)
    shared_damage = shared_output["total_damage"]
    shared_breakdowns = shared_output["breakdowns"]

    # Remove overridden entries
    for key in ["basic_attack", "combo_attack", "rage"]:
        if key in shared_breakdowns:
            del shared_breakdowns[key]

    # Inject flame skill breakdowns
    def inject_breakdown(skill, dmg, count, coef):
        shared_breakdowns[skill] = DamageBreakdown(
            skill=skill,
            count=count,
            base_coef=coef,
            bonus_coef=0.0,
            total_coef=coef,
            final_atk=final_atk,
            crit_multiplier=get_expected_crit_multiplier(cfg, skill),
            local_multiplier=1.0,
            global_multiplier=1.0,
            final_multiplier=1.0,
        )

    inject_breakdown("breath", breath, count=(cfg[Num_Basic_Attacks] + cfg[Num_Combos] + cfg[Num_Rage_Strikes]), coef=dragon_breath_coef)

    if level >= 4:
        inject_breakdown("catastrophic", catastrophic, count=1, coef=catastrophic_coef)

    if level >= 8:
        # Estimate a placeholder count of 1 and average coef (for display only)
        inject_breakdown("dragon_wrath", dragon_wrath, count=1, coef=5.0)

    output = {
        "basic_attack": basic_attack,
        "combo_attack": combo_attack,
        "breath": breath,
        "rage": rage,
        "catastrophic": catastrophic,
        "dragon_wrath": dragon_wrath,
        "breakdowns": shared_breakdowns
    }

    # Add shared skills not already overridden
    overridden_keys = set(output.keys()) | {"total_dragon_girl"}
    for k, v in shared_damage.items():
        if k not in overridden_keys and k.lower() != "total":
            output[k] = v

    # Ensure all known skills show up
    for skill_key in DAMAGE_SKILLS:
        if skill_key not in output:
            output[skill_key] = 0.0

    # Compute total
    non_damage_keys = {"breakdowns", "total_dragon_girl"}
    output["total_dragon_girl"] = sum(
        v for k, v in output.items()
        if isinstance(v, (int, float)) and k not in non_damage_keys
    )

    return output



def run_dragon_girl_scenario(config: dict, scenario_label: str, stacks: bool = True):
    levels = [0, 2, 4, 5, 7, 8, 10]
    rounds = list(range(1, 16))
    skill_rows = []
    round_rows = []
    debug_rows = []

    for lvl in levels:
        cfg = apply_adventurer_passives(config, lvl, "DragonGirl")
        dmg = dg_damage(lvl, cfg, stacks)

        final_atk = calculate_final_atk(cfg, cfg.get(P_Strength, 1.20))
        debug_rows.append({
            "level": lvl,
            P_Strength: cfg.get(P_Strength, 0),
            Skill_DMG_pct: cfg.get(Skill_DMG_pct, 0),
            Global_Skill_DMG_pct: cfg.get(Global_Skill_DMG_pct, 0),
            Dragon_Flame_DMG_pct: cfg.get(Dragon_Flame_DMG_pct, 0),
            Global_Dragon_Flame_DMG_pct: cfg.get("Global_Dragon_Flame_DMG_pct", 0),
            Global_Dagger_DMG_pct: cfg.get(Global_Dagger_DMG_pct, 0),
            Rage_ATK_coef: cfg.get(Rage_ATK_coef, 0),
            Global_DMG_pct: cfg.get(Global_DMG_pct, 0),
            "Final_ATK": final_atk,
        })

        skill_rows.append({
            "source": "dragon_girl",
            "scenario": scenario_label,
            "level": lvl,
            **dmg  # includes breakdowns
        })

        total = 0
        for rnd in rounds:
            round_dmg = (
                dmg["basic_attack"]
                + dmg["combo_attack"]
                + dmg["breath"]
                + dmg["rage"]
            )
            if lvl >= 4 and rnd % 2 == 1:
                round_dmg += dmg["catastrophic"]
            if lvl >= 8:
                round_dmg += dmg["dragon_wrath"]

            total += round_dmg
            round_rows.append({
                "source": "dragon_girl",
                "scenario": scenario_label,
                "level": lvl,
                "round": rnd,
                "total_damage": total
            })

    return pd.DataFrame(skill_rows), pd.DataFrame(round_rows), pd.DataFrame(debug_rows)
