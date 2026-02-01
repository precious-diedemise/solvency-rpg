import streamlit as st
import random
import time

# --- 1. CONFIGURATION: THE 4 YEARS (LEVELS) ---
STAGES = {
    1: {
        "name": "Freshman Year",
        "cash": 800, "debt": 15000, "stress_max": 50,
        "desc": "LEVEL 1: Survive the dorms. Avoid the 'Freshman 15' (Debt & Weight).",
        "inflation": 1.0
    },
    2: {
        "name": "Sophomore Year",
        "cash": 600, "debt": 25000, "stress_max": 60,
        "desc": "LEVEL 2: You moved off-campus. Rent and bills are real now.",
        "inflation": 1.2
    },
    3: {
        "name": "Junior Year",
        "cash": 400, "debt": 35000, "stress_max": 70,
        "desc": "LEVEL 3: Internships and burnout. The grind gets real.",
        "inflation": 1.5
    },
    4: {
        "name": "Senior Year",
        "cash": 200, "debt": 45000, "stress_max": 80,
        "desc": "LEVEL 4: Graduation panic. Job hunting. Loan repayment looms.",
        "inflation": 2.0
    }
}

# --- 2. THE MALL (PERMANENT UPGRADES) ---
SHOP_ITEMS = {
    "Noise Cancelling Headphones": {"cost": 150, "effect": "resist", "val": 5, "desc": "🎧 Focus better. -5 Stress from bad events."},
    "Second-Hand Bike": {"cost": 100, "effect": "transport", "val": 20, "desc": "🚲 Reduces transport costs significantly."},
    "Chegg/ChatGPT Sub": {"cost": 80, "effect": "luck", "val": 0.15, "desc": "🤖 Increases success chance of 'Gamble' choices by 15%."},
    "Meal Prep Containers": {"cost": 40, "effect": "food", "val": 10, "desc": "🍱 Reduces food costs by $10/week."},
}

