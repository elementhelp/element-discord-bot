from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import uuid

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user(user_id: int):
    result = supabase.table("users").select("*").eq("user_id", user_id).execute()
    if result.data:
        return result.data[0]
    return None

def create_user_if_not_exists(user_id: int):
    user = get_user(user_id)
    if not user:
        new_id = str(uuid.uuid4())
        supabase.table("users").insert({
            "user_id": user_id,
            "unique_id": new_id,
            "webhook": None,
            "username": None,
            "autojoiner_key": None,
            "script_code": None
        }).execute()
        return get_user(user_id)
    return user

def update_user(user_id: int, data: dict):
    supabase.table("users").update(data).eq("user_id", user_id).execute()

def set_webhook(user_id: int, webhook: str):
    update_user(user_id, {"webhook": webhook})

def set_username(user_id: int, username: str):
    update_user(user_id, {"username": username})

def generate_script(user_id: int):
    user = create_user_if_not_exists(user_id)
    script_code = f'-- Element X script\nlocal id = "{user["unique_id"]}"\nprint("Running script for ID:", id)'
    update_user(user_id, {"script_code": script_code})
    return user["unique_id"], script_code

def generate_autojoiner_key(user_id: int):
    key = str(uuid.uuid4())
    update_user(user_id, {"autojoiner_key": key})
    return key
