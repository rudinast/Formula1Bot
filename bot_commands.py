import string

import httpx
from sqlmodel import select
from telegram import Update, BotCommand, Bot
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler
from sqlalchemy.orm import Session

from Models.db_models import Drivers, Circuits, Seasons
from Models.response_models import RacesPerYear, RaceResultShort, TopDriverPoints, FastestPitstop
from Utility.response_beautifier import format_circuit_info
from constants import START_CONVERSATION, ASK_URL
from db.db import get_session

FASTAPI_URL = "http://localhost:8000"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is alive!")

async def get_drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/drivers/")

    if response.status_code != 200:
        await update.message.reply_text("⚠ Error contacting API. Please try again later.")
        return

    drivers_data = response.json()

    if not drivers_data:
        await update.message.reply_text("No drivers found.")
        return

    # Convert to model instances for cleaner access (optional but nice)
    drivers = [Drivers(**d) for d in drivers_data]

    # Build the reply
    reply_text = "Drivers List:\n"
    for driver in drivers:
        full_name = f"{driver.forename or ''} {driver.surname or ''}".strip()
        reply_text += f"- {full_name} (id: {driver.code or 'N/A'})\n"

    await send_chunkced_message(update,reply_text.strip())

async def start_circuits_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type the country name.")
    return START_CONVERSATION

async def start_oldest_drivers_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type the number of oldest drivers to get.")
    return START_CONVERSATION

async def start_race_results_year_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the year to see race results:")
    return START_CONVERSATION

async def start_top_drivers_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("How many top drivers would you like to see? (1-100)")
    return START_CONVERSATION

async def start_pitstop_year_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the year to see fastest pitstops:")
    return START_CONVERSATION

async def start_add_season_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the year of the season to add:")
    return START_CONVERSATION

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

async def get_circuits_by_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country = update.message.text

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/circuits/by-country/", params={"country": country})

    if response.status_code != 200:
        await update.message.reply_text("⚠ Error contacting API. Please try again later.")
        return ConversationHandler.END

    circuits_data = response.json()

    if not circuits_data:
        await update.message.reply_text(f"No circuits found for {country}.")
        return ConversationHandler.END

    # Convert to model instances (optional, for cleaner access)
    circuits = [Circuits(**c) for c in circuits_data]

    beautified_result = "\n".join([format_circuit_info(c) for c in circuits])
    await send_chunkced_message(update, beautified_result)

    return ConversationHandler.END

async def receive_limit(update, context):
    try:
        limit = int(update.message.text)
        if limit < 1 or limit > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a valid number between 1 and 100.")
        return START_CONVERSATION

    # Make request to FastAPI
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/drivers/oldest", params={"limit": limit})

    if response.status_code != 200:
        await update.message.reply_text("Something went wrong contacting the server.")
        return ConversationHandler.END

    drivers = [Drivers(**d) for d in response.json()]
    if not drivers:
        await update.message.reply_text("No drivers found.")
        return ConversationHandler.END

    # Format drivers
    msg = ""
    # No conversion to dicts — just use model instances
    for d in drivers:
        full_name = f"{d.forename} {d.surname}"
        msg += f"👤 <b>{full_name}</b>\n🌍 {d.nationality} | DOB: {d.dob}\n\n"
    await send_chunkced_message(update, msg.strip())
    return ConversationHandler.END