# --- 3. MASSIVE STUDENT SCENARIO DB (40+ Cards) ---
MASTER_DB = [
    # --- LEVEL 1: FRESHMAN (Dorm Life, Social Pressure) ---
    {"lvl": 1, "title": "Textbook Racket", "desc": "Prof says you NEED the 5th Edition ($300).", "inspect": "⚠️ TRICK: The library has a copy on reserve.", "def_t": "Planned Obsolescence", "def_d": "Forcing upgrades for profit.", "ops": [("Buy New", "trap"), ("Library", "smart"), ("PDF", "gamble")], "ops_i": [("Buy New ($300)", "trap"), ("Library (Free)", "smart"), ("Rent ($40)", "safe")]},
    {"lvl": 1, "title": "Dorm Party", "desc": "Everyone is going. Cover is $20.", "inspect": "⚠️ FOMO: Social pressure is high.", "def_t": "Social Tax", "def_d": "Spending to maintain social standing.", "ops": [("Go Wild", "trap"), ("Stay In", "smart"), ("One Drink", "safe")], "ops_i": [("VIP ($100)", "trap"), ("Study", "smart"), ("Water Only ($20)", "safe")]},
    {"lvl": 1, "title": "Meal Plan", "desc": "Cafeteria food is gross. UberEats?", "inspect": "⚠️ MARKUP: Delivery adds 30% to cost.", "def_t": "Convenience Cost", "def_d": "Premium paid for saving effort.", "ops": [("Delivery", "trap"), ("Ramen", "smart"), ("Steal Fruit", "gamble")], "ops_i": [("Order ($30)", "trap"), ("Cook ($3)", "smart"), ("Sneak Food", "gamble")]},
    {"lvl": 1, "title": "The Roommate", "desc": "Roommate keeps eating your snacks.", "inspect": "⚠️ CONFLICT: A mini-fridge costs $50.", "def_t": "Asset Protection", "def_d": "Spending to secure your property.", "ops": [("Buy Fridge", "safe"), ("Yell", "trap"), ("Hide Food", "smart")], "ops_i": [("Fridge ($50)", "safe"), ("Fight", "trap"), ("Hide Under Bed", "smart")]},
    {"lvl": 1, "title": "Credit Card Stall", "desc": "Free T-shirt if you sign up for a card!", "inspect": "⚠️ TRAP: 25% APR and annual fees.", "def_t": "Predatory Lending", "def_d": "Lending with unfair terms.", "ops": [("Sign Up", "trap"), ("Walk Away", "smart"), ("Read Terms", "inspect")], "ops_i": [("Get Shirt (Debt)", "trap"), ("Walk Away", "smart"), ("Report", "safe")]},
    {"lvl": 1, "title": "Laundry Day", "desc": "Out of clean clothes. Machines cost $5.", "inspect": "⚠️ HACK: You can hand wash in the sink.", "def_t": "Labor Substitution", "def_d": "Trading time/effort to save money.", "ops": [("Pay $5", "safe"), ("Sink Wash", "smart"), ("Wear Dirty", "gamble")], "ops_i": [("Pay", "safe"), ("Sink Wash", "smart"), ("Febreze It", "gamble")]},
    {"lvl": 1, "title": "Sorority/Frat Rush", "desc": "Dues are $500/semester.", "inspect": "⚠️ NETWORK: Buying friends works sometimes.", "def_t": "Networking Cost", "def_d": "Pay-to-play social access.", "ops": [("Join", "trap"), ("Skip", "smart"), ("Parties Only", "gamble")], "ops_i": [("Pay Dues", "trap"), ("Join Clubs (Free)", "smart"), ("Sneak In", "gamble")]},
    {"lvl": 1, "title": "Sick Day", "desc": "Flu hitting hard. Urgent care?", "inspect": "⚠️ CAMPUS: Student Health Center is free.", "def_t": "Benefit Utilization", "def_d": "Using perks you already pay for.", "ops": [("Urgent Care", "safe"), ("Campus Clinic", "smart"), ("Sleep it off", "gamble")], "ops_i": [("Urgent Care ($100)", "safe"), ("Clinic (Free)", "smart"), ("Sleep", "gamble")]},

    # --- LEVEL 2: SOPHOMORE (Off Campus, Bills) ---
    {"lvl": 2, "title": "Utility Bill Shock", "desc": "AC left on. Bill is $200.", "inspect": "⚠️ SPLIT: You can argue roommates owe half.", "def_t": "Shared Liability", "def_d": "Joint responsibility for debt.", "ops": [("Pay All", "safe"), ("Fight Roommates", "gamble"), ("Payment Plan", "smart")], "ops_i": [("Pay All", "safe"), ("Demand Split", "gamble"), ("Call Utility", "smart")]},
    {"lvl": 2, "title": "Car Booted", "desc": "Parked in wrong zone. $100 fine.", "inspect": "⚠️ APPEAL: The sign was covered by a bush.", "def_t": "Bureaucracy", "def_d": "Navigating complex rules.", "ops": [("Pay Now", "safe"), ("Appeal", "smart"), ("Saw it off", "trap")], "ops_i": [("Pay ($100)", "safe"), ("Appeal w/ Photo", "smart"), ("Destroy Boot", "trap")]},
    {"lvl": 2, "title": "Grocery Inflation", "desc": "Eggs are $8. Meat is expensive.", "inspect": "⚠️ SUBSTITUTE: Frozen veggies/beans are cheap.", "def_t": "Substitution Effect", "def_d": "Switching to cheaper alternatives.", "ops": [("Buy Normal", "trap"), ("Buy Bulk", "smart"), ("Fast", "gamble")], "ops_i": [("Buy Normal ($100)", "trap"), ("Rice & Beans ($20)", "smart"), ("Starve", "gamble")]},
    {"lvl": 2, "title": "Concert Tickets", "desc": "Fav band in town. Tickets $150.", "inspect": "⚠️ SCALPERS: Prices drop 1 hour before show.", "def_t": "Dynamic Pricing", "def_d": "Prices changing based on demand.", "ops": [("Buy Now", "trap"), ("Wait", "smart"), ("Skip", "safe")], "ops_i": [("Buy ($150)", "trap"), ("Buy Last Min ($50)", "smart"), ("Listen Spotify", "safe")]},
    {"lvl": 2, "title": "Parking Pass", "desc": "Semester pass is $300.", "inspect": "⚠️ CALC: Park & Ride bus is free.", "def_t": "Sunk Cost", "def_d": "Paying for convenience you don't need.", "ops": [("Buy Pass", "trap"), ("Take Bus", "smart"), ("Risk Tickets", "gamble")], "ops_i": [("Buy Pass", "trap"), ("Bus (Free)", "smart"), ("Risk It", "gamble")]},
    {"lvl": 2, "title": "Subscription Audit", "desc": "You have Netflix, Hulu, HBO, Spotify...", "inspect": "⚠️ CHURN: Cancel and rotate them monthly.", "def_t": "Subscription Fatigue", "def_d": "Accumulating recurring small costs.", "ops": [("Keep All", "trap"), ("Cancel All", "smart"), ("Share Pwd", "gamble")], "ops_i": [("Pay ($80/mo)", "trap"), ("Rotate 1", "smart"), ("Use Mom's", "gamble")]},
    {"lvl": 2, "title": "Spring Break Trip", "desc": "Friends booking Airbnb. $400 share.", "inspect": "⚠️ BUDGET: You have $200 in bank.", "def_t": "Living Beyond Means", "def_d": "Spending more than you earn.", "ops": [("Credit Card", "trap"), ("Say No", "smart"), ("Drive Self", "safe")], "ops_i": [("Debt", "trap"), ("Stay Home", "smart"), ("Budget Trip", "safe")]},

    # --- LEVEL 3: JUNIOR (Career, Internships) ---
    {"lvl": 3, "title": "Unpaid Internship", "desc": "Great resume booster. $0 pay.", "inspect": "⚠️ ROI: Leads to high paying job?", "def_t": "Opportunity Cost", "def_d": "Loss of income from paid work.", "ops": [("Take it", "gamble"), ("Keep Job", "safe"), ("Negotiate", "smart")], "ops_i": [("Work Free", "gamble"), ("Wait Tables", "safe"), ("Ask Stipend", "smart")]},
    {"lvl": 3, "title": "Interview Suit", "desc": "Old suit doesn't fit. Need new one.", "inspect": "⚠️ THRIFT: Rich neighborhoods have great Goodwill stores.", "def_t": "Signaling", "def_d": "Visual cues of status.", "ops": [("Buy Designer", "trap"), ("Thrift", "smart"), ("Borrow", "safe")], "ops_i": [("Mall ($300)", "trap"), ("Thrift ($30)", "smart"), ("Borrow Friend's", "safe")]},
    {"lvl": 3, "title": "Laptop Crash", "desc": "Blue screen of death. Mid-terms.", "inspect": "⚠️ REPAIR: Campus IT fixes software free.", "def_t": "Repairability", "def_d": "Ease of fixing vs replacing.", "ops": [("Buy New Mac", "trap"), ("Campus IT", "smart"), ("YouTube Fix", "gamble")], "ops_i": [("Buy ($1200)", "trap"), ("IT Help", "smart"), ("DIY", "gamble")]},
    {"lvl": 3, "title": "LinkedIn Premium", "desc": "$40/mo to see who viewed you.", "inspect": "⚠️ VALUE: Recruiters don't care if you have Premium.", "def_t": "Freemium", "def_d": "Paying for features you don't need.", "ops": [("Subscribe", "trap"), ("Free Trial", "smart"), ("Ignore", "safe")], "ops_i": [("Pay", "trap"), ("Cancel Trial", "smart"), ("Ignore", "safe")]},
    {"lvl": 3, "title": "Coffee Habit", "desc": "Starbucks daily adds up to $150/mo.", "inspect": "⚠️ LATTE FACTOR: Small daily costs compound.", "def_t": "Compound Cost", "def_d": "Small leaks sinking the ship.", "ops": [("Keep Buying", "trap"), ("Brew Home", "smart"), ("Cut Back", "safe")], "ops_i": [("Buy", "trap"), ("Thermos", "smart"), ("Every other day", "safe")]},

    # --- LEVEL 4: SENIOR (Graduation, Loans) ---
    {"lvl": 4, "title": "Graduation Robes", "desc": "School store selling gown for $100.", "inspect": "⚠️ MARKET: Seniors are selling used ones for $20.", "def_t": "Secondary Market", "def_d": "Buying used goods cheaper.", "ops": [("Buy New", "trap"), ("Buy Used", "smart"), ("Rent", "safe")], "ops_i": [("Store ($100)", "trap"), ("eBay ($20)", "smart"), ("Rent", "safe")]},
    {"lvl": 4, "title": "Job Offer A vs B", "desc": "A: High Pay/High Stress. B: Low Pay/Chill.", "inspect": "⚠️ BURNOUT: High stress leads to medical bills.", "def_t": "Work-Life Balance", "def_d": "Trade-off between money and health.", "ops": [("Job A", "gamble"), ("Job B", "safe"), ("Negotiate A", "smart")], "ops_i": [("Take A", "gamble"), ("Take B", "safe"), ("Negotiate A", "smart")]},
    {"lvl": 4, "title": "Loan Exit Counseling", "desc": "Pick a plan. Standard or Income-Driven?", "inspect": "⚠️ MATH: Income-Driven lowers payments but increases total interest.", "def_t": "Amortization", "def_d": "Paying off debt over time.", "ops": [("Standard", "safe"), ("Income Driven", "smart"), ("Defer", "trap")], "ops_i": [("Standard (Fast)", "safe"), ("IDR (Flex)", "smart"), ("Defer (Bad)", "trap")]},
    {"lvl": 4, "title": "Moving Costs", "desc": "Job is in new city. Mover quote: $2,000.", "inspect": "⚠️ RELOCATION: Ask employer to cover it.", "def_t": "Relocation Package", "def_d": "Employer paying moving costs.", "ops": [("Pay It", "trap"), ("Ask Boss", "smart"), ("U-Haul", "safe")], "ops_i": [("Pay", "trap"), ("Negotiate", "smart"), ("DIY ($500)", "safe")]},
    {"lvl": 4, "title": "Networking Dinner", "desc": "Fancy dinner with alumni. $80 plate.", "inspect": "⚠️ ROI: One job lead pays for 100 dinners.", "def_t": "Investment", "def_d": "Spending now for future gain.", "ops": [("Go", "smart"), ("Skip", "trap"), ("Coffee Instead", "safe")], "ops_i": [("Go ($80)", "smart"), ("Skip", "trap"), ("Ask for Coffee", "safe")]},
]

