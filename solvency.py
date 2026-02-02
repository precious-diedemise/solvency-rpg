import streamlit as st
import random
import time

# --- 1. CONFIGURATION ---
WEEKS_PER_LEVEL = 12 

# --- 2. THE MALL ---
SHOP_ITEMS = {
    "Noise Cancelling Headphones": {"cost": 150, "effect": "resist", "val": 5, "desc": "🎧 -5 Stress from bad events."},
    "Second-Hand Bike": {"cost": 100, "effect": "transport", "val": 20, "desc": "🚲 Reduces transport costs."},
    "Chegg/AI Subscription": {"cost": 80, "effect": "luck", "val": 0.15, "desc": "🤖 +15% Luck on Gambles."},
}

# --- 3. STARTING OPTIONS (FUNDING) ---
FUNDING_OPTS = {
    "Full Scholarship": {"debt": 0, "desc": "Lucky! You start with $0 Debt."},
    "Partial Loan": {"debt": 10000, "desc": "Standard Federal Loans."},
    "Private Loans": {"debt": 40000, "desc": "High interest, high stress start."}
}

# --- 4. LIFESTYLE OPTIONS ---
HOUSING_OPTS = {
    "Mom's Basement": {"cost": 0, "stress": 10, "desc": "Free, but zero privacy (+10 Stress)."},
    "Shared Dorm": {"cost": 100, "stress": 0, "desc": "Standard student living."},
    "Studio Apt": {"cost": 300, "stress": -5, "desc": "Expensive, but peaceful (-5 Stress)."}
}

JOB_OPTS = {
    "Unemployed": {"pay": 0, "stress": -5, "desc": "Focus on school. Low stress."},
    "Library Aide": {"pay": 100, "stress": 5, "desc": "Easy work, low pay."},
    "Barista": {"pay": 200, "stress": 15, "desc": "Fast paced, decent cash."},
    "Bartender": {"pay": 350, "stress": 25, "desc": "High cash, EXTREME stress."}
}

FOOD_OPTS = {
    "Beans & Rice": {"cost": 20, "stress": 10, "desc": "Survival mode (+10 Stress)."},
    "Home Cooking": {"cost": 60, "stress": 0, "desc": "Balanced and standard."},
    "Takeout/Delivery": {"cost": 150, "stress": -5, "desc": "Convenient but pricey (-5 Stress)."}
}

