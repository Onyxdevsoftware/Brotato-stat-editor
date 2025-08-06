import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import copy
import os

'''
@Author OnyxDev

Description:
A simple Brotato stat editor.
'''

class BrotatoSaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Brotato stat editor - Contact: @Onyxdev on Discord.")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.save_data = None
        self.original_save_data = None
        self.current_file = None
        self.dlc_mode = tk.BooleanVar(value=False)
        self.dlc_mode.trace('w', self.on_dlc_mode_change)
        
        self.setup_style()
        self.setup_ui()
        
    def setup_style(self):
        style = ttk.Style()
        
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Modern.TButton', padding=(10, 5))
        style.configure('Accent.TButton', padding=(8, 4))
        
    def setup_ui(self):
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self.create_header(main_container)
        self.create_main_content(main_container)
        self.create_status_bar(main_container)
        
    def create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="🥔 Brotato stat editor", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        controls_frame = ttk.Frame(header_frame)
        controls_frame.grid(row=0, column=2, sticky="e")
        
        file_frame = ttk.LabelFrame(controls_frame, text="File Operations", padding="5")
        file_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(file_frame, text="📁 Open", command=self.open_file, 
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="💾 Save", command=self.save_file, 
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="📋 Save As", command=self.save_as_file, 
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="↶ Revert back to original save", command=self.revert_save, 
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        settings_frame = ttk.LabelFrame(controls_frame, text="Settings", padding="5")
        settings_frame.pack(side=tk.RIGHT)
        
        ttk.Checkbutton(settings_frame, text="🎮 DLC Mode", 
                       variable=self.dlc_mode).pack()

    def revert_save(self):
        if not self.current_file or not self.original_save_data:
            messagebox.showerror("Error", "No file loaded to revert.")
            return
            
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                json.dump(self.original_save_data, file, indent=None, separators=(',', ':'), ensure_ascii=False)
                self.save_data = json.loads(json.dumps(self.original_save_data))
                self.load_data()
                
            self.status_var.set(f"Successfully reverted save: {self.current_file}")
            messagebox.showinfo("Success", "Save file has been reverted successfully!")
            
        except Exception as e:
            self.status_var.set("Error reverting save file")
            messagebox.showerror("Error", f"Failed to revert save file: {str(e)}")
        
    def create_main_content(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        self.create_overview_tab()
        self.create_character_tab()
        self.create_inventory_tab()
        self.create_stats_tab()
        self.create_special_stats_tab()
        self.create_caps_limits_tab()
        self.create_shop_settings_tab()
        
    def create_status_bar(self, parent):
        self.status_var = tk.StringVar(value="Ready - No file loaded")
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Label(status_frame, textvariable=self.status_var, 
                 relief=tk.SUNKEN, padding="5").pack(fill=tk.X)
        
    def create_overview_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Overview")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        left_frame = ttk.Frame(frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        self.create_run_info_section(left_frame)
        self.create_game_mode_section(left_frame)
        self.create_enemy_scaling_section(right_frame)
        self.create_progress_section(right_frame)
        
    def create_run_info_section(self, parent):
        info_frame = ttk.LabelFrame(parent, text="🎯 Current Run", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)
        
        self.run_vars = {}
        run_fields = [
            ("current_wave", "Wave:", 0, 0),
            ("current_zone", "Zone:", 0, 2), 
            ("current_difficulty", "Difficulty:", 1, 0),
            ("gold", "💰 Gold:", 1, 2),
            ("current_health", "❤️ Health:", 2, 0),
            ("current_level", "⭐ Level:", 2, 2),
            ("current_xp", "✨ XP:", 3, 0),
            ("nb_of_waves", "Total Waves:", 3, 2),
            ("bonus_gold", "💰 Bonus Gold:", 4, 0),
            ("total_bonus_gold", "💰 Total Bonus:", 4, 2)
        ]
        
        for key, label, row, col in run_fields:
            self.run_vars[key] = tk.StringVar()
            ttk.Label(info_frame, text=label, font=('Segoe UI', 9)).grid(
                row=row, column=col, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(info_frame, textvariable=self.run_vars[key], width=12)
            entry.grid(row=row, column=col+1, sticky="ew", padx=(0, 10), pady=3)
            
    def create_game_mode_section(self, parent):
        mode_frame = ttk.LabelFrame(parent, text="🎮 Game Mode", padding="10")
        mode_frame.pack(fill="x", pady=(0, 10))
        
        self.is_endless_var = tk.BooleanVar()
        self.is_coop_var = tk.BooleanVar()
        self.has_run_state_var = tk.BooleanVar()
        
        ttk.Checkbutton(mode_frame, text="♾️ Endless Mode", 
                       variable=self.is_endless_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(mode_frame, text="👥 Co-op Mode", 
                       variable=self.is_coop_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(mode_frame, text="🏃 Has Run State", 
                       variable=self.has_run_state_var).pack(anchor="w", pady=2)
        
    def create_character_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👤 Character")
        
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        char_frame = ttk.LabelFrame(frame, text="👤 Character Selection", padding="10")
        char_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        char_frame.grid_columnconfigure(1, weight=1)
        char_frame.grid_columnconfigure(3, weight=1)
        
        self.current_character_var = tk.StringVar()
        self.current_background_var = tk.StringVar()
        self.selected_weapon_var = tk.StringVar()
        
        ttk.Label(char_frame, text="Current Character:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(char_frame, textvariable=self.current_character_var).grid(row=0, column=1, sticky="ew")
        
        ttk.Label(char_frame, text="Background:").grid(row=0, column=2, sticky="w", padx=(10, 10))
        ttk.Entry(char_frame, textvariable=self.current_background_var).grid(row=0, column=3, sticky="ew")
        
        ttk.Label(char_frame, text="Selected Weapon:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        ttk.Entry(char_frame, textvariable=self.selected_weapon_var).grid(row=1, column=1, sticky="ew", pady=(5, 0))
        
        challenge_frame = ttk.LabelFrame(frame, text="🏆 Challenge Progress", padding="10")
        challenge_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        self.challenge_vars = {}
        challenge_fields = [
            ("chal_recycling_current", "♻️ Recycling Current:"),
            ("retries", "🔄 Retries:"),
            ("loot_aliens_killed_this_run", "👽 Loot Aliens Killed:"),
            ("max_endless_wave_record_beaten", "📊 Endless Record:"),
            ("consumables_picked_up_this_run", "🍎 Consumables Picked:")
        ]
        
        for i, (key, label) in enumerate(challenge_fields):
            self.challenge_vars[key] = tk.StringVar()
            ttk.Label(challenge_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Entry(challenge_frame, textvariable=self.challenge_vars[key], width=15).grid(
                row=i, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        unlocks_frame = ttk.LabelFrame(frame, text="🔓 Quick Stats", padding="10")
        unlocks_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        
        self.quick_stats_vars = {}
        quick_stats = [
            ("enemies_killed", "👹 Enemies Killed:"),
            ("materials_collected", "⛏️ Materials Collected:"),
            ("trees_killed", "🌳 Trees Killed:"),
            ("steps_taken", "👣 Steps Taken:"),
            ("curse_locked_shop_items_pity", "🔒 Curse Pity:")
        ]
        
        for i, (key, label) in enumerate(quick_stats):
            self.quick_stats_vars[key] = tk.StringVar()
            ttk.Label(unlocks_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Entry(unlocks_frame, textvariable=self.quick_stats_vars[key], width=15).grid(
                row=i, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        reroll_frame = ttk.LabelFrame(frame, text="🎲 Reroll Data", padding="10")
        reroll_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        reroll_frame.grid_columnconfigure(1, weight=1)
        reroll_frame.grid_columnconfigure(3, weight=1)
        reroll_frame.grid_columnconfigure(5, weight=1)
        reroll_frame.grid_columnconfigure(7, weight=1)
        
        self.reroll_vars = {}
        for i in range(4):
            self.reroll_vars[f"reroll_count_{i}"] = tk.StringVar()
            self.reroll_vars[f"paid_reroll_count_{i}"] = tk.StringVar()
            self.reroll_vars[f"free_rerolls_{i}"] = tk.StringVar()
            self.reroll_vars[f"initial_free_rerolls_{i}"] = tk.StringVar()
            
            player_label = ttk.Label(reroll_frame, text=f"Player {i+1}:", font=('Segoe UI', 9, 'bold'))
            player_label.grid(row=0, column=i*2, sticky="w", padx=5)
            
            ttk.Label(reroll_frame, text="Rerolls:").grid(row=1, column=i*2, sticky="w", padx=5, pady=2)
            ttk.Entry(reroll_frame, textvariable=self.reroll_vars[f"reroll_count_{i}"], width=8).grid(
                row=1, column=i*2+1, sticky="ew", padx=(0, 10), pady=2)
            
            ttk.Label(reroll_frame, text="Paid:").grid(row=2, column=i*2, sticky="w", padx=5, pady=2)
            ttk.Entry(reroll_frame, textvariable=self.reroll_vars[f"paid_reroll_count_{i}"], width=8).grid(
                row=2, column=i*2+1, sticky="ew", padx=(0, 10), pady=2)
            
            ttk.Label(reroll_frame, text="Free:").grid(row=3, column=i*2, sticky="w", padx=5, pady=2)
            ttk.Entry(reroll_frame, textvariable=self.reroll_vars[f"free_rerolls_{i}"], width=8).grid(
                row=3, column=i*2+1, sticky="ew", padx=(0, 10), pady=2)
            
            ttk.Label(reroll_frame, text="Initial:").grid(row=4, column=i*2, sticky="w", padx=5, pady=2)
            ttk.Entry(reroll_frame, textvariable=self.reroll_vars[f"initial_free_rerolls_{i}"], width=8).grid(
                row=4, column=i*2+1, sticky="ew", padx=(0, 10), pady=2)

    def create_inventory_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎒 Inventory")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        weapons_frame = ttk.LabelFrame(frame, text="⚔️ Current Weapons", padding="10")
        weapons_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))

        self.weapons_text = tk.Text(weapons_frame, height=15, wrap=tk.WORD)
        weapons_scroll = ttk.Scrollbar(weapons_frame, orient="vertical", command=self.weapons_text.yview)
        self.weapons_text.configure(yscrollcommand=weapons_scroll.set)

        self.weapons_text.grid(row=0, column=0, sticky="nsew")
        weapons_scroll.grid(row=0, column=1, sticky="ns")

        weapons_frame.rowconfigure(0, weight=1)
        weapons_frame.columnconfigure(0, weight=1)

        items_frame = ttk.LabelFrame(frame, text="🎒 Current Items", padding="10")
        items_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))

        self.items_text = tk.Text(items_frame, height=15, wrap=tk.WORD)
        items_scroll = ttk.Scrollbar(items_frame, orient="vertical", command=self.items_text.yview)
        self.items_text.configure(yscrollcommand=items_scroll.set)

        self.items_text.grid(row=0, column=0, sticky="nsew")
        items_scroll.grid(row=0, column=1, sticky="ns")

        items_frame.rowconfigure(0, weight=1)
        items_frame.columnconfigure(0, weight=1)

        note_frame = ttk.Frame(frame)
        note_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        ttk.Label(
            note_frame,
            text="⚠️ Warning: Editing inventory directly can cause crashes.",
            foreground="red",
            font=('Segoe UI', 9, 'italic')
        ).pack()

        def on_mousewheel(event, text_widget):
            text_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_mousewheel(widget, text_widget):
            widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", lambda e: on_mousewheel(e, text_widget)))
            widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))

        bind_mousewheel(weapons_frame, self.weapons_text)
        bind_mousewheel(items_frame, self.items_text)

    def create_enemy_scaling_section(self, parent):
        scaling_frame = ttk.LabelFrame(parent, text="👹 Enemy Scaling", padding="10")
        scaling_frame.pack(fill="x", pady=(0, 10))
        
        scaling_frame.grid_columnconfigure(1, weight=1)
        scaling_frame.grid_columnconfigure(3, weight=1)
        
        self.scaling_vars = {}
        scaling_fields = [
            ("damage", "💥 Damage:", 0, 0),
            ("health", "❤️ Health:", 0, 2),
            ("speed", "💨 Speed:", 1, 0),
            ("number_of_enemies", "👹 Enemy Count:", 1, 2)
        ]
        
        for key, label, row, col in scaling_fields:
            self.scaling_vars[key] = tk.StringVar()
            ttk.Label(scaling_frame, text=label).grid(row=row, column=col, sticky="w", padx=5, pady=3)
            ttk.Entry(scaling_frame, textvariable=self.scaling_vars[key], width=10).grid(
                row=row, column=col+1, sticky="ew", padx=(0, 10), pady=3)
        
    def create_progress_section(self, parent):
        progress_frame = ttk.LabelFrame(parent, text="📈 Boss & Elite Spawns", padding="10")
        progress_frame.pack(fill="x")
        
        progress_frame.grid_columnconfigure(1, weight=1)
        
        self.boss_spawn_var = tk.StringVar()
        self.elite_spawn_var = tk.StringVar()
        
        ttk.Label(progress_frame, text="👑 Boss Spawns:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(progress_frame, textvariable=self.boss_spawn_var).grid(
            row=0, column=1, sticky="ew", padx=(0, 10), pady=3)
        
        ttk.Label(progress_frame, text="⭐ Elite Spawns:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(progress_frame, textvariable=self.elite_spawn_var).grid(
            row=1, column=1, sticky="ew", padx=(0, 10), pady=3)
        
    def create_stats_tab(self):
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="📊 Stats")
            
            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            outer_frame = ttk.Frame(scrollable_frame)
            outer_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            outer_frame.grid_columnconfigure(0, weight=1)
            outer_frame.grid_columnconfigure(1, weight=1)
            outer_frame.grid_columnconfigure(2, weight=1)
            outer_frame.grid_rowconfigure(0, weight=1)
            outer_frame.grid_rowconfigure(1, weight=1)
            outer_frame.grid_rowconfigure(2, weight=1)
            
            self.player_stats = {}
            
            stat_groups = [
                ("💪 Core Stats", [
                    ("stat_max_hp", "❤️ Max HP"),
                    ("stat_armor", "🛡️ Armor"), 
                    ("stat_hp_regeneration", "💚 HP Regen"),
                    ("stat_lifesteal", "🩸 Lifesteal"),
                    ("stat_speed", "💨 Speed"),
                    ("stat_dodge", "🏃 Dodge"),
                    ("stat_luck", "🍀 Luck"),
                    ("stat_harvesting", "🌾 Harvesting")
                ]),
                ("⚔️ Damage Stats", [
                    ("stat_melee_damage", "🗡️ Melee Damage"),
                    ("stat_ranged_damage", "🏹 Ranged Damage"),
                    ("stat_elemental_damage", "⚡ Elemental Damage"),
                    ("stat_damage", "📈 + Damage (Seems to do nothing)"),
                    ("stat_percent_damage", "📈 % Damage"),
                    ("stat_attack_speed", "⚡ Attack Speed"),
                    ("stat_crit_chance", "💥 Crit Chance"),
                    ("stat_crit_damage", "💀 Crit Damage"),
                    ("stat_engineering", "🔧 Engineering"),
                    ("damage_against_bosses", "👑 Damage vs Bosses"),
                    ("elite_damage", "⭐ Elite Damage")
                ]),
                ("🎯 Accuracy & Range", [
                    ("stat_range", "📏 Range"),
                    ("stat_accuracy", "🎯 Accuracy"),
                    ("accuracy", "🎯 Accuracy (Alt)"),
                    ("piercing", "🏹 Piercing"),
                    ("piercing_damage", "🏹 Pierce Damage"),
                    ("knockback", "👊 Knockback"),
                    ("negative_knockback", "👊 Negative Knockback"),
                    ("knockback_aura", "👊 Knockback Aura"),
                    ("bounce", "⚡ Bounce"),
                    ("bounce_damage", "⚡ Bounce Damage"),
                    ("bounce_on_crit", "⚡ Bounce on Crit"),
                    ("pierce_on_crit", "🏹 Pierce on Crit"),
                    ("projectiles", "🎯 Projectiles")
                ]),
                ("🔥 Elemental Effects", [
                    ("burning_chance", "🔥 Burn Chance"),
                    ("burning_damage", "🔥 Burn Damage"),
                    ("burning_spread", "🔥 Burn Spread"),
                    ("burning_cooldown_increase", "🔥 Burn CD Increase"),
                    ("burning_cooldown_reduction", "🔥 Burn CD Reduction"),
                    ("burning_enemy_speed", "🔥 Burning Enemy Speed"),
                    ("can_burn_enemies", "🔥 Can Burn Enemies"),
                    ("bonus_non_elemental_damage_against_burning_targets", "🔥 Bonus vs Burning"),
                    ("explosion_chance", "💥 Explosion Chance"),
                    ("explosion_damage", "💥 Explosion Damage"),
                    ("explosion_size", "💥 Explosion Size"),
                    ("freeze_chance", "❄️ Freeze Chance"),
                    ("poison_chance", "☠️ Poison Chance"),
                    ("poison_damage", "☠️ Poison Damage"),
                    ("poisoned_fruit", "☠️ Poisoned Fruit")
                ]),
                ("💰 Economy & Utility", [
                    ("chance_double_gold", "💰 Double Gold"),
                    ("bonus_gold", "💰 Bonus Gold"),
                    ("enemy_gold", "💰 Enemy Gold"),
                    ("enemy_gold_drops", "💰 Enemy Gold Drops"),
                    ("neutral_gold_drops", "💰 Neutral Gold Drops"),
                    ("gold_drops", "💰 Gold Drops"),
                    ("gain_pct_gold_start_wave", "💰 % Gold Start Wave"),
                    ("gold_on_cursed_enemy_kill", "💰 Gold on Cursed Kill"),
                    ("xp_gain", "✨ XP Gain"),
                    ("consumable_heal", "🍎 Consumable Heal"),
                    ("consumable_heal_over_time", "🍎 Heal Over Time"),
                    ("free_rerolls", "🎲 Free Rerolls"),
                    ("reroll_price", "🎲 Reroll Price"),
                    ("pickup_range", "🧲 Pickup Range"),
                    ("item_attracting_chance", "🧲 Item Attract")
                ]),
                ("🏪 Shop & Items", [
                    ("weapons_price", "⚔️ Weapon Price"),
                    ("items_price", "🎒 Item Price"),
                    ("weapon_slot", "⚔️ Weapon Slots"),
                    ("item_slot", "🎒 Item Slots"),
                    ("max_weapon_tier", "⭐ Max Weapon Tier"),
                    ("min_weapon_tier", "⭐ Min Weapon Tier"),
                    ("weapon_tier_probability", "🎲 Weapon Tier Prob"),
                    ("item_steals", "🔄 Item Steals"),
                    ("item_steals_spawns_random_elite", "🔄 Item Steals Spawn Elite"),
                    ("recycling_gains", "♻️ Recycling Gains"),
                    ("increase_material_value", "💎 Material Value"),
                    ("materials_per_living_enemy", "💎 Materials per Enemy")
                ]),
                ("🎲 Secondary Stats", [
                    ("boss_strength", "👑 Boss Strength"),
                    ("number_of_enemies", "👹 Enemy Count"),
                    ("enemy_damage", "👹 Enemy Damage"),
                    ("enemy_health", "❤️ Enemy Health"),
                    ("enemy_speed", "💨 Enemy Speed"),
                    ("danger_enemy_damage", "⚠️ Danger Enemy Damage"),
                    ("danger_enemy_health", "⚠️ Danger Enemy Health"),
                    ("enemy_fruit_drops", "🍎 Enemy Fruit Drops"),
                    ("special_enemies_last_wave", "👹 Special Enemies Last Wave"),
                    ("stronger_elites_on_kill", "⭐ Stronger Elites on Kill"),
                    ("stronger_loot_aliens_on_kill", "👽 Stronger Loot Aliens")
                ]),
                ("🌟 Special Effects", [
                    ("loot_alien_chance", "👽 Loot Alien Chance"),
                    ("loot_alien_speed", "👽 Loot Alien Speed"),
                    ("crate_chance", "📦 Crate Chance"),
                    ("extra_loot_aliens", "👽 Extra Loot Aliens"),
                    ("extra_loot_aliens_next_wave", "👽 Extra Loot Next Wave"),
                    ("harvesting_growth", "🌱 Harvesting Growth"),
                    ("hp_start_wave", "❤️ HP Start Wave"),
                    ("hp_start_next_wave", "❤️ HP Start Next Wave"),
                    ("next_level_xp_needed", "✨ XP Needed"),
                    ("life_on_crit", "💖 Life On Crit"),
                    ("steal_on_crit", "🔄 Steal On Crit"),
                    ("heal_on_crit_kill", "💖 Heal on Crit Kill"),
                    ("heal_on_kill", "💖 Heal on Kill"),
                    ("heal_when_pickup_gold", "💖 Heal on Gold Pickup"),
                    ("reload_when_pickup_gold", "🔄 Reload on Gold Pickup"),
                    ("lose_hp_per_second", "💔 Lose HP per Second"),
                    ("all_weapons_count_for_sets", "⚔️ All Weapons Count Sets"),
                    ("level_upgrades_modifications", "⬆️ Level Upgrade Mods"),
                    ("one_shot_trees", "🌳 One Shot Trees"),
                    ("destroy_weapons", "💔 Destroy Weapons"),
                    ("upgraded_baits", "🎣 Upgraded Baits"),
                    ("wandering_bots", "🤖 Wandering Bots")
                ])
            ]
            
            for i, (group_name, stats) in enumerate(stat_groups):
                row = i // 3
                col = i % 3
                
                group_frame = ttk.LabelFrame(outer_frame, text=group_name, padding="8")
                group_frame.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
                
                group_frame.grid_columnconfigure(1, weight=1)
                
                for j, (stat_key, display_name) in enumerate(stats):
                    self.player_stats[stat_key] = tk.StringVar()
                    ttk.Label(group_frame, text=f"{display_name}:", font=('Segoe UI', 8)).grid(
                        row=j, column=0, sticky="w", padx=(0, 5), pady=1)
                    ttk.Entry(group_frame, textvariable=self.player_stats[stat_key], 
                             width=10, font=('Segoe UI', 8)).grid(row=j, column=1, sticky="ew", pady=1)
            
            self.dlc_stats_frame = ttk.LabelFrame(outer_frame, text="🎮 DLC Stats", padding="8")
            self.dlc_stats_frame.grid(row=2, column=2, sticky="nsew", padx=3, pady=3)
            self.dlc_stats_frame.grid_columnconfigure(1, weight=1)
            
            dlc_stats = [
                ("curse_attack_speed", "⚡ Curse Attack Speed"),
                ("curse_damage", "💀 Curse Damage"),
                ("curse_hp", "❤️ Curse HP"),
                ("curse_speed", "💨 Curse Speed"),
                ("temp_stats_stacking", "📊 Temp Stats Stack"),
                ("giant_crit_damage", "💥 Giant Crit Damage"),
                ("gain_stat_curse", "💀 Gain Curse"),
                ("curse", "💀 Curse")
            ]
            
            self.dlc_entries = {}
            for i, (stat_key, display_name) in enumerate(dlc_stats):
                self.player_stats[stat_key] = tk.StringVar()
                ttk.Label(self.dlc_stats_frame, text=f"{display_name}:", font=('Segoe UI', 8)).grid(
                    row=i, column=0, sticky="w", padx=(0, 5), pady=1)
                entry = ttk.Entry(self.dlc_stats_frame, textvariable=self.player_stats[stat_key], 
                                 width=10, font=('Segoe UI', 8))
                entry.grid(row=i, column=1, sticky="ew", pady=1)
                self.dlc_entries[stat_key] = entry
                entry.config(state='disabled')

            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            frame.bind("<Enter>", lambda e: frame.bind_all("<MouseWheel>", _on_mousewheel))
            frame.bind("<Leave>", lambda e: frame.unbind_all("<MouseWheel>"))

    def create_special_stats_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🌟 Special Stats")
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        special_stats_frame = ttk.LabelFrame(scrollable_frame, text="🌟 Special Stats", padding="10")
        special_stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        special_stats_frame.grid_columnconfigure(1, weight=1)
        special_stats_frame.grid_columnconfigure(3, weight=1)
        
        self.special_vars = {}
        special_fields = [
            ("trees", "🌳 Trees", 0, 0),
            ("trees_start_wave", "🌳 Trees Start Wave", 0, 2),
            ("structures", "🏗️ Structures", 1, 0),
            ("group_structures", "🏗️ Group Structures", 1, 2),
            ("tree_turrets", "🌳 Tree Turrets", 2, 0),
            ("structure_attack_speed", "🏗️ Structure Attack Speed", 2, 2),
            ("structure_percent_damage", "🏗️ Structure % Damage", 3, 0),
            ("structure_range", "🏗️ Structure Range", 3, 2),
            ("structures_can_crit", "🏗️ Structures Can Crit", 4, 0),
            ("pacifist", "☮️ Pacifist", 4, 2),
            ("torture", "😈 Torture", 5, 0),
            ("cryptid", "👾 Cryptid", 5, 2),
            ("no_heal", "🚫 No Heal", 6, 0),
            ("hit_protection", "🛡️ Hit Protection", 6, 2),
            ("invulnerability_while_dashing", "⚡ Invuln While Dash", 7, 0),
            ("can_attack_while_moving", "🏃 Attack While Moving", 7, 2),
            ("double_boss", "👑 Double Boss", 8, 0),
            ("map_size", "🗺️ Map Size", 8, 2),
            ("max_turret_count", "🏗️ Max Turrets", 9, 0),
            ("max_weapon_slots", "⚔️ Max Weapon Slots", 9, 2),
            ("curse_locked_items", "🔒 Curse Locked Items", 10, 0),
            ("curse_locked_shop_items", "🔒 Curse Locked Shop Items", 10, 2),
            ("instant_gold_attracting", "💰 Instant Gold Attract", 11, 0)
        ]
        
        for key, label, row, col in special_fields:
            self.special_vars[key] = tk.StringVar()
            if key not in self.player_stats:
                self.player_stats[key] = self.special_vars[key]
            ttk.Label(special_stats_frame, text=f"{label}:").grid(
                row=row, column=col, sticky="w", padx=5, pady=2)
            ttk.Entry(special_stats_frame, textvariable=self.special_vars[key], width=12).grid(
                row=row, column=col+1, sticky="ew", padx=(0, 10), pady=2)

        def _on_mousewheel_special(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        frame.bind("<Enter>", lambda e: frame.bind_all("<MouseWheel>", _on_mousewheel_special))
        frame.bind("<Leave>", lambda e: frame.unbind_all("<MouseWheel>"))

    def create_caps_limits_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Caps & Limits")
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        caps_frame = ttk.LabelFrame(scrollable_frame, text="📊 Caps & Limits", padding="10")
        caps_frame.pack(fill="both", expand=True, padx=10, pady=10)
        caps_frame.grid_columnconfigure(1, weight=1)
        caps_frame.grid_columnconfigure(3, weight=1)
        
        self.caps_vars = {}
        caps_fields = [
            ("hp_cap", "❤️ HP Cap", 0, 0),
            ("speed_cap", "💨 Speed Cap", 0, 2),
            ("dodge_cap", "🏃 Dodge Cap", 1, 0),
            ("crit_chance_cap", "💥 Crit Chance Cap", 1, 2),
            ("attack_speed_cap", "⚡ Attack Speed Cap", 2, 0),
            ("armor_cap", "🛡️ Armor Cap", 2, 2),
            ("lifesteal_cap", "🩸 Lifesteal Cap", 3, 0),
            ("piercing_cap", "🏹 Pierce Cap", 3, 2),
            ("max_melee_weapons", "🗡️ Max Melee Weapons", 4, 0),
            ("max_ranged_weapons", "🏹 Max Ranged Weapons", 4, 2),
            ("weapon_slot_upgrades", "⚔️ Weapon Slot Upgrades", 5, 0),
            ("no_melee_weapons", "🚫 No Melee Weapons", 5, 2),
            ("no_ranged_weapons", "🚫 No Ranged Weapons", 6, 0),
            ("no_duplicate_weapons", "🚫 No Duplicate Weapons", 6, 2),
            ("lock_current_weapons", "🔒 Lock Current Weapons", 7, 0),
            ("max_item_slots", "🎒 Max Item Slots", 7, 2)
        ]
        
        for key, label, row, col in caps_fields:
            self.caps_vars[key] = tk.StringVar()
            if key not in self.player_stats:
                self.player_stats[key] = self.caps_vars[key]
            ttk.Label(caps_frame, text=f"{label}:").grid(
                row=row, column=col, sticky="w", padx=5, pady=2)
            ttk.Entry(caps_frame, textvariable=self.caps_vars[key], width=12).grid(
                row=row, column=col+1, sticky="ew", padx=(0, 10), pady=2)

        def _on_mousewheel_caps(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        frame.bind("<Enter>", lambda e: frame.bind_all("<MouseWheel>", _on_mousewheel_caps))
        frame.bind("<Leave>", lambda e: frame.unbind_all("<MouseWheel>"))

    def create_shop_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏪 Shop Settings")
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        shop_frame = ttk.LabelFrame(scrollable_frame, text="🏪 Shop Settings", padding="10")
        shop_frame.pack(fill="both", expand=True, padx=10, pady=10)
        shop_frame.grid_columnconfigure(1, weight=1)
        shop_frame.grid_columnconfigure(3, weight=1)
        
        self.shop_vars = {}
        shop_fields = [
            ("minimum_weapons_in_shop", "⚔️ Min Weapons in Shop", 0, 0),
            ("hp_shop", "❤️ HP Shop", 0, 2),
            ("disable_item_locking", "🔓 Disable Item Locking", 1, 0),
            ("shop_size", "🏪 Shop Size", 1, 2),
            ("shop_tier_probability", "🎲 Shop Tier Prob", 2, 0),
            ("item_box_gold", "📦 Item Box Gold", 2, 2),
            ("shop_effects_checked", "✅ Shop Effects Checked", 3, 0),
            ("shop_locked", "🔒 Shop Locked", 3, 2)
        ]
        
        for key, label, row, col in shop_fields:
            if key == "shop_effects_checked" or key == "shop_locked":
                self.shop_vars[key] = tk.BooleanVar()
                ttk.Label(shop_frame, text=f"{label}:").grid(
                    row=row, column=col, sticky="w", padx=5, pady=2)
                ttk.Checkbutton(shop_frame, variable=self.shop_vars[key]).grid(
                    row=row, column=col+1, sticky="w", padx=(0, 10), pady=2)
            else:
                self.shop_vars[key] = tk.StringVar()
                if key not in self.player_stats:
                    self.player_stats[key] = self.shop_vars[key]
                ttk.Label(shop_frame, text=f"{label}:").grid(
                    row=row, column=col, sticky="w", padx=5, pady=2)
                ttk.Entry(shop_frame, textvariable=self.shop_vars[key], width=12).grid(
                    row=row, column=col+1, sticky="ew", padx=(0, 10), pady=2)

        def _on_mousewheel_shop(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        frame.bind("<Enter>", lambda e: frame.bind_all("<MouseWheel>", _on_mousewheel_shop))
        frame.bind("<Leave>", lambda e: frame.unbind_all("<MouseWheel>"))
                
    def on_dlc_mode_change(self, *args):
        state = 'normal' if self.dlc_mode.get() else 'disabled'
        for entry in self.dlc_entries.values():
            entry.config(state=state)
    
    def safe_convert_to_int(self, value, default=0):
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                if value.strip() == "":
                    return default
                return int(float(value.strip()))
            return default
        except (ValueError, TypeError):
            return default
    
    def safe_convert_to_float(self, value, default=0.0):
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                if value.strip() == "":
                    return default
                return float(value.strip())
            return default
        except (ValueError, TypeError):
            return default
    
    def open_file(self):
        appdata_path = os.getenv("APPDATA") 
        brotato_path = os.path.join(appdata_path, "brotato")

        file_path = filedialog.askopenfilename(
            title="Open Brotato Save File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=brotato_path 
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.save_data = json.load(file)
                    self.original_save_data = json.loads(json.dumps(self.save_data))
                self.current_file = file_path
                self.load_data()
                self.status_var.set(f"Loaded: {file_path}")
                messagebox.showinfo("Success", "Save file loaded successfully!")
            except Exception as e:
                self.status_var.set("Error loading file")
                messagebox.showerror("Error", f"Failed to load save file: {str(e)}")
    
    def load_inventory_data(self):
        if not self.save_data:
            return
            
        current_run = self.save_data.get("current_run_state", {})
        if current_run.get("players_data") and len(current_run["players_data"]) > 0:
            player_data = current_run["players_data"][0]
            
            weapons = player_data.get("weapons", [])
            items = player_data.get("items", [])
            
            self.weapons_text.delete(1.0, tk.END)
            self.items_text.delete(1.0, tk.END)
            
            if weapons:
                weapons_display = json.dumps(weapons, indent=2)
                self.weapons_text.insert(1.0, weapons_display)
            else:
                self.weapons_text.insert(1.0, "No weapons found")
            
            if items:
                items_display = json.dumps(items, indent=2)
                self.items_text.insert(1.0, items_display)
            else:
                self.items_text.insert(1.0, "No items found")
    
    def load_data(self):
        if not self.save_data:
            return
            
        current_run = self.save_data.get("current_run_state", {})
        
        for key, var in self.run_vars.items():
            if key in ["current_health", "current_level", "current_xp", "gold"]:
                if current_run.get("players_data") and len(current_run["players_data"]) > 0:
                    var.set(str(current_run["players_data"][0].get(key, 0)))
                else:
                    var.set("0")
            else:
                default = 20 if key == "nb_of_waves" else 0
                var.set(str(current_run.get(key, default)))
        
        if current_run.get("players_data") and len(current_run["players_data"]) > 0:
            player_data = current_run["players_data"][0]
            self.current_character_var.set(str(player_data.get("current_character", "")))
            self.selected_weapon_var.set(str(player_data.get("selected_weapon", "")))
            
            for key in self.challenge_vars:
                if key == "consumables_picked_up_this_run":
                    self.challenge_vars[key].set(str(player_data.get(key, 0)))
                elif key == "chal_recycling_current":
                    self.challenge_vars[key].set(str(player_data.get(key, 0)))
                else:
                    self.challenge_vars[key].set(str(current_run.get(key, 0)))
            
            effects = player_data.get("effects", {})
            for stat_name, var in self.player_stats.items():
                value = effects.get(stat_name, 0)
                if isinstance(value, dict):
                    if "chance" in value:
                        var.set(str(value.get("chance", 0)))
                    elif "value" in value:
                        var.set(str(value.get("value", 0)))
                    else:
                        var.set("0")
                else:
                    var.set(str(value))
        else:
            self.current_character_var.set("")
            self.selected_weapon_var.set("")
            for var in self.player_stats.values():
                var.set("0")
            for var in self.challenge_vars.values():
                var.set("0")
        
        self.current_background_var.set(str(current_run.get("current_background", "")))
        self.is_endless_var.set(current_run.get("is_endless_run", False))
        self.is_coop_var.set(current_run.get("is_coop_run", False))
        self.has_run_state_var.set(current_run.get("has_run_state", True))
        
        enemy_scaling = current_run.get("enemy_scaling", {})
        for key, var in self.scaling_vars.items():
            if key == "number_of_enemies":
                if current_run.get("players_data") and len(current_run["players_data"]) > 0:
                    effects = current_run["players_data"][0].get("effects", {})
                    var.set(str(effects.get(key, 50)))
                else:
                    var.set("50")
            else:
                var.set(str(enemy_scaling.get(key, 1.0)))
        
        bosses_spawn = current_run.get("bosses_spawn", [])
        if isinstance(bosses_spawn, list):
            self.boss_spawn_var.set(json.dumps(bosses_spawn))
        else:
            self.boss_spawn_var.set(str(bosses_spawn))
        
        elites_spawn = current_run.get("elites_spawn", [])
        if isinstance(elites_spawn, list):
            self.elite_spawn_var.set(json.dumps(elites_spawn))
        else:
            self.elite_spawn_var.set(str(elites_spawn))
        
        for i in range(4):
            reroll_count = current_run.get("reroll_count", [0, 0, 0, 0])
            paid_reroll = current_run.get("paid_reroll_count", [0, 0, 0, 0])
            free_rerolls = current_run.get("free_rerolls", [0, 0, 0, 0])
            initial_free = current_run.get("initial_free_rerolls", [0, 0, 0, 0])
            
            self.reroll_vars[f"reroll_count_{i}"].set(str(reroll_count[i] if i < len(reroll_count) else 0))
            self.reroll_vars[f"paid_reroll_count_{i}"].set(str(paid_reroll[i] if i < len(paid_reroll) else 0))
            self.reroll_vars[f"free_rerolls_{i}"].set(str(free_rerolls[i] if i < len(free_rerolls) else 0))
            self.reroll_vars[f"initial_free_rerolls_{i}"].set(str(initial_free[i] if i < len(initial_free) else 0))
        
        data_section = self.save_data.get("data", {})
        for key, var in self.quick_stats_vars.items():
            if key != "curse_locked_shop_items_pity":
                var.set(str(data_section.get(key, 0)))
        
        if hasattr(self, 'shop_vars'):
            if isinstance(self.shop_vars.get("shop_effects_checked"), tk.BooleanVar):
                self.shop_vars["shop_effects_checked"].set(current_run.get("shop_effects_checked", True))
            if isinstance(self.shop_vars.get("shop_locked"), tk.BooleanVar):
                self.shop_vars["shop_locked"].set(current_run.get("shop_locked", False))
        
        if current_run.get("players_data") and len(current_run["players_data"]) > 0:
            player_data = current_run["players_data"][0]
            curse_pity = player_data.get("curse_locked_shop_items_pity", 0)
            self.quick_stats_vars["curse_locked_shop_items_pity"].set(str(curse_pity))
        
        self.load_inventory_data()
    
    def save_data_to_structure(self):
        if not self.save_data or not self.original_save_data:
            return
        
        current_run = self.save_data.get("current_run_state", {})
        if not current_run:
            return
        
        for key, var in self.run_vars.items():
            if key in ["current_health", "current_level", "current_xp", "gold"]:
                if current_run.get("players_data") and len(current_run["players_data"]) > 0:
                    new_val = self.safe_convert_to_int(var.get())
                    current_run["players_data"][0][key] = new_val
            else:
                new_val = self.safe_convert_to_int(var.get(), 20 if key == "nb_of_waves" else 0)
                current_run[key] = new_val
        
        if current_run.get("players_data") and len(current_run["players_data"]) > 0:
            player_data = current_run["players_data"][0]
            
            if self.current_character_var.get().strip():
                player_data["current_character"] = self.current_character_var.get().strip()
            if self.selected_weapon_var.get().strip():
                player_data["selected_weapon"] = self.selected_weapon_var.get().strip()
            
            for key, var in self.challenge_vars.items():
                if key in ["consumables_picked_up_this_run", "chal_recycling_current"]:
                    player_data[key] = self.safe_convert_to_int(var.get())
                else:
                    current_run[key] = self.safe_convert_to_int(var.get())
            
            if self.current_background_var.get().strip():
                current_run["current_background"] = self.current_background_var.get().strip()
            current_run["is_endless_run"] = self.is_endless_var.get()
            current_run["is_coop_run"] = self.is_coop_var.get()
            current_run["has_run_state"] = self.has_run_state_var.get()
            
            enemy_scaling = current_run.get("enemy_scaling", {})
            for key, var in self.scaling_vars.items():
                if key == "number_of_enemies":
                    effects = player_data.get("effects", {})
                    if effects is not None:
                        effects[key] = self.safe_convert_to_int(var.get(), 50)
                else:
                    enemy_scaling[key] = self.safe_convert_to_float(var.get(), 1.0)
            
            boss_spawn_str = self.boss_spawn_var.get().strip()
            if boss_spawn_str:
                try:
                    if boss_spawn_str.startswith('[') and boss_spawn_str.endswith(']'):
                        parsed_bosses = json.loads(boss_spawn_str)
                        if isinstance(parsed_bosses, list):
                            current_run["bosses_spawn"] = parsed_bosses
                    elif boss_spawn_str != "[]":
                        current_run["bosses_spawn"] = boss_spawn_str
                except (json.JSONDecodeError, ValueError):
                    pass
            
            elite_spawn_str = self.elite_spawn_var.get().strip()
            if elite_spawn_str:
                try:
                    if elite_spawn_str.startswith('[') and elite_spawn_str.endswith(']'):
                        parsed_elites = json.loads(elite_spawn_str)
                        if isinstance(parsed_elites, list):
                            current_run["elites_spawn"] = parsed_elites
                    elif elite_spawn_str != "[]":
                        current_run["elites_spawn"] = elite_spawn_str
                except (json.JSONDecodeError, ValueError):
                    pass
            
            reroll_count = []
            paid_reroll = []
            free_rerolls_list = []
            initial_free = []
            
            for i in range(4):
                reroll_count.append(self.safe_convert_to_int(self.reroll_vars[f"reroll_count_{i}"].get()))
                paid_reroll.append(self.safe_convert_to_int(self.reroll_vars[f"paid_reroll_count_{i}"].get()))
                free_rerolls_list.append(self.safe_convert_to_int(self.reroll_vars[f"free_rerolls_{i}"].get()))
                initial_free.append(self.safe_convert_to_int(self.reroll_vars[f"initial_free_rerolls_{i}"].get()))
            
            current_run["reroll_count"] = reroll_count
            current_run["paid_reroll_count"] = paid_reroll
            current_run["free_rerolls"] = free_rerolls_list
            current_run["initial_free_rerolls"] = initial_free
            
            effects = player_data.get("effects", {})
            if effects is not None:
                for stat_name, var in self.player_stats.items():
                    new_value_str = var.get().strip()
                    
                    if new_value_str == "":
                        continue
                    
                    try:
                        if stat_name in ["weapon_tier_probability", "pickup_range", "shop_tier_probability"]:
                            new_value = float(new_value_str)
                        else:
                            new_value = int(float(new_value_str))
                        
                        original_value = effects.get(stat_name)
                        if isinstance(original_value, dict):
                            if "chance" in original_value:
                                effects[stat_name]["chance"] = new_value
                            elif "value" in original_value:
                                effects[stat_name]["value"] = new_value
                        else:
                            effects[stat_name] = new_value
                    except (ValueError, TypeError):
                        continue
            
            player_data["curse_locked_shop_items_pity"] = self.safe_convert_to_int(
                self.quick_stats_vars["curse_locked_shop_items_pity"].get()
            )
        
        data_section = self.save_data.get("data", {})
        if data_section is not None:
            for key, var in self.quick_stats_vars.items():
                if key != "curse_locked_shop_items_pity":
                    data_section[key] = self.safe_convert_to_int(var.get())
        
        if hasattr(self, 'shop_vars'):
            if isinstance(self.shop_vars.get("shop_effects_checked"), tk.BooleanVar):
                current_run["shop_effects_checked"] = self.shop_vars["shop_effects_checked"].get()
            if isinstance(self.shop_vars.get("shop_locked"), tk.BooleanVar):
                current_run["shop_locked"] = self.shop_vars["shop_locked"].get()

    def save_file(self):
        if not self.current_file or not self.save_data:
            messagebox.showerror("Error", "No file loaded to save!")
            return
            
        try:
            self.save_data_to_structure()
            
            with open(self.current_file, 'w', encoding='utf-8') as file:
                json.dump(self.save_data, file, indent=None, separators=(',', ':'), ensure_ascii=False)
            
            self.status_var.set(f"Saved: {self.current_file}")
            messagebox.showinfo("Success", "Save file updated successfully!")
        except Exception as e:
            self.status_var.set("Error saving file")
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        

    def save_as_file(self):
        if not self.save_data:
            messagebox.showerror("Error", "No data to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Brotato Save File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.save_data_to_structure()
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(self.save_data, file, indent=None, separators=(',', ':'), ensure_ascii=False)
                
                self.current_file = file_path
                self.status_var.set(f"Saved as: {file_path}")
                messagebox.showinfo("Success", "Save file created successfully!")
            except Exception as e:
                self.status_var.set("Error creating file")
                messagebox.showerror("Error", f"Failed to create save file: {str(e)}")
            

def main():
    root = tk.Tk()
    
    try:
        root.iconbitmap('brotato.ico') # gotta figure out what kinda icon i want lol
    except:
        pass
    
    app = BrotatoSaveEditor(root)
    
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()