async def get_first_season(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/seasons/first")

    if response.status_code != 200:
        await update.message.reply_text("⚠ Error contacting API. Please try again later.")
        return

    season_data = response.json()
    if not season_data:
        await update.message.reply_text("No season found.")
        return

    # Optionally convert to model instance
    season = Seasons(**season_data)

    msg = (
        f"🏁 <b>First Season</b>\n"
        f"📅 Year: {season.year}\n"
        f"🔗 <a href='{season.url}'>More info</a>"
    )

    await update.message.reply_text(msg, parse_mode="HTML")


async def get_races_per_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/races/by-year")

    if response.status_code != 200:
        await update.message.reply_text("⚠ Error contacting API. Please try again later.")
        return

    races_data = response.json()
    if not races_data:
        await update.message.reply_text("No race data found.")
        return

    # Optional: convert to model instances
    races = [RacesPerYear(**r) for r in races_data]

    # Build reply
    msg = "<b>🏁 Races Per Year:</b>\n"
    for race in races:
        msg += f"📅 {race.year}: {race.total_races} races\n"

    await send_chunkced_message(update, msg.strip())


async def fetch_race_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    year_text = update.message.text
    try:
        year = int(year_text)
    except ValueError:
        await update.message.reply_text("❗ Please enter a valid year (e.g. 2020).")
        return START_CONVERSATION

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/races/results-by-year", params={"year": year})

    if response.status_code != 200:
        await update.message.reply_text("⚠ Error contacting API. Please try again later.")
        return ConversationHandler.END

    results_data = response.json()
    if not results_data:
        await update.message.reply_text(f"No race results found for {year}.")
        return ConversationHandler.END

    # Convert to model instances (optional for clean code)
    results = [RaceResultShort(**r) for r in results_data]

    # Build reply
    msg = f"<b>🏁 Race Results {year}:</b>\n"
    for r in results:
        msg += (
            f"📌 {r.race_name}\n"
            f"👤 {r.driver_name} | 🏎 {r.constructor_name}\n"
            f"🏅 Pos: {r.position}, Pts: {r.points}\n\n"
        )

    await send_chunkced_message(update, msg.strip())
    return ConversationHandler.END

async def fetch_top_drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    limit_text = update.message.text
    try:
        limit = int(limit_text)
        if limit < 1 or limit > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❗ Please enter a valid number between 1 and 100.")
        return START_CONVERSATION

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/drivers/top", params={"limit": limit})

    if response.status_code != 200:
        await update.message.reply_text("⚠ Error contacting API. Please try again later.")
        return ConversationHandler.END

    drivers_data = response.json()
    if not drivers_data:
        await update.message.reply_text("No top drivers found.")
        return ConversationHandler.END

    drivers = [TopDriverPoints(**d) for d in drivers_data]

    msg = "<b>🏁 Top Drivers:</b>\n"
    for d in drivers:
        msg += (
            f"👤 {d.driver_name}\n"
            f"📌 {d.race_name} ({d.race_year}) | 🏅 {d.points} points\n\n"
        )

    await send_chunkced_message(update, msg.strip())
    return ConversationHandler.END


async def fetch_fastest_pitstops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    year_text = update.message.text.strip()

    try:
        year = int(year_text)
    except ValueError:
        await update.message.reply_text("❗ Please enter a valid year (e.g. 2021).")
        return START_CONVERSATION

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/pitstops/fastest-by-year", params={"year": year})

    if response.status_code != 200:
        await update.message.reply_text("⚠ Error contacting API. Please try again later.")
        return ConversationHandler.END

    pitstops_data = response.json()
    if not pitstops_data:
        await update.message.reply_text(f"No fastest pitstops found for {year}.")
        return ConversationHandler.END

    pitstops = [FastestPitstop(**p) for p in pitstops_data]

    msg = f"<b>🏁 Fastest Pitstops in {year}:</b>\n"
    for p in pitstops:
        msg += (
            f"👤 {p.driver_name}\n"
            f"⏱ {p.duration:.3f}s on lap {p.lap}\n"
            f"📌 {p.race_name}\n\n"
        )

    await update.message.reply_text(msg.strip(), parse_mode="HTML")
    return ConversationHandler.END

async def receive_season_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    year_text = update.message.text.strip()
    try:
        year = int(year_text)
    except ValueError:
        await update.message.reply_text("❗ Please enter a valid year (e.g. 2024).")
        return START_CONVERSATION

    context.user_data["season_year"] = year
    await update.message.reply_text("Please enter the URL for the season:")
    return ASK_URL

async def receive_season_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url_text = update.message.text.strip()

    if not url_text:
        await update.message.reply_text("❗ URL cannot be empty. Please enter a valid URL:")
        return ASK_URL

    season_data = {
        "year": context.user_data["season_year"],
        "url": url_text
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FASTAPI_URL}/seasons/add", json=season_data)

    if response.status_code == 201:
        season = response.json()
        await update.message.reply_text(
            f"✅ Season added!\nYear: {season['year']}\nURL: {season['url']}"
        )
    elif response.status_code == 400:
        await update.message.reply_text("⚠ Season already exists.")
    else:
        await update.message.reply_text("⚠ Failed to add season. Please try again later.")

    return ConversationHandler.END

async def send_chunkced_message(update: Update, message: string):
    max_len = 4000
    chunks = [message[i:i + max_len] for i in range(0, len(message), max_len)]
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode="HTML")