import streamlit as st
import random
import time

# --- 1. CONFIGURATION ---
WEEKS_PER_LEVEL = 10 

# --- 2. THE MALL ---
SHOP_ITEMS = {
    "Noise Cancelling Headphones": {"cost": 150, "effect": "resist", "val": 5, "desc": "🎧 -5 Stress from bad events."},
    "Second-Hand Bike": {"cost": 100, "effect": "transport", "val": 20, "desc": "🚲 Reduces transport costs."},
    "Chegg/AI Subscription": {"cost": 80, "effect": "luck", "val": 0.15, "desc": "🤖 +15% Luck on Gambles."},
}

# --- 3. LIFESTYLE OPTIONS (YOU CONTROL THIS) ---
HOUSING_OPTS = {
    "Mom's Basement": {"cost": 0, "stress": 10, "desc": "Free, but zero privacy."},
    "Shared Dorm": {"cost": 100, "stress": 0, "desc": "Standard student living."},
    "Studio Apt": {"cost": 300, "stress": -5, "desc": "Expensive, but peaceful."}
}

JOB_OPTS = {
    "Unemployed": {"pay": 0, "stress": -5, "desc": "Focus on school. Low stress, no money."},
    "Library Aide": {"pay": 100, "stress": 5, "desc": "Easy work, low pay."},
    "Barista": {"pay": 200, "stress": 15, "desc": "Fast paced, decent cash."},
    "Bartender": {"pay": 350, "stress": 25, "desc": "High cash, EXTREME stress."}
}

FOOD_OPTS = {
    "Beans & Rice": {"cost": 20, "stress": 10, "desc": "Survival mode. High stress."},
    "Home Cooking": {"cost": 60, "stress": 0, "desc": "Balanced and standard."},
    "Takeout/Delivery": {"cost": 150, "stress": -5, "desc": "Convenient but pricey."}
}

