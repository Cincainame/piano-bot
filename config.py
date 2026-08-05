import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

PONDERING_LIST = [
    "Hmm... let me think about this one.",
    "Give me a second, my brain is buffering.",
    "Hold on, I need to pretend I'm not confused.",
    "Interesting... you really chose this question.",
    "Let me untangle this mess.",
    "Alright, let's figure this out."
    "Okay, this is actually harder than it looks.",
    "Give me a moment, I need to work overtime.",
    "My imaginary coffee is not helping, but I'll try.",
    "Let me put my thoughts in order before I embarrass myself.",
    "This one needs a little more brain power.",
    "I was not expecting that plot twist.",
    "You really made me think today, huh?",
    "Okay, I need a minute for this one.",
    "Let me stare into the void for a moment.",
    "Processing... with emotional damage.",
    "I need to consult my last remaining brain cell.",
    "My neurons are filing a complaint.",
    "The gears are turning... slowly.",
    "I'm going to need a little more than three brain cells for this.",
    "Please wait while I argue with myself.",
    "My thoughts are currently fighting in the arena.",
    "Three possible answers entered. Only one survives.",
    "I have opened 17 imaginary tabs.",
    "My brain has left the chat temporarily.",
    "I asked myself for help. It did not go well.",
    "I am experiencing a minor intellectual crisis.",
    "The answer is somewhere... probably.",
    "I know this. I just need to convince myself.",
    "My confidence and my calculations are currently negotiating.",
    "Running emergency brain maintenance.",
    "Rebooting my common sense module.",
    "My thoughts are loading in 4K.",
    "The hamster powering my brain is taking a break."
]