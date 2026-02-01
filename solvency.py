import streamlit as st
import random
import time

# --- 1. CONFIGURATION ---
# Difficulty scales mathematically based on Level
WEEKS_PER_LEVEL = 10 

# --- 2. THE MALL (PERMANENT UPGRADES) ---
SHOP_ITEMS = {
    "Noise Cancelling Headphones": {"cost": 150, "effect": "resist", "val": 5, "desc": "🎧 -5 Stress from bad events."},
    "Second-Hand Bike": {"cost": 100, "effect": "transport", "val": 20, "desc": "🚲 Reduces transport costs."},
    "Chegg/AI Subscription": {"cost": 80, "effect": "luck", "val": 0.15, "desc": "🤖 +15% Luck on Gambles."},
    "Meal Prep Containers": {"cost": 40, "effect": "food", "val": 10, "desc": "🍱 Reduces weekly food costs."},
    "Part-Time Job": {"cost": 0, "effect": "income", "val": 50, "desc": "💼 Increases weekly income by $50."},
}

# --- 3. MASSIVE SCENARIO POOL (Continuous) ---
# No levels here. Just a massive list of problems.
MASTER_DB = [
    {"title": "Textbook Racket", "desc": "Prof says you NEED the 5th Edition ($300).", "inspect": "⚠️ TRICK: The library has a copy on reserve.", "def_t": "Planned Obsolescence", "def_d": "Forcing upgrades for profit.", "ops": [("Buy New", "trap"), ("Library", "smart"), ("PDF", "gamble")], "ops_i": [("Buy New ($300)", "trap"), ("Library (Free)", "smart"), ("Rent ($40)", "safe")]},
    {"title": "Dorm Party", "desc": "Everyone is going. Cover is $20.", "inspect": "⚠️ FOMO: Social pressure is high.", "def_t": "Social Tax", "def_d": "Spending to maintain social standing.", "ops": [("Go Wild", "trap"), ("Stay In", "smart"), ("One Drink", "safe")], "ops_i": [("VIP ($100)", "trap"), ("Study", "smart"), ("Water Only ($20)", "safe")]},
    {"title": "Meal Plan", "desc": "Cafeteria food is gross. UberEats?", "inspect": "⚠️ MARKUP: Delivery adds 30% to cost.", "def_t": "Convenience Cost", "def_d": "Premium paid for saving effort.", "ops": [("Delivery", "trap"), ("Ramen", "smart"), ("Steal Fruit", "gamble")], "ops_i": [("Order ($30)", "trap"), ("Cook ($3)", "smart"), ("Sneak Food", "gamble")]},
    {"title": "The Roommate", "desc": "Roommate keeps eating your snacks.", "inspect": "⚠️ CONFLICT: A mini-fridge costs $50.", "def_t": "Asset Protection", "def_d": "Spending to secure your property.", "ops": [("Buy Fridge", "safe"), ("Yell", "trap"), ("Hide Food", "smart")], "ops_i": [("Fridge ($50)", "safe"), ("Fight", "trap"), ("Hide Under Bed", "smart")]},
    {"title": "Credit Card Stall", "desc": "Free T-shirt if you sign up for a card!", "inspect": "⚠️ TRAP: 25% APR and annual fees.", "def_t": "Predatory Lending", "def_d": "Lending with unfair terms.", "ops": [("Sign Up", "trap"), ("Walk Away", "smart"), ("Read Terms", "inspect")], "ops_i": [("Get Shirt (Debt)", "trap"), ("Walk Away", "smart"), ("Report", "safe")]},
    {"title": "Laundry Day", "desc": "Out of clean clothes. Machines cost $5.", "inspect": "⚠️ HACK: You can hand wash in the sink.", "def_t": "Labor Substitution", "def_d": "Trading time/effort to save money.", "ops": [("Pay $5", "safe"), ("Sink Wash", "smart"), ("Wear Dirty", "gamble")], "ops_i": [("Pay", "safe"), ("Sink Wash", "smart"), ("Febreze It", "gamble")]},
    {"title": "Utility Bill Shock", "desc": "AC left on. Bill is $200.", "inspect": "⚠️ SPLIT: You can argue roommates owe half.", "def_t": "Shared Liability", "def_d": "Joint responsibility for debt.", "ops": [("Pay All", "safe"), ("Fight Roommates", "gamble"), ("Payment Plan", "smart")], "ops_i": [("Pay All", "safe"), ("Demand Split", "gamble"), ("Call Utility", "smart")]},
    {"title": "Car Booted", "desc": "Parked in wrong zone. $100 fine.", "inspect": "⚠️ APPEAL: The sign was covered by a bush.", "def_t": "Bureaucracy", "def_d": "Navigating complex rules.", "ops": [("Pay Now", "safe"), ("Appeal", "smart"), ("Saw it off", "trap")], "ops_i": [("Pay ($100)", "safe"), ("Appeal w/ Photo", "smart"), ("Destroy Boot", "trap")]},
    {"title": "Grocery Inflation", "desc": "Eggs are $8. Meat is expensive.", "inspect": "⚠️ SUBSTITUTE: Frozen veggies/beans are cheap.", "def_t": "Substitution Effect", "def_d": "Switching to cheaper alternatives.", "ops": [("Buy Normal", "trap"), ("Buy Bulk", "smart"), ("Fast", "gamble")], "ops_i": [("Buy Normal ($100)", "trap"), ("Rice & Beans ($20)", "smart"), ("Starve", "gamble")]},
    {"title": "Concert Tickets", "desc": "Fav band in town. Tickets $150.", "inspect": "⚠️ SCALPERS: Prices drop 1 hour before show.", "def_t": "Dynamic Pricing", "def_d": "Prices changing based on demand.", "ops": [("Buy Now", "trap"), ("Wait", "smart"), ("Skip", "safe")], "ops_i": [("Buy ($150)", "trap"), ("Buy Last Min ($50)", "smart"), ("Listen Spotify", "safe")]},
    {"title": "Parking Pass", "desc": "Semester pass is $300.", "inspect": "⚠️ CALC: Park & Ride bus is free.", "def_t": "Sunk Cost", "def_d": "Paying for convenience you don't need.", "ops": [("Buy Pass", "trap"), ("Take Bus", "smart"), ("Risk Tickets", "gamble")], "ops_i": [("Buy Pass", "trap"), ("Bus (Free)", "smart"), ("Risk It", "gamble")]},
    {"title": "Subscription Audit", "desc": "You have Netflix, Hulu, HBO, Spotify...", "inspect": "⚠️ CHURN: Cancel and rotate them monthly.", "def_t": "Subscription Fatigue", "def_d": "Accumulating recurring small costs.", "ops": [("Keep All", "trap"), ("Cancel All", "smart"), ("Share Pwd", "gamble")], "ops_i": [("Pay ($80/mo)", "trap"), ("Rotate 1", "smart"), ("Use Mom's", "gamble")]},
    {"title": "Unpaid Internship", "desc": "Great resume booster. $0 pay.", "inspect": "⚠️ ROI: Leads to high paying job?", "def_t": "Opportunity Cost", "def_d": "Loss of income from paid work.", "ops": [("Take it", "gamble"), ("Keep Job", "safe"), ("Negotiate", "smart")], "ops_i": [("Work Free", "gamble"), ("Wait Tables", "safe"), ("Ask Stipend", "smart")]},
    {"title": "Interview Suit", "desc": "Old suit doesn't fit. Need new one.", "inspect": "⚠️ THRIFT: Rich neighborhoods have great Goodwill stores.", "def_t": "Signaling", "def_d": "Visual cues of status.", "ops": [("Buy Designer", "trap"), ("Thrift", "smart"), ("Borrow", "safe")], "ops_i": [("Mall ($300)", "trap"), ("Thrift ($30)", "smart"), ("Borrow Friend's", "safe")]},
    {"title": "Laptop Crash", "desc": "Blue screen of death. Mid-terms.", "inspect": "⚠️ REPAIR: Campus IT fixes software free.", "def_t": "Repairability", "def_d": "Ease of fixing vs replacing.", "ops": [("Buy New Mac", "trap"), ("Campus IT", "smart"), ("YouTube Fix", "gamble")], "ops_i": [("Buy ($1200)", "trap"), ("IT Help", "smart"), ("DIY", "gamble")]},
    {"title": "LinkedIn Premium", "desc": "$40/mo to see who viewed you.", "inspect": "⚠️ VALUE: Recruiters don't care if you have Premium.", "def_t": "Freemium", "def_d": "Paying for features you don't need.", "ops": [("Subscribe", "trap"), ("Free Trial", "smart"), ("Ignore", "safe")], "ops_i": [("Pay", "trap"), ("Cancel Trial", "smart"), ("Ignore", "safe")]},
    {"title": "Coffee Habit", "desc": "Starbucks daily adds up to $150/mo.", "inspect": "⚠️ LATTE FACTOR: Small daily costs compound.", "def_t": "Compound Cost", "def_d": "Small leaks sinking the ship.", "ops": [("Keep Buying", "trap"), ("Brew Home", "smart"), ("Cut Back", "safe")], "ops_i": [("Buy", "trap"), ("Thermos", "smart"), ("Every other day", "safe")]},
    {"title": "Networking Dinner", "desc": "Fancy dinner with alumni. $80 plate.", "inspect": "⚠️ ROI: One job lead pays for 100 dinners.", "def_t": "Investment", "def_d": "Spending now for future gain.", "ops": [("Go", "smart"), ("Skip", "trap"), ("Coffee Instead", "safe")], "ops_i": [("Go ($80)", "smart"), ("Skip", "trap"), ("Ask for Coffee", "safe")]},
    {"title": "Spring Break Trip", "desc": "Friends booking Airbnb. $400 share.", "inspect": "⚠️ BUDGET: You have $200 in bank.", "def_t": "Living Beyond Means", "def_d": "Spending more than you earn.", "ops": [("Credit Card", "trap"), ("Say No", "smart"), ("Drive Self", "safe")], "ops_i": [("Debt", "trap"), ("Stay Home", "smart"), ("Budget Trip", "safe")]},
    {"title": "Crypto Bro", "desc": "Roommate says buy 'DogeMoon'.", "inspect": "⚠️ SCAM: It's a pump and dump scheme.", "def_t": "Speculation", "def_d": "High risk trading vs investing.", "ops": [("Invest $500", "trap"), ("Research", "inspect"), ("Ignore", "smart")], "ops_i": [("Invest", "trap"), ("Index Fund", "smart"), ("Laugh", "safe")]},
]