# --- 4. GAME ENGINE ---
class StudentSim:
    def __init__(self):
        self.level = 1
        self.set_level_stats()
        
        self.week = 1
        self.lifelines = 3
        self.inventory = []
        self.history = []
        self.intel = []
        self.buffs = {"resist": 0, "luck": 0.0, "transport": 0, "food": 0}
        
        # Interaction ID for Streamlit button fixes
        self.uid_salt = 0
        
        self.build_deck()

    def set_level_stats(self):
        cfg = STAGES[self.level]
        self.cash = cfg["cash"]
        self.debt = cfg["debt"]
        self.stress = 20 # Start with some stress
        self.stress_max = cfg["stress_max"]
        self.desc = cfg["desc"]
        self.inflation = cfg["inflation"]

    def build_deck(self):
        # Filter DB by current Level + Universal cards (Lvl 0 if we had them)
        self.deck = [s for s in MASTER_DB if s["lvl"] == self.level]
        random.shuffle(self.deck)
        self.draw_card()

    def draw_card(self):
        if not self.deck:
            return "level_complete"
        self.current_scen = self.deck.pop(0) # Remove from deck (No Repeats)
        self.indices = [0, 1, 2]
        random.shuffle(self.indices)
        return "ok"

    def process_turn(self, choice_idx, inspected):
        scen = self.current_scen
        
        # LIFELINE
        if choice_idx == 99:
            self.lifelines -= 1
            self.stress = max(0, self.stress - 30)
            status = self.draw_card()
            if status == "level_complete": return "level_up", "You survived the semester!"
            return "next", "☎️ LIFELINE: You called mom. She fixed it. Stress -30."

        real_idx = self.indices[choice_idx]
        
        # INSPECT
        if real_idx == 1:
            return "inspect", scen["inspect"]

        c_type = scen["ops"][real_idx][1]
        
        msg = ""
        d_cash = 0
        d_stress = 0
        
        # BUFFS
        luck = self.buffs["luck"]
        resist = self.buffs["resist"]
        
        if c_type == "trap":
            d_cash = -random.randint(100, 300) * self.inflation
            d_stress = 20 - resist
            msg = "❌ TRAP! Expensive mistake."
        elif c_type == "smart":
            d_stress = -10
            msg = "🧠 SMART! Good handling."
        elif c_type == "safe":
            d_cash = -50 * self.inflation
            d_stress = -5
            msg = "🛡️ SAFE. Cost money, saved stress."
        elif c_type == "gamble":
            if random.random() < (0.5 + luck):
                d_stress = -20
                msg = "🎲 WON! Lucky break."
            else:
                d_cash = -200 * self.inflation
                d_stress = 10
                msg = "💀 LOST! Bad luck."

        # APPLY BUFFS (Discounts)
        if "transport" in scen["title"].lower(): d_cash += self.buffs["transport"]
        if "food" in scen["title"].lower(): d_cash += self.buffs["food"]
        
        # Weekly Drain (Rent/Food)
        weekly_cost = (100 * self.inflation) - self.buffs["food"]
        
        self.cash += (d_cash - weekly_cost)
        self.stress = min(100, max(0, self.stress + d_stress))
        
        self.history.insert(0, f"Wk {self.week}: {msg}")
        
        # INTEL
        intel_data = {"t": scen["def_t"], "d": scen["def_d"]}
        if intel_data not in self.intel: self.intel.append(intel_data)

        # CHECK DEATH
        if self.stress >= self.stress_max: return "game_over", "🤯 BURNOUT! You dropped out due to stress."
        if self.cash < -500: return "game_over", "💸 BANKRUPT! You can't pay tuition."

        # NEXT TURN
        self.week += 1
        status = self.draw_card()
        
        if status == "level_complete":
            if self.level < 4:
                return "level_up", f"🎉 YEAR {self.level} COMPLETED!"
            else:
                return "win", "🎓 YOU GRADUATED! You are Debt Smart."
                
        return "next", msg

    def buy_item(self, item_name):
        item = SHOP_ITEMS[item_name]
        if self.cash >= item["cost"]:
            self.cash -= item["cost"]
            self.inventory.append(item_name)
            
            if item["effect"] == "resist": self.buffs["resist"] += item["val"]
            elif item["effect"] == "luck": self.buffs["luck"] += item["val"]
            elif item["effect"] == "transport": self.buffs["transport"] += item["val"]
            elif item["effect"] == "food": self.buffs["food"] += item["val"]
            return True
        return False
        
    def advance_level(self):
        self.level += 1
        self.set_level_stats()
        self.build_deck()
        self.week = 1

