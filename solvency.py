import streamlit as st
import random
import time
import pandas as pd

# --- 1. CONFIGURATION: MODES & REALITIES ---
# Each mode has specific stats and "Tags" that filter which questions they see.
LIFE_PATHS = {
    "Student": {
        "salary": 0, "start_cash": 800, "debt": 40000, "kids": 0, 
        "fragility_start": 40, "desc": "Living on loans. High debt pressure.",
        "tags": ["student", "everyday"]
    },
    "Unemployed": {
        "salary": 0, "start_cash": 1200, "debt": 5000, "kids": 0, 
        "fragility_start": 60, "desc": "Savings are draining. You need a job ASAP.",
        "tags": ["survival", "everyday"]
    },
    "Divorced Dad (2 Kids)": {
        "salary": 2500, "start_cash": 1000, "debt": 25000, "kids": 2, 
        "fragility_start": 50, "desc": "High income, but alimony & kids drain it all.",
        "tags": ["parent", "legal", "everyday"]
    },
    "Recession Survivor": {
        "salary": 1500, "start_cash": 300, "debt": 10000, "kids": 0, 
        "fragility_start": 65, "desc": "Economy crashed. Prices are high. Everyone is panic selling.",
        "tags": ["crisis", "everyday", "survival"]
    },
    "Broke & Broken": {
        "salary": 600, "start_cash": 50, "debt": 2000, "kids": 0, 
        "fragility_start": 68, "desc": "One bad move and it's over. Hardcore mode.",
        "tags": ["survival", "debt"]
    }
}

# --- 2. SCENARIO DATABASE (Tagged) ---
MASTER_DB = [
    # --- PARENT / DIVORCED ---
    {"title": "Custody Battle", "tags": ["parent", "legal"], "desc": "Ex demands more support money.", "inspect": "⚠️ LEGAL: Lawyer retainer is $2k. Representing self is free but risky.", "def_t": "Retainer Fee", "def_d": "Upfront cost for legal services.", "ops": [("Hire Lawyer ($2k)", "safe"), ("Represent Self", "gamble"), ("Ignore", "trap")], "ops_i": [("Pay Retainer", "safe"), ("Mediation ($200)", "smart"), ("Represent Self", "gamble")]},
    {"title": "The Field Trip", "tags": ["parent"], "desc": "Kids want to go to Disney ($500).", "inspect": "⚠️ GUILT: Saying no increases Fragility (stress).", "def_t": "Social Inflation", "def_d": "Pressure to spend to match peers.", "ops": [("Go ($500)", "trap"), ("Stay Home", "smart"), ("Credit Card", "trap")], "ops_i": [("Go ($500)", "trap"), ("Local Park ($50)", "smart"), ("Stay Home", "smart")]},
    
    # --- STUDENT ---
    {"title": "Textbook Scam", "tags": ["student"], "desc": "Prof says you need the 'New Edition' ($300).", "inspect": "⚠️ CHECK: The old edition is 99% the same.", "def_t": "Planned Obsolescence", "def_d": "Products designed to be useless quickly.", "ops": [("Buy New", "trap"), ("Check Library", "inspect"), ("Download PDF", "gamble")], "ops_i": [("Buy New", "trap"), ("Rent Used ($30)", "smart"), ("Library (Free)", "safe")]},
    {"title": "Spring Break", "tags": ["student"], "desc": "Friends going to Cancun ($1,200).", "inspect": "⚠️ FOMO: Fear Of Missing Out drives bad debt.", "def_t": "FOMO Spending", "def_d": "Spending to avoid social exclusion.", "ops": [("Charge it!", "trap"), ("Check Budget", "inspect"), ("Stay Campus", "smart")], "ops_i": [("Go ($1200)", "trap"), ("Road Trip ($200)", "safe"), ("Stay Home", "smart")]},

    # --- SURVIVAL / UNEMPLOYED ---
    {"title": "The Job Interview", "tags": ["survival", "career"], "desc": "Interview across town. Uber is $40.", "inspect": "⚠️ ROI: The job pays $50k. The $40 is an investment.", "def_t": "Return on Investment", "def_d": "Spending money to make money.", "ops": [("Take Uber", "smart"), ("Walk (2hrs)", "trap"), ("Skip it", "trap")], "ops_i": [("Take Uber", "smart"), ("Bus ($2)", "safe"), ("Skip", "trap")]},
    {"title": "Grocery Inflation", "tags": ["survival", "crisis"], "desc": "Eggs are $10. Milk is $8.", "inspect": "⚠️ SUBSTITUTE: Frozen veggies are cheaper and last longer.", "def_t": "Substitution Effect", "def_d": "Switching to cheaper alternatives when prices rise.", "ops": [("Buy Normal", "trap"), ("Check Sales", "inspect"), ("Fast", "gamble")], "ops_i": [("Buy Normal", "trap"), ("Buy Frozen/Bulk", "smart"), ("Fast", "gamble")]},

    # --- EVERYDAY / GENERAL ---
    {"title": "Car Noise", "tags": ["everyday"], "desc": "Clunking sound. Mechanic wants $100 to look.", "inspect": "⚠️ DIY: It's likely just a loose shield.", "def_t": "Information Asymmetry", "def_d": "When the seller knows more than the buyer.", "ops": [("Pay $100", "safe"), ("YouTube It", "inspect"), ("Turn up Radio", "trap")], "ops_i": [("Pay Shop", "safe"), ("Fix Self ($0)", "smart"), ("Ignore", "trap")]},
    {"title": "Subscription Renewal", "tags": ["everyday"], "desc": "Streaming service renewed for $150/yr.", "inspect": "⚠️ REFUND: If you cancel within 3 days, they refund.", "def_t": "Zombie Cost", "def_d": "Recurring costs you forgot about.", "ops": [("Keep it", "trap"), ("Cancel", "smart"), ("Email Support", "safe")], "ops_i": [("Keep it", "trap"), ("Cancel for Refund", "smart"), ("Email Support", "safe")]},
]