# --- 5. MASSIVE SCENARIO POOL (30+ Cards) ---
MASTER_DB = [
    # --- ACADEMIC & CAREER ---
    {"title": "Textbook Racket", "desc": "Prof says you NEED the 5th Edition ($300).", "inspect": "⚠️ TRICK: The library has a copy on reserve.", "def_t": "Planned Obsolescence", "def_d": "Forcing upgrades for profit.", 
     "ops": [("Buy New", "trap"), ("Check Library", "inspect"), ("PDF", "gamble")], 
     "ops_i": [("Buy New ($300)", "trap"), ("Use Reserve (Free)", "smart"), ("Rent ($40)", "safe")]},

    {"title": "Unpaid Internship", "desc": "Great resume booster. $0 pay.", "inspect": "⚠️ ROI: Leads to high paying job?", "def_t": "Opportunity Cost", "def_d": "Loss of income from paid work.", 
     "ops": [("Take it", "gamble"), ("Check Reviews", "inspect"), ("Keep Job", "safe")], 
     "ops_i": [("Work Free", "gamble"), ("Read Glassdoor", "smart"), ("Wait Tables", "safe")]},

    {"title": "Laptop Crash", "desc": "Blue screen of death. Mid-terms.", "inspect": "⚠️ REPAIR: Campus IT fixes software free.", "def_t": "Repairability", "def_d": "Ease of fixing vs replacing.", 
     "ops": [("Buy New Mac", "trap"), ("Check IT", "inspect"), ("YouTube Fix", "gamble")], 
     "ops_i": [("Buy ($1200)", "trap"), ("IT Help", "smart"), ("DIY", "gamble")]},
     
    {"title": "Plagiarism Checker", "desc": "Essay due. Check score on 'TurnItIn'?", "inspect": "⚠️ PRIVACY: Free sites sell your essay.", "def_t": "Data Mining", "def_d": "Free services selling user data.", 
     "ops": [("Use Free Site", "trap"), ("Check Reviews", "inspect"), ("Submit Blind", "gamble_stress")], 
     "ops_i": [("Use Free", "trap"), ("Campus Tool", "smart"), ("Submit Blind", "gamble_stress")]},

    # --- SOCIAL & FOMO ---
    {"title": "Dorm Party", "desc": "Everyone is going. Cover is $20.", "inspect": "⚠️ FOMO: Social pressure is high.", "def_t": "Social Tax", "def_d": "Spending to maintain social standing.", 
     "ops": [("Go Wild", "trap"), ("Check Cover", "inspect"), ("One Drink", "safe")], 
     "ops_i": [("VIP ($100)", "trap"), ("Stay In ($0)", "smart"), ("Water Only ($20)", "safe")]},

    {"title": "Spring Break", "desc": "Friends booking trip to Cabo ($800).", "inspect": "⚠️ PEER PRESSURE: Staycation is free.", "def_t": "Living Beyond Means", "def_d": "Spending to match wealthy peers.", 
     "ops": [("Book It", "trap"), ("Check Bank", "inspect"), ("Road Trip", "safe")], 
     "ops_i": [("Book ($800)", "trap"), ("Stay Home", "smart"), ("Camping ($100)", "safe")]},

    {"title": "Dating App Gold", "desc": "No matches. Upgrade to Gold for $30/mo?", "inspect": "⚠️ ALGO: Apps hide matches to make you pay.", "def_t": "Freemium", "def_d": "Free product that charges for features.", 
     "ops": [("Subscribe", "trap"), ("Check Algo", "inspect"), ("Stay Free", "smart")], 
     "ops_i": [("Pay $30", "trap"), ("Update Bio", "smart"), ("Delete App", "safe")]},
     
    {"title": "Concert Tickets", "desc": "Fav band in town. Tickets $150.", "inspect": "⚠️ SCALPERS: Prices drop 1 hour before show.", "def_t": "Dynamic Pricing", "def_d": "Prices changing based on demand.", 
     "ops": [("Buy Now", "trap"), ("Check StubHub", "inspect"), ("Skip", "safe")], 
     "ops_i": [("Buy ($150)", "trap"), ("Buy Last Min ($50)", "smart"), ("Listen Spotify", "safe")]},

    # --- FINANCIAL & BILLS ---
    {"title": "Credit Card Stall", "desc": "Free T-shirt if you sign up for a card!", "inspect": "⚠️ TRAP: 25% APR and annual fees.", "def_t": "Predatory Lending", "def_d": "Lending with unfair terms.", 
     "ops": [("Sign Up", "trap"), ("Read Terms", "inspect"), ("Walk Away", "smart")], 
     "ops_i": [("Get Shirt (Debt)", "trap"), ("Read Fine Print", "smart"), ("Walk Away", "smart")]},

    {"title": "Crypto Bro", "desc": "Roommate says buy 'DogeMoon'.", "inspect": "⚠️ SCAM: It's a pump and dump scheme.", "def_t": "Speculation", "def_d": "High risk trading vs investing.", 
     "ops": [("Invest $500", "trap"), ("Research", "inspect"), ("Ignore", "smart")], 
     "ops_i": [("Invest", "trap"), ("Index Fund", "smart"), ("Laugh", "safe")]},

    {"title": "Tax Refund?", "desc": "Email says you have a pending refund.", "inspect": "⚠️ PHISHING: Check the sender URL.", "def_t": "Phishing", "def_d": "Fake messages stealing info.", 
     "ops": [("Click Link", "trap"), ("Check Sender", "inspect"), ("Ignore", "safe")], 
     "ops_i": [("Enter SSN", "trap"), ("Delete Email", "smart"), ("Ignore", "safe")]},

    {"title": "Subscription Audit", "desc": "You have Netflix, Hulu, HBO, Spotify...", "inspect": "⚠️ CHURN: You pay $80/mo. Cancel and rotate them.", "def_t": "Subscription Fatigue", "def_d": "Accumulating recurring small costs.", 
     "ops": [("Keep All", "trap"), ("Audit Bills", "inspect"), ("Use Mom's", "gamble_stress")], 
     "ops_i": [("Pay ($80/mo)", "trap"), ("Cancel All", "smart"), ("Use Mom's", "gamble_stress")]},

    {"title": "Coffee Habit", "desc": "Starbucks daily adds up to $150/mo.", "inspect": "⚠️ LATTE FACTOR: Small daily costs compound.", "def_t": "Compound Cost", "def_d": "Small leaks sinking the ship.", 
     "ops": [("Keep Buying", "trap"), ("Check Budget", "inspect"), ("Cut Back", "safe")], 
     "ops_i": [("Buy ($150)", "trap"), ("Thermos ($0)", "smart"), ("Every other day ($70)", "safe")]},

    # --- HEALTH & WELLNESS ---
    {"title": "Gym Membership", "desc": "Fancy gym is $80/mo. Campus gym is crowded.", "inspect": "⚠️ COMMITMENT: You'll stop going in Feb.", "def_t": "Breakage", "def_d": "Revenue from unused services.", 
     "ops": [("Sign Contract", "trap"), ("Check Campus", "inspect"), ("Jog Outside", "safe")], 
     "ops_i": [("Pay ($80/mo)", "trap"), ("Campus (Free)", "smart"), ("Jog", "safe")]},

    {"title": "Dental Pain", "desc": "Tooth hurts. Dentist is expensive.", "inspect": "⚠️ INFECTION: Waiting makes it a $2k Root Canal.", "def_t": "Preventative Care", "def_d": "Fixing problems early to save money.", 
     "ops": [("Wait", "trap"), ("Check School", "inspect"), ("Clove Oil", "gamble")], 
     "ops_i": [("Ignore", "trap"), ("Student Clinic ($)", "smart"), ("ER ($$$)", "trap")]},

    {"title": "Sick Day", "desc": "Flu hitting hard. Shift starts in 1 hour.", "inspect": "⚠️ POLICY: Boss fires if you miss without note.", "def_t": "Presenteeism", "def_d": "Working while sick (low productivity).", 
     "ops": [("Go to Work", "gamble_stress"), ("Check Policy", "inspect"), ("Call Out", "safe")], 
     "ops_i": [("Work Sick", "gamble_stress"), ("Get Note ($30)", "safe"), ("Quit", "trap")]},

    # --- HOUSING & EVERYDAY ---
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

    {"title": "Parking Pass", "desc": "Semester pass is $300.", "inspect": "⚠️ CALC: Park & Ride bus is free.", "def_t": "Sunk Cost", "def_d": "Paying for convenience you don't need.", 
     "ops": [("Buy Pass", "trap"), ("Check Bus", "inspect"), ("Risk Tickets", "gamble")], 
     "ops_i": [("Buy Pass", "trap"), ("Bus (Free)", "smart"), ("Risk It", "gamble")]},
     
    {"title": "Moving Out", "desc": "Landlord claims you damaged the wall.", "inspect": "⚠️ DEPOSIT: Did you take photos when you moved in?", "def_t": "Security Deposit", "def_d": "Money held to cover damages.", 
     "ops": [("Pay Damages", "safe"), ("Check Photos", "inspect"), ("Argue", "gamble_stress")], 
     "ops_i": [("Pay ($200)", "safe"), ("Show Photos", "smart"), ("Threaten Court", "gamble")]},
]

