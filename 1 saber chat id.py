from telegram.ext import Application, MessageHandler, filters

async def registrar_grupos(update, context):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    if chat_type in ["group", "supergroup"]:
        print(f"Bot recebeu mensagem do grupo ID = {chat_id}")
        # faça o registro em BD, arquivo etc.

def main():
    # Crie a aplicação (sem Updater)
    application = Application.builder().token("8139155308:AAEvx1a077ngaxPNpXfUUaBuRxWUPnO8Zr0").build()

    # Adicione os handlers
    application.add_handler(MessageHandler(filters.ALL, registrar_grupos))

    # Execute o polling
    application.run_polling()

if __name__ == "__main__":
    main()