# --- 3. GAME ENGINE ---
class SolvencyEngine:
    def __init__(self, mode_name):
        self.mode = mode_name
        config = LIFE_PATHS[mode_name]
        
        # Stats
        self.cash = config["start_cash"]
        self.debt = config["debt"]
        self.fragility = config["fragility_start"]
        self.fragility_max = 70 # GAME OVER LIMIT
        self.fragility_target = 0 # LEVEL UP TARGET
        
        self.level = 1
        self.expense_mult = 1.0
        self.week = 1
        
        # Profile Details
        self.kids = config["kids"]
        self.salary = config["salary"]
        self.tags = config["tags"]
        
        # Logs
        self.history = []
        self.intel_collected = [] # For the "Lesson Tab"
        
        # Deck Management
        self.full_deck = [s for s in MASTER_DB if any(t in s["tags"] for t in self.tags)]
        if not self.full_deck: self.full_deck = MASTER_DB # Fallback
        
        self.current_scen = random.choice(self.full_deck)
        self.shuffled_indices = [0, 1, 2]
        random.shuffle(self.shuffled_indices)

    def process_turn(self, choice_idx, is_inspected):
        logical_idx = self.shuffled_indices[choice_idx]
        
        # 1. HANDLE INSPECT
        if logical_idx == 1:
            return "inspect", self.current_scen["inspect"]

        # 2. HANDLE CHOICE
        scen = self.current_scen
        choice_type = scen["ops"][logical_idx][1]
        
        msg = ""
        delta_cash = 0
        delta_frag = 0
        
        if choice_type == "trap":
            delta_cash = -random.randint(100, 300)
            delta_frag = 15
            msg = "❌ TRAP! Stress increased."
        elif choice_type == "smart":
            delta_frag = -15 # Big relief for being smart
            msg = "🧠 SMART! Stress reduced."
        elif choice_type == "safe":
            delta_cash = -50
            delta_frag = -5
            msg = "🛡️ SAFE. Small relief."
        elif choice_type == "gamble":
            if random.random() > 0.5:
                delta_frag = -20
                msg = "🎲 WON! Huge relief."
            else:
                self.debt += 1000
                delta_frag = 10
                msg = "💀 LOST! Debt increased."

        # 3. APPLY ECONOMICS (Expenses & Income)
        pay = random.randint(0, 1000) if self.salary == "var" else self.salary
        expenses = int((200 + (self.kids * 150)) * self.expense_mult)
        
        self.cash += (delta_cash + pay - expenses)
        self.fragility += delta_frag
        self.fragility = max(0, self.fragility) # Cannot go below 0 (triggers level up)
        
        # Log History & Intel
        self.history.insert(0, f"Wk {self.week}: {msg} (Fragility {delta_frag})")
        
        intel_entry = {"term": scen["def_t"], "def": scen["def_d"], "scen": scen["title"]}
        if intel_entry not in self.intel_collected:
            self.intel_collected.append(intel_entry)

        # 4. CHECK WIN/LOSS
        if self.fragility >= self.fragility_max:
            return "game_over", "🤯 MENTAL BREAKDOWN! Fragility hit 70%. Game Over."
        
        if self.cash < -500: # Allow small overdraft
             return "game_over", "💸 BANKRUPT! Cash is too low."

        # 5. CHECK LEVEL UP
        if self.fragility == 0:
            self.level += 1
            self.fragility = 30 # Reset to mid-stress
            self.expense_mult += 0.2 # INFLATION!
            self.week = 1
            return "level_up", f"🚀 LEVEL {self.level}! Difficulty Increased (Inflation +20%)"

        # 6. NEXT TURN
        self.week += 1
        self.current_scen = random.choice(self.full_deck)
        random.shuffle(self.shuffled_indices)
        
        return "next", msg

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="Solvency: Pressure Cooker", page_icon="🔥", layout="wide")

