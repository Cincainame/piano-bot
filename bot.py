import logging
import json
import random
import roster_logic
import schedule_logic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from schedule_logic import build_full_schedule, load_student
from gemini_helpers import extract_from_photo, route_text, route_text_with_context, route_audio
from config import PONDERING_LIST, TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PENDING_ADD_STUDENT_KEY = "pending_add_student"
ADD_STUDENT_CONFIRM_CALLBACK = "add_student_confirm"
ADD_STUDENT_EDIT_CALLBACK = "add_student_edit"
ADD_STUDENT_CANCEL_CALLBACK = "add_student_cancel"

def build_wa_link(parent_number: str, message: str) -> str:
    import urllib.parse
    return f"https://wa.me/{parent_number}?text={urllib.parse.quote(message)}"


def _get_pending_add_student(context: ContextTypes.DEFAULT_TYPE):
    return context.user_data.get(PENDING_ADD_STUDENT_KEY)


def _clear_pending_add_student(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop(PENDING_ADD_STUDENT_KEY, None)


def _set_pending_add_student(context: ContextTypes.DEFAULT_TYPE, args: dict, stage: str):
    context.user_data[PENDING_ADD_STUDENT_KEY] = {
        "intent": "add_student_to_student_roster",
        "args": args,
        "stage": stage,
    }


def _pending_add_student_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Confirm ✅", callback_data=ADD_STUDENT_CONFIRM_CALLBACK),
            InlineKeyboardButton("Edit ✏️", callback_data=ADD_STUDENT_EDIT_CALLBACK),
            InlineKeyboardButton("Cancel ❌", callback_data=ADD_STUDENT_CANCEL_CALLBACK),
        ]
    ])


def _pending_add_student_context(pending: dict) -> str:
    return (
        "You are revising a pending Telegram action.\n"
        "Current intent: add_student_to_student_roster\n"
        f"Current args: {json.dumps(pending.get('args', {}), ensure_ascii=False)}\n\n"
        "The user will now describe only the change they want, for example:\n"
        "- change the name to Jayson\n"
        "- change the time to 6pm-6:30pm\n\n"
        "Update the current action using the user's correction. Keep all fields that are not mentioned unchanged."
    )


def _pending_add_student_summary(args: dict) -> str:
    return (
        "You sure this correct ah:\n"
        f"• name: {args.get('name')}\n"
        f"• start time: {args.get('start_time')}\n"
        f"• end time: {args.get('end_time')}"
    )


async def _prompt_add_student_confirmation(message, context: ContextTypes.DEFAULT_TYPE, args: dict):
    _set_pending_add_student(context, args, stage="awaiting_confirmation")
    await message.reply_text(
        _pending_add_student_summary(args) + "\n\nWhat would you like to do next?",
        reply_markup=_pending_add_student_keyboard(),
    )


async def _finalize_add_student(message, context: ContextTypes.DEFAULT_TYPE, args: dict):
    roster_logic.add_student_to_student_roster(
        name=args["name"],
        start_time=args["start_time"],
        end_time=args["end_time"],
    )
    _clear_pending_add_student(context)
    await message.reply_text(f"Added {args['name']} to the roster.")
    await message.reply_text(f"Updated roster:\n{roster_logic.timetable_to_text()}")

async def send_draft(update: Update, student_name: str, schedule_text: str):
    student = load_student(student_name)  # raises ValueError if not found
    wa_link = build_wa_link(student["parent_number"], schedule_text)
    await update.message.reply_text(f"{schedule_text}\n\n👉 Tap to open & send: {wa_link}")

async def dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE, intent, args):
    await update.message.reply_text(f"Intent: {intent}, args: {args}")

    reply_text = ""
    for key, value in args.items():
        if value is None or value == "None" or value == "":
            reply_text += f"⚠️ Missing required argument: {key}\n"
    if reply_text:
        await update.message.reply_text(reply_text)
        return
    if intent == "get_student_roster":
        roster = roster_logic.timetable_to_text()
        await update.message.reply_text(f"Current student roster:\n{roster}")
    elif intent == "add_student_to_student_roster":
        await _prompt_add_student_confirmation(update.message, context, args)
    elif intent is None:
        await update.message.reply_text(
            "Sorry, I didn't catch a clear request. Try:\n"
            "• \"Show me Emmett's schedule\"\n"
            "• \"Edelle can't come 19 August\""
        )
        return
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
        pending_add_student = _get_pending_add_student(context)
        if pending_add_student:
            if pending_add_student.get("stage") == "editing":
                intent, args = route_text_with_context(
                    update.message.text,
                    _pending_add_student_context(pending_add_student),
                )

                if intent != "add_student_to_student_roster" or not args:
                    await update.message.reply_text(
                        "I couldn't understand that change. Try something like:\n"
                        '• "change the name to Jayson"\n'
                        '• "change the time to 6pm-6:30pm"'
                    )
                    return

                merged_args = {**pending_add_student.get("args", {}), **args}
                _set_pending_add_student(context, merged_args, stage="awaiting_confirmation")
                await update.message.reply_text(
                    _pending_add_student_summary(merged_args) + "\n\nWhat would you like to do next?",
                    reply_markup=_pending_add_student_keyboard(),
                )
                return

            await update.message.reply_text(
                "Please use the buttons below to confirm, edit, or cancel this pending action."
            )
            return

        intent, args = route_text(update.message.text)
        await dispatch(update, context, intent, args)
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
        await dispatch(update, context, intent, args)
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


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    pending_add_student = _get_pending_add_student(context)
    if not pending_add_student:
        await query.answer("This request is no longer pending.", show_alert=True)
        return

    if query.data == ADD_STUDENT_CONFIRM_CALLBACK:
        try:
            await query.answer()
            await query.message.edit_reply_markup(reply_markup=None)
            await _finalize_add_student(query.message, context, pending_add_student["args"])
        except ValueError as e:
            await query.message.reply_text(f"⚠️ {e}")
            await _clear_pending_add_student(context)
        return

    if query.data == ADD_STUDENT_EDIT_CALLBACK:
        pending_add_student["stage"] = "editing"
        context.user_data[PENDING_ADD_STUDENT_KEY] = pending_add_student
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "What would you like to change?\n"
            'You can say something like "change the name to Jayson" or '
            '"change the time to 6pm-6:30pm".'
        )
        return

    if query.data == ADD_STUDENT_CANCEL_CALLBACK:
        _clear_pending_add_student(context)
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text("Cancelled.")
        return

    await query.answer("Unknown action.", show_alert=True)
        
# Global safety net — catches anything that slips past the try/excepts above
async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Unexpected error — I've logged it, please try again.")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))  
    app.add_error_handler(global_error_handler)
    app.run_polling()

if __name__ == "__main__":
    main()