import telegram_bot
import asyncio
import uvicorn
from api import app

async def start_fastapi():
    """Run FastAPI server."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot():
    """Run Telegram bot."""
    await  telegram_bot.startup()
    print("Bot is running...")

async def main():
    await asyncio.gather(
        start_fastapi(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())