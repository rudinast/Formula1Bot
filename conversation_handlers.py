from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

from bot_commands import start_circuits_conversation, get_circuits_by_country, cancel_conversation, \
    start_oldest_drivers_conversation, receive_limit, start_race_results_year_conversation, fetch_race_results, \
    fetch_top_drivers, start_top_drivers_conversation, start_pitstop_year_conversation, fetch_fastest_pitstops, \
    start_add_season_conversation, receive_season_year, receive_season_url
from constants import START_CONVERSATION, ASK_URL

# Create the ConversationHandler
circuits_by_country_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("circuits_by_country", start_circuits_conversation)],
    states={
        START_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_circuits_by_country)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation)],
)

oldest_drivers_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("oldest_drivers", start_oldest_drivers_conversation)],
    states={
        START_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_limit)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation)],
)

race_results_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("year_race_results", start_race_results_year_conversation)],
    states={
        START_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_race_results)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation)],
)

top_drivers_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("top_drivers", start_top_drivers_conversation)],
    states={
        START_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_top_drivers)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation)],
)

pitstop_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("fastest_pitstops", start_pitstop_year_conversation)],
    states={
        START_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_fastest_pitstops)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation)],
)

add_season_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("add_season", start_add_season_conversation)],
    states={
        START_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_season_year)],
        ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_season_url)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation)],
)