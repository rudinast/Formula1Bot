from fastapi import FastAPI, Request
from telegram import Update, Bot, BotCommand
from telegram.ext import Application, CommandHandler

from api import app
from bot_commands import get_drivers, start_command, get_first_season, get_races_per_year
from conversation_handlers import circuits_by_country_conv_handler, oldest_drivers_conv_handler, \
    race_results_conv_handler, top_drivers_conv_handler, pitstop_conv_handler, add_season_conv_handler

BOT_TOKEN = "7716059869:AAHNkFAV1pex4mQA3Yj8WEJ6W3Y_ZElFwEI"
WEBHOOK_URL = "https://9c83-146-158-59-72.ngrok-free.app/webhook"

bot_app = Application.builder().token(BOT_TOKEN).build()

async def startup():
    # Initialize bot_app
    await bot_app.initialize()
    await bot_app.start()

    await setup_webhook()  # First set webhook
    await set_commands()

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    print("=== WEBHOOK CALLED ===")
    print(data)  # <- See if you get incoming data
    update = Update.de_json(data, bot_app.bot)

    await bot_app.process_update(update)
    return {"ok": True}

async def setup_webhook():
    bot = Bot(token=BOT_TOKEN)
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        print(f"Setting webhook to {WEBHOOK_URL}")
        await bot.set_webhook(url=WEBHOOK_URL)
        print("Webhook set!")
    else:
        print(f"Webhook already set to {WEBHOOK_URL}")

async def set_commands():
    bot_app.add_handler(CommandHandler("drivers", get_drivers))
    bot_app.add_handler(CommandHandler("first_season", get_first_season))
    bot_app.add_handler(CommandHandler("races_per_year", get_races_per_year))
    bot_app.add_handler(CommandHandler("start", start_command))

    bot_app.add_handler(circuits_by_country_conv_handler)
    bot_app.add_handler(oldest_drivers_conv_handler)
    bot_app.add_handler(race_results_conv_handler)
    bot_app.add_handler(top_drivers_conv_handler)
    bot_app.add_handler(pitstop_conv_handler)
    bot_app.add_handler(add_season_conv_handler)

    bot = Bot(token=BOT_TOKEN)

    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="drivers", description="List available drivers"),
        BotCommand(command="circuits_by_country", description="Get list of all circuits ever held in a specific country"),
        BotCommand(command="oldest_drivers", description="Get list of a number of oldest drivers"),
        BotCommand(command="first_season", description="Show first season"),
        BotCommand(command="races_per_year", description="List of races for each year"),
        BotCommand(command="year_race_results", description="List of races results for specified year"),
        BotCommand(command="top_drivers", description="List of top drivers"),
        BotCommand(command="fastest_pitstops", description="Fastest pitstop of the year"),
        BotCommand(command="add_season", description="Add new season"),
        BotCommand(command="cancel", description="Cancel any long operation")
    ]

    await bot.set_my_commands(commands)
    print("Commands set!")