from supabase import create_client
import os

# Conectare la Supabase
SUPABASE_URL = os.getenv("https://vwvpvaeculfzerrrpzyr.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3dnB2YWVjdWxmemVycnJwenlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5ODI0MDQsImV4cCI6MjA3MjU1ODQwNH0.HSXwT7iFCmxr62eKBn36xM4_P_gv_wyTvCo7b93bWWw")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================
# USERS
# ==============================
def add_user(username: str):
    return supabase.table("users").insert({"username": username}).execute()

def get_users():
    return supabase.table("users").select("*").execute()

# ==============================
# ELEMENTS
# ==============================
def add_element(name: str, description: str):
    return supabase.table("elements").insert({
        "name": name,
        "description": description
    }).execute()

def get_elements():
    return supabase.table("elements").select("*").execute()

# ==============================
# LOGS
# ==============================
def log_event(event: str):
    return supabase.table("logs").insert({"event": event}).execute()
