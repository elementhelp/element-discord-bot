from supabase import create_client
import os

# preia datele din variabile de mediu
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================
# Funcții pentru USERS
# ==============================
def add_user(username: str):
    """Adaugă un user nou în tabelul users"""
    return supabase.table("users").insert({"username": username}).execute()

def get_users():
    """Ia toți userii din DB"""
    return supabase.table("users").select("*").execute()

# ==============================
# Funcții pentru ELEMENTS
# ==============================
def add_element(name: str, description: str):
    """Adaugă un element nou în tabelul elements"""
    return supabase.table("elements").insert({
        "name": name,
        "description": description
    }).execute()

def get_elements():
    """Ia toate elementele"""
    return supabase.table("elements").select("*").execute()

# ==============================
# Funcții pentru LOGS
# ==============================
def log_event(event: str):
    """Salvează un log"""
    return supabase.table("logs").insert({"event": event}).execute()