# --- 6. GAME ENGINE ---
class EndlessSim:
    def __init__(self, funding_source):
        self.funding = funding_source
        self.cash = 1000
        # Set Debt based on selection
        self.debt = FUNDING_OPTS[funding_source]["debt"]
        
        self.stress = 20
        self.stress_max = 100
        self.level = 1
        self.week = 1
        self.inflation = 1.0 
        
        # User Choices
        self.mode_housing = "Shared Dorm"
        self.mode_job = "Unemployed"
        self.mode_food = "Home Cooking"
        
        self.inventory = []
        self.history = []
        self.intel = []
        
        self.buffs = {"resist": 0, "luck": 0.0, "transport": 0}
        
        self.full_deck = MASTER_DB.copy()
        random.shuffle(self.full_deck)
        self.draw_card()

    def get_difficulty_desc(self):
        if self.level == 1: return "Normal"
        if self.level == 2: return "Hard (Prices +20%)"
        if self.level == 3: return "Expert (Prices +40%)"
        if self.level >= 4: return "NIGHTMARE (Prices Skyrocketing)"

    def generate_bill_card(self):
        # 1. Calculate Monthly Totals based on sidebar
        house = HOUSING_OPTS[self.mode_housing]
        food = FOOD_OPTS[self.mode_food]
        job = JOB_OPTS[self.mode_job]
        
        # Monthly = Weekly * 4
        m_rent = house["cost"] * 4 * self.inflation
        m_food = food["cost"] * 4 * self.inflation
        m_income = job["pay"] * 4 * self.inflation
        
        total_due = m_rent + m_food
        
        # Create a dynamic card
        return {
            "title": "📅 MONTHLY BILLS",
            "desc": f"Rent and Grocery bills are due. Total: ${int(total_due)}.",
            "inspect": f"BREAKDOWN: Housing (${int(m_rent)}) + Food (${int(m_food)}) - Income ($0 paid separately).",
            "def_t": "Burn Rate",
            "def_d": "The rate at which you spend money in excess of income.",
            # Store the values in the card so we can access them in process_turn
            "values": {"due": total_due, "income": m_income, "rent": m_rent},
            "ops": [("Pay Full", "pay_full"), ("Use Credit", "pay_credit"), ("Skimp Food", "pay_skimp")],
            "ops_i": [("Pay Full", "pay_full"), ("Use Credit (Debt)", "pay_credit"), ("Skimp (Stress)", "pay_skimp")]
        }

    def draw_card(self):
        # EVERY 4 WEEKS -> BILL CARD
        if self.week % 4 == 0:
            self.current_scen = self.generate_bill_card()
            self.indices = [0, 1, 2] # No shuffle for bills, keep order
            return

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
        d_debt = 0
        d_stress = 0
        msg = ""
        
        # --- SPECIAL: BILL PAYMENT LOGIC ---
        if c_type in ["pay_full", "pay_credit", "pay_skimp"]:
            # We add income FIRST (Monthly Paycheck)
            monthly_income = scen["values"]["income"]
            self.cash += monthly_income
            
            bill_total = scen["values"]["due"]
            
            if c_type == "pay_full":
                d_cash = -bill_total
                d_stress = -5 # Relief
                msg = f"✅ PAID BILLS. (Income +${int(monthly_income)} | Bills -${int(bill_total)})"
                
            elif c_type == "pay_credit":
                d_cash = 0 # Keep cash
                d_debt = bill_total * 1.05 # Add to debt + 5% fee
                d_stress = 10
                msg = f"💳 CHARGED IT. (Income +${int(monthly_income)} | Debt +${int(d_debt)})"
                
            elif c_type == "pay_skimp":
                # Pay rent only, skip food cost from total
                rent_only = scen["values"]["rent"]
                d_cash = -rent_only
                d_stress = 20 # Hungry/Stressed
                msg = f"🍜 SKIMPED. Paid Rent only. (Income +${int(monthly_income)} | Bills -${int(rent_only)})"

        # --- STANDARD SCENARIO LOGIC ---
        elif c_type == "trap":
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

        # Apply Buffs
        if "transport" in scen["title"].lower(): d_cash += self.buffs["transport"]
        
        # --- FINAL MATH ---
        self.cash += d_cash
        self.debt += d_debt
        self.stress = min(100, max(0, self.stress + d_stress))
        
        self.history.insert(0, f"Wk {self.week}: {msg}")
        
        intel_data = {"t": scen["def_t"], "d": scen["def_d"]}
        if intel_data not in self.intel: self.intel.append(intel_data)

        if self.stress >= self.stress_max:
            st.session_state.game_over = True
            st.session_state.end_msg = f"🤯 BURNOUT! You lasted {self.week} weeks."
            return
        if self.cash < -1000:
            st.session_state.game_over = True
            st.session_state.end_msg = f"💸 BANKRUPT! You lasted {self.week} weeks."
            return

        self.week += 1
        if self.week > WEEKS_PER_LEVEL * self.level: # Simple Level Scaling
            self.level += 1
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

