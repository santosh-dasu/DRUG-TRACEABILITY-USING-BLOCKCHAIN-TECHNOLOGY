# traceability/views.py

from datetime import date
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import os
import json

from .utils import read_details, save_data_blockchain, update_quantity_block

# Demo user credentials (simple testing)
DEMO_USERS = {
    'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Administrator'},
    'pharmacy_manager': {'password': 'pharma123', 'role': 'user', 'name': 'John Smith - Pharmacy Manager'},
    'supplier_rep': {'password': 'supply123', 'role': 'user', 'name': 'Sarah Johnson - Supplier Representative'},
    'quality_control': {'password': 'qc123', 'role': 'user', 'name': 'Dr. Michael Brown - Quality Control'},
    'distributor': {'password': 'dist123', 'role': 'user', 'name': 'Emily Davis - Distribution Manager'},
    'hospital_admin': {'password': 'hosp123', 'role': 'user', 'name': 'Dr. Lisa Wilson - Hospital Administrator'},
    'regulatory': {'password': 'reg123', 'role': 'admin', 'name': 'Mark Thompson - Regulatory Affairs'},
    'manufacturer': {'password': 'mfg123', 'role': 'admin', 'name': 'David Chen - Manufacturing Director'},
}

# Real user credentials for different pharmaceutical roles
REAL_USERS = {
    # System Administrators
    'system_admin': {'password': 'SecureAdmin2025!', 'role': 'admin', 'name': 'Dr. Robert Martinez - System Administrator', 'company': 'PharmTrace Systems', 'license': 'SYS-001'},
    'data_admin': {'password': 'DataSecure2025!', 'role': 'admin', 'name': 'Jennifer Liu - Data Administrator', 'company': 'PharmTrace Systems', 'license': 'SYS-002'},
    
    # Pharmaceutical Manufacturers
    'pfizer_manager': {'password': 'Pfizer2025Secure!', 'role': 'admin', 'name': 'Dr. James Wilson - Manufacturing Director', 'company': 'Pfizer Inc.', 'license': 'MFG-PFZ-001'},
    'johnson_manager': {'password': 'JnJ2025Safe!', 'role': 'admin', 'name': 'Dr. Maria Rodriguez - Quality Director', 'company': 'Johnson & Johnson', 'license': 'MFG-JNJ-001'},
    'novartis_qc': {'password': 'Novartis2025QC!', 'role': 'user', 'name': 'Dr. Ahmed Hassan - Quality Control Manager', 'company': 'Novartis AG', 'license': 'QC-NOV-001'},
    'roche_production': {'password': 'RocheProd2025!', 'role': 'user', 'name': 'Dr. Lisa Chen - Production Manager', 'company': 'Roche Pharmaceuticals', 'license': 'PRD-ROC-001'},
    
    # Distribution Centers
    'mckesson_dist': {'password': 'McKessonDist2025!', 'role': 'user', 'name': 'Michael Thompson - Distribution Manager', 'company': 'McKesson Corporation', 'license': 'DST-MCK-001'},
    'cardinal_logistics': {'password': 'CardinalLog2025!', 'role': 'user', 'name': 'Sarah Davis - Logistics Coordinator', 'company': 'Cardinal Health', 'license': 'LOG-CDH-001'},
    'amerisource_mgr': {'password': 'AmerisourceMgr2025!', 'role': 'user', 'name': 'David Park - Operations Manager', 'company': 'AmerisourceBergen', 'license': 'OPS-ASB-001'},
    
    # Hospital Systems
    'mayo_pharmacy': {'password': 'MayoPharm2025!', 'role': 'user', 'name': 'Dr. Emily Johnson - Chief Pharmacist', 'company': 'Mayo Clinic', 'license': 'PH-MAYO-001'},
    'cleveland_pharm': {'password': 'ClevelandRx2025!', 'role': 'user', 'name': 'Dr. Robert Kim - Pharmacy Director', 'company': 'Cleveland Clinic', 'license': 'PH-CCF-001'},
    'johns_hopkins': {'password': 'JHHPharmacy2025!', 'role': 'user', 'name': 'Dr. Rachel Green - Hospital Pharmacist', 'company': 'Johns Hopkins Hospital', 'license': 'PH-JHH-001'},
    
    # Retail Pharmacies
    'cvs_manager': {'password': 'CVSManager2025!', 'role': 'user', 'name': 'Patricia Williams - Pharmacy Manager', 'company': 'CVS Health', 'license': 'RT-CVS-001'},
    'walgreens_mgr': {'password': 'WalgreensRx2025!', 'role': 'user', 'name': 'Kevin Brown - Store Manager', 'company': 'Walgreens', 'license': 'RT-WAG-001'},
    'rite_aid_pharm': {'password': 'RiteAidRx2025!', 'role': 'user', 'name': 'Dr. Angela Martinez - Pharmacist', 'company': 'Rite Aid', 'license': 'RT-RAD-001'},
    
    # Regulatory & Quality Assurance
    'fda_inspector': {'password': 'FDAInspect2025!', 'role': 'admin', 'name': 'Dr. Thomas Anderson - FDA Inspector', 'company': 'U.S. FDA', 'license': 'REG-FDA-001'},
    'dea_agent': {'password': 'DEAAgent2025!', 'role': 'admin', 'name': 'Agent Susan Mitchell - DEA Compliance', 'company': 'U.S. DEA', 'license': 'REG-DEA-001'},
    'state_inspector': {'password': 'StateInsp2025!', 'role': 'admin', 'name': 'Dr. Mark Taylor - State Inspector', 'company': 'State Board of Pharmacy', 'license': 'REG-SBP-001'},
    
    # Independent Pharmacies
    'local_pharmacy': {'password': 'LocalPharm2025!', 'role': 'user', 'name': 'Dr. Nancy Garcia - Owner Pharmacist', 'company': 'Garcia Family Pharmacy', 'license': 'IND-GFP-001'},
    'community_rx': {'password': 'CommunityRx2025!', 'role': 'user', 'name': 'Dr. Peter Lee - Community Pharmacist', 'company': 'Community Care Pharmacy', 'license': 'IND-CCP-001'},
    
    # Specialty Pharmacies
    'specialty_onc': {'password': 'SpecialtyOnc2025!', 'role': 'user', 'name': 'Dr. Michelle White - Oncology Specialist', 'company': 'Specialty Oncology Pharmacy', 'license': 'SP-ONC-001'},
    'rare_disease': {'password': 'RareDisease2025!', 'role': 'user', 'name': 'Dr. Carlos Rodriguez - Rare Disease Specialist', 'company': 'Rare Disease Pharmacy', 'license': 'SP-RDS-001'},
}