# --- 4. SCENARIO POOL ---
MASTER_DB = [
    # TYPE: GAMBLE_STRESS
    {"title": "Subscription Audit", "desc": "You have Netflix, Hulu, HBO, Spotify...", "inspect": "⚠️ CHURN: You pay $80/mo. Cancel and rotate them.", "def_t": "Subscription Fatigue", "def_d": "Accumulating recurring small costs.", 
     "ops": [("Keep All", "trap"), ("Audit Bills", "inspect"), ("Use Mom's", "gamble_stress")], 
     "ops_i": [("Pay ($80/mo)", "trap"), ("Cancel All", "smart"), ("Use Mom's", "gamble_stress")]},

    # TYPE: STANDARD SCENARIOS
    {"title": "LinkedIn Premium", "desc": "Pop-up: 'See who viewed your profile' ($40/mo).", "inspect": "⚠️ VANITY: Recruiters will message you if they want you.", "def_t": "Vanity Metric", "def_d": "Data that looks good but means nothing.", 
     "ops": [("Subscribe", "trap"), ("Check Price", "inspect"), ("Ignore", "smart")], 
     "ops_i": [("Subscribe ($40)", "trap"), ("Free Trial", "gamble_stress"), ("Ignore ($0)", "smart")]},

    {"title": "Textbook Racket", "desc": "Prof says you NEED the 5th Edition ($300).", "inspect": "⚠️ TRICK: The library has a copy on reserve.", "def_t": "Planned Obsolescence", "def_d": "Forcing upgrades for profit.", 
     "ops": [("Buy New", "trap"), ("Check Library", "inspect"), ("PDF", "gamble")], 
     "ops_i": [("Buy New ($300)", "trap"), ("Use Reserve (Free)", "smart"), ("Rent ($40)", "safe")]},

    {"title": "Dorm Party", "desc": "Everyone is going. Cover is $20.", "inspect": "⚠️ FOMO: Social pressure is high.", "def_t": "Social Tax", "def_d": "Spending to maintain social standing.", 
     "ops": [("Go Wild", "trap"), ("Check Cover", "inspect"), ("One Drink", "safe")], 
     "ops_i": [("VIP ($100)", "trap"), ("Stay In ($0)", "smart"), ("Water Only ($20)", "safe")]},

    {"title": "The Roommate", "desc": "Roommate keeps eating your snacks.", "inspect": "⚠️ CONFLICT: A mini-fridge costs $50.", "def_t": "Asset Protection", "def_d": "Spending to secure your property.", 
     "ops": [("Buy Fridge", "safe"), ("Check Rules", "inspect"), ("Hide Food", "smart")], 
     "ops_i": [("Fridge ($50)", "safe"), ("Yell at them", "trap"), ("Hide Under Bed", "smart")]},

    {"title": "Credit Card Stall", "desc": "Free T-shirt if you sign up for a card!", "inspect": "⚠️ TRAP: 25% APR and annual fees.", "def_t": "Predatory Lending", "def_d": "Lending with unfair terms.", 
     "ops": [("Sign Up", "trap"), ("Read Terms", "inspect"), ("Walk Away", "smart")], 
     "ops_i": [("Get Shirt (Debt)", "trap"), ("Read Fine Print", "smart"), ("Walk Away", "smart")]},

    {"title": "Laundry Day", "desc": "Out of clean clothes. Machines cost $5.", "inspect": "⚠️ HACK: You can hand wash in the sink.", "def_t": "Labor Substitution", "def_d": "Trading time/effort to save money.", 
     "ops": [("Pay $5", "safe"), ("Check Sink", "inspect"), ("Wear Dirty", "gamble_stress")], 
     "ops_i": [("Pay", "safe"), ("Sink Wash", "smart"), ("Febreze It", "gamble_stress")]},

    {"title": "Utility Bill Shock", "desc": "AC left on. Bill is $200.", "inspect": "⚠️ SPLIT: You can argue roommates owe half.", "def_t": "Shared Liability", "def_d": "Joint responsibility for debt.", 
     "ops": [("Pay All", "safe"), ("Check Usage", "inspect"), ("Fight Roommates", "gamble_stress")], 
     "ops_i": [("Pay All", "safe"), ("Demand Split", "gamble_stress"), ("Call Utility", "smart")]},

    {"title": "Car Booted", "desc": "Parked in wrong zone. $100 fine.", "inspect": "⚠️ APPEAL: The sign was covered by a bush.", "def_t": "Bureaucracy", "def_d": "Navigating complex rules.", 
     "ops": [("Pay Now", "safe"), ("Check Sign", "inspect"), ("Saw it off", "trap")], 
     "ops_i": [("Pay ($100)", "safe"), ("Appeal w/ Photo", "smart"), ("Destroy Boot", "trap")]},

    {"title": "Grocery Inflation", "desc": "Eggs are $8. Meat is expensive.", "inspect": "⚠️ SUBSTITUTE: Frozen veggies/beans are cheap.", "def_t": "Substitution Effect", "def_d": "Switching to cheaper alternatives.", 
     "ops": [("Buy Normal", "trap"), ("Check Sales", "inspect"), ("Fast", "gamble")], 
     "ops_i": [("Buy Normal ($100)", "trap"), ("Rice & Beans ($20)", "smart"), ("Starve", "gamble")]},

    {"title": "Concert Tickets", "desc": "Fav band in town. Tickets $150.", "inspect": "⚠️ SCALPERS: Prices drop 1 hour before show.", "def_t": "Dynamic Pricing", "def_d": "Prices changing based on demand.", 
     "ops": [("Buy Now", "trap"), ("Check StubHub", "inspect"), ("Skip", "safe")], 
     "ops_i": [("Buy ($150)", "trap"), ("Buy Last Min ($50)", "smart"), ("Listen Spotify", "safe")]},

    {"title": "Unpaid Internship", "desc": "Great resume booster. $0 pay.", "inspect": "⚠️ ROI: Leads to high paying job?", "def_t": "Opportunity Cost", "def_d": "Loss of income from paid work.", 
     "ops": [("Take it", "gamble"), ("Check Reviews", "inspect"), ("Keep Job", "safe")], 
     "ops_i": [("Work Free", "gamble"), ("Read Glassdoor", "smart"), ("Wait Tables", "safe")]},

    {"title": "Laptop Crash", "desc": "Blue screen of death. Mid-terms.", "inspect": "⚠️ REPAIR: Campus IT fixes software free.", "def_t": "Repairability", "def_d": "Ease of fixing vs replacing.", 
     "ops": [("Buy New Mac", "trap"), ("Check IT", "inspect"), ("YouTube Fix", "gamble")], 
     "ops_i": [("Buy ($1200)", "trap"), ("IT Help", "smart"), ("DIY", "gamble")]},

    {"title": "Coffee Habit", "desc": "Starbucks daily adds up to $150/mo.", "inspect": "⚠️ LATTE FACTOR: Small daily costs compound.", "def_t": "Compound Cost", "def_d": "Small leaks sinking the ship.", 
     "ops": [("Keep Buying", "trap"), ("Check Budget", "inspect"), ("Cut Back", "safe")], 
     "ops_i": [("Buy ($150)", "trap"), ("Thermos ($0)", "smart"), ("Every other day ($70)", "safe")]},
]