# --- 4. GAME ENGINE (ENDLESS MODE) ---
class EndlessSim:
    def __init__(self):
        # Starting Stats
        self.cash = 1000
        self.debt = 10000
        self.stress = 20
        self.stress_max = 100
        
        # Progression
        self.level = 1
        self.week = 1
        self.inflation = 1.0 # 1.0 = 100% price, 2.0 = 200% price
        
        # Tools
        self.inventory = []
        self.history = []
        self.intel = []
        self.buffs = {"resist": 0, "luck": 0.0, "transport": 0, "food": 0, "income": 0}
        
        # Deck Management
        self.full_deck = MASTER_DB.copy()
        random.shuffle(self.full_deck)
        self.draw_card()

    def get_difficulty_desc(self):
        # Just text to show how hard it is getting
        if self.level == 1: return "Normal"
        if self.level == 2: return "Hard (Prices +20%)"
        if self.level == 3: return "Expert (Prices +40%)"
        if self.level >= 4: return "NIGHTMARE (Prices Skyrocketing)"

    def draw_card(self):
        # If deck is empty, reshuffle and add infinite randoms
        if not self.full_deck:
            self.full_deck = MASTER_DB.copy()
            random.shuffle(self.full_deck)
            
        self.current_scen = self.full_deck.pop(0)
        self.indices = [0, 1, 2]
        random.shuffle(self.indices)

    def process_turn(self, choice_idx):
        scen = self.current_scen
        
        # Standard Turn Logic
        real_idx = self.indices[choice_idx]
        c_type = scen["ops"][real_idx][1] if not st.session_state.inspected else scen["ops_i"][real_idx][1]
        
        # Calculate Results with Inflation
        d_cash = 0
        d_stress = 0
        msg = ""
        
        if c_type == "trap":
            d_cash = -random.randint(100, 300) * self.inflation
            d_stress = 20 - self.buffs["resist"]
            msg = "❌ TRAP! You fell for it."
        elif c_type == "smart":
            d_stress = -10
            msg = "🧠 SMART! Good handling."
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
                msg = "💀 LOST! Bad luck."

        # Apply Buffs
        if "transport" in scen["title"].lower(): d_cash += self.buffs["transport"]
        if "food" in scen["title"].lower(): d_cash += self.buffs["food"]
        
        # Economics (Weekly Drain increases with Inflation)
        weekly_cost = (100 * self.inflation) - self.buffs["food"]
        income = self.buffs["income"]
        
        self.cash += (d_cash + income - weekly_cost)
        self.stress = min(100, max(0, self.stress + d_stress))
        
        self.history.insert(0, f"Lvl {self.level}-Wk {self.week}: {msg}")
        
        # Intel Collection
        intel_data = {"t": scen["def_t"], "d": scen["def_d"]}
        if intel_data not in self.intel: self.intel.append(intel_data)

        # Check Game Over
        if self.stress >= self.stress_max:
            st.session_state.game_over = True
            st.session_state.end_msg = f"🤯 BURNOUT! You lasted {self.week + ((self.level-1)*10)} weeks."
            return
        if self.cash < -1000: # Allow small overdraft
            st.session_state.game_over = True
            st.session_state.end_msg = f"💸 BANKRUPT! You lasted {self.week + ((self.level-1)*10)} weeks."
            return

        # Advance Week
        self.week += 1
        
        # Level Up Logic (Every 10 weeks)
        if self.week > WEEKS_PER_LEVEL:
            self.level += 1
            self.week = 1
            self.inflation += 0.2 # 20% Inflation every level
            st.session_state.level_up = True
            
        st.session_state.inspected = False # RESET INSPECT
        self.draw_card()

    def buy_item(self, item_name):
        item = SHOP_ITEMS[item_name]
        if self.cash >= item["cost"]:
            self.cash -= item["cost"]
            self.inventory.append(item_name)
            
            if item["effect"] == "resist": self.buffs["resist"] += item["val"]
            elif item["effect"] == "luck": self.buffs["luck"] += item["val"]
            elif item["effect"] == "transport": self.buffs["transport"] += item["val"]
            elif item["effect"] == "food": self.buffs["food"] += item["val"]
            elif item["effect"] == "income": self.buffs["income"] += item["val"]
            return True
        return False

