import logging
import random
import schedule_logic
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from schedule_logic import build_full_schedule, load_student
from gemini_helpers import extract_from_photo, route_text, route_audio
from config import PONDERING_LIST, TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_wa_link(parent_number: str, message: str) -> str:
    import urllib.parse
    return f"https://wa.me/{parent_number}?text={urllib.parse.quote(message)}"

async def send_draft(update: Update, student_name: str, schedule_text: str):
    student = load_student(student_name)  # raises ValueError if not found
    wa_link = build_wa_link(student["parent_number"], schedule_text)
    await update.message.reply_text(f"{schedule_text}\n\n👉 Tap to open & send: {wa_link}")

async def dispatch(update: Update, intent, args):
    print(f"Dispatching intent: {intent}, args: {args}")
    await update.message.reply_text(f"Intent: {intent}, args: {args}")
    # if intent is None:
    #     await update.message.reply_text(
    #         "Sorry, I didn't catch a clear request. Try:\n"
    #         "• \"Show me Emmett's schedule\"\n"
    #         "• \"Edelle can't come 19 August\""
    #     )
    #     return
    # if intent == "get_full_schedule_for_student":
    #     text = build_full_schedule(name=args["name"])
    # elif intent == "report_absence":
    #     text = build_full_schedule(name=args["name"], specific_absent_list=[args["specific_absent_date"]])
    # else:
    #     await update.message.reply_text(f"I don't know how to handle '{intent}' yet.")
    #     return
    # await send_draft(update, args["name"], text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        intent, args = route_text(update.message.text)
        await dispatch(update, intent, args)
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")  # e.g. student not found in student_data.json
    except Exception:
        logger.exception("handle_text failed")
        await update.message.reply_text("⚠️ Something went wrong on my end — try rephrasing?")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(PONDERING_LIST[random.randint(0, len(PONDERING_LIST) - 1)]) 
        voice_file = await update.message.voice.get_file()
        audio_bytes = await voice_file.download_as_bytearray()
        intent, args = route_audio(bytes(audio_bytes))
        await dispatch(update, intent, args)
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
    except Exception:
        logger.exception("handle_voice failed")
        await update.message.reply_text("⚠️ Couldn't process that voice note — try again?")
        
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(PONDERING_LIST[random.randint(0, len(PONDERING_LIST) - 1)]) 
              
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        extracted_students = extract_from_photo(bytes(image_bytes))
        if not extracted_students:
            await update.message.reply_text("⚠️ Couldn't find any students in that photo.")
            return

        print(type(extracted_students))
        print(f"Extracted students: {extracted_students}")
     
        results = schedule_logic.update_terms_from_photo(extracted_students)

        # Summary line first, so you get the overview before scrolling through details
        ok_names = [r["name"] for r in results if r["ok"]]
        failed = [r for r in results if not r["ok"]]

        summary = f"📋 Processed {len(ok_names)}/{len(results)} students."
        if failed:
            summary += "\n\n❌ Couldn't save:\n" + "\n".join(f"• {r['name']}: {r['error']}" for r in failed)
        await update.message.reply_text(summary)

        # Then one message per successful student, with their draft + wa.me link
        for r in results:
            if not r["ok"]:
                continue
            if r["unclear_dates"]:
                await update.message.reply_text(
                    f"⚠️ {r['name']}: unclear dates {', '.join(r['unclear_dates'])} — worth double-checking."
                )
            if r["discrepancies"]:
                await update.message.reply_text(
                    f"❓ {r['name']}: possible unreported absence(s) {', '.join(r['discrepancies'])}. "
                    f"Confirm with e.g. \"{r['name']} was absent {r['discrepancies'][0]}\"."
                )
            await send_draft(update, r["name"], r["schedule_text"])

    except Exception:
        logger.exception("handle_photo failed")
        await update.message.reply_text("⚠️ Couldn't process that photo — try again?")
        
# Global safety net — catches anything that slips past the try/excepts above
async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Unexpected error — I've logged it, please try again.")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))  
    app.add_error_handler(global_error_handler)
    app.run_polling()

if __name__ == "__main__":
    main()