# --- 5. GAME ENGINE ---
class EndlessSim:
    def __init__(self):
        self.cash = 1000
        self.debt = 10000
        self.stress = 20
        self.stress_max = 100
        self.level = 1
        self.week = 1
        self.inflation = 1.0 
        
        # User Choices (Defaults)
        self.mode_housing = "Shared Dorm"
        self.mode_job = "Unemployed"
        self.mode_food = "Home Cooking"
        
        self.inventory = []
        self.history = []
        self.intel = []
        self.receipt = None
        
        self.buffs = {"resist": 0, "luck": 0.0, "transport": 0}
        
        self.full_deck = MASTER_DB.copy()
        random.shuffle(self.full_deck)
        self.draw_card()

    def get_difficulty_desc(self):
        if self.level == 1: return "Normal"
        if self.level == 2: return "Hard (Prices +20%)"
        if self.level == 3: return "Expert (Prices +40%)"
        if self.level >= 4: return "NIGHTMARE (Prices Skyrocketing)"

    def draw_card(self):
        if not self.full_deck:
            self.full_deck = MASTER_DB.copy()
            random.shuffle(self.full_deck)
        self.current_scen = self.full_deck.pop(0)
        self.indices = [0, 1, 2]
        random.shuffle(self.indices)

    def process_turn(self, choice_idx):
        scen = self.current_scen
        real_idx = self.indices[choice_idx]
        
        c_type = scen["ops"][real_idx][1] if not st.session_state.inspected else scen["ops_i"][real_idx][1]
        
        d_cash = 0
        d_stress = 0
        msg = ""
        
        # --- 1. EVENT CHOICE LOGIC ---
        if c_type == "trap":
            d_cash = -random.randint(100, 300) * self.inflation
            d_stress = 20 - self.buffs["resist"]
            msg = "❌ TRAP! Expensive."
        elif c_type == "smart":
            d_stress = -10
            msg = "🧠 SMART! Good choice."
        elif c_type == "safe":
            d_cash = -50 * self.inflation
            d_stress = -5
            msg = "🛡️ SAFE. Small cost."
        
        elif c_type == "gamble":
            if random.random() < (0.5 + self.buffs["luck"]):
                d_stress = -20
                msg = "🎲 WON! Lucky break."
            else:
                d_cash = -200 * self.inflation
                d_stress = 10
                msg = "💀 LOST! Money down the drain."

        elif c_type == "gamble_stress":
            if random.random() < (0.5 + self.buffs["luck"]):
                d_stress = -20
                msg = "🎲 WON! It worked!"
            else:
                d_cash = 0 
                d_stress = 25 
                msg = "💀 FAIL! Frustrating!"

        if "transport" in scen["title"].lower(): d_cash += self.buffs["transport"]
        
        # --- 2. LIFESTYLE CALCULATIONS (The "Control" Part) ---
        
        # GET SETTINGS
        job_data = JOB_OPTS[self.mode_job]
        house_data = HOUSING_OPTS[self.mode_housing]
        food_data = FOOD_OPTS[self.mode_food]
        
        # INCOME
        income = job_data["pay"] * self.inflation # Pay scales with inflation? Maybe. Let's say yes for balance.
        
        # EXPENSES
        rent_cost = house_data["cost"] * self.inflation
        food_cost = food_data["cost"] * self.inflation
        fixed_expenses = rent_cost + food_cost
        
        # STRESS IMPACT
        lifestyle_stress = job_data["stress"] + house_data["stress"] + food_data["stress"]
        
        # --- 3. FINAL MATH ---
        net_change = d_cash + income - fixed_expenses
        
        self.cash += net_change
        self.stress = min(100, max(0, self.stress + d_stress + lifestyle_stress))
        
        # --- 4. RECEIPT ---
        self.receipt = {
            "desc": msg,
            "choice": int(d_cash),
            "income": int(income),
            "expenses": int(fixed_expenses),
            "total": int(net_change)
        }
        
        self.history.insert(0, f"Wk {self.week}: {msg} [Net: ${int(net_change)}]")
        
        intel_data = {"t": scen["def_t"], "d": scen["def_d"]}
        if intel_data not in self.intel: self.intel.append(intel_data)

        if self.stress >= self.stress_max:
            st.session_state.game_over = True
            st.session_state.end_msg = f"🤯 BURNOUT! You lasted {self.week + ((self.level-1)*10)} weeks."
            return
        if self.cash < -1000:
            st.session_state.game_over = True
            st.session_state.end_msg = f"💸 BANKRUPT! You lasted {self.week + ((self.level-1)*10)} weeks."
            return

        self.week += 1
        if self.week > WEEKS_PER_LEVEL:
            self.level += 1
            self.week = 1
            self.inflation += 0.2
            st.session_state.level_up = True
            
        st.session_state.inspected = False
        self.draw_card()

    def buy_item(self, item_name):
        item = SHOP_ITEMS[item_name]
        if self.cash >= item["cost"]:
            self.cash -= item["cost"]
            self.inventory.append(item_name)
            if item["effect"] == "resist": self.buffs["resist"] += item["val"]
            elif item["effect"] == "luck": self.buffs["luck"] += item["val"]
            elif item["effect"] == "transport": self.buffs["transport"] += item["val"]
            return True
        return False