def get_local_storage_path():
    """Get path for local data storage."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'local_data.json')

def initialize_sample_data():
    """Initialize the system with sample pharmaceutical data"""
    sample_products = [
        # Pfizer Products
        {
            'name': 'Lipitor (Atorvastatin) 20mg',
            'price': '89.99',
            'qty': '500',
            'desc': 'Cholesterol-lowering medication. HMG-CoA reductase inhibitor for cardiovascular health.',
            'image': 'lipitor.svg',
            'last_update': '2025-09-20',
            'tracing_info': 'Quality Tested - FDA Approved Batch',
            'manufacturer': 'Pfizer Inc.',
            'batch_number': 'PFZ-LIP-20250920-001',
            'expiry_date': '2027-09-20'
        },
        {
            'name': 'Paxlovid (Nirmatrelvir-Ritonavir)',
            'price': '529.99',
            'qty': '100',
            'desc': 'COVID-19 oral antiviral treatment. Emergency Use Authorization medication.',
            'image': 'paxlovid.svg',
            'last_update': '2025-09-22',
            'tracing_info': 'Shipped - Temperature Controlled Transport',
            'manufacturer': 'Pfizer Inc.',
            'batch_number': 'PFZ-PAX-20250922-001',
            'expiry_date': '2026-09-22'
        },
        
        # Johnson & Johnson Products
        {
            'name': 'Tylenol (Acetaminophen) 500mg',
            'price': '12.99',
            'qty': '1000',
            'desc': 'Pain reliever and fever reducer. Over-the-counter analgesic medication.',
            'image': 'tylenol.svg',
            'last_update': '2025-09-21',
            'tracing_info': 'Distributed - Retail Network Delivery',
            'manufacturer': 'Johnson & Johnson',
            'batch_number': 'JNJ-TYL-20250921-001',
            'expiry_date': '2027-09-21'
        },
        {
            'name': 'Stelara (Ustekinumab) 45mg',
            'price': '4899.99',
            'qty': '25',
            'desc': 'Biologic immunosuppressant for psoriasis and Crohn\'s disease treatment.',
            'image': 'stelara.svg',
            'last_update': '2025-09-23',
            'tracing_info': 'Received - Specialty Pharmacy Cold Chain',
            'manufacturer': 'Johnson & Johnson',
            'batch_number': 'JNJ-STE-20250923-001',
            'expiry_date': '2026-03-23'
        },
        
        # Novartis Products
        {
            'name': 'Diovan (Valsartan) 80mg',
            'price': '45.99',
            'qty': '300',
            'desc': 'ACE inhibitor for hypertension and heart failure management.',
            'image': 'generic_placeholder.svg',
            'last_update': '2025-09-19',
            'tracing_info': 'Manufacturing Complete - Quality Verification Pending',
            'manufacturer': 'Novartis AG',
            'batch_number': 'NOV-DIO-20250919-001',
            'expiry_date': '2027-09-19'
        },
        {
            'name': 'Gleevec (Imatinib) 400mg',
            'price': '8999.99',
            'qty': '50',
            'desc': 'Targeted therapy for chronic myeloid leukemia and GIST tumors.',
            'image': 'generic_placeholder.svg',
            'last_update': '2025-09-24',
            'tracing_info': 'Dispensed - Oncology Specialty Pharmacy',
            'manufacturer': 'Novartis AG',
            'batch_number': 'NOV-GLE-20250924-001',
            'expiry_date': '2026-09-24'
        },
        
        # Roche Products
        {
            'name': 'Tamiflu (Oseltamivir) 75mg',
            'price': '129.99',
            'qty': '200',
            'desc': 'Antiviral medication for influenza treatment and prevention.',
            'image': 'generic_placeholder.svg',
            'last_update': '2025-09-18',
            'tracing_info': 'Quality Tested - Seasonal Stockpile Preparation',
            'manufacturer': 'Roche Pharmaceuticals',
            'batch_number': 'ROC-TAM-20250918-001',
            'expiry_date': '2027-09-18'
        },
        {
            'name': 'Herceptin (Trastuzumab) 440mg',
            'price': '3299.99',
            'qty': '30',
            'desc': 'Targeted therapy for HER2-positive breast cancer treatment.',
            'image': 'generic_placeholder.svg',
            'last_update': '2025-09-25',
            'tracing_info': 'Shipped - Hospital Oncology Department',
            'manufacturer': 'Roche Pharmaceuticals',
            'batch_number': 'ROC-HER-20250925-001',
            'expiry_date': '2026-06-25'
        },
        
        # Generic/Common Medications
        {
            'name': 'Metformin HCl 500mg',
            'price': '8.99',
            'qty': '2000',
            'desc': 'First-line diabetes medication. Biguanide antidiabetic agent.',
            'image': 'metformin.svg',
            'last_update': '2025-09-20',
            'tracing_info': 'Distributed - Community Pharmacy Network',
            'manufacturer': 'Teva Pharmaceuticals',
            'batch_number': 'TEV-MET-20250920-001',
            'expiry_date': '2027-09-20'
        },
        {
            'name': 'Lisinopril 10mg',
            'price': '6.99',
            'qty': '1500',
            'desc': 'ACE inhibitor for hypertension and heart failure management.',
            'image': 'lisinopril.svg',
            'last_update': '2025-09-21',
            'tracing_info': 'Received - Retail Pharmacy Distribution',
            'manufacturer': 'Lupin Pharmaceuticals',
            'batch_number': 'LUP-LIS-20250921-001',
            'expiry_date': '2027-09-21'
        },
        {
            'name': 'Omeprazole 20mg',
            'price': '15.99',
            'qty': '800',
            'desc': 'Proton pump inhibitor for acid reflux and peptic ulcer treatment.',
            'image': 'generic_placeholder.svg',
            'last_update': '2025-09-22',
            'tracing_info': 'Manufacturing Complete - Packaging in Progress',
            'manufacturer': 'Dr. Reddy\'s Laboratories',
            'batch_number': 'DRL-OME-20250922-001',
            'expiry_date': '2027-09-22'
        },
        
        # Controlled Substances
        {
            'name': 'OxyContin (Oxycodone) 10mg',
            'price': '89.99',
            'qty': '100',
            'desc': 'Schedule II controlled substance for severe pain management. DEA tracking required.',
            'image': 'generic_placeholder.svg',
            'last_update': '2025-09-23',
            'tracing_info': 'DEA Secured Transport - Chain of Custody Verified',
            'manufacturer': 'Purdue Pharma',
            'batch_number': 'PUR-OXY-20250923-001',
            'expiry_date': '2027-09-23'
        },
        {
            'name': 'Adderall XR (Amphetamine) 20mg',
            'price': '199.99',
            'qty': '150',
            'desc': 'Schedule II stimulant for ADHD treatment. Controlled substance monitoring required.',
            'image': 'generic_placeholder.svg',
            'last_update': '2025-09-24',
            'tracing_info': 'Dispensed - Hospital Pharmacy Controlled Substance Vault',
            'manufacturer': 'Shire Pharmaceuticals',
            'batch_number': 'SHI-ADD-20250924-001',
            'expiry_date': '2027-09-24'
        }
    ]
    
    # Save sample products to local storage
    storage_path = get_local_storage_path()
    
    if os.path.exists(storage_path):
        with open(storage_path, 'r') as f:
            storage = json.load(f)
    else:
        storage = {}
    
    # Add products to blockchain format
    if 'products' not in storage:
        storage['products'] = []
    
    for product in sample_products:
        # Create blockchain-style entry
        blockchain_entry = f"addproduct#{product['name']}#{product['price']}#{product['qty']}#{product['desc']}#{product['image']}#{product['last_update']}#{product['tracing_info']}\n"
        
        # Also save detailed product info
        detailed_product = {
            'blockchain_entry': blockchain_entry.strip(),
            'manufacturer': product['manufacturer'],
            'batch_number': product['batch_number'],
            'expiry_date': product['expiry_date'],
            'date_added': str(date.today())
        }
        storage['products'].append(detailed_product)
    
    with open(storage_path, 'w') as f:
        json.dump(storage, f)
    
    return len(sample_products)

def save_to_local_storage(data_type, data):
    """Save data to local JSON file as fallback."""
    storage_path = get_local_storage_path()
    
    if os.path.exists(storage_path):
        with open(storage_path, 'r') as f:
            storage = json.load(f)
    else:
        storage = {}
    
    if data_type not in storage:
        storage[data_type] = []
    
    storage[data_type].append(data)
    
    with open(storage_path, 'w') as f:
        json.dump(storage, f)

def read_from_local_storage(data_type):
    """Read data from local JSON file as fallback."""
    storage_path = get_local_storage_path()
    
    if not os.path.exists(storage_path):
        return []
    
    with open(storage_path, 'r') as f:
        storage = json.load(f)
    
    return storage.get(data_type, [])


# ------------------ Basic Views ------------------ #
def index(request):
    # Initialize sample data if not exists
    try:
        storage_path = get_local_storage_path()
        if not os.path.exists(storage_path):
            initialize_sample_data()
    except:
        pass
    
    context = {
        'demo_users': DEMO_USERS,
        'real_users': REAL_USERS
    }
    
    return render(request, "traceability/index.html", context)


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check demo users first
        if username in DEMO_USERS and DEMO_USERS[username]['password'] == password:
            user_info = DEMO_USERS[username]
            request.session["username"] = username
            request.session["user_role"] = user_info['role']
            request.session["display_name"] = user_info['name']
            
            if user_info['role'] == 'admin':
                return render(request, "traceability/admin_screen.html", {
                    "data": f"Welcome back, {user_info['name']}",
                    "username": username
                })
            else:
                return render(request, "traceability/user_screen.html", {
                    "data": f"Welcome back, {user_info['name']}",
                    "username": username
                })

        # Check real users
        if username in REAL_USERS and REAL_USERS[username]['password'] == password:
            user_info = REAL_USERS[username]
            request.session["username"] = username
            request.session["user_role"] = user_info['role']
            request.session["display_name"] = user_info['name']
            
            if user_info['role'] == 'admin':
                return render(request, "traceability/admin_screen.html", {
                    "data": f"Welcome back, {user_info['name']}",
                    "username": username
                })
            else:
                return render(request, "traceability/user_screen.html", {
                    "data": f"Welcome back, {user_info['name']}",
                    "username": username
                })

        # Check registered users (blockchain/local storage)
        try:
            rows = read_details("signup").split("\n")
            for row in rows[:-1]:
                arr = row.split("#")
                if len(arr) >= 3 and arr[0] == "signup" and arr[1] == username and arr[2] == password:
                    request.session["username"] = username
                    request.session["user_role"] = "user"
                    request.session["display_name"] = username.title()
                    return render(request, "traceability/user_screen.html", {"data": f"Welcome {username}"})
        except:
            # Fallback to local storage
            users = read_from_local_storage("users")
            for user in users:
                if user.get("username") == username and user.get("password") == password:
                    request.session["username"] = username
                    request.session["user_role"] = "user"
                    request.session["display_name"] = user.get("name", username.title())
                    return render(request, "traceability/user_screen.html", {"data": f"Welcome {user.get('name', username)}"})

        return render(request, "traceability/login.html", {
            "data": "Invalid login credentials. Please try again.",
            'demo_users': DEMO_USERS,
            'real_users': REAL_USERS
        })

    return render(request, "traceability/login.html", {
        'demo_users': DEMO_USERS,
        'real_users': REAL_USERS
    })


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        contact = request.POST.get("contact")
        email = request.POST.get("email")
        address = request.POST.get("address")
        name = request.POST.get("full_name", username.title())

        # Check if username already exists in demo users
        if username in DEMO_USERS:
            return render(request, "traceability/register.html", {
                "data": "Username already exists in the system",
                'demo_users': DEMO_USERS,
                'real_users': REAL_USERS
            })

        # Check if username already exists in real users
        if username in REAL_USERS:
            return render(request, "traceability/register.html", {
                "data": "Username already exists in the system",
                'demo_users': DEMO_USERS,
                'real_users': REAL_USERS
            })

        try:
            # Try blockchain first
            rows = read_details("signup").split("\n")
            for row in rows[:-1]:
                arr = row.split("#")
                if len(arr) >= 2 and arr[0] == "signup" and arr[1] == username:
                    return render(request, "traceability/register.html", {
                        "data": "Username already exists",
                        'demo_users': DEMO_USERS,
                        'real_users': REAL_USERS
                    })

            data = f"signup#{username}#{password}#{contact}#{email}#{address}#{name}\n"
            save_data_blockchain(data, "signup")
            return render(request, "traceability/register.html", {
                "data": "Registration successful! You can now login.",
                'demo_users': DEMO_USERS,
                'real_users': REAL_USERS
            })
        except:
            # Fallback to local storage
            users = read_from_local_storage("users")
            for user in users:
                if user.get("username") == username:
                    return render(request, "traceability/register.html", {
                        "data": "Username already exists",
                        'demo_users': DEMO_USERS,
                        'real_users': REAL_USERS
                    })

            user_data = {
                "username": username,
                "password": password,
                "contact": contact,
                "email": email,
                "address": address,
                "name": name,
                "registration_date": str(date.today())
            }
            save_to_local_storage("users", user_data)
            return render(request, "traceability/register.html", {
                "data": "Registration successful! You can now login.",
                'demo_users': DEMO_USERS,
                'real_users': REAL_USERS
            })

    return render(request, "traceability/register.html", {
        'demo_users': DEMO_USERS,
        'real_users': REAL_USERS
    })


# ------------------ Product Views ------------------ #
def add_product(request):
    if request.method == "POST":
        cname = request.POST.get("t1")
        qty = request.POST.get("t2")
        price = request.POST.get("t3")
        desc = request.POST.get("t4")
        image = request.FILES["t5"]
        imagename = image.name
        today = date.today()

        fs = FileSystemStorage()
        fs.save(f"static/products/{imagename}", image)

        data = f"addproduct#{cname}#{price}#{qty}#{desc}#{imagename}#{today}#Production State\n"
        save_data_blockchain(data, "addproduct")
        return render(request, "traceability/add_product.html", {"data": "Product added successfully"})

    return render(request, "traceability/add_product.html")


def update_tracing(request):
    try:
        rows = read_details("addproduct").split("\n")
        products = []
        for row in rows[:-1]:
            arr = row.split("#")
            if arr[0] == "addproduct":
                products.append({
                    "name": arr[1],
                    "price": arr[2],
                    "qty": arr[3],
                    "desc": arr[4],
                    "image": arr[5],
                    "last_update": arr[6],
                    "tracing_info": arr[7] if len(arr) > 7 else "Production State",
                })
    except:
        # Use local storage as fallback
        products = []
        storage_path = get_local_storage_path()
        if os.path.exists(storage_path):
            with open(storage_path, 'r') as f:
                storage = json.load(f)
                for product_data in storage.get('products', []):
                    blockchain_entry = product_data['blockchain_entry']
                    arr = blockchain_entry.split("#")
                    if len(arr) >= 7:
                        products.append({
                            "name": arr[1],
                            "price": arr[2],
                            "qty": arr[3],
                            "desc": arr[4],
                            "image": arr[5],
                            "last_update": arr[6],
                            "tracing_info": arr[7] if len(arr) > 7 else "Production State",
                        })

    return render(request, "traceability/update_tracing.html", {"products": products})


def add_tracing_action(request):
    if request.method == "POST":
        product_name = request.POST.get("t1")
        tracing_type = request.POST.get("t2")
        tracing_status = request.POST.get("t3")
        today = date.today()

        rows = read_details("addproduct").split("\n")
        record, index = "", 0

        for i, row in enumerate(rows[:-1]):
            arr = row.split("#")
            if arr[0] == "addproduct" and arr[1] == product_name:
                index = i
                record = (
                    f"{arr[0]}#{arr[1]}#{arr[2]}#{arr[3]}#{arr[4]}#"
                    f"{arr[5]}#{today}#{tracing_type}! {tracing_status}\n"
                )
                break

        for i, row in enumerate(rows[:-1]):
            if i != index:
                record += row + "\n"

        update_quantity_block(record)
        return render(request, "traceability/admin_screen.html", {"data": "Tracing details updated"})

    return redirect("update_tracing")


def view_tracing(request):
    try:
        rows = read_details("addproduct").split("\n")
    except:
        # If blockchain reading fails, initialize with sample data and use local storage
        try:
            initialize_sample_data()
        except:
            pass
        
        # Use local storage as fallback
        storage_path = get_local_storage_path()
        if os.path.exists(storage_path):
            with open(storage_path, 'r') as f:
                storage = json.load(f)
                products = []
                for product_data in storage.get('products', []):
                    blockchain_entry = product_data['blockchain_entry']
                    arr = blockchain_entry.split("#")
                    if len(arr) >= 7:
                        products.append({
                            "name": arr[1],
                            "price": arr[2],
                            "qty": arr[3],
                            "desc": arr[4],
                            "image": arr[5],
                            "last_update": arr[6],
                            "tracing_info": arr[7] if len(arr) > 7 else "Production State",
                        })
                return render(request, "traceability/view_tracing.html", {"products": products})
        
        # If no data exists, return empty
        return render(request, "traceability/view_tracing.html", {"products": []})
    
    products = []
    for row in rows[:-1]:
        arr = row.split("#")
        if arr[0] == "addproduct":
            products.append({
                "name": arr[1],
                "price": arr[2],
                "qty": arr[3],
                "desc": arr[4],
                "image": arr[5],
                "last_update": arr[6],
                "tracing_info": arr[7] if len(arr) > 7 else "Production State",
            })

    return render(request, "traceability/view_tracing.html", {"products": products})


# ------------------ Screen Views ------------------ #
def admin_screen(request):
    return render(request, "traceability/admin_screen.html")


def user_screen(request):
    username = request.session.get("username", "Guest")
    return render(request, "traceability/user_screen.html", {"data": f"Welcome {username}"})


def add_tracing(request):
    if request.method == "POST":
        product_name = request.POST.get("t1")
        tracing_type = request.POST.get("t2")
        tracing_status = request.POST.get("t3")
        location = request.POST.get("location", "")
        responsible_person = request.POST.get("responsible_person", "")
        notes = request.POST.get("notes", "")
        today = date.today()

        try:
            rows = read_details("addproduct").split("\n")
            record, index = "", 0

            for i, row in enumerate(rows[:-1]):
                arr = row.split("#")
                if arr[0] == "addproduct" and arr[1] == product_name:
                    index = i
                    # Enhanced tracing info with location and responsible person
                    tracing_info = f"{tracing_type}! {tracing_status}"
                    if location:
                        tracing_info += f" @ {location}"
                    if responsible_person:
                        tracing_info += f" - {responsible_person}"
                    if notes:
                        tracing_info += f" | Notes: {notes}"
                    
                    record = (
                        f"{arr[0]}#{arr[1]}#{arr[2]}#{arr[3]}#{arr[4]}#"
                        f"{arr[5]}#{today}#{tracing_info}\n"
                    )
                    break

            for i, row in enumerate(rows[:-1]):
                if i != index:
                    record += row + "\n"

            update_quantity_block(record)
            return render(request, "traceability/add_tracing.html", {"data": "Tracing details updated successfully!", "products": []})
        except:
            # Fallback to local storage update
            try:
                storage_path = get_local_storage_path()
                if os.path.exists(storage_path):
                    with open(storage_path, 'r') as f:
                        storage = json.load(f)
                    
                    # Update the product in local storage
                    for product_data in storage.get('products', []):
                        blockchain_entry = product_data['blockchain_entry']
                        arr = blockchain_entry.split("#")
                        if len(arr) >= 2 and arr[1] == product_name:
                            # Update tracing info
                            tracing_info = f"{tracing_type}! {tracing_status}"
                            if location:
                                tracing_info += f" @ {location}"
                            if responsible_person:
                                tracing_info += f" - {responsible_person}"
                            if notes:
                                tracing_info += f" | Notes: {notes}"
                            
                            # Update the blockchain entry
                            arr[6] = str(today)
                            if len(arr) >= 8:
                                arr[7] = tracing_info
                            else:
                                arr.append(tracing_info)
                            
                            product_data['blockchain_entry'] = "#".join(arr)
                            break
                    
                    # Save updated storage
                    with open(storage_path, 'w') as f:
                        json.dump(storage, f)
                    
                    return render(request, "traceability/add_tracing.html", {"data": "Tracing details updated successfully!", "products": []})
            except:
                pass
            
            return render(request, "traceability/add_tracing.html", {"data": "Error updating tracing information", "products": []})

    # Get products for the form
    try:
        rows = read_details("addproduct").split("\n")
        products = []
        for row in rows[:-1]:
            arr = row.split("#")
            if arr[0] == "addproduct":
                products.append({
                    "name": arr[1],
                    "price": arr[2],
                    "qty": arr[3],
                    "desc": arr[4],
                    "image": arr[5],
                    "last_update": arr[6],
                    "tracing_info": arr[7] if len(arr) > 7 else "Production State",
                })
    except:
        # Use local storage as fallback
        products = []
        storage_path = get_local_storage_path()
        if os.path.exists(storage_path):
            with open(storage_path, 'r') as f:
                storage = json.load(f)
                for product_data in storage.get('products', []):
                    blockchain_entry = product_data['blockchain_entry']
                    arr = blockchain_entry.split("#")
                    if len(arr) >= 7:
                        products.append({
                            "name": arr[1],
                            "price": arr[2],
                            "qty": arr[3],
                            "desc": arr[4],
                            "image": arr[5],
                            "last_update": arr[6],
                            "tracing_info": arr[7] if len(arr) > 7 else "Production State",
                        })

    return render(request, "traceability/add_tracing.html", {"products": products})