# --- 5. UI CONFIG ---
st.set_page_config(page_title="Student Survival", page_icon="🎓", layout="wide")
st.markdown("""
<style>
    div.stButton > button { width: 100%; height: 60px; border-radius: 12px; font-weight: bold; }
    .stMetric { background-color: #111; padding: 10px; border-radius: 8px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

if "game" not in st.session_state: st.session_state.game = None
if "inspected" not in st.session_state: st.session_state.inspected = False
if "uid" not in st.session_state: st.session_state.uid = 0

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎓 STUDENT SURVIVAL")
    
    if st.session_state.game is None:
        st.info("Can you survive 4 years of college without going broke or burning out?")
        if st.button("🚀 Start Freshman Year"):
            st.session_state.game = StudentSim()
            st.rerun()
    else:
        g = st.session_state.game
        st.markdown(f"### Year {g.level}: {STAGES[g.level]['name']}")
        st.progress(g.stress / g.stress_max, f"Stress: {g.stress}/{g.stress_max}")
        
        st.divider()
        st.markdown("### 🛍️ Campus Store")
        for name, item in SHOP_ITEMS.items():
            if name not in g.inventory:
                if st.button(f"{name} (${item['cost']})", help=item['desc']):
                    if g.buy_item(name):
                        st.toast(f"Bought {name}!", icon="🛍️")
                        st.rerun()
                    else: st.toast("Not enough cash!", icon="❌")
        
        st.divider()
        if st.button("🛑 Dropout (Quit)"):
            st.session_state.game = None
            st.rerun()

# --- MAIN AREA ---
if st.session_state.game:
    g = st.session_state.game
    
    # METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash", f"${int(g.cash)}")
    c2.metric("Debt", f"${g.debt}", delta_color="inverse")
    c3.metric("Inflation", f"{int((g.inflation-1)*100)}%")
    c4.metric("Week", g.week)

    # TABS
    tab1, tab2 = st.tabs(["🎮 Decisions", "🧠 Notebook"])

    with tab1:
        if hasattr(g, 'current_scen'):
            scen = g.current_scen
            st.divider()
            st.markdown(f"#### 📍 {scen['title']}")
            st.info(scen['desc'])
            
            if st.session_state.inspected: st.warning(f"🕵️ RESEARCH: {scen['inspect']}")

            # BUTTONS (Fixed ID System)
            ops = scen["ops_i"] if st.session_state.inspected else scen["ops"]
            idx = g.indices
            col_a, col_b, col_c = st.columns(3)
            
            # Unique Key for every render
            key_id = f"{g.level}_{g.week}_{st.session_state.uid}"
            
            def click(i):
                st.session_state.uid += 1
                res, txt = g.process_turn(i, st.session_state.inspected)
                
                if res == "inspect": st.session_state.inspected = True
                elif res == "level_up":
                    st.balloons()
                    st.success(txt)
                    time.sleep(2)
                    g.advance_level()
                    st.rerun()
                elif res == "win":
                    st.balloons()
                    st.success(txt)
                    time.sleep(5)
                    st.session_state.game = None
                    st.rerun()
                elif res == "game_over":
                    st.error(txt)
                    st.snow()
                    time.sleep(4)
                    st.session_state.game = None
                    st.rerun()
                else:
                    st.session_state.inspected = False
                    if "TRAP" in txt: st.toast(txt, icon="❌")
                    if "SMART" in txt: st.toast(txt, icon="🧠")

            with col_a:
                if st.button(ops[idx[0]][0], key=f"a_{key_id}", use_container_width=True): click(0); st.rerun()
            with col_b:
                if st.button(ops[idx[1]][0], key=f"b_{key_id}", use_container_width=True): click(1); st.rerun()
            with col_c:
                if st.button(ops[idx[2]][0], key=f"c_{key_id}", use_container_width=True): click(2); st.rerun()

            st.divider()
            if g.lifelines > 0:
                if st.button(f"☎️ CALL MOM (Lifelines: {g.lifelines})", key=f"lifeline_{key_id}"):
                    click(99); st.rerun()
        else:
            st.error("Level Complete! Loading next year...")

    with tab2:
        if not g.intel: st.info("Play to learn financial terms!")
        else:
            for i in g.intel:
                with st.expander(f"📌 {i['t']}"): st.write(i['d'])
else:
    st.markdown("# Welcome to Student Survival")
    st.markdown("### The 4-Year Challenge")
    st.markdown("Most students graduate with debt. Can you graduate with **Net Worth**?")