# --- 6. UI SETUP ---
st.set_page_config(page_title="Student Survival: Control", page_icon="🎛️", layout="wide")
st.markdown("""<style>div.stButton > button { width: 100%; height: 60px; border-radius: 12px; font-weight: bold; }</style>""", unsafe_allow_html=True)

if "game" not in st.session_state: st.session_state.game = None
if "inspected" not in st.session_state: st.session_state.inspected = False
if "game_over" not in st.session_state: st.session_state.game_over = False
if "level_up" not in st.session_state: st.session_state.level_up = False
if "uid" not in st.session_state: st.session_state.uid = 0 

if st.session_state.game is None:
    st.title("🎛️ STUDENT SURVIVAL: CONTROL")
    st.info("You control your job, your home, and your diet. Can you balance the budget?")
    if st.button("🚀 Start Run"):
        st.session_state.game = EndlessSim()
        st.rerun()

elif st.session_state.game_over:
    st.error(st.session_state.end_msg)
    st.metric("Final Level", st.session_state.game.level)
    st.snow()
    if st.button("Try Again"):
        st.session_state.game = None
        st.session_state.game_over = False
        st.rerun()

elif st.session_state.level_up:
    g = st.session_state.game
    st.success(f"🚀 LEVEL {g.level} REACHED! Inflation is now {int((g.inflation-1)*100)}%")
    st.balloons()
    if st.button("Continue"):
        st.session_state.level_up = False
        st.rerun()