# --- 5. UI SETUP ---
st.set_page_config(page_title="Student Survival: Endless", page_icon="🔥", layout="wide")
st.markdown("""<style>div.stButton > button { width: 100%; height: 60px; border-radius: 12px; font-weight: bold; }</style>""", unsafe_allow_html=True)

# Session Initialization
if "game" not in st.session_state: st.session_state.game = None
if "inspected" not in st.session_state: st.session_state.inspected = False
if "game_over" not in st.session_state: st.session_state.game_over = False
if "level_up" not in st.session_state: st.session_state.level_up = False
if "uid" not in st.session_state: st.session_state.uid = 0 # FOR CLICK FIX

# --- UI LOGIC ---
if st.session_state.game is None:
    st.title("🔥 STUDENT SURVIVAL: ENDLESS")
    st.info("How long can you survive? Prices rise 20% every level.")
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
    if st.button("Continue... if you dare"):
        st.session_state.level_up = False
        st.rerun()

else:
    g = st.session_state.game
    
    # Sidebar
    with st.sidebar:
        st.title(f"Level {g.level}")
        st.caption(g.get_difficulty_desc())
        st.progress(g.stress / g.stress_max, f"Stress: {g.stress}/{g.stress_max}")
        st.divider()
        st.markdown("### 🛍️ The Mall")
        for name, item in SHOP_ITEMS.items():
            if name not in g.inventory:
                if st.button(f"{name} (${item['cost']})", help=item['desc']):
                    if g.buy_item(name): st.rerun()
                    else: st.toast("Not enough cash!", icon="❌")
        st.divider()
        if st.button("🛑 Give Up"):
            st.session_state.game = None
            st.rerun()

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash", f"${int(g.cash)}")
    c2.metric("Debt", f"${g.debt}", delta_color="inverse")
    c3.metric("Inflation", f"{int((g.inflation-1)*100)}%")
    c4.metric("Week", f"{g.week}/10")

    # Game Area
    tab1, tab2 = st.tabs(["🎮 Play", "🧠 Notebook"])
    
    with tab1:
        scen = g.current_scen
        st.markdown(f"#### 📍 {scen['title']}")
        st.info(scen['desc'])
        
        if st.session_state.inspected: 
            st.warning(f"🕵️ RESEARCH: {scen['inspect']}")

        # BUTTONS (DIRECT LOGIC + KEY FIX)
        ops = scen["ops_i"] if st.session_state.inspected else scen["ops"]
        idx = g.indices
        
        col_a, col_b, col_c = st.columns(3)
        
        # FORCE NEW ID ON EVERY ACTION
        key_base = f"{g.level}_{g.week}_{st.session_state.uid}"
        
        def handle_click(i):
            st.session_state.uid += 1 # INCREMENT UID TO RESET BUTTONS
            if i == 1 and not st.session_state.inspected:
                 st.session_state.inspected = True
            else:
                 g.process_turn(i)
            st.rerun()

        with col_a:
            # We look at idx[0] to see if it's the INSPECT button (which is usually index 1 in the logic list)
            if st.button(ops[idx[0]][0], key=f"a_{key_base}", use_container_width=True):
                handle_click(idx[0])
                    
        with col_b:
            if st.button(ops[idx[1]][0], key=f"b_{key_base}", use_container_width=True):
                handle_click(idx[1])
                    
        with col_c:
            if st.button(ops[idx[2]][0], key=f"c_{key_base}", use_container_width=True):
                handle_click(idx[2])

    with tab2:
        if not g.intel: st.info("Play to learn!")
        else:
            for i in g.intel:
                with st.expander(f"📌 {i['t']}"): st.write(i['d'])
