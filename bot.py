import discord
from discord import app_commands
import random
import string
import os

# ================= CONFIG =================

TOKEN = os.getenv("MTQ5OTg5MjAxOTcxODM4OTgzMQ.GFQBvG.6NQRU1oIANE3Jw4291a3Iyhkb5FWD1t1MEGSUk")

ADMIN_IDS = {1032772227453698178, 1114371072360468580}

# Use absolute path to avoid bugs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "keys.txt")
USED_FILE = os.path.join(BASE_DIR, "used_keys.txt")

# ================= KEY GENERATION =================

def generate_key():
    part = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ZNRX-{part()}-{part()}-{part()}"

def save_key(key):
    with open(KEY_FILE, "a") as f:
        f.write(key.strip().upper() + "\n")

# ================= LOAD SYSTEM =================

def load_keys():
    if not os.path.exists(KEY_FILE):
        return set()

    with open(KEY_FILE, "r") as f:
        return set(line.strip().upper() for line in f if line.strip())


def load_used_keys():
    if not os.path.exists(USED_FILE):
        return set()

    with open(USED_FILE, "r") as f:
        return set(line.strip().upper() for line in f if line.strip())

def mark_used(key):
    key = key.strip().upper()

    with open(USED_FILE, "a") as f:
        f.write(key + "\n")

    print(f"KEY MARKED USED: {key}")

# ================= KEY VALIDATION =================

def is_valid_key(key):
    key = key.strip().upper()

    keys = load_keys()
    used = load_used_keys()

    print(f"DEBUG KEY: {key}")
    print(f"ALL KEYS: {keys}")
    print(f"USED KEYS: {used}")

    if key not in keys:
        return "invalid"

    if key in used:
        return "used"

    return "valid"

# ================= DISCORD BOT =================

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ================= GENERATE KEY =================

@tree.command(name="generate-key", description="Generate a license key")
async def gen_key(interaction: discord.Interaction):

    if interaction.user.id not in ADMIN_IDS:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    key = generate_key()
    save_key(key)

    await interaction.response.send_message(
        f"🔑 **New Key Generated:**\n```{key}```\n(click to copy)",
        ephemeral=True
    )

# ================= USE KEY (ONE-TIME) =================

@tree.command(name="use-key", description="Use a key (ONE TIME ONLY)")
async def use_key(interaction: discord.Interaction, key: str):

    key = key.strip().upper()

    # Load fresh every time
    keys = load_keys()
    used = load_used_keys()

    print("----- DEBUG -----")
    print("INPUT:", key)
    print("ALL KEYS:", keys)
    print("USED KEYS:", used)
    print("-----------------")

    if key not in keys:
        await interaction.response.send_message("❌ Invalid key", ephemeral=True)
        return

    if key in used:
        await interaction.response.send_message("❌ Key already used", ephemeral=True)
        return

    # WRITE IMMEDIATELY
    with open(USED_FILE, "a") as f:
        f.write(key + "\n")

    await interaction.response.send_message(
        "✅ Key activated\n🔒 This key is now permanently locked",
        ephemeral=True
    )

# ================= READY =================

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot logged in as {client.user}")

# ================= RUN =================

client.run(TOKEN)