else:
    g = st.session_state.game
    
    with st.sidebar:
        st.title(f"Level {g.level}")
        st.caption(g.get_difficulty_desc())
        
        # --- LIFESTYLE DASHBOARD ---
        st.divider()
        st.markdown("### 🎛️ Lifestyle Dashboard")
        
        # 1. JOB SELECTOR
        new_job = st.selectbox("💼 Income Source", list(JOB_OPTS.keys()), index=list(JOB_OPTS.keys()).index(g.mode_job))
        if new_job != g.mode_job: g.mode_job = new_job; st.rerun()
        
        # 2. HOUSING SELECTOR
        new_house = st.selectbox("🏠 Housing", list(HOUSING_OPTS.keys()), index=list(HOUSING_OPTS.keys()).index(g.mode_housing))
        if new_house != g.mode_housing: g.mode_housing = new_house; st.rerun()
        
        # 3. FOOD SELECTOR
        new_food = st.selectbox("🍔 Food Plan", list(FOOD_OPTS.keys()), index=list(FOOD_OPTS.keys()).index(g.mode_food))
        if new_food != g.mode_food: g.mode_food = new_food; st.rerun()
        
        # --- REAL TIME BUDGET PREVIEW ---
        j = JOB_OPTS[g.mode_job]
        h = HOUSING_OPTS[g.mode_housing]
        f = FOOD_OPTS[g.mode_food]
        
        est_inc = j["pay"] * g.inflation
        est_exp = (h["cost"] + f["cost"]) * g.inflation
        est_net = est_inc - est_exp
        est_stress = j["stress"] + h["stress"] + f["stress"]
        
        st.markdown(f"""
        **Weekly Budget:**
        * 🟢 Income: +${int(est_inc)}
        * 🔴 Expenses: -${int(est_exp)}
        * **Net Flow:** :{'green' if est_net >= 0 else 'red'}[${int(est_net)}]
        
        **Weekly Stress:** {est_stress:+}
        """)
        
        st.divider()
        st.progress(g.stress / g.stress_max, f"Stress: {g.stress}/{g.stress_max}")
        
        st.markdown("### 🛍️ The Mall")
        for name, item in SHOP_ITEMS.items():
            if name not in g.inventory:
                if st.button(f"{name} (${item['cost']})", help=item['desc']):
                    if g.buy_item(name): st.rerun()
                    else: st.toast("Not enough cash!", icon="❌")
        
        if st.button("🛑 Give Up"):
            st.session_state.game = None
            st.rerun()

    # --- TOP METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash", f"${int(g.cash)}")
    c2.metric("Debt", f"${g.debt}", delta_color="inverse")
    c3.metric("Inflation", f"{int((g.inflation-1)*100)}%")
    c4.metric("Week", f"{g.week}/10")
    
    # --- THE RECEIPT ---
    if g.receipt:
        st.divider()
        r = g.receipt
        r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns(5)
        r_col1.markdown(f"**Choice:** {r['choice']}")
        r_col2.markdown(f"**Income:** :green[+{r['income']}]")
        r_col3.markdown(f"**Bills:** :red[-{r['expenses']}]")
        
        total_color = "green" if r['total'] >= 0 else "red"
        r_col4.markdown(f"**NET:** :{total_color}[${r['total']}]")
        r_col5.caption(f"Last: {r['desc']}")
    st.divider()

    # --- GAME TABS ---
    tab1, tab2 = st.tabs(["🎮 Play", "🧠 Notebook"])
    
    with tab1:
        scen = g.current_scen
        st.markdown(f"#### 📍 {scen['title']}")
        st.info(scen['desc'])
        
        if st.session_state.inspected: 
            st.warning(f"🕵️ RESEARCH: {scen['inspect']}")

        ops = scen["ops_i"] if st.session_state.inspected else scen["ops"]
        idx = g.indices
        
        col_a, col_b, col_c = st.columns(3)
        key_base = f"{g.level}_{g.week}_{st.session_state.uid}"
        
        def handle_click(i):
            st.session_state.uid += 1
            clicked_op_type = ops[i][1]
            if clicked_op_type == "inspect":
                 st.session_state.inspected = True
            else:
                 g.process_turn(i)
            st.rerun()

        with col_a:
            if st.button(ops[idx[0]][0], key=f"a_{key_base}", use_container_width=True): handle_click(idx[0])
        with col_b:
            if st.button(ops[idx[1]][0], key=f"b_{key_base}", use_container_width=True): handle_click(idx[1])
        with col_c:
            if st.button(ops[idx[2]][0], key=f"c_{key_base}", use_container_width=True): handle_click(idx[2])

    with tab2:
        if not g.intel: st.info("Play to learn!")
        else:
            for i in g.intel:
                with st.expander(f"📌 {i['t']}"): st.write(i['d'])
