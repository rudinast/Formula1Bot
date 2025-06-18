from Models.db_models import Circuits

def format_circuit_info(c: Circuits) -> str:
    return (
        f"📍 <b>{c.name}</b>\n"
        f"🌍 Location: {c.location}, {c.country}\n"
        f"🔗 <a href='{c.url}'>Official Website</a>\n\n"
    )