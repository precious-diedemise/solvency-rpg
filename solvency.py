import streamlit as st
import random
import time
import pandas as pd

# --- CONFIGURATION: REALITIES ---
LIFE_PATHS = {
    "Fresh Grad": {"salary": 800, "start_cash": 1000, "debt": 30000, "kids": 0, "alimony": 0, "desc": "Single. High loans. Entry salary."},
    "Divorced Dad": {"salary": 2000, "start_cash": 1500, "debt": 15000, "kids": 2, "alimony": 400, "desc": "2 Kids + Alimony. Money vanishes."},
    "Single Mom": {"salary": "var", "start_cash": 500, "debt": 5000, "kids": 1, "alimony": 0, "desc": "Gig work. 1 Kid. Hustle mode."},
    "Luxury Broke": {"salary": 2500, "start_cash": 200, "debt": 80000, "kids": 0, "alimony": 0, "desc": "High income, drowning in luxury debt."}
}

MOODS = {
    "Standard": {"expense_mult": 1.0, "fragility_cap": 70},
    "Inflation Crisis": {"expense_mult": 1.5, "fragility_cap": 60},
    "Recession": {"expense_mult": 1.0, "fragility_cap": 50}
}

# --- SCENARIO DATABASE ---
MASTER_DB = [
    {"title": "School Field Trip", "tags": ["parent"], "desc": "Kid needs $50 for the zoo.", "inspect": "⚠️ SOCIAL: If they don't go, they sit alone.", "def_t": "Social Tax", "def_d": "Cost to maintain social standing.", "ops": [("Pay $50", "safe"), ("Check Budget", "inspect"), ("Don't go", "trap")], "ops_i": [("Pay $50", "safe"), ("Pack Lunch ($10)", "smart"), ("Don't go", "trap")]},
    {"title": "Car Breakdown", "tags": ["everyday"], "desc": "Car died. Need it for work.", "inspect": "⚠️ TRAP: Dealer charges $150 just to look.", "def_t": "Sunk Cost", "def_d": "Spending money on broken assets.", "ops": [("Tow to Dealer", "trap"), ("Research", "inspect"), ("Bus", "smart")], "ops_i": [("Dealer ($500)", "trap"), ("Local Shop ($200)", "safe"), ("Bus", "smart")]},
    {"title": "Credit Card Bill", "tags": ["debt"], "desc": "Bill due: $800. Min: $25.", "inspect": "⚠️ MATH: Min pay costs $200 interest.", "def_t": "Amortization", "def_d": "Schedule of paying off debt.", "ops": [("Pay Min", "trap"), ("Calc Interest", "inspect"), ("Pay Full", "smart")], "ops_i": [("Pay Min", "trap"), ("Pay Full", "smart"), ("Pay Half", "safe")]},
    {"title": "Grocery Run", "tags": ["everyday"], "desc": "Fridge empty.", "inspect": "⚠️ MARKUP: Delivery apps add 20%.", "def_t": "Convenience Tax", "def_d": "Premium paid for saving time.", "ops": [("DoorDash ($100)", "trap"), ("Check Apps", "inspect"), ("Walmart ($50)", "safe")], "ops_i": [("DoorDash", "trap"), ("Bike & Cook ($30)", "smart"), ("Walmart", "safe")]},
    {"title": "The Looter", "tags": ["everyday"], "desc": "Chaos in streets. Stolen laptop for $50.", "inspect": "⚠️ RISK: Bail is $5,000 if caught.", "def_t": "Black Market Risk", "def_d": "Hidden costs of illegal deals.", "ops": [("Buy it", "gamble"), ("Assess Risk", "inspect"), ("Walk Away", "smart")], "ops_i": [("Buy it", "gamble"), ("Walk Away", "smart"), ("Report", "safe")]}
]

# --- GAME ENGINE ---
class LifeSim:
    def __init__(self, reality, mood):
        config = LIFE_PATHS[reality]
        mood_cfg = MOODS[mood]
        
        self.profile_name = reality
        self.salary = config["salary"]
        self.cash = config["start_cash"]
        self.debt = config["debt"]
        self.kids = config["kids"]
        self.alimony = config["alimony"]
        
        self.fragility = 20
        self.fragility_cap = mood_cfg["fragility_cap"]
        self.expense_mult = mood_cfg["expense_mult"]
        self.week = 1
        
        self.history = []
        self.data_log = [] 
        
        self.deck = MASTER_DB 
        self.current_scen = random.choice(self.deck)
        self.shuffled_indices = [0, 1, 2]
        random.shuffle(self.shuffled_indices)
        self.start_time = time.time()

    def process_turn(self, choice_idx, inspected_status):
        logical_idx = self.shuffled_indices[choice_idx]
        reaction_time = round(time.time() - self.start_time, 2)
        
        if logical_idx == 1:
            return "inspect", self.current_scen["inspect"]
            
        scen = self.current_scen
        c_type = scen["ops"][logical_idx][1]
        
        # LOG DATA
        self.data_log.append({
            "Profile": self.profile_name,
            "Scenario": scen["title"],
            "Choice Type": c_type,
            "Did Inspect": inspected_status,
            "Reaction Time (s)": reaction_time,
            "Week": self.week
        })
        
        msg = ""
        delta_cash = 0
        
        if c_type == "trap":
            delta_cash = -random.randint(100, 300)
            self.fragility += 15
            msg = "❌ TRAP! Lost cash & stress up."
        elif c_type == "smart":
            self.fragility = max(0, self.fragility - 10)
            msg = "✅ SMART! Crisis averted."
        elif c_type == "safe":
            delta_cash = -50
            msg = "⚠️ SAFE. Paid premium."
        elif c_type == "gamble":
             if random.random() > 0.5:
                 msg = "🎲 WON! You got lucky."
             else:
                 self.debt += 1000
                 msg = "💀 LOST! Debt increased $1000."

        pay = random.randint(500, 1500) if self.salary == "var" else self.salary
        expenses = int((200 + (self.kids * 150) + self.alimony) * self.expense_mult)
        
        self.cash += (delta_cash + pay - expenses)
        self.history.insert(0, f"Wk {self.week}: {msg} (Net: ${delta_cash + pay - expenses})")
        
        if self.cash < 0: return "game_over", "BANKRUPT! You ran out of cash."
        if self.fragility >= self.fragility_cap: return "game_over", "MENTAL BREAKDOWN! Too much stress."

        self.week += 1
        self.current_scen = random.choice(self.deck)
        random.shuffle(self.shuffled_indices)
        self.start_time = time.time()
        
        return "next", msg