# --- 7. UI SETUP ---
st.set_page_config(page_title="Student Survival", page_icon="🎓", layout="wide")
st.markdown("""<style>div.stButton > button { width: 100%; height: 60px; border-radius: 12px; font-weight: bold; }</style>""", unsafe_allow_html=True)

if "game" not in st.session_state: st.session_state.game = None
if "inspected" not in st.session_state: st.session_state.inspected = False
if "game_over" not in st.session_state: st.session_state.game_over = False
if "level_up" not in st.session_state: st.session_state.level_up = False
if "uid" not in st.session_state: st.session_state.uid = 0 

if st.session_state.game is None:
    st.title("🎓 STUDENT SURVIVAL SETUP")
    
    # 1. Ask for Funding
    funding_choice = st.selectbox("How are you funding your education?", list(FUNDING_OPTS.keys()))
    st.caption(FUNDING_OPTS[funding_choice]["desc"])
    
    st.divider()
    
    if st.button("🚀 Start Game"):
        st.session_state.game = EndlessSim(funding_choice)
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
        st.caption(f"Funding: {g.funding}")
        
        # --- LIFESTYLE DASHBOARD ---
        st.divider()
        st.markdown("### 🎛️ Lifestyle Settings")
        st.caption("These determine your bill on Week 4.")
        
        # 1. JOB
        new_job = st.selectbox("💼 Job", list(JOB_OPTS.keys()), index=list(JOB_OPTS.keys()).index(g.mode_job))
        if new_job != g.mode_job: g.mode_job = new_job; st.rerun()
        
        # 2. HOUSING
        new_house = st.selectbox("🏠 Housing", list(HOUSING_OPTS.keys()), index=list(HOUSING_OPTS.keys()).index(g.mode_housing))
        if new_house != g.mode_housing: g.mode_housing = new_house; st.rerun()
        
        # 3. FOOD
        new_food = st.selectbox("🍔 Food", list(FOOD_OPTS.keys()), index=list(FOOD_OPTS.keys()).index(g.mode_food))
        if new_food != g.mode_food: g.mode_food = new_food; st.rerun()
        
        # --- PREVIEW ---
        j = JOB_OPTS[g.mode_job]
        h = HOUSING_OPTS[g.mode_housing]
        f = FOOD_OPTS[g.mode_food]
        
        m_inc = j["pay"] * 4 * g.inflation
        m_exp = (h["cost"] + f["cost"]) * 4 * g.inflation
        
        st.markdown(f"""
        **Monthly Projection:**
        * Income: +${int(m_inc)}
        * Bill Due: -${int(m_exp)}
        """)
        
        st.divider()
        st.progress(g.stress / g.stress_max, f"Stress: {g.stress}/{g.stress_max}")
        
        st.markdown("### 🛍️ The Mall")
        for name, item in SHOP_ITEMS.items():
            if name not in g.inventory:
                if st.button(f"{name} (${item['cost']})", help=item['desc']):
                    if g.buy_item(name): st.rerun()
                    else: st.toast("Not enough cash!", icon="❌")
        
        st.divider()
        st.markdown("### 💸 Manage Debt")
        
        pay_20 = int(g.debt * 0.2)
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            if st.button(f"Pay 20%\n(-${pay_20})"):
                if g.cash >= pay_20 and g.debt > 0:
                    g.cash -= pay_20
                    g.debt -= pay_20
                    st.toast(f"Paid down ${pay_20}!", icon="📉")
                    st.rerun()
                else:
                    st.toast("Not enough cash or no debt!", icon="❌")

        with col_d2:
            if st.button("Pay ALL\n(Clear It)"):
                if g.cash >= g.debt and g.debt > 0:
                    g.cash -= g.debt
                    g.debt = 0
                    st.balloons()
                    st.toast("YOU ARE DEBT FREE!", icon="🎉")
                    st.rerun()
                else:
                    st.toast("You can't afford to clear it yet.", icon="❌")
        
        if st.button("🛑 Give Up"):
            st.session_state.game = None
            st.rerun()

    # --- TOP METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash", f"${int(g.cash)}")
    c2.metric("Debt", f"${int(g.debt)}", delta_color="inverse")
    c3.metric("Inflation", f"{int((g.inflation-1)*100)}%")
    
    # Show "Weeks until Bill"
    weeks_left = 4 - (g.week % 4)
    if weeks_left == 4: weeks_left = 0 # Is Bill week
    
    if weeks_left == 0:
        c4.error("🔴 BILL WEEK")
    else:
        c4.metric("Next Bill", f"in {weeks_left} wks")
    
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

        st.divider()
        st.caption("📜 History:")
        for log in g.history[:3]:
            st.text(log)

    with tab2:
        if not g.intel: st.info("Play to learn!")
        else:
            for i in g.intel:
                with st.expander(f"📌 {i['t']}"): st.write(i['d'])