# Custom CSS for "Fun" Vibe
st.markdown("""
<style>
    .stMetric { background-color: #1E1E1E; padding: 10px; border-radius: 10px; border: 1px solid #333; }
    .css-1v0mbdj { margin-top: -50px; }
</style>
""", unsafe_allow_html=True)

if "game" not in st.session_state: st.session_state.game = None
if "inspected" not in st.session_state: st.session_state.inspected = False

# --- SIDEBAR (SETUP) ---
with st.sidebar:
    st.title("🔥 SOLVENCY")
    st.caption("Reduce Fragility to 0% to Level Up.")
    
    if st.session_state.game is None:
        mode = st.selectbox("Select Reality", list(LIFE_PATHS.keys()))
        st.info(LIFE_PATHS[mode]["desc"])
        if st.button("🚀 Start Life", type="primary"):
            st.session_state.game = SolvencyEngine(mode)
            st.rerun()
    else:
        st.subheader("🏦 Bank App")
        pay_amt = st.number_input("Pay Debt", step=100)
        if st.button("💸 Transfer"):
            g = st.session_state.game
            if pay_amt <= g.cash:
                g.cash -= pay_amt
                g.debt -= pay_amt
                g.fragility = max(0, g.fragility - 5) # Paying debt relieves stress!
                st.toast("Payment Successful! Stress -5", icon="💳")
                if g.fragility == 0: # Check instant level up
                    g.level += 1
                    g.fragility = 30
                    g.expense_mult += 0.2
                    st.balloons()
                st.rerun()
            else:
                st.toast("Insufficient Funds", icon="❌")
        
        st.divider()
        if st.button("🏳️ Give Up"):
            st.session_state.game = None
            st.rerun()

# --- MAIN SCREEN ---
if st.session_state.game:
    g = st.session_state.game
    scen = g.current_scen
    
    # 1. THE HUD
    st.markdown(f"### 🚩 Level {g.level} | Week {g.week}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash", f"${int(g.cash)}")
    c2.metric("Debt", f"${g.debt}", delta_color="inverse")
    
    # Fragility Bar (The Main Mechanic)
    frag_ratio = min(g.fragility / g.fragility_max, 1.0)
    bar_color = "red" if g.fragility > 50 else "green"
    c3.metric("Fragility (Risk)", f"{g.fragility}%", help="Get this to 0 to advance!")
    st.progress(frag_ratio, text=f"Mental Stress: {g.fragility}/70 (Game Over at 70)")

    # 2. TABS (Play vs Intel)
    tab_play, tab_intel = st.tabs(["🎮 Decisions", "🧠 Intel & Lessons"])
    
    with tab_play:
        st.divider()
        st.subheader(f"📍 {scen['title']}")
        st.caption("Tags: " + ", ".join(scen['tags']))
        st.write(f"**{scen['desc']}**")
        
        if st.session_state.inspected:
            st.warning(f"🕵️ INTEL: {scen['inspect']}")
        
        # Buttons
        ops_src = scen["ops_i"] if st.session_state.inspected else scen["ops"]
        indices = g.shuffled_indices
        
        col1, col2, col3 = st.columns(3)
        
        def click(idx):
            res, txt = g.process_turn(idx, st.session_state.inspected)
            if res == "inspect":
                st.session_state.inspected = True
            elif res == "game_over":
                st.error(txt)
                st.snow()
                time.sleep(3)
                st.session_state.game = None