# --- STREAMLIT UI ---
st.set_page_config(page_title="Solvency RPG", layout="wide", page_icon="🛡️")

if "game" not in st.session_state: st.session_state.game = None
if "inspected" not in st.session_state: st.session_state.inspected = False

# TABS
tab1, tab2 = st.tabs(["🎮 Simulation", "📊 The Data Lab"])

with tab1:
    with st.sidebar:
        st.title("🛡️ SOLVENCY")
        if st.session_state.game is None:
            real = st.selectbox("Life Path", list(LIFE_PATHS.keys()))
            mood = st.selectbox("Economy", list(MOODS.keys()))
            if st.button("🚀 Start Simulation", type="primary"):
                st.session_state.game = LifeSim(real, mood)
                st.rerun()
        else:
            pay_amt = st.number_input("Pay Debt", min_value=0, step=100)
            if st.button("💸 Pay Bank"):
                game = st.session_state.game
                if pay_amt <= game.cash:
                    game.cash -= pay_amt
                    game.debt -= pay_amt
                    game.fragility = max(0, game.fragility - 5)
                    st.toast(f"Paid ${pay_amt}!", icon="✅")
                    st.rerun()
                else: st.toast("Insufficient Funds!", icon="❌")
            st.divider()
            if st.button("🏳️ Reset"):
                st.session_state.game = None
                st.rerun()

    if st.session_state.game:
        g = st.session_state.game
        scen = g.current_scen
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cash", f"${int(g.cash)}")
        c2.metric("Debt", f"${g.debt}")
        c3.metric("Fragility", f"{g.fragility}/{g.fragility_cap}")
        c4.metric("Week", g.week)
        st.progress(min(g.fragility / g.fragility_cap, 1.0), text="Breakdown Risk")

        st.divider()
        st.subheader(f"📍 {scen['title']}")
        st.markdown(" ".join([f"`{t}`" for t in scen['tags']]))
        st.info(scen['desc'])
        
        if st.session_state.inspected: st.warning(f"🕵️ RESEARCH: {scen['inspect']}")

        ops_source = scen["ops_i"] if st.session_state.inspected else scen["ops"]
        indices = g.shuffled_indices
        col_a, col_b, col_c = st.columns(3)
        
        def handle_click(btn_idx):
            status, msg = g.process_turn(btn_idx, st.session_state.inspected)
            if status == "inspect": st.session_state.inspected = True
            elif status == "game_over": 
                st.error(msg)
                st.session_state.game = None
            else:
                st.session_state.inspected = False
                if "TRAP" in msg: st.toast(msg, icon="❌")
                elif "SMART" in msg: st.toast(msg, icon="✅")
                else: st.toast(msg, icon="⚠️")

        with col_a:
            if st.button(ops_source[indices[0]][0], use_container_width=True):
                handle_click(0)
                st.rerun()
        with col_b:
            if st.button(ops_source[indices[1]][0], use_container_width=True):
                handle_click(1)
                st.rerun()
        with col_c:
            if st.button(ops_source[indices[2]][0], use_container_width=True):
                handle_click(2)
                st.rerun()

        with st.expander("📜 History", expanded=True):
            for line in g.history[:5]: st.write(line)
    else:
        st.info("👈 Use the sidebar to set up your Reality.")

with tab2:
    st.header("📊 The 'Sellable' Data")
    if st.session_state.game and len(st.session_state.game.data_log) > 0:
        df = pd.DataFrame(st.session_state.game.data_log)
        st.dataframe(df, use_container_width=True)
        
        impulse = len(df[df["Reaction Time (s)"] < 2.0])
        inspect_rate = round((len(df[df["Did Inspect"] == True]) / len(df)) * 100, 1)
        
        m1, m2 = st.columns(2)
        m1.metric("Impulse Clicks (<2s)", impulse)
        m2.metric("Inspection Rate", f"{inspect_rate}%")
    else:
        st.warning("Play the game to generate data.")
