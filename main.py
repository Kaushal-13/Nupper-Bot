import telebot
from dotenv import load_dotenv
from nup_pdf import nup
from telebot.types import InputFile

import os

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(bot_token)

# Ensure input and output directories exist
os.makedirs("input_files", exist_ok=True)
os.makedirs("output_files", exist_ok=True)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(
        message, "Howdy, how are you doing? Send me a PDF file, and I will n-up it for you!"
    )
    bot.send_document(message.chat.id, InputFile("sample.pdf"))


@bot.message_handler(content_types=['document'])
def handle_document(message):
    bot.reply_to(
        message, "I have received the file and will process it shortly.")

    # Check if the file is a PDF
    if message.document.mime_type == 'application/pdf':
        try:
            # Download the file
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            print(downloaded_file)
            # Save the file locally
            input_path = f"input_files/{message.document.file_name}"
            with open(input_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Generate the output file path
            output_path = f"output_files/{message.document.file_name}-nupped.pdf"

            # Perform N-Up processing
            nup(input_path, output_path)

            # Send the processed file back to the user

            print(output_path)
            print("hello")
            bot.send_document(message.chat.id, InputFile(output_path))
            bot.reply_to(message, "Here is your processed PDF!")

            # Delete files after processing
            os.remove(input_path)
            os.remove(output_path)
            print(f"Deleted files: {input_path}, {output_path}")

        except Exception as e:
            bot.reply_to(message, f"An error occurred: {e}")
            print(f"Error: {e}")
    else:
        bot.reply_to(message, "Please send a valid PDF file.")


# Start polling
bot.infinity_polling(timeout=120, long_polling_timeout=120)
