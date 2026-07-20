import os
import time
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
import pyrogram
import pyrogram.enums
import random
import aiohttp

# Configuration
API_ID = int(os.environ.get("API_ID", "2040"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# Initialize client with StringSession
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Global state
START_TIME = time.time()
AFK_MODE = False
AFK_REASON = ""
AFK_TIME = None


def get_uptime():
    diff = time.time() - START_TIME
    hours, remainder = divmod(int(diff), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def get_uptime_from(start):
    diff = time.time() - start
    hours, remainder = divmod(int(diff), 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


# Command: .alive
@app.on_message(filters.me & filters.command("alive", prefixes="."))
async def alive_cmd(client, message: Message):
    uptime = get_uptime()
    await message.edit_text(
        f"✅ **Userbot is Alive!**\n"
        f"⏱ **Uptime:** `{uptime}`\n"
        f"🐍 **Pyrogram** v2.0.106"
    )


# Command: .ping
@app.on_message(filters.me & filters.command("ping", prefixes="."))
async def ping_cmd(client, message: Message):
    start = time.time()
    await message.edit_text("🏓 Pong!")
    end = time.time()
    ms = (end - start) * 1000
    await message.edit_text(f"🏓 **Pong!** `{ms:.2f}ms`")


# Command: .id
@app.on_message(filters.me & filters.command("id", prefixes="."))
async def id_cmd(client, message: Message):
    text = f"💡 **Chat ID:** `{message.chat.id}`\n"
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        text += f"👤 **User ID:** `{user.id}`\n"
        text += f"📛 **Name:** {user.first_name or ''} {user.last_name or ''}"
    else:
        text += f"👤 **Your ID:** `{message.from_user.id}`"
    await message.edit_text(text)


# Command: .info
@app.on_message(filters.me & filters.command("info", prefixes="."))
async def info_cmd(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    full_user = await client.get_users(user.id)
    name = f"{full_user.first_name or ''} {full_user.last_name or ''}".strip()
    username = f"@{full_user.username}" if full_user.username else "N/A"
    dc_id = full_user.dc_id or "Unknown"

    text = (
        f"👤 **User Info**\n"
        f"├ **Name:** {name}\n"
        f"├ **Username:** {username}\n"
        f"├ **ID:** `{full_user.id}`\n"
        f"├ **DC:** {dc_id}\n"
        f"└ **Bot:** {'Yes' if full_user.is_bot else 'No'}"
    )
    await message.edit_text(text)


# Command: .tr [lang] — supports reply + inline text
# Usage: .tr hi (reply to msg) OR .tr hi Hello World (inline text)
@app.on_message(filters.me & filters.command("tr", prefixes="."))
async def translate_cmd(client, message: Message):
    try:
        from googletrans import Translator
        translator = Translator()

        args = message.text.split(None, 2)
        dest_lang = args[1] if len(args) > 1 else "en"

        # Get text: inline text OR replied message
        if len(args) > 2:
            # .tr hi Hello World (inline)
            text = args[2]
        elif message.reply_to_message and message.reply_to_message.text:
            # Reply to message
            text = message.reply_to_message.text
        else:
            await message.edit_text(
                "⚠️ **Usage:**\n"
                "`.tr hi` — reply kisi message pe\n"
                "`.tr en Hello kaise ho` — inline text"
            )
            return

        result = translator.translate(text, dest=dest_lang)
        await message.edit_text(
            f"🌐 **Translation** `{result.src}` → `{dest_lang}`\n\n{result.text}"
        )
    except Exception as e:
        await message.edit_text(f"❌ Translation error: `{e}`")


# Command: .tts
@app.on_message(filters.me & filters.command("tts", prefixes="."))
async def tts_cmd(client, message: Message):
    try:
        from gtts import gTTS
        import tempfile

        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or provide text.")
                return
            text = args[1]

        await message.edit_text("🔊 Converting to speech...")
        tts = gTTS(text=text, lang="en")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.save(f.name)
            await message.delete()
            await client.send_voice(message.chat.id, f.name)
            os.unlink(f.name)
    except Exception as e:
        await message.edit_text(f"❌ TTS error: `{e}`")


# Command: .del
@app.on_message(filters.me & filters.command("del", prefixes="."))
async def del_cmd(client, message: Message):
    try:
        if message.reply_to_message:
            await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        await message.edit_text(f"❌ Delete error: `{e}`")


# Command: .purge
@app.on_message(filters.me & filters.command("purge", prefixes="."))
async def purge_cmd(client, message: Message):
    try:
        if not message.reply_to_message:
            await message.edit_text("⚠️ Reply to a message to start purge from.")
            return

        chat_id = message.chat.id
        start_id = message.reply_to_message.id
        end_id = message.id
        msg_ids = list(range(start_id, end_id + 1))

        count = 0
        for i in range(0, len(msg_ids), 100):
            chunk = msg_ids[i:i+100]
            await client.delete_messages(chat_id, chunk)
            count += len(chunk)

        status = await client.send_message(chat_id, f"🗑 **Purged {count} messages.**")
        await asyncio.sleep(2)
        await status.delete()
    except Exception as e:
        await message.edit_text(f"❌ Purge error: `{e}`")


# Command: .afk [reason]
@app.on_message(filters.me & filters.command("afk", prefixes="."))
async def afk_cmd(client, message: Message):
    global AFK_MODE, AFK_REASON, AFK_TIME
    args = message.text.split(None, 1)
    AFK_REASON = args[1] if len(args) > 1 else "No reason given."
    AFK_MODE = True
    AFK_TIME = time.time()
    await message.edit_text(f"💤 **AFK Mode Enabled**\nReason: {AFK_REASON}")


# Command: .unafk
@app.on_message(filters.me & filters.command("unafk", prefixes="."))
async def unafk_cmd(client, message: Message):
    global AFK_MODE, AFK_REASON, AFK_TIME
    if AFK_MODE:
        AFK_MODE = False
        duration = get_uptime_from(AFK_TIME) if AFK_TIME else "0s"
        AFK_REASON = ""
        AFK_TIME = None
        await message.edit_text(f"✅ **Back online!** Was AFK for {duration}")
    else:
        await message.edit_text("ℹ️ You weren't AFK.")


# AFK auto-reply handler
@app.on_message(filters.mentioned & filters.incoming & ~filters.me)
async def afk_reply(client, message: Message):
    if AFK_MODE:
        duration = get_uptime_from(AFK_TIME) if AFK_TIME else "0s"
        await message.reply_text(
            f"💤 **I'm currently AFK** ({duration})\n"
            f"📝 **Reason:** {AFK_REASON}"
        )


# Command: .speedtest
@app.on_message(filters.me & filters.command("speedtest", prefixes="."))
async def speedtest_cmd(client, message: Message):
    try:
        import speedtest
        await message.edit_text("⏳ **Running speedtest...**")
        st = speedtest.Speedtest()
        st.get_best_server()
        st.download()
        st.upload()
        results = st.results.dict()

        download = results["download"] / 1_000_000
        upload = results["upload"] / 1_000_000
        ping = results["ping"]
        server = results["server"]["name"]
        country = results["server"]["country"]

        await message.edit_text(
            f"🚀 **Speedtest Results**\n"
            f"├ **Download:** `{download:.2f} Mbps`\n"
            f"├ **Upload:** `{upload:.2f} Mbps`\n"
            f"├ **Ping:** `{ping:.2f} ms`\n"
            f"└ **Server:** {server}, {country}"
        )
    except Exception as e:
        try:
            await message.edit_text(f"❌ Speedtest error: `{e}`")
        except:
            await message.reply_text(f"❌ Speedtest error: `{e}`")


# Command: .calc [expression]
@app.on_message(filters.me & filters.command("calc", prefixes="."))
async def calc_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.calc <expression>`")
            return

        expr = args[1]
        allowed_chars = set("0123456789+-*/.() %")
        if not all(c in allowed_chars for c in expr.replace(" ", "")):
            await message.edit_text("⚠️ Invalid expression. Only math operators allowed.")
            return

        result = eval(expr)
        await message.edit_text(f"🧮 `{expr}` = **{result}**")
    except ZeroDivisionError:
        await message.edit_text("⚠️ Division by zero!")
    except Exception as e:
        await message.edit_text(f"❌ Calc error: `{e}`")


# Command: .help
@app.on_message(filters.me & filters.command("help", prefixes="."))
async def help_cmd(client, message: Message):
    help_text = """📚 **Userbot Commands** (prefix: `.`)

🔧 **Utility:**
├ `.alive` — Status & uptime
├ `.ping` — Response time
├ `.id` — User/chat ID
├ `.info` — User info
├ `.tr [lang] [text]` — Translate
├ `.tts` — Text to speech
├ `.del` — Delete replied msg
├ `.purge` — Bulk delete
├ `.afk` / `.unafk` — AFK mode
├ `.speedtest` — Speed test
├ `.calc [expr]` — Calculator

👤 **Profile:**
├ `.bio [text]` — Update bio
├ `.name [first] [last]` — Change name
├ `.pfp` — Change profile pic
├ `.stats` — Account info
├ `.tg @user` — Full user details
├ `.clone @user` — Clone profile

📱 **Social/Info:**
├ `.chatinfo` — Chat details
├ `.admins` — Group admins
├ `.invite` — Invite link
├ `.top10` / `.topmsg` — Active users
├ `.msgcount @user` — Message count
├ `.activity` — Chat activity

🎵 **Media:**
├ `.yt [query]` — YouTube video
├ `.ytm [query]` — YouTube audio
├ `.sticker` — Image/GIF to sticker
├ `.resize [WxH]` — Resize image
├ `.pdf` — Images to PDF
├ `.ss [url]` — Website screenshot
├ `.down [url]` — Download file
├ `.ocr` — Extract text from image
├ `.invert` / `.blur` / `.gray` / `.enhance`
├ `.dlall [@chat]` — Download all media

🤖 **AI:**
├ `.ai [text]` — Chat with AI

💬 **Text Effects:**
├ `.mock` / `.fancy` / `.reverse` / `.ascii`
├ `.bold` / `.italic` / `.spoiler` / `.strike`
├ `.type [text]` — Typing effect

😎 **Fun:**
├ `.joke` — Random joke
├ `.quote` — Inspirational quote
├ `.flip` / `.roll` / `.roast [name]`

🔍 **Search/Info:**
├ `.wiki [query]` — Wikipedia
├ `.weather [city]` — Weather
├ `.crypto [coin]` — Crypto price
├ `.currency [amt] [from] [to]` — Convert
├ `.news [topic]` — Latest news
├ `.ip [address]` — IP lookup
├ `.search [text]` — Chat search
├ `.bin [bin]` — BIN info

💳 **Card Tools:**
├ `.gen [bin|mm|yy|cvv] [n]` — Generate cards

🎭 **Chat Actions:**
├ `.typing [sec]` — ⌨️ Typing
├ `.recording [sec]` — 🎤 Recording
├ `.uploading [sec]` — 📤 Uploading
├ `.playing [sec]` — 🎮 Playing
├ `.cancel` — Stop action

🛡️ **Privacy:**
├ `.ghost [sec]` — Auto delete
├ `.disappear [sec]` — Chat TTL
├ `.encrypt` / `.decrypt`

⚡ **Automation:**
├ `.autoreply [trigger] | [resp]`
├ `.delauto [trigger]` / `.listauto`
├ `.autofwd @src @dst`
├ `.forward [chat_id]`
├ `.spam [n] [text]`

🛡️ **Group Admin:**
├ `.promote` / `.demote`
├ `.title [text]` — Admin title
├ `.ban` / `.unban`
├ `.kick` / `.mute` / `.unmute`
├ `.tmute [10m/2h/1d]` — Timed mute
├ `.warn [reason]` (3=ban) / `.unwarn`
├ `.pin` / `.unpin`

📁 **Scrape:**
├ `.scr @group [n]` — Scrape cards
├ `.scrfile @group` — Scrape files
├ `.fwd @src @dst [n]` — Bulk forward
├ `.nuke` — Delete own msgs

📦 **Tools:**
├ `.qr [text]` — QR code
├ `.short [url]` — Shorten URL
├ `.paste [text]` — Upload to paste
├ `.base64 encode/decode`

📊 **Productivity:**
├ `.remind [time] [text]`
├ `.notes save/list`
├ `.todo add/list/done`

📧 **Mail (mail.tm):**
├ `.mail new` / `.mail inbox`
├ `.mail read` / `.mail otp`
├ `.mail watch [sec]`
├ `.mail delete` / `.mail domains`
├ `.mail chatpdf` — ChatPDF checkout

🔐 **Checkout Generators:**
├ `.setsk sk_live_xxx` — Set Stripe SK (global)
├ `.ch [amount]` — Generate Stripe checkout
├ `.inb [amount]` — Generate Stripe invoice
├ `.pi [amount]` — Payment Intent
├ `.pl [amount]` — Payment Link (shareable)
├ `.skinfo` — SK account info
├ `.balance` — Account balance
├ `.charges [n]` — Recent charges
├ `.customers [n]` — Recent customers
├ `.refund [id]` — Refund payment
├ `.coupon [%]` — Create discount coupon
├ `.freecad [amount]` — FreeCAD Stripe
├ `.1vpn [monthly/yearly]` — 1VPN

└ `.help` — Show this help
"""
    await message.edit_text(help_text)


import random
import json

# ==========================================
# AUTO-REPLY STATE
# ==========================================
AUTO_REPLIES = {}


# ==========================================
# 📱 SOCIAL/INFO COMMANDS
# ==========================================

# Command: .chatinfo
@app.on_message(filters.me & filters.command("chatinfo", prefixes="."))
async def chatinfo_cmd(client, message: Message):
    try:
        chat = await client.get_chat(message.chat.id)
        members = getattr(chat, 'members_count', 'N/A')
        desc = getattr(chat, 'description', 'N/A') or 'N/A'
        chat_type = str(chat.type).split('.')[-1].title()
        text = (
            f"📱 **Chat Info**\n"
            f"├ **Name:** {chat.title or chat.first_name or 'N/A'}\n"
            f"├ **ID:** `{chat.id}`\n"
            f"├ **Type:** {chat_type}\n"
            f"├ **Members:** {members}\n"
            f"└ **Description:** {desc[:100]}"
        )
        await message.edit_text(text)
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


# Command: .admins
@app.on_message(filters.me & filters.command("admins", prefixes="."))
async def admins_cmd(client, message: Message):
    try:
        await message.edit_text("⏳ Fetching admins...")
        admins = []
        async for member in client.get_chat_members(message.chat.id, filter=pyrogram.enums.ChatMembersFilter.ADMINISTRATORS):
            name = f"{member.user.first_name or ''} {member.user.last_name or ''}".strip()
            tag = f"@{member.user.username}" if member.user.username else name
            admins.append(f"├ {tag} (`{member.user.id}`)")
        if admins:
            text = f"👑 **Admins ({len(admins)}):**\n" + "\n".join(admins)
        else:
            text = "⚠️ No admins found or not a group."
        await message.edit_text(text)
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


# Command: .invite
@app.on_message(filters.me & filters.command("invite", prefixes="."))
async def invite_cmd(client, message: Message):
    try:
        link = await client.export_chat_invite_link(message.chat.id)
        await message.edit_text(f"🔗 **Invite Link:**\n{link}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


# ==========================================
# 🎵 MEDIA COMMANDS
# ==========================================

# Command: .yt [query]
@app.on_message(filters.me & filters.command("yt", prefixes="."))
async def yt_cmd(client, message: Message):
    try:
        import yt_dlp
        import tempfile
        import glob

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.yt <search query or URL>`")
            return

        query = args[1]
        await message.edit_text(f"⏳ Searching & downloading: `{query}`...")

        tmp_dir = tempfile.mkdtemp()
        ydl_opts = {
            'format': 'best[filesize<50M]/best',
            'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'max_filesize': 50 * 1024 * 1024,
        }

        if not query.startswith("http"):
            ydl_opts['default_search'] = 'ytsearch'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            title = info.get('title', 'Video')

        files = glob.glob(f"{tmp_dir}/*")
        if files:
            await message.delete()
            await client.send_video(message.chat.id, files[0], caption=f"🎬 **{title}**")
            os.unlink(files[0])
        else:
            await message.edit_text("❌ Download failed.")
        os.rmdir(tmp_dir) if os.path.exists(tmp_dir) else None
    except Exception as e:
        await message.edit_text(f"❌ YT Error: `{str(e)[:200]}`")


# Command: .ytm [query]
@app.on_message(filters.me & filters.command("ytm", prefixes="."))
async def ytm_cmd(client, message: Message):
    try:
        import yt_dlp
        import tempfile
        import glob

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.ytm <search query or URL>`")
            return

        query = args[1]
        await message.edit_text(f"⏳ Downloading audio: `{query}`...")

        tmp_dir = tempfile.mkdtemp()
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        if not query.startswith("http"):
            ydl_opts['default_search'] = 'ytsearch'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            title = info.get('title', 'Audio')

        files = glob.glob(f"{tmp_dir}/*")
        if files:
            await message.delete()
            await client.send_audio(message.chat.id, files[0], title=title, caption=f"🎵 **{title}**")
            os.unlink(files[0])
        else:
            await message.edit_text("❌ Download failed.")
        os.rmdir(tmp_dir) if os.path.exists(tmp_dir) else None
    except Exception as e:
        await message.edit_text(f"❌ YTM Error: `{str(e)[:200]}`")


# Command: .sticker — supports image (static) + GIF/video (animated)
@app.on_message(filters.me & filters.command("sticker", prefixes="."))
async def sticker_cmd(client, message: Message):
    try:
        from PIL import Image
        import tempfile, subprocess

        reply = message.reply_to_message
        if not reply:
            await message.edit_text(
                "⚠️ **Usage:**\n"
                "Reply to an **image** → static sticker\n"
                "Reply to a **GIF/video** → animated sticker"
            )
            return

        # Animated sticker — GIF or video
        if reply.animation or reply.video or reply.document:
            await message.edit_text("⏳ Converting to animated sticker...")
            file_path = await reply.download()
            out_path = file_path + ".webm"

            # Convert to webm (VP9) for animated sticker
            subprocess.run([
                "ffmpeg", "-i", file_path,
                "-vf", "scale=512:512:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2",
                "-t", "3",  # max 3 seconds
                "-c:v", "libvpx-vp9",
                "-b:v", "0", "-crf", "30",
                "-an", "-y", out_path
            ], capture_output=True)

            await message.delete()
            await client.send_sticker(message.chat.id, out_path)
            os.unlink(file_path)
            os.unlink(out_path)

        # Static sticker — image/photo
        elif reply.photo or (reply.document and reply.document.mime_type and "image" in reply.document.mime_type):
            await message.edit_text("⏳ Converting to sticker...")
            photo_path = await reply.download()
            # Wait for file to be fully written
            import time as _time
            _time.sleep(0.5)
            # Verify file exists and is readable
            if not os.path.exists(photo_path) or os.path.getsize(photo_path) == 0:
                await message.edit_text("❌ Download failed, try again!")
                return

            with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as f:
                try:
                    img = Image.open(photo_path)
                    img = img.convert("RGBA")
                    img = img.resize((512, 512))
                    img.save(f.name, "WEBP")
                except Exception as img_err:
                    await message.edit_text(f"❌ Image error: `{img_err}`")
                    os.unlink(photo_path)
                    return
                await message.delete()
                await client.send_sticker(message.chat.id, f.name)
                os.unlink(f.name)
            os.unlink(photo_path)

        else:
            await message.edit_text("⚠️ Reply to an image, GIF, or video!")

    except Exception as e:
        await message.edit_text(f"❌ Sticker error: `{e}`")


# ==========================================
# 🤖 AI COMMANDS
# ==========================================

# Command: .ai [text]
@app.on_message(filters.me & filters.command("ai", prefixes="."))
async def ai_cmd(client, message: Message):
    try:
        import g4f

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.ai <your question>`")
            return

        text = args[1]
        await message.edit_text("🤖 **Thinking...**")

        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )

        if isinstance(response, str):
            reply = response
        else:
            reply = "".join(response)

        if not reply.strip():
            reply = "⚠️ No response received."

        await message.edit_text(f"🤖 **AI:**\n\n{reply[:4000]}")
    except Exception as e:
        await message.edit_text(f"❌ AI Error: `{str(e)[:200]}`")


# ==========================================
# 😎 FUN COMMANDS
# ==========================================

# Command: .joke
@app.on_message(filters.me & filters.command("joke", prefixes="."))
async def joke_cmd(client, message: Message):
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://v2.jokeapi.dev/joke/Any?safe-mode") as resp:
                data = await resp.json()
                if data.get("type") == "single":
                    joke = data["joke"]
                else:
                    joke = f"{data['setup']}\n\n{data['delivery']}"
        await message.edit_text(f"😂 **Joke:**\n\n{joke}")
    except Exception as e:
        await message.edit_text(f"❌ Joke error: `{e}`")


# Command: .quote
@app.on_message(filters.me & filters.command("quote", prefixes="."))
async def quote_cmd(client, message: Message):
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.quotable.io/random") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    text = data.get("content", "No quote found.")
                    author = data.get("author", "Unknown")
                else:
                    # Fallback quotes
                    fallback = [
                        ("The only way to do great work is to love what you do.", "Steve Jobs"),
                        ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
                        ("Life is what happens when you're busy making other plans.", "John Lennon"),
                        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
                        ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
                    ]
                    text, author = random.choice(fallback)
        await message.edit_text(f"💬 **Quote:**\n\n_{text}_\n\n— **{author}**")
    except Exception as e:
        # Fallback on error
        fallback = [
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
            ("Life is what happens when you're busy making other plans.", "John Lennon"),
        ]
        text, author = random.choice(fallback)
        await message.edit_text(f"💬 **Quote:**\n\n_{text}_\n\n— **{author}**")


# Command: .flip
@app.on_message(filters.me & filters.command("flip", prefixes="."))
async def flip_cmd(client, message: Message):
    result = random.choice(["🪙 **Heads!**", "🪙 **Tails!**"])
    await message.edit_text(result)


# Command: .roll
@app.on_message(filters.me & filters.command("roll", prefixes="."))
async def roll_cmd(client, message: Message):
    result = random.randint(1, 6)
    dice_emoji = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    await message.edit_text(f"🎲 **Rolled:** {dice_emoji[result-1]} **{result}**")


# Command: .roast [name]
@app.on_message(filters.me & filters.command("roast", prefixes="."))
async def roast_cmd(client, message: Message):
    roasts = [
        "Tu itna boring hai ki teri Wi-Fi bhi disconnect ho jaati hai. 💀",
        "Tera phone bhi airplane mode me rehna chahta hai tujhse baat na kare. ✈️",
        "Google pe 'useless' search karunga toh tera LinkedIn aayega. 😂",
        "Tera brain cell bhi single hai, tujhse zyada lonely. 🧠",
        "Tu itna slow hai, tera hotspot bhi 2G deta hai. 🐌",
        "Teri personality ka update aaya hai — still loading... ⏳",
        "Tujhe dekh ke WiFi router bhi buffering karta hai. 📶",
        "Tera code bina bug ke nahi chalta, aur life bhi. 🪲",
        "Tu itna basic hai, tera blood type 'Hello World' hai. 💉",
        "Tera sense of humor 404 Not Found hai bhai. 🚫",
        "Tujhe roast karna microwave me ice cream dalna hai — too easy. 🍦",
        "Tera resume dekh ke recruiter ne apni job chhod di. 📄",
        "Tu itna irrelevant hai, tere notifications bhi nahi aate. 🔕",
        "Tujhse zyada personality toh mere error messages me hai. ⚠️",
        "Teri life ka git log sirf 'initial commit' pe ruka hai. 🗂️",
    ]
    args = message.text.split(None, 1)
    name = args[1] if len(args) > 1 else "Bhai"
    roast = random.choice(roasts)
    await message.edit_text(f"🔥 **{name}:** {roast}")


# ==========================================
# ⚡ AUTOMATION COMMANDS
# ==========================================

# Command: .autoreply [trigger] | [response]
@app.on_message(filters.me & filters.command("autoreply", prefixes="."))
async def autoreply_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2 or "|" not in args[1]:
            await message.edit_text("⚠️ Usage: `.autoreply trigger | response`")
            return
        parts = args[1].split("|", 1)
        trigger = parts[0].strip().lower()
        response = parts[1].strip()
        AUTO_REPLIES[trigger] = response
        await message.edit_text(f"✅ Auto-reply set:\n**Trigger:** `{trigger}`\n**Response:** {response}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


# Command: .delauto [trigger]
@app.on_message(filters.me & filters.command("delauto", prefixes="."))
async def delauto_cmd(client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.edit_text("⚠️ Usage: `.delauto <trigger>`")
        return
    trigger = args[1].strip().lower()
    if trigger in AUTO_REPLIES:
        del AUTO_REPLIES[trigger]
        await message.edit_text(f"✅ Auto-reply for `{trigger}` deleted.")
    else:
        await message.edit_text(f"⚠️ No auto-reply found for `{trigger}`.")


# Command: .listauto
@app.on_message(filters.me & filters.command("listauto", prefixes="."))
async def listauto_cmd(client, message: Message):
    if not AUTO_REPLIES:
        await message.edit_text("ℹ️ No auto-replies set.")
        return
    text = "📋 **Auto-Replies:**\n\n"
    for trigger, response in AUTO_REPLIES.items():
        text += f"├ `{trigger}` → {response}\n"
    await message.edit_text(text)


# Auto-reply handler
@app.on_message(filters.incoming & ~filters.me & filters.text)
async def auto_reply_handler(client, message: Message):
    if AUTO_REPLIES and message.text:
        msg_lower = message.text.lower()
        for trigger, response in AUTO_REPLIES.items():
            if trigger in msg_lower:
                await message.reply_text(response)
                break


# Command: .forward [chat_id]
@app.on_message(filters.me & filters.command("forward", prefixes="."))
async def forward_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.forward <chat_id>` (reply to a message)")
            return
        if not message.reply_to_message:
            await message.edit_text("⚠️ Reply to a message to forward it.")
            return

        target = int(args[1])
        await message.reply_to_message.forward(target)
        await message.edit_text(f"✅ Message forwarded to `{target}`.")
    except ValueError:
        await message.edit_text("⚠️ Invalid chat ID. Must be a number.")
    except Exception as e:
        await message.edit_text(f"❌ Forward error: `{e}`")


# ==========================================
# 🛡️ GROUP ADMIN COMMANDS
# ==========================================

# Command: .ban
@app.on_message(filters.me & filters.command("ban", prefixes="."))
async def ban_cmd(client, message: Message):
    try:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.edit_text("⚠️ Reply to a user to ban them.")
            return
        user = message.reply_to_message.from_user
        await client.ban_chat_member(message.chat.id, user.id)
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        await message.edit_text(f"🔨 **Banned:** {name} (`{user.id}`)")
    except Exception as e:
        await message.edit_text(f"❌ Ban error: `{e}`")


# Command: .kick
@app.on_message(filters.me & filters.command("kick", prefixes="."))
async def kick_cmd(client, message: Message):
    try:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.edit_text("⚠️ Reply to a user to kick them.")
            return
        user = message.reply_to_message.from_user
        await client.ban_chat_member(message.chat.id, user.id)
        await asyncio.sleep(1)
        await client.unban_chat_member(message.chat.id, user.id)
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        await message.edit_text(f"👢 **Kicked:** {name} (`{user.id}`)")
    except Exception as e:
        await message.edit_text(f"❌ Kick error: `{e}`")


# Command: .mute
@app.on_message(filters.me & filters.command("mute", prefixes="."))
async def mute_cmd(client, message: Message):
    try:
        from pyrogram.types import ChatPermissions
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.edit_text("⚠️ Reply to a user to mute them.")
            return
        user = message.reply_to_message.from_user
        await client.restrict_chat_member(
            message.chat.id, user.id,
            ChatPermissions(can_send_messages=False)
        )
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        await message.edit_text(f"🔇 **Muted:** {name} (`{user.id}`)")
    except Exception as e:
        await message.edit_text(f"❌ Mute error: `{e}`")


# Command: .unmute
@app.on_message(filters.me & filters.command("unmute", prefixes="."))
async def unmute_cmd(client, message: Message):
    try:
        from pyrogram.types import ChatPermissions
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.edit_text("⚠️ Reply to a user to unmute them.")
            return
        user = message.reply_to_message.from_user
        await client.restrict_chat_member(
            message.chat.id, user.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        await message.edit_text(f"🔊 **Unmuted:** {name} (`{user.id}`)")
    except Exception as e:
        await message.edit_text(f"❌ Unmute error: `{e}`")


# Command: .pin
@app.on_message(filters.me & filters.command("pin", prefixes="."))
async def pin_cmd(client, message: Message):
    try:
        if not message.reply_to_message:
            await message.edit_text("⚠️ Reply to a message to pin it.")
            return
        await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.edit_text("📌 **Message pinned!**")
    except Exception as e:
        await message.edit_text(f"❌ Pin error: `{e}`")


# Command: .unpin
@app.on_message(filters.me & filters.command("unpin", prefixes="."))
async def unpin_cmd(client, message: Message):
    try:
        if not message.reply_to_message:
            await message.edit_text("⚠️ Reply to a message to unpin it.")
            return
        await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.edit_text("📌 **Message unpinned!**")
    except Exception as e:
        await message.edit_text(f"❌ Unpin error: `{e}`")








# ==========================================
# 📊 PRODUCTIVITY COMMANDS (v3)
# ==========================================

NOTES = {}
TODO_LIST = []


# Command: .remind [time] [text]
@app.on_message(filters.me & filters.command("remind", prefixes="."))
async def remind_cmd(client, message: Message):
    try:
        args = message.text.split(None, 2)
        if len(args) < 3:
            await message.edit_text("⚠️ Usage: `.remind 10m call karna`\nFormats: 10s, 5m, 1h")
            return

        time_str = args[1]
        reminder_text = args[2]

        # Parse time
        multiplier = {'s': 1, 'm': 60, 'h': 3600}
        unit = time_str[-1].lower()
        if unit not in multiplier:
            await message.edit_text("⚠️ Use s/m/h format. Example: `10m`, `30s`, `1h`")
            return
        seconds = int(time_str[:-1]) * multiplier[unit]

        await message.edit_text(f"⏰ Reminder set for **{time_str}**: {reminder_text}")
        chat_id = message.chat.id

        async def send_reminder():
            await asyncio.sleep(seconds)
            await client.send_message(chat_id, f"🔔 **Reminder:** {reminder_text}")

        asyncio.get_event_loop().create_task(send_reminder())
    except ValueError:
        await message.edit_text("⚠️ Invalid time format. Use: `10s`, `5m`, `1h`")
    except Exception as e:
        await message.edit_text(f"❌ Remind error: `{e}`")


# Command: .notes save [text] / .notes list
@app.on_message(filters.me & filters.command("notes", prefixes="."))
async def notes_cmd(client, message: Message):
    try:
        args = message.text.split(None, 2)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage:\n`.notes save <text>`\n`.notes list`")
            return

        action = args[1].lower()

        if action == "save":
            if len(args) < 3:
                await message.edit_text("⚠️ Usage: `.notes save <text>`")
                return
            note_text = args[2]
            note_id = len(NOTES) + 1
            NOTES[note_id] = note_text
            await message.edit_text(f"📝 Note #{note_id} saved: {note_text}")

        elif action == "list":
            if not NOTES:
                await message.edit_text("📝 No notes saved yet.")
                return
            text = "📝 **Your Notes:**\n\n"
            for nid, note in NOTES.items():
                text += f"**#{nid}:** {note}\n"
            await message.edit_text(text)
        else:
            await message.edit_text("⚠️ Usage:\n`.notes save <text>`\n`.notes list`")
    except Exception as e:
        await message.edit_text(f"❌ Notes error: `{e}`")


# Command: .todo add [task] / .todo list / .todo done [num]
@app.on_message(filters.me & filters.command("todo", prefixes="."))
async def todo_cmd(client, message: Message):
    try:
        args = message.text.split(None, 2)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage:\n`.todo add <task>`\n`.todo list`\n`.todo done <num>`")
            return

        action = args[1].lower()

        if action == "add":
            if len(args) < 3:
                await message.edit_text("⚠️ Usage: `.todo add <task>`")
                return
            task = args[2]
            TODO_LIST.append({"task": task, "done": False})
            await message.edit_text(f"✅ Task added: {task}\nTotal: {len(TODO_LIST)} tasks")

        elif action == "list":
            if not TODO_LIST:
                await message.edit_text("📋 Todo list is empty!")
                return
            text = "📋 **Todo List:**\n\n"
            for i, item in enumerate(TODO_LIST, 1):
                status = "✅" if item["done"] else "⬜"
                text += f"{status} **{i}.** {item['task']}\n"
            await message.edit_text(text)

        elif action == "done":
            if len(args) < 3:
                await message.edit_text("⚠️ Usage: `.todo done <number>`")
                return
            num = int(args[2])
            if 1 <= num <= len(TODO_LIST):
                TODO_LIST[num - 1]["done"] = True
                await message.edit_text(f"✅ Task #{num} marked done: {TODO_LIST[num-1]['task']}")
            else:
                await message.edit_text(f"⚠️ Invalid task number. You have {len(TODO_LIST)} tasks.")
        else:
            await message.edit_text("⚠️ Usage:\n`.todo add <task>`\n`.todo list`\n`.todo done <num>`")
    except ValueError:
        await message.edit_text("⚠️ Invalid number for `.todo done`")
    except Exception as e:
        await message.edit_text(f"❌ Todo error: `{e}`")


# ==========================================
# 🔍 SEARCH/INFO COMMANDS (v3)
# ==========================================

# Command: .wiki [query]
@app.on_message(filters.me & filters.command("wiki", prefixes="."))
async def wiki_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.wiki <query>`")
            return

        query = args[1]
        await message.edit_text(f"🔍 Searching Wikipedia for: `{query}`...")

        async with aiohttp.ClientSession() as session:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    title = data.get("title", query)
                    extract = data.get("extract", "No summary found.")
                    link = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    await message.edit_text(
                        f"📖 **{title}**\n\n{extract[:2000]}\n\n🔗 {link}"
                    )
                else:
                    await message.edit_text(f"⚠️ No Wikipedia article found for `{query}`.")
    except Exception as e:
        await message.edit_text(f"❌ Wiki error: `{e}`")


# Command: .weather [city]
@app.on_message(filters.me & filters.command("weather", prefixes="."))
async def weather_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.weather <city>`")
            return

        city = args[1]
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://wttr.in/{city}?format=3") as resp:
                if resp.status == 200:
                    weather = await resp.text()
                    await message.edit_text(f"🌤 **Weather:**\n`{weather.strip()}`")
                else:
                    await message.edit_text(f"⚠️ Could not fetch weather for `{city}`.")
    except Exception as e:
        await message.edit_text(f"❌ Weather error: `{e}`")


# Command: .crypto [coin]
@app.on_message(filters.me & filters.command("crypto", prefixes="."))
async def crypto_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.crypto bitcoin` or `.crypto ethereum`")
            return

        coin = args[1].lower().strip()
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr&include_24hr_change=true"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if coin in data:
                        usd = data[coin].get("usd", "N/A")
                        inr = data[coin].get("inr", "N/A")
                        change = data[coin].get("usd_24h_change", 0)
                        emoji = "📈" if change >= 0 else "📉"
                        await message.edit_text(
                            f"💰 **{coin.title()}**\n"
                            f"├ **USD:** ${usd:,.2f}\n"
                            f"├ **INR:** ₹{inr:,.2f}\n"
                            f"└ {emoji} **24h:** {change:.2f}%"
                        )
                    else:
                        await message.edit_text(f"⚠️ Coin `{coin}` not found. Use full name like `bitcoin`, `ethereum`.")
                else:
                    await message.edit_text("⚠️ CoinGecko API error. Try again later.")
    except Exception as e:
        await message.edit_text(f"❌ Crypto error: `{e}`")


# Command: .currency [amount] [from] [to]
@app.on_message(filters.me & filters.command("currency", prefixes="."))
async def currency_cmd(client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 4:
            await message.edit_text("⚠️ Usage: `.currency 100 USD INR`")
            return

        amount = float(args[1])
        from_cur = args[2].upper()
        to_cur = args[3].upper()

        async with aiohttp.ClientSession() as session:
            url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_cur}&to={to_cur}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result = data.get("rates", {}).get(to_cur, "N/A")
                    await message.edit_text(
                        f"💱 **Currency Conversion**\n"
                        f"├ **{amount} {from_cur}** = **{result} {to_cur}**\n"
                        f"└ Rate: 1 {from_cur} = {result/amount:.4f} {to_cur}"
                    )
                else:
                    await message.edit_text("⚠️ Conversion failed. Check currency codes (USD, INR, EUR, etc.)")
    except ValueError:
        await message.edit_text("⚠️ Invalid amount. Usage: `.currency 100 USD INR`")
    except Exception as e:
        await message.edit_text(f"❌ Currency error: `{e}`")


# Command: .news [topic]
@app.on_message(filters.me & filters.command("news", prefixes="."))
async def news_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.news <topic>`")
            return

        topic = args[1]
        await message.edit_text(f"📰 Fetching news for: `{topic}`...")

        async with aiohttp.ClientSession() as session:
            rss_url = f"https://news.google.com/rss/search?q={topic}&hl=en-IN&gl=IN&ceid=IN:en"
            async with session.get(rss_url) as resp:
                if resp.status == 200:
                    import re as re_mod
                    content = await resp.text()
                    titles = re_mod.findall(r'<title>(.*?)</title>', content)[2:7]
                    if titles:
                        text = f"📰 **News: {topic}**\n\n"
                        for i, title in enumerate(titles, 1):
                            title = title.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
                            text += f"**{i}.** {title}\n\n"
                        await message.edit_text(text)
                    else:
                        await message.edit_text(f"⚠️ No news found for `{topic}`.")
                else:
                    await message.edit_text("⚠️ News fetch failed.")
    except Exception as e:
        await message.edit_text(f"❌ News error: `{e}`")


# ==========================================
# 🛡️ PRIVACY COMMANDS (v3)
# ==========================================

# Command: .ghost [seconds]
@app.on_message(filters.me & filters.command("ghost", prefixes="."))
async def ghost_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        seconds = int(args[1]) if len(args) > 1 else 5

        await message.edit_text(f"👻 This message will disappear in {seconds}s...")
        await asyncio.sleep(seconds)
        await message.delete()
    except ValueError:
        await message.edit_text("⚠️ Usage: `.ghost 10` (seconds)")
    except Exception as e:
        await message.edit_text(f"❌ Ghost error: `{e}`")


# Command: .disappear [seconds]
@app.on_message(filters.me & filters.command("disappear", prefixes="."))
async def disappear_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.disappear 30` (seconds for TTL)")
            return

        seconds = int(args[1])
        try:
            await client.set_chat_ttl(message.chat.id, seconds)
            await message.edit_text(f"💨 Auto-delete set to **{seconds}s** for this chat.")
        except AttributeError:
            await message.edit_text(
                f"⚠️ `set_chat_ttl` not available in this Pyrogram version.\n"
                f"Use Telegram's built-in auto-delete setting instead."
            )
    except ValueError:
        await message.edit_text("⚠️ Usage: `.disappear 30` (seconds)")
    except Exception as e:
        await message.edit_text(f"❌ Disappear error: `{e}`")


# ==========================================
# 🎨 FUN/TEXT COMMANDS (v3)
# ==========================================

# Command: .mock — reply mOcKiNg TeXt
@app.on_message(filters.me & filters.command("mock", prefixes="."))
async def mock_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.mock some text`")
                return
            text = args[1]

        mocked = ""
        for i, char in enumerate(text):
            mocked += char.upper() if i % 2 == 0 else char.lower()
        await message.edit_text(f"🐔 {mocked}")
    except Exception as e:
        await message.edit_text(f"❌ Mock error: `{e}`")


# Command: .fancy — fancy text
@app.on_message(filters.me & filters.command("fancy", prefixes="."))
async def fancy_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.fancy some text`")
                return
            text = args[1]

        normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        fancy_chars = "\U0001d4ea\U0001d4eb\U0001d4ec\U0001d4ed\U0001d4ee\U0001d4ef\U0001d4f0\U0001d4f1\U0001d4f2\U0001d4f3\U0001d4f4\U0001d4f5\U0001d4f6\U0001d4f7\U0001d4f8\U0001d4f9\U0001d4fa\U0001d4fb\U0001d4fc\U0001d4fd\U0001d4fe\U0001d4ff\U0001d500\U0001d501\U0001d502\U0001d503\U0001d4d0\U0001d4d1\U0001d4d2\U0001d4d3\U0001d4d4\U0001d4d5\U0001d4d6\U0001d4d7\U0001d4d8\U0001d4d9\U0001d4da\U0001d4db\U0001d4dc\U0001d4dd\U0001d4de\U0001d4df\U0001d4e0\U0001d4e1\U0001d4e2\U0001d4e3\U0001d4e4\U0001d4e5\U0001d4e6\U0001d4e7\U0001d4e8\U0001d4e9"
        mapping = str.maketrans(normal, fancy_chars)
        result = text.translate(mapping)
        await message.edit_text(f"✨ {result}")
    except Exception as e:
        await message.edit_text(f"❌ Fancy error: `{e}`")


# Command: .reverse — reverse text
@app.on_message(filters.me & filters.command("reverse", prefixes="."))
async def reverse_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.reverse some text`")
                return
            text = args[1]

        await message.edit_text(f"🔄 {text[::-1]}")
    except Exception as e:
        await message.edit_text(f"❌ Reverse error: `{e}`")


# Command: .ascii [text]
@app.on_message(filters.me & filters.command("ascii", prefixes="."))
async def ascii_cmd(client, message: Message):
    try:
        import pyfiglet

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.ascii <text>`")
            return

        text = args[1]
        art = pyfiglet.figlet_format(text, font="small")
        if len(art) > 4000:
            art = art[:4000]
        await message.edit_text(f"```\n{art}\n```")
    except Exception as e:
        await message.edit_text(f"❌ ASCII error: `{e}`")


# ==========================================
# 📡 UTILITY COMMANDS (v3)
# ==========================================

# Command: .qr [text]
@app.on_message(filters.me & filters.command("qr", prefixes="."))
async def qr_cmd(client, message: Message):
    try:
        import qrcode
        import tempfile

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.qr <text or URL>`")
            return

        text = args[1]
        await message.edit_text("⏳ Generating QR code...")

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f.name)
            await message.delete()
            await client.send_photo(message.chat.id, f.name, caption=f"📱 QR: `{text[:100]}`")
            os.unlink(f.name)
    except Exception as e:
        await message.edit_text(f"❌ QR error: `{e}`")


# Command: .short [url]
@app.on_message(filters.me & filters.command("short", prefixes="."))
async def short_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.short <url>`")
            return

        url = args[1]
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://tinyurl.com/api-create.php?url={url}") as resp:
                if resp.status == 200:
                    short_url = await resp.text()
                    await message.edit_text(f"🔗 **Shortened URL:**\n{short_url}")
                else:
                    await message.edit_text("⚠️ URL shortening failed.")
    except Exception as e:
        await message.edit_text(f"❌ Short error: `{e}`")


# Command: .paste [text]
@app.on_message(filters.me & filters.command("paste", prefixes="."))
async def paste_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.paste <text>`")
                return
            text = args[1]

        await message.edit_text("⏳ Uploading to dpaste...")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://dpaste.com/api/v2/",
                data={"content": text, "syntax": "text", "expiry_days": 7}
            ) as resp:
                if resp.status in (200, 201):
                    paste_url = (await resp.text()).strip()
                    await message.edit_text(f"📋 **Paste URL:**\n{paste_url}\n\n⏳ Expires in 7 days")
                else:
                    await message.edit_text("⚠️ Paste upload failed.")
    except Exception as e:
        await message.edit_text(f"❌ Paste error: `{e}`")


# Command: .base64 encode/decode [text]
@app.on_message(filters.me & filters.command("base64", prefixes="."))
async def base64_cmd(client, message: Message):
    try:
        import base64 as b64

        args = message.text.split(None, 2)
        if len(args) < 3:
            await message.edit_text("⚠️ Usage:\n`.base64 encode <text>`\n`.base64 decode <text>`")
            return

        action = args[1].lower()
        text = args[2]

        if action == "encode":
            result = b64.b64encode(text.encode()).decode()
            await message.edit_text(f"🔐 **Base64 Encoded:**\n`{result}`")
        elif action == "decode":
            result = b64.b64decode(text.encode()).decode()
            await message.edit_text(f"🔓 **Base64 Decoded:**\n`{result}`")
        else:
            await message.edit_text("⚠️ Usage:\n`.base64 encode <text>`\n`.base64 decode <text>`")
    except Exception as e:
        await message.edit_text(f"❌ Base64 error: `{e}`")





# ==========================================
# 👤 PROFILE MANAGEMENT (v4)
# ==========================================

# Command: .bio [text]
@app.on_message(filters.me & filters.command("bio", prefixes="."))
async def bio_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.bio <new bio text>`")
            return
        bio_text = args[1]
        await client.update_profile(bio=bio_text)
        await message.edit_text(f"✅ **Bio updated:**\n{bio_text}")
    except Exception as e:
        await message.edit_text(f"❌ Bio error: `{e}`")


# Command: .name [first] [last]
@app.on_message(filters.me & filters.command("name", prefixes="."))
async def name_cmd(client, message: Message):
    try:
        args = message.text.split(None, 2)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.name <first> [last]`")
            return
        first_name = args[1]
        last_name = args[2] if len(args) > 2 else ""
        await client.update_profile(first_name=first_name, last_name=last_name)
        full_name = f"{first_name} {last_name}".strip()
        await message.edit_text(f"✅ **Name updated:** {full_name}")
    except Exception as e:
        await message.edit_text(f"❌ Name error: `{e}`")


# Command: .pfp — reply to image to set as profile pic
@app.on_message(filters.me & filters.command("pfp", prefixes="."))
async def pfp_cmd(client, message: Message):
    try:
        reply = message.reply_to_message
        if not reply or not reply.photo:
            await message.edit_text("⚠️ Reply to an image to set as profile photo.")
            return
        await message.edit_text("⏳ Updating profile photo...")
        photo_path = await reply.download()
        await client.set_profile_photo(photo=photo_path)
        os.unlink(photo_path)
        await message.edit_text("✅ **Profile photo updated!**")
    except Exception as e:
        await message.edit_text(f"❌ PFP error: `{e}`")


# ==========================================
# 📸 IMAGE FILTERS (v4)
# ==========================================

# Command: .invert — invert image colors
@app.on_message(filters.me & filters.command("invert", prefixes="."))
async def invert_cmd(client, message: Message):
    try:
        from PIL import Image, ImageOps
        import tempfile

        reply = message.reply_to_message
        if not reply or not reply.photo:
            await message.edit_text("⚠️ Reply to an image to invert colors.")
            return

        await message.edit_text("⏳ Inverting...")
        photo_path = await reply.download()
        img = Image.open(photo_path).convert("RGB")
        inverted = ImageOps.invert(img)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            inverted.save(f.name)
            await message.delete()
            await client.send_photo(message.chat.id, f.name, caption="🔄 **Inverted**")
            os.unlink(f.name)
        os.unlink(photo_path)
    except Exception as e:
        await message.edit_text(f"❌ Invert error: `{e}`")


# Command: .blur — blur image
@app.on_message(filters.me & filters.command("blur", prefixes="."))
async def blur_cmd(client, message: Message):
    try:
        from PIL import Image, ImageFilter
        import tempfile

        reply = message.reply_to_message
        if not reply or not reply.photo:
            await message.edit_text("⚠️ Reply to an image to blur it.")
            return

        await message.edit_text("⏳ Blurring...")
        photo_path = await reply.download()
        img = Image.open(photo_path)
        blurred = img.filter(ImageFilter.BLUR)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            blurred.save(f.name)
            await message.delete()
            await client.send_photo(message.chat.id, f.name, caption="🌫️ **Blurred**")
            os.unlink(f.name)
        os.unlink(photo_path)
    except Exception as e:
        await message.edit_text(f"❌ Blur error: `{e}`")


# Command: .gray — grayscale image
@app.on_message(filters.me & filters.command("gray", prefixes="."))
async def gray_cmd(client, message: Message):
    try:
        from PIL import Image
        import tempfile

        reply = message.reply_to_message
        if not reply or not reply.photo:
            await message.edit_text("⚠️ Reply to an image to convert to grayscale.")
            return

        await message.edit_text("⏳ Converting to grayscale...")
        photo_path = await reply.download()
        img = Image.open(photo_path).convert("L")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f.name)
            await message.delete()
            await client.send_photo(message.chat.id, f.name, caption="⬛ **Grayscale**")
            os.unlink(f.name)
        os.unlink(photo_path)
    except Exception as e:
        await message.edit_text(f"❌ Gray error: `{e}`")


# Command: .enhance — sharpen/enhance image
@app.on_message(filters.me & filters.command("enhance", prefixes="."))
async def enhance_cmd(client, message: Message):
    try:
        from PIL import Image, ImageEnhance
        import tempfile

        reply = message.reply_to_message
        if not reply or not reply.photo:
            await message.edit_text("⚠️ Reply to an image to enhance/sharpen it.")
            return

        await message.edit_text("⏳ Enhancing...")
        photo_path = await reply.download()
        img = Image.open(photo_path)
        enhancer = ImageEnhance.Sharpness(img)
        enhanced = enhancer.enhance(2.0)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            enhanced.save(f.name)
            await message.delete()
            await client.send_photo(message.chat.id, f.name, caption="✨ **Enhanced (Sharpened)**")
            os.unlink(f.name)
        os.unlink(photo_path)
    except Exception as e:
        await message.edit_text(f"❌ Enhance error: `{e}`")


# ==========================================
# 💬 TEXT EFFECTS (v4)
# ==========================================

# Command: .type [text] — typing effect
@app.on_message(filters.me & filters.command("type", prefixes="."))
async def type_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.type <text>`")
            return
        text = args[1]
        output = ""
        for char in text:
            output += char
            try:
                await message.edit_text(output + "▌")
                await asyncio.sleep(0.1)
            except Exception:
                pass
        await message.edit_text(output)
    except Exception as e:
        await message.edit_text(f"❌ Type error: `{e}`")


# Command: .bold — bold text
@app.on_message(filters.me & filters.command("bold", prefixes="."))
async def bold_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.bold <text>`")
                return
            text = args[1]
        await message.edit_text(f"**{text}**")
    except Exception as e:
        await message.edit_text(f"❌ Bold error: `{e}`")


# Command: .italic — italic text
@app.on_message(filters.me & filters.command("italic", prefixes="."))
async def italic_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.italic <text>`")
                return
            text = args[1]
        await message.edit_text(f"__{text}__")
    except Exception as e:
        await message.edit_text(f"❌ Italic error: `{e}`")


# Command: .spoiler — spoiler text
@app.on_message(filters.me & filters.command("spoiler", prefixes="."))
async def spoiler_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.spoiler <text>`")
                return
            text = args[1]
        await message.edit_text(f"||{text}||")
    except Exception as e:
        await message.edit_text(f"❌ Spoiler error: `{e}`")


# Command: .strike — strikethrough text
@app.on_message(filters.me & filters.command("strike", prefixes="."))
async def strike_cmd(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Reply to a message or: `.strike <text>`")
                return
            text = args[1]
        await message.edit_text(f"~~{text}~~")
    except Exception as e:
        await message.edit_text(f"❌ Strike error: `{e}`")


# ==========================================
# 🔒 SIMPLE ENCRYPTION (v4)
# ==========================================

# Command: .encrypt [text] — Caesar cipher + base64
@app.on_message(filters.me & filters.command("encrypt", prefixes="."))
async def encrypt_cmd(client, message: Message):
    try:
        import base64 as b64

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.encrypt <text>`")
            return
        text = args[1]
        # Caesar cipher shift 13 (ROT13) + base64
        shifted = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted += chr((ord(char) - base + 13) % 26 + base)
            else:
                shifted += char
        encoded = b64.b64encode(shifted.encode()).decode()
        await message.edit_text(f"🔐 **Encrypted:**\n`{encoded}`")
    except Exception as e:
        await message.edit_text(f"❌ Encrypt error: `{e}`")


# Command: .decrypt [text] — decode base64 + reverse Caesar
@app.on_message(filters.me & filters.command("decrypt", prefixes="."))
async def decrypt_cmd(client, message: Message):
    try:
        import base64 as b64

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.decrypt <encrypted_text>`")
            return
        text = args[1]
        # Decode base64 then reverse ROT13
        decoded = b64.b64decode(text.encode()).decode()
        result = ""
        for char in decoded:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + 13) % 26 + base)
            else:
                result += char
        await message.edit_text(f"🔓 **Decrypted:**\n{result}")
    except Exception as e:
        await message.edit_text(f"❌ Decrypt error: `{e}`")


# ==========================================
# 📊 STATS (v4)
# ==========================================

# Command: .stats — show account info
@app.on_message(filters.me & filters.command("stats", prefixes="."))
async def stats_cmd(client, message: Message):
    try:
        await message.edit_text("⏳ Fetching stats...")
        me = await client.get_me()
        full = await client.get_chat(me.id)
        username = f"@{me.username}" if me.username else "N/A"
        phone = me.phone_number or "Hidden"
        dc_id = me.dc_id or "Unknown"
        bio = getattr(full, 'bio', None) or "N/A"
        name = f"{me.first_name or ''} {me.last_name or ''}".strip()

        await message.edit_text(
            f"📊 **Account Stats**\n"
            f"├ **Name:** {name}\n"
            f"├ **Username:** {username}\n"
            f"├ **ID:** `{me.id}`\n"
            f"├ **DC:** {dc_id}\n"
            f"├ **Phone:** `{phone}`\n"
            f"└ **Bio:** {bio}"
        )
    except Exception as e:
        await message.edit_text(f"❌ Stats error: `{e}`")


# Command: .topmsg [limit] — top message senders in group
@app.on_message(filters.me & filters.command("topmsg", prefixes="."))
async def topmsg_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        limit = int(args[1]) if len(args) > 1 else 100
        limit = min(limit, 1000)

        await message.edit_text(f"⏳ Analyzing last **{limit}** messages...")
        senders = {}
        async for msg in client.get_chat_history(message.chat.id, limit=limit):
            if msg.from_user:
                uid = msg.from_user.id
                name = f"{msg.from_user.first_name or ''} {msg.from_user.last_name or ''}".strip()
                if uid not in senders:
                    senders[uid] = {"name": name, "count": 0}
                senders[uid]["count"] += 1

        if not senders:
            await message.edit_text("⚠️ No messages found or not a group.")
            return

        sorted_senders = sorted(senders.values(), key=lambda x: x["count"], reverse=True)[:10]
        text = f"📊 **Top Senders** (last {limit} msgs):\n\n"
        for i, s in enumerate(sorted_senders, 1):
            bar = "█" * min(int(s["count"] / sorted_senders[0]["count"] * 10), 10)
            text += f"**{i}.** {s['name']} — `{s['count']}` msgs {bar}\n"

        await message.edit_text(text)
    except ValueError:
        await message.edit_text("⚠️ Usage: `.topmsg [number]` (default: 100)")
    except Exception as e:
        await message.edit_text(f"❌ Topmsg error: `{e}`")


async def main():
    await app.start()
    me = await app.get_me()
    print(f"Userbot started! Logged in as {me.first_name} (ID: {me.id})")
    await idle()
    await app.stop()



# ==========================================
# 💳 BIN LOOKUP COMMAND
# ==========================================

# Command: .bin [bin_number]
# Usage: .bin 414720 OR reply to a message with BIN
@app.on_message(filters.me & filters.command("bin", prefixes="."))
async def bin_lookup(client, message: Message):
    try:
        import requests as _req

        args = message.text.split(None, 1)
        bin_number = None

        if len(args) > 1:
            bin_number = args[1].strip()[:6]
        elif message.reply_to_message and message.reply_to_message.text:
            bin_number = message.reply_to_message.text.strip()[:6]

        if not bin_number or not bin_number.isdigit() or len(bin_number) < 6:
            await message.edit_text("⚠️ **Usage:** `.bin 414720`")
            return

        await message.edit_text("🔍 Looking up BIN...")

        r = _req.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            brand   = d.get("brand", "N/A")
            btype   = d.get("type", "N/A")
            level   = d.get("level", "N/A")
            bank    = d.get("bank", "N/A")
            country = d.get("country_name", "N/A")
            flag    = d.get("country_flag", "")

            import json as _json
            result = {
                "bin": bin_number,
                "bank": bank,
                "brand": brand,
                "type": btype,
                "level": level,
                "country": f"{flag} {country}"
            }
            text = f"```json\n{_json.dumps(result, indent=2, ensure_ascii=False)}\n```"
            await message.edit_text(text)
        else:
            await message.edit_text(f"❌ BIN not found: `{bin_number}`")

    except Exception as e:
        await message.edit_text(f"❌ BIN error: `{e}`")



# ==========================================
# 💳 GEN COMMAND (VClub-X exact logic)
# ==========================================

def _luhn_algorithm(number):
    total = 0
    reverse_digits = str(number)[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def _complete_luhn(base):
    for d in "0123456789":
        candidate = base + d
        if _luhn_algorithm(candidate):
            return candidate
    return None

def _get_card_length(brand="", bin_prefix=""):
    brand = (brand or "").upper()
    bin_str = str(bin_prefix)[:6]
    
    # Check by BIN prefix first (more accurate)
    if bin_str[:2] in {"34", "37"}:
        return 15  # AMEX
    if bin_str[:2] == "36" or bin_str[:3] in {"300","301","302","303","304","305","309"}:
        return 14  # Diners
    if bin_str[:1] == "4":
        return 16  # Visa
    if bin_str[:2] in {"51","52","53","54","55"}:
        return 16  # Mastercard
    if bin_str[:4] in {"6011","6304","6759","6761","6762","6763"}:
        return 16  # Maestro/Discover
    
    # Fallback by brand name
    if brand in {"AMEX", "AMERICAN EXPRESS"}:
        return 15
    if brand in {"DINERS CLUB", "DINERS"}:
        return 14
    return 16

async def _gen_cards(cc_bin, amount=10, mes="x", ano="x", cvv="x"):
    import re, random, requests as _req
    from datetime import datetime
    now = datetime.now()

    bin_part = re.sub(r"\D", "", cc_bin.replace("x", "0"))[:6].ljust(6, "0")
    
    # Get BIN info for card length
    brand = "VISA"
    try:
        r = _req.get(f"https://bins.antipublic.cc/bins/{bin_part}", timeout=5)
        if r.status_code == 200:
            brand = r.json().get("brand", "VISA")
    except:
        pass
    
    card_length = _get_card_length(brand, bin_part)
    cvv_length = 4 if card_length == 15 else 3

    output = []
    seen = set()
    attempts = 0
    
    while len(output) < amount and attempts < amount * 30:
        attempts += 1
        
        # Build base from BIN pattern
        raw_base = ''.join(
            random.choice("0123456789") if c.lower() == "x" else c 
            for c in cc_bin
            if c.isdigit() or c.lower() == "x"
        )
        # Pad/trim to exactly card_length - 1
        if len(raw_base) > card_length - 1:
            base = raw_base[:card_length - 1]
        else:
            base = raw_base + ''.join(random.choices("0123456789", k=card_length - 1 - len(raw_base)))
        
        card_number = _complete_luhn(base)
        if not card_number or card_number in seen:
            continue
        seen.add(card_number)
        
        # Year
        if ano.lower() == "x":
            year = random.randint(now.year, 2032)
        else:
            try:
                y = int(ano)
                if y < 100: y += 2000
                year = y if now.year <= y <= 2032 else now.year
            except:
                year = now.year
        
        # Month
        if mes.lower() == "x":
            month = random.randint(now.month if year == now.year else 1, 12)
        else:
            try:
                m = int(mes)
                month = m if 1 <= m <= 12 else now.month
            except:
                month = now.month
        
        # Fix expired
        if year == now.year and month < now.month:
            if ano.lower() == "x":
                year = now.year + 1
        
        mes_str = str(month).zfill(2)
        ano_str = str(year)
        cvv_str = ''.join(random.choices("0123456789", k=cvv_length)) if cvv.lower() == "x" else cvv
        
        output.append(f"{card_number}|{mes_str}|{ano_str}|{cvv_str}")
    
    return output

@app.on_message(filters.me & filters.command("gen", prefixes="."))
async def gen_cmd(client, message: Message):
    try:
        import requests as _req, re
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ **Usage:** `.gen 414720|xx|xx|xxx 10`")
            return

        await message.edit_text("⚙️ Generating cards...")
        raw = args[1].strip()
        parts = raw.rsplit(" ", 1)
        block = parts[0]
        amount = min(int(parts[1]), 50) if len(parts) > 1 and parts[1].isdigit() else 10

        tokens = re.sub(r"[|/ ]+", "|", block).split("|")
        bin_ = tokens[0] if tokens else "414720"
        mes  = tokens[1] if len(tokens) > 1 else "x"
        ano  = tokens[2] if len(tokens) > 2 else "x"
        cvv  = tokens[3] if len(tokens) > 3 else "x"

        # Normalize
        mes = "x" if mes.lower() in {"x","xx"} else mes
        ano = "x" if ano.lower() in {"x","xx","xxxx"} else ano
        cvv = "x" if cvv.lower() in {"x","xx","xxx","xxxx"} else cvv

        cards = await _gen_cards(bin_, amount, mes, ano, cvv)

        # BIN info
        bin_part = bin_[:6]
        d = {}
        try:
            r = _req.get(f"https://bins.antipublic.cc/bins/{bin_part}", timeout=5)
            if r.status_code == 200:
                d = r.json()
        except:
            pass

        card_lines = "\n".join(f"`{c}`" for c in cards)
        text = (
            f"**Generated** `{len(cards)}` cards — BIN `{bin_part}`\n\n"
            f"{card_lines}\n\n"
            f"**Info:** `{d.get('brand','?')}` | `{d.get('type','?')}` | `{d.get('level','?')}`\n"
            f"**Bank:** `{d.get('bank','?')}`\n"
            f"**Country:** {d.get('country_flag','')} `{d.get('country_name','?')}`"
        )
        
        if len(text) > 4096:
            # Send as file if too many cards
            with open("/tmp/gen_cards.txt", "w") as f:
                f.write("\n".join(cards))
            await message.delete()
            await client.send_document(
                message.chat.id, "/tmp/gen_cards.txt",
                caption=f"**BIN:** `{bin_part}` | `{d.get('brand','?')}` | `{d.get('bank','?')}`"
            )
        else:
            await message.edit_text(text)

    except Exception as e:
        await message.edit_text(f"❌ Gen error: `{e}`")

# ==========================================
# 🌐 IP LOOKUP COMMAND
# ==========================================

@app.on_message(filters.me & filters.command("ip", prefixes="."))
async def ip_lookup(client, message: Message):
    try:
        import requests as _req, json as _json
        args = message.text.split(None, 1)
        ip = args[1].strip() if len(args) > 1 else ""
        if not ip:
            await message.edit_text("⚠️ **Usage:** `.ip 8.8.8.8`")
            return
        await message.edit_text("🔍 Looking up IP...")
        r = _req.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query,mobile,proxy,hosting", timeout=10)
        d = r.json()
        if d.get("status") != "success":
            await message.edit_text(f"❌ IP not found: `{ip}`")
            return
        result = {
            "ip": d.get("query"),
            "country": d.get("country"),
            "region": d.get("regionName"),
            "city": d.get("city"),
            "isp": d.get("isp"),
            "org": d.get("org"),
            "proxy": d.get("proxy"),
            "hosting": d.get("hosting"),
            "mobile": d.get("mobile"),
            "lat": d.get("lat"),
            "lon": d.get("lon")
        }
        text = f"```json\n{_json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        await message.edit_text(text)
    except Exception as e:
        await message.edit_text(f"❌ IP error: `{e}`")

# ==========================================
# 🔍 SEARCH COMMAND
# ==========================================

@app.on_message(filters.me & filters.command("search", prefixes="."))
async def search_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ **Usage:** `.search text to find`")
            return
        query = args[1].strip()
        await message.edit_text(f"🔍 Searching for `{query}`...")
        count = 0
        results = []

        # Use get_chat_history with manual filtering to avoid UTF-16 issues
        async for msg in client.get_chat_history(message.chat.id, limit=500):
            try:
                text_content = msg.text or msg.caption or ""
                if not text_content:
                    continue
                # Safe decode
                safe_text = text_content.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
                if query.lower() in safe_text.lower():
                    count += 1
                    date_str = msg.date.strftime("%d/%m %H:%M") if msg.date else "?"
                    preview = safe_text[:60].replace("\n", " ")
                    results.append(f"`{date_str}` — {preview}")
                    if count >= 10:
                        break
            except:
                continue

        if results:
            lines = "\n".join(results)
            text = f"🔍 **Found {count} results for** `{query}`:\n\n{lines}"
            try:
                await message.edit_text(text)
            except:
                await message.reply_text(text)
        else:
            await message.edit_text(f"❌ No results for `{query}` in last 500 messages")

    except Exception as e:
        err = str(e).encode('ascii', errors='replace').decode('ascii')
        try:
            await message.edit_text(f"❌ Search error: `{err}`")
        except:
            await message.reply_text(f"❌ Search error: `{err}`")



# ==========================================
# 📁 SCRFILE COMMAND - Scrape & Merge Files
# ==========================================

# Usage: .scrfile @username / chat_id / https://t.me/username
# Scrapes all text/document files from a chat and merges into one file

@app.on_message(filters.me & filters.command("scrfile", prefixes="."))
async def scrfile_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text(
                "⚠️ **Usage:**\n"
                "`.scrfile @username`\n"
                "`.scrfile -100123456789`\n"
                "`.scrfile https://t.me/username`"
            )
            return

        target = args[1].strip()

        # Extract chat id/username from t.me link
        if "t.me/" in target:
            path = target.split("t.me/")[-1].strip("/")
            # Private invite link starts with +
            if path.startswith("+"):
                target = path  # keep as invite hash
            else:
                target = path

        await message.edit_text(f"🔍 Accessing `{target[:30]}`...")

        # Resolve chat — handle private invite links
        try:
            if target.startswith("+"):
                # Private invite link — join first
                invite_link = f"https://t.me/{target}" if not target.startswith("http") else target
                try:
                    chat = await client.join_chat(invite_link)
                    chat_id = chat.id
                    chat_title = chat.title or str(chat_id)
                    await message.edit_text(f"✅ Joined `{chat_title}`, scraping...")
                except Exception as join_e:
                    if "already" in str(join_e).lower() or "USER_ALREADY" in str(join_e):
                        # Already member, try to get via invite
                        await message.edit_text("📥 Already in group, scraping...")
                        # Get all dialogs and find by recent activity
                        async for dialog in client.get_dialogs(limit=50):
                            if dialog.chat.type.name in ["GROUP","SUPERGROUP","CHANNEL"]:
                                chat = dialog.chat
                                chat_id = chat.id
                                chat_title = chat.title
                                break
                    else:
                        await message.edit_text(f"❌ Could not join: `{str(join_e)[:100]}`")
                        return
            else:
                chat = await client.get_chat(target)
                chat_id = chat.id
                chat_title = chat.title or chat.username or str(chat_id)
        except Exception as e:
            await message.edit_text(f"❌ Could not access chat: `{str(e)[:100]}`")
            return

        await message.edit_text(f"📥 Scraping files from **{chat_title}**...")

        merged_content = []
        file_count = 0
        msg_count = 0

        async for msg in client.get_chat_history(chat_id, limit=500):
            msg_count += 1

            # Text messages with content
            if msg.text and len(msg.text) > 5:
                merged_content.append(msg.text)
                file_count += 1

            # Document files (txt, csv, etc.)
            elif msg.document:
                mime = msg.document.mime_type or ""
                if any(x in mime for x in ["text", "plain", "csv", "json"]):
                    try:
                        file_path = await msg.download()
                        with open(file_path, "r", errors="ignore") as f:
                            merged_content.append(f.read())
                        os.unlink(file_path)
                        file_count += 1
                    except:
                        pass

            if msg_count % 100 == 0:
                await message.edit_text(
                    f"📥 Scraping **{chat_title}**...\n"
                    f"Scanned: `{msg_count}` msgs | Found: `{file_count}` files"
                )

        if not merged_content:
            await message.edit_text(f"❌ No text files found in **{chat_title}**")
            return

        # Merge all content
        final_content = "\n".join(merged_content)
        output_file = f"/tmp/scrfile_{chat_id}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_content)

        total_lines = final_content.count("\n") + 1
        await message.delete()
        await client.send_document(
            message.chat.id,
            output_file,
            caption=(
                f"📁 **Scraped:** {chat_title}\n"
                f"📊 **Files merged:** `{file_count}`\n"
                f"📝 **Total lines:** `{total_lines}`\n"
                f"💾 **Size:** `{len(final_content)} chars`"
            ),
            file_name=f"scrfile_{chat_title}.txt"
        )
        os.unlink(output_file)

    except Exception as e:
        await message.edit_text(f"❌ Scrfile error: `{e}`")




# ==========================================
# 📦 NEW COMMANDS v5 (10 commands)
# ==========================================

import zipfile
import re
from collections import Counter, defaultdict

# Global state for autofwd
AUTOFWD_RULES = {}
AUTOFWD_HANDLERS = {}


# Command: .dlall — Download all media from a chat to zip and send
@app.on_message(filters.me & filters.command("dlall", prefixes="."))
async def dlall_cmd(client, message: Message):
    try:
        import tempfile
        import shutil

        args = message.text.split(None, 1)
        if len(args) > 1:
            target = args[1].strip()
            try:
                chat = await client.get_chat(target)
                chat_id = chat.id
                chat_title = chat.title or chat.username or str(chat_id)
            except Exception as e:
                await message.edit_text(f"❌ Could not access chat: `{e}`")
                return
        else:
            chat_id = message.chat.id
            chat_title = message.chat.title or message.chat.username or str(chat_id)

        await message.edit_text(f"📥 Downloading media from **{chat_title}**...\nThis may take a while...")

        tmp_dir = tempfile.mkdtemp(prefix="dlall_")
        media_count = 0
        scanned = 0

        async for msg in client.get_chat_history(chat_id, limit=200):
            scanned += 1
            has_media = msg.photo or msg.video or msg.document or msg.audio or msg.voice or msg.animation
            if has_media:
                try:
                    file_path = await msg.download(file_name=f"{tmp_dir}/")
                    if file_path:
                        media_count += 1
                except:
                    pass

            if scanned % 50 == 0:
                await message.edit_text(
                    f"📥 Downloading from **{chat_title}**...\n"
                    f"Scanned: `{scanned}` | Downloaded: `{media_count}`"
                )

        if media_count == 0:
            await message.edit_text(f"❌ No media found in **{chat_title}**")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return

        # Create zip
        zip_path = f"/tmp/dlall_{chat_id}.zip"
        await message.edit_text(f"📦 Zipping `{media_count}` files...")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    file_full = os.path.join(root, file)
                    zf.write(file_full, file)

        # Send zip
        zip_size = os.path.getsize(zip_path) / (1024 * 1024)
        if zip_size > 2000:
            await message.edit_text(f"❌ Zip too large ({zip_size:.1f}MB). Telegram limit is 2GB.")
        else:
            await message.delete()
            await client.send_document(
                message.chat.id,
                zip_path,
                caption=f"📦 **Media from:** {chat_title}\n📊 **Files:** `{media_count}`\n💾 **Size:** `{zip_size:.1f}MB`",
                file_name=f"media_{chat_title}.zip"
            )

        # Cleanup
        shutil.rmtree(tmp_dir, ignore_errors=True)
        if os.path.exists(zip_path):
            os.unlink(zip_path)

    except Exception as e:
        await message.edit_text(f"❌ Dlall error: `{e}`")


# Command: .nuke — Delete all YOUR messages in current chat
@app.on_message(filters.me & filters.command("nuke", prefixes="."))
async def nuke_cmd(client, message: Message):
    try:
        await message.edit_text("💣 **Nuking your messages...**")
        chat_id = message.chat.id
        deleted = 0
        msg_ids = []

        async for msg in client.search_messages(chat_id, from_user="me"):
            msg_ids.append(msg.id)

        if not msg_ids:
            await message.edit_text("ℹ️ No messages found to delete.")
            return

        total = len(msg_ids)
        for i in range(0, len(msg_ids), 100):
            batch = msg_ids[i:i+100]
            await client.delete_messages(chat_id, batch)
            deleted += len(batch)

        status = await client.send_message(chat_id, f"💣 **Nuked {deleted}/{total} messages.**")
        await asyncio.sleep(3)
        await status.delete()

    except Exception as e:
        try:
            await message.edit_text(f"❌ Nuke error: `{e}`")
        except:
            pass


# Command: .clone — Copy another user's profile
@app.on_message(filters.me & filters.command("clone", prefixes="."))
async def clone_cmd(client, message: Message):
    try:
        # Get target user
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ Usage: `.clone @username` or reply to a user")
                return
            target_user = await client.get_users(args[1].strip())

        await message.edit_text(f"🎭 Cloning **{target_user.first_name}**...")

        # Update name
        first_name = target_user.first_name or ""
        last_name = target_user.last_name or ""
        await client.update_profile(first_name=first_name, last_name=last_name)

        # Download and set profile photo
        try:
            photos = []
            async for photo in client.get_chat_photos(target_user.id, limit=1):
                photos.append(photo)
            if photos:
                photo_path = await client.download_media(photos[0].file_id)
                if photo_path:
                    await client.set_profile_photo(photo=photo_path)
                    os.unlink(photo_path)
        except:
            pass

        await message.edit_text(
            f"🎭 **Cloned!**\n"
            f"├ **Name:** {first_name} {last_name}\n"
            f"└ **Photo:** Updated"
        )

    except Exception as e:
        await message.edit_text(f"❌ Clone error: `{e}`")


# Command: .scr — Scrape text content (cards, combos, emails) from a chat
@app.on_message(filters.me & filters.command("scr", prefixes="."))
async def scr_cmd(client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.edit_text(
                "⚠️ **Usage:** `.scr @username [limit]`\n"
                "Scrapes cards (xxxx|xx|xx|xxx), email:pass combos"
            )
            return

        target = args[1].strip()
        try:
            limit = int(args[2]) if len(args) > 2 else 500
            limit = max(1, min(limit, 5000))  # 1 to 5000
        except:
            limit = 500

        try:
            chat = await client.get_chat(target)
            chat_id = chat.id
            chat_title = chat.title or chat.username or str(chat_id)
        except Exception as e:
            await message.edit_text(f"❌ Could not access chat: `{e}`")
            return

        await message.edit_text(f"🔍 Scraping **{chat_title}** ({limit} msgs)...")

        # Patterns
        card_pattern = re.compile(r'\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}')
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[:|;][^\s]+')

        found_items = []
        scanned = 0

        async for msg in client.get_chat_history(chat_id, limit=min(limit, 200)):
            scanned += 1
            if msg.text:
                # Find cards
                cards = card_pattern.findall(msg.text)
                found_items.extend(cards)
                # Find email:pass
                emails = email_pattern.findall(msg.text)
                found_items.extend(emails)

            if scanned % 100 == 0:
                await message.edit_text(
                    f"🔍 Scraping **{chat_title}**...\n"
                    f"Scanned: `{scanned}` | Found: `{len(found_items)}`"
                )

        if not found_items:
            await message.edit_text(f"❌ No cards/combos found in **{chat_title}**")
            return

        # Remove duplicates
        found_items = list(dict.fromkeys(found_items))

        # Save to file
        output_file = f"/tmp/scr_{chat_id}.txt"
        with open(output_file, "w") as f:
            f.write("\n".join(found_items))

        await message.delete()
        await client.send_document(
            message.chat.id,
            output_file,
            caption=(
                f"🔍 **Scraped:** {chat_title}\n"
                f"📊 **Items found:** `{len(found_items)}`\n"
                f"📝 **Scanned:** `{scanned}` messages"
            ),
            file_name=f"scr_{chat_title}.txt"
        )
        os.unlink(output_file)

    except ValueError:
        await message.edit_text("⚠️ Invalid limit number.")
    except Exception as e:
        await message.edit_text(f"❌ Scr error: `{e}`")


# Command: .fwd — Bulk forward messages from one chat to another
@app.on_message(filters.me & filters.command("fwd", prefixes="."))
async def fwd_cmd(client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 3:
            await message.edit_text("⚠️ **Usage:** `.fwd @source @destination [count]`")
            return

        source = args[1].strip()
        destination = args[2].strip()
        count = int(args[3]) if len(args) > 3 else 100

        # Resolve chats
        try:
            src_chat = await client.get_chat(source)
            dst_chat = await client.get_chat(destination)
        except Exception as e:
            await message.edit_text(f"❌ Could not access chats: `{e}`")
            return

        await message.edit_text(
            f"📨 Forwarding `{count}` msgs\n"
            f"From: **{src_chat.title or source}**\n"
            f"To: **{dst_chat.title or destination}**"
        )

        forwarded = 0
        msg_ids = []

        async for msg in client.get_chat_history(src_chat.id, limit=count):
            msg_ids.append(msg.id)

        # Forward in batches of 100
        msg_ids.reverse()  # oldest first
        for i in range(0, len(msg_ids), 100):
            batch = msg_ids[i:i+100]
            try:
                await client.forward_messages(dst_chat.id, src_chat.id, batch)
                forwarded += len(batch)
            except Exception:
                # Try one by one on failure
                for mid in batch:
                    try:
                        await client.forward_messages(dst_chat.id, src_chat.id, mid)
                        forwarded += 1
                    except:
                        pass
            await message.edit_text(
                f"📨 Forwarding... `{forwarded}/{len(msg_ids)}`"
            )
            await asyncio.sleep(1)

        await message.edit_text(f"✅ **Forwarded {forwarded}/{len(msg_ids)} messages!**")

    except ValueError:
        await message.edit_text("⚠️ Invalid count number.")
    except Exception as e:
        await message.edit_text(f"❌ Fwd error: `{e}`")


# Command: .autofwd — Auto-forward new messages from one chat to another
@app.on_message(filters.me & filters.command("autofwd", prefixes="."))
async def autofwd_cmd(client, message: Message):
    try:
        args = message.text.split()

        if len(args) >= 2 and args[1].lower() == "stop":
            if not AUTOFWD_RULES:
                await message.edit_text("ℹ️ No active auto-forward rules.")
                return
            AUTOFWD_RULES.clear()
            await message.edit_text("✅ **All auto-forward rules stopped.**")
            return

        if len(args) < 3:
            rules_text = ""
            if AUTOFWD_RULES:
                rules_text = "\n\n**Active rules:**\n"
                for src, dst in AUTOFWD_RULES.items():
                    rules_text += f"├ `{src}` → `{dst}`\n"
            await message.edit_text(
                f"⚠️ **Usage:**\n"
                f"`.autofwd @source @destination` — start\n"
                f"`.autofwd stop` — stop all{rules_text}"
            )
            return

        source = args[1].strip()
        destination = args[2].strip()

        # Resolve chats
        try:
            src_chat = await client.get_chat(source)
            dst_chat = await client.get_chat(destination)
        except Exception as e:
            await message.edit_text(f"❌ Could not access chats: `{e}`")
            return

        AUTOFWD_RULES[src_chat.id] = dst_chat.id

        await message.edit_text(
            f"✅ **Auto-forward enabled!**\n"
            f"├ **From:** {src_chat.title or source} (`{src_chat.id}`)\n"
            f"└ **To:** {dst_chat.title or destination} (`{dst_chat.id}`)\n\n"
            f"Use `.autofwd stop` to disable."
        )

    except Exception as e:
        await message.edit_text(f"❌ Autofwd error: `{e}`")


# Auto-forward handler (checks AUTOFWD_RULES)
@app.on_message(filters.incoming & ~filters.me)
async def autofwd_handler(client, message: Message):
    if AUTOFWD_RULES and message.chat.id in AUTOFWD_RULES:
        dst_id = AUTOFWD_RULES[message.chat.id]
        try:
            await message.forward(dst_id)
        except:
            pass


# Command: .spam — Send a message N times
@app.on_message(filters.me & filters.command("spam", prefixes="."))
async def spam_cmd(client, message: Message):
    try:
        args = message.text.split(None, 2)
        if len(args) < 3:
            await message.edit_text("⚠️ **Usage:** `.spam 5 Hello World`\nMax: 20 times")
            return

        count = int(args[1])
        text = args[2]

        if count > 20:
            count = 20
        if count < 1:
            await message.edit_text("⚠️ Count must be at least 1.")
            return

        await message.delete()

        for i in range(count):
            await client.send_message(message.chat.id, text)
            await asyncio.sleep(0.5)

    except ValueError:
        await message.edit_text("⚠️ Invalid count. Usage: `.spam 5 Hello`")
    except Exception as e:
        try:
            await message.edit_text(f"❌ Spam error: `{e}`")
        except:
            pass


# Command: .top10 — Show top 10 most active members
@app.on_message(filters.me & filters.command("top10", prefixes="."))
async def top10_cmd(client, message: Message):
    try:
        args = message.text.split()
        limit = int(args[1]) if len(args) > 1 else 200

        await message.edit_text(f"📊 Scanning last `{limit}` messages...")

        user_counts = Counter()
        scanned = 0

        async for msg in client.get_chat_history(message.chat.id, limit=limit):
            scanned += 1
            if msg.from_user:
                name = f"{msg.from_user.first_name or ''} {msg.from_user.last_name or ''}".strip()
                if msg.from_user.username:
                    name = f"@{msg.from_user.username}"
                user_counts[name] += 1

        if not user_counts:
            await message.edit_text("❌ No messages found.")
            return

        top = user_counts.most_common(10)
        text = f"🏆 **Top 10 Active Members** (last {scanned} msgs)\n\n"
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for i, (name, count) in enumerate(top):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            bar = "█" * min(int(count / max(1, top[0][1]) * 10), 10)
            text += f"{medal} **{name}** — `{count}` msgs {bar}\n"

        await message.edit_text(text)

    except ValueError:
        await message.edit_text("⚠️ Usage: `.top10 [scan_limit]` (default: 200)")
    except Exception as e:
        await message.edit_text(f"❌ Top10 error: `{e}`")


# Command: .msgcount — Count messages from a specific user
@app.on_message(filters.me & filters.command("msgcount", prefixes="."))
async def msgcount_cmd(client, message: Message):
    try:
        # Get target user
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
        else:
            args = message.text.split(None, 1)
            if len(args) < 2:
                await message.edit_text("⚠️ **Usage:** `.msgcount @username` or reply to a user")
                return
            target_user = await client.get_users(args[1].strip())

        target_name = f"{target_user.first_name or ''} {target_user.last_name or ''}".strip()
        await message.edit_text(f"🔢 Counting messages from **{target_name}**...")

        count = 0
        async for msg in client.search_messages(message.chat.id, from_user=target_user.id, limit=500):
            count += 1

        await message.edit_text(
            f"🔢 **Message Count**\n"
            f"├ **User:** {target_name}\n"
            f"├ **Username:** @{target_user.username or 'N/A'}\n"
            f"└ **Messages:** `{count}` (in last 500 scanned)"
        )

    except Exception as e:
        await message.edit_text(f"❌ Msgcount error: `{e}`")


# Command: .activity — Show chat activity as ASCII bar chart
@app.on_message(filters.me & filters.command("activity", prefixes="."))
async def activity_cmd(client, message: Message):
    try:
        await message.edit_text("📊 Analyzing chat activity...")

        hour_counts = defaultdict(int)
        scanned = 0

        async for msg in client.get_chat_history(message.chat.id, limit=200):
            scanned += 1
            if msg.date:
                hour = msg.date.hour
                hour_counts[hour] += 1

        if not hour_counts:
            await message.edit_text("❌ No messages found to analyze.")
            return

        max_count = max(hour_counts.values())
        text = f"📊 **Chat Activity** (last {scanned} msgs)\n\n"
        text += "```\n"

        for hour in range(24):
            count = hour_counts.get(hour, 0)
            bar_len = int(count / max(1, max_count) * 15)
            bar = "█" * bar_len
            hour_str = f"{hour:02d}:00"
            text += f"{hour_str} | {bar} {count}\n"

        text += "```\n"
        text += f"\n🔥 **Peak hour:** `{max(hour_counts, key=hour_counts.get):02d}:00` ({max_count} msgs)"

        await message.edit_text(text)

    except Exception as e:
        await message.edit_text(f"❌ Activity error: `{e}`")



# ==========================================
# 👤 TG - Full User Details Command
# ==========================================

@app.on_message(filters.me & filters.command("tg", prefixes="."))
async def tg_cmd(client, message: Message):
    try:
        import json as _json

        args = message.text.split(None, 1)
        target = None

        if len(args) > 1:
            target = args[1].strip()
        elif message.reply_to_message:
            target = message.reply_to_message.from_user.id
        else:
            await message.edit_text(
                "⚠️ **Usage:**\n"
                "`.tg @username`\n"
                "`.tg 123456789`\n"
                "Or reply to a user"
            )
            return

        await message.edit_text("🔍 Fetching user details...")

        # Get user
        try:
            user = await client.get_users(target)
        except Exception as e:
            await message.edit_text(f"❌ User not found: `{e}`")
            return

        # Basic details
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "None"
        user_id = user.id
        dc = user.dc_id or "?"
        is_bot = user.is_bot
        is_verified = user.is_verified
        is_premium = user.is_premium
        is_fake = user.is_fake
        is_scam = user.is_scam
        phone = user.phone_number or "Hidden"
        bio = None

        # Get full user info with bio
        try:
            full = await client.get_chat(user_id)
            bio = full.bio or "None"
        except:
            bio = "N/A"

        # Find common groups
        await message.edit_text("🔍 Finding common groups...")
        common_groups = []
        try:
            async for dialog in client.get_dialogs():
                if dialog.chat.type.name in ["GROUP", "SUPERGROUP"]:
                    try:
                        member = await client.get_chat_member(dialog.chat.id, user_id)
                        if member:
                            common_groups.append(f"• {dialog.chat.title}")
                        if len(common_groups) >= 15:
                            break
                    except:
                        pass
        except:
            pass

        groups_text = "\n".join(common_groups) if common_groups else "No common groups found"

        # Last seen
        last_seen = "Hidden"
        try:
            status = user.status
            if status:
                sname = type(status).__name__
                if "Online" in sname: last_seen = "🟢 Online Now"
                elif "Recently" in sname: last_seen = "🕐 Recently"
                elif "LastMonth" in sname: last_seen = "📅 Last Month"
                elif "LastWeek" in sname: last_seen = "📅 Last Week"
                elif "Long" in sname: last_seen = "📅 Long Ago"
                elif "Offline" in sname and hasattr(status, "date"):
                    last_seen = status.date.strftime("%d %b %Y %H:%M") if status.date else "Hidden"
        except: pass

        # Profile photos count
        photos_count = 0
        try:
            photos_count = await client.get_profile_photos_count(user_id)
        except: pass

        # Stories count
        stories_count = 0
        try:
            stories = await client.get_user_stories(user_id)
            stories_count = len(stories) if stories else 0
        except: pass

        # Admin in groups check
        admin_groups = []
        for g in common_groups:
            try:
                gname = g.replace("• ", "")
                async for dialog in client.get_dialogs():
                    if dialog.chat.title == gname:
                        member = await client.get_chat_member(dialog.chat.id, user_id)
                        if member.status.name in ["ADMINISTRATOR", "OWNER"]:
                            admin_groups.append(gname)
                        break
            except: pass

        admin_text = "\n".join(f"⭐ {g}" for g in admin_groups) if admin_groups else "None"

        # Profile link
        profile_link = f"tg://user?id={user_id}"

        text = (
            f"👤 **User Details**\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"**Name:** [{full_name}]({profile_link})\n"
            f"**Username:** {username}\n"
            f"**ID:** `{user_id}`\n"
            f"**Phone:** `{phone}`\n"
            f"**DC:** `{dc}`\n"
            f"**Bio:** {bio}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"**Last Seen:** {last_seen}\n"
            f"**Profile Photos:** `{photos_count}`\n"
            f"**Stories:** `{stories_count}`\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"**Bot:** {'✅' if is_bot else '❌'} | "
            f"**Verified:** {'✅' if is_verified else '❌'} | "
            f"**Premium:** {'✅' if is_premium else '❌'}\n"
            f"**Fake:** {'⚠️' if is_fake else '❌'} | "
            f"**Scam:** {'⚠️' if is_scam else '❌'}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"**Common Groups ({len(common_groups)}):**\n"
            f"{groups_text}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"**Admin In:**\n"
            f"{admin_text}"
        )

        # Send with profile photo
        try:
            photo = await client.download_media(user.photo.big_file_id)
            await message.delete()
            await client.send_photo(message.chat.id, photo, caption=text)
            os.unlink(photo)
        except:
            await message.edit_text(text)

    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")



# ==========================================
# ⌨️ TYPING COMMAND
# ==========================================

# Usage: .typing 10 → Show typing for 10 seconds (default 5s, max 60s)
@app.on_message(filters.me & filters.command("typing", prefixes="."))
async def typing_cmd(client, message: Message):
    try:
        from pyrogram.enums import ChatAction
        args = message.text.split(None, 1)
        duration = min(int(args[1]), 60) if len(args) > 1 and args[1].isdigit() else 5
        await message.delete()
        elapsed = 0
        while elapsed < duration:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            await asyncio.sleep(5)
            elapsed += 5
        await client.send_chat_action(message.chat.id, ChatAction.CANCEL)
    except Exception as e:
        try:
            await client.send_message(message.chat.id, f"❌ Error: `{e}`")
        except: pass



# ==========================================
# 🎭 CHAT ACTION COMMANDS
# ==========================================

@app.on_message(filters.me & filters.command("recording", prefixes="."))
async def recording_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        duration = min(int(args[1]), 60) if len(args) > 1 and args[1].isdigit() else 5
        await message.delete()
        elapsed = 0
        while elapsed < duration:
            await client.send_chat_action(message.chat.id, "record_audio")
            await asyncio.sleep(5)
            elapsed += 5
        await client.send_chat_action(message.chat.id, "cancel")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")

@app.on_message(filters.me & filters.command("uploading", prefixes="."))
async def uploading_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        duration = min(int(args[1]), 60) if len(args) > 1 and args[1].isdigit() else 5
        await message.delete()
        elapsed = 0
        while elapsed < duration:
            await client.send_chat_action(message.chat.id, "upload_document")
            await asyncio.sleep(5)
            elapsed += 5
        await client.send_chat_action(message.chat.id, "cancel")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")

@app.on_message(filters.me & filters.command("playing", prefixes="."))
async def playing_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        duration = min(int(args[1]), 60) if len(args) > 1 and args[1].isdigit() else 5
        await message.delete()
        elapsed = 0
        while elapsed < duration:
            await client.send_chat_action(message.chat.id, "choose_sticker")
            await asyncio.sleep(5)
            elapsed += 5
        await client.send_chat_action(message.chat.id, "cancel")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")

@app.on_message(filters.me & filters.command("cancel", prefixes="."))
async def cancel_action_cmd(client, message: Message):
    try:
        await message.delete()
        await client.send_chat_action(message.chat.id, "cancel")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")




# ==========================================
# 🖼️ IMAGE/FILE UTILITY COMMANDS (v6)
# ==========================================

# Command: .resize — Resize replied image
# Usage: .resize 512x512 or .resize 50%
@app.on_message(filters.me & filters.command("resize", prefixes="."))
async def resize_cmd(client, message: Message):
    try:
        from PIL import Image
        import tempfile

        reply = message.reply_to_message
        if not reply or not reply.photo:
            await message.edit_text("⚠️ Reply to an image with `.resize 512x512` or `.resize 50%`")
            return

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.resize 512x512` or `.resize 50%`")
            return

        size_arg = args[1].strip()
        await message.edit_text("⏳ Resizing image...")

        photo_path = await reply.download()
        img = Image.open(photo_path)

        if "%" in size_arg:
            percent = int(size_arg.replace("%", ""))
            new_w = int(img.width * percent / 100)
            new_h = int(img.height * percent / 100)
        elif "x" in size_arg.lower():
            parts = size_arg.lower().split("x")
            new_w = int(parts[0])
            new_h = int(parts[1])
        else:
            await message.edit_text("⚠️ Format: `512x512` or `50%`")
            os.unlink(photo_path)
            return

        img_resized = img.resize((new_w, new_h), Image.LANCZOS)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img_resized.save(f.name, "PNG")
            await message.delete()
            await client.send_photo(
                message.chat.id,
                f.name,
                caption=f"🖼 Resized to **{new_w}x{new_h}**"
            )
            os.unlink(f.name)
        os.unlink(photo_path)

    except Exception as e:
        await message.edit_text(f"❌ Resize error: `{e}`")


# Command: .pdf — Convert replied images to a single PDF
# Usage: Reply to image and type .pdf or .pdf 5 (take last 5 images)
@app.on_message(filters.me & filters.command("pdf", prefixes="."))
async def pdf_cmd(client, message: Message):
    try:
        from PIL import Image
        import tempfile

        reply = message.reply_to_message
        if not reply or not reply.photo:
            await message.edit_text("⚠️ Reply to an image. Use `.pdf` or `.pdf 5` (last 5 images)")
            return

        args = message.text.split(None, 1)
        count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1

        await message.edit_text(f"⏳ Converting {count} image(s) to PDF...")

        images = []
        if count == 1:
            # Single image from reply
            photo_path = await reply.download()
            img = Image.open(photo_path).convert("RGB")
            images.append(img)
            temp_paths = [photo_path]
        else:
            # Fetch last N images from chat
            temp_paths = []
            collected = 0
            async for msg in client.get_chat_history(message.chat.id, limit=50):
                if msg.photo and collected < count:
                    photo_path = await msg.download()
                    img = Image.open(photo_path).convert("RGB")
                    images.append(img)
                    temp_paths.append(photo_path)
                    collected += 1
                if collected >= count:
                    break
            images.reverse()

        if not images:
            await message.edit_text("⚠️ No images found.")
            return

        # Save as PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
            if len(images) == 1:
                images[0].save(pdf_path, "PDF")
            else:
                images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])

        await message.delete()
        await client.send_document(
            message.chat.id,
            pdf_path,
            caption=f"📄 PDF — {len(images)} page(s)"
        )

        os.unlink(pdf_path)
        for p in temp_paths:
            try:
                os.unlink(p)
            except:
                pass

    except Exception as e:
        await message.edit_text(f"❌ PDF error: `{e}`")


# Command: .ss — Take screenshot of a website
# Usage: .ss https://google.com
@app.on_message(filters.me & filters.command("ss", prefixes="."))
async def ss_cmd(client, message: Message):
    try:
        import tempfile

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.ss https://google.com`")
            return

        url = args[1].strip()
        if not url.startswith("http"):
            url = "https://" + url

        await message.edit_text(f"📸 Taking screenshot of `{url}`...")

        screenshot_url = f"https://image.thum.io/get/width/1280/crop/900/noanimate/{url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(screenshot_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    img_data = await resp.read()
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                        f.write(img_data)
                        tmp_path = f.name

                    await message.delete()
                    await client.send_photo(
                        message.chat.id,
                        tmp_path,
                        caption=f"📸 Screenshot: {url}"
                    )
                    os.unlink(tmp_path)
                else:
                    await message.edit_text(f"❌ Screenshot failed. Status: {resp.status}")

    except asyncio.TimeoutError:
        await message.edit_text("❌ Screenshot timed out. Try again.")
    except Exception as e:
        await message.edit_text(f"❌ Screenshot error: `{e}`")


# Command: .down — Download file from URL and send
# Usage: .down https://example.com/file.zip
@app.on_message(filters.me & filters.command("down", prefixes="."))
async def down_cmd(client, message: Message):
    try:
        import tempfile
        import urllib.parse

        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ Usage: `.down <url>`")
            return

        url = args[1].strip()
        if not url.startswith("http"):
            url = "https://" + url

        await message.edit_text(f"⬇️ Downloading...")

        max_size = 50 * 1024 * 1024  # 50MB

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status != 200:
                    await message.edit_text(f"❌ Download failed. HTTP {resp.status}")
                    return

                content_length = resp.headers.get("Content-Length")
                if content_length and int(content_length) > max_size:
                    await message.edit_text(f"❌ File too large (>{50}MB limit)")
                    return

                # Get filename from URL or headers
                fname = ""
                if "Content-Disposition" in resp.headers:
                    cd = resp.headers["Content-Disposition"]
                    if "filename=" in cd:
                        fname = cd.split("filename=")[-1].strip('"').strip("'")
                if not fname:
                    fname = os.path.basename(urllib.parse.urlparse(url).path) or "downloaded_file"

                # Download with progress
                downloaded = 0
                chunks = []
                async for chunk in resp.content.iter_chunked(1024 * 256):
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    if downloaded > max_size:
                        await message.edit_text(f"❌ File exceeds 50MB limit. Stopped.")
                        return

                mb = downloaded / (1024 * 1024)
                await message.edit_text(f"⬇️ Downloaded {mb:.1f} MB. Sending...")

                with tempfile.NamedTemporaryFile(delete=False, suffix="_" + fname) as f:
                    for c in chunks:
                        f.write(c)
                    tmp_path = f.name

        await message.delete()
        await client.send_document(
            message.chat.id,
            tmp_path,
            file_name=fname,
            caption=f"📥 **{fname}** ({mb:.1f} MB)"
        )
        os.unlink(tmp_path)

    except asyncio.TimeoutError:
        await message.edit_text("❌ Download timed out (120s limit).")
    except Exception as e:
        await message.edit_text(f"❌ Download error: `{e}`")


# Command: .ocr — Extract text from image using OCR
# Usage: Reply to image and type .ocr
@app.on_message(filters.me & filters.command("ocr", prefixes="."))
async def ocr_cmd(client, message: Message):
    try:
        import tempfile

        reply = message.reply_to_message
        if not reply or not (reply.photo or (reply.document and reply.document.mime_type and "image" in reply.document.mime_type)):
            await message.edit_text("⚠️ Reply to an image with `.ocr`")
            return

        await message.edit_text("🔍 Extracting text (OCR)...")

        photo_path = await reply.download()

        # Try pytesseract first
        ocr_text = None
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(photo_path)
            ocr_text = pytesseract.image_to_string(img)
        except Exception:
            pass

        # Fallback: OCR.space API
        if not ocr_text or not ocr_text.strip():
            try:
                import requests
                with open(photo_path, "rb") as img_file:
                    resp = requests.post(
                        "https://api.ocr.space/parse/image",
                        files={"file": img_file},
                        data={"apikey": "helloworld", "language": "eng"},
                        timeout=30
                    )
                result = resp.json()
                if result.get("ParsedResults"):
                    ocr_text = result["ParsedResults"][0].get("ParsedText", "")
            except Exception as api_err:
                await message.edit_text(f"❌ OCR API error: `{api_err}`")
                os.unlink(photo_path)
                return

        os.unlink(photo_path)

        if not ocr_text or not ocr_text.strip():
            await message.edit_text("⚠️ No text detected in this image.")
            return

        ocr_text = ocr_text.strip()

        # If text too long, send as file
        if len(ocr_text) > 4000:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write(ocr_text)
                tmp_path = f.name
            await message.delete()
            await client.send_document(
                message.chat.id,
                tmp_path,
                caption="📝 OCR Result (text too long)"
            )
            os.unlink(tmp_path)
        else:
            await message.edit_text(f"📝 **OCR Result:**\n\n```\n{ocr_text}\n```")

    except Exception as e:
        await message.edit_text(f"❌ OCR error: `{e}`")




# ==========================================
# 📧 MAIL.TM TEMP EMAIL COMMANDS
# ==========================================
import re
import string

mail_sessions = {}  # chat_id -> {email, password, token, account_id}


# Command: .mail
@app.on_message(filters.me & filters.command("mail", prefixes="."))
async def mail_cmd(client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.edit_text(
                "📧 **Mail.tm Commands:**\n\n"
                "├ `.mail new` — Create temp email\n"
                "├ `.mail inbox` — Check inbox\n"
                "├ `.mail read [id]` — Read email\n"
                "├ `.mail otp` — Extract OTP from latest\n"
                "├ `.mail watch [sec]` — Monitor inbox\n"
                "├ `.mail delete` — Delete account\n"
                "├ `.mail domains` — Show domains\n"
                "└ `.mail chatpdf` — Generate ChatPDF account"
            )
            return

        sub_cmd = args[1].lower()
        chat_id = message.chat.id

        # ─── .mail new ───
        if sub_cmd == "new":
            await message.edit_text("📧 Creating temp email...")
            async with aiohttp.ClientSession() as session:
                # Get available domain
                async with session.get("https://api.mail.tm/domains") as resp:
                    if resp.status != 200:
                        await message.edit_text("❌ Failed to fetch domains from mail.tm")
                        return
                    data = await resp.json()
                    domains = data.get("hydra:member", data) if isinstance(data, dict) else data
                    if not domains:
                        await message.edit_text("❌ No domains available.")
                        return
                    domain = domains[0]["domain"]

                # Generate random credentials
                username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                email = f"{username}@{domain}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

                # Create account
                async with session.post(
                    "https://api.mail.tm/accounts",
                    json={"address": email, "password": password},
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status not in (200, 201):
                        err = await resp.text()
                        await message.edit_text(f"❌ Account creation failed: `{err[:200]}`")
                        return
                    acc_data = await resp.json()
                    account_id = acc_data.get("id", "")

                # Get auth token
                async with session.post(
                    "https://api.mail.tm/token",
                    json={"address": email, "password": password},
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status != 200:
                        await message.edit_text("❌ Failed to get auth token.")
                        return
                    token_data = await resp.json()
                    token = token_data.get("token", "")

                # Store session
                mail_sessions[chat_id] = {
                    "email": email,
                    "password": password,
                    "token": token,
                    "account_id": account_id
                }

                await message.edit_text(
                    f"📧 **Temp Email Created!**\n\n"
                    f"├ **Email:** `{email}`\n"
                    f"├ **Password:** `{password}`\n"
                    f"└ **Status:** ✅ Active\n\n"
                    f"Use `.mail inbox` to check messages."
                )

        # ─── .mail inbox ───
        elif sub_cmd == "inbox":
            if chat_id not in mail_sessions:
                await message.edit_text("⚠️ No active mail session. Use `.mail new` first.")
                return

            token = mail_sessions[chat_id]["token"]
            email = mail_sessions[chat_id]["email"]
            await message.edit_text("📥 Checking inbox...")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.mail.tm/messages",
                    headers={"Authorization": f"Bearer {token}"}
                ) as resp:
                    if resp.status == 401:
                        await message.edit_text("❌ Token expired. Create new email with `.mail new`")
                        return
                    if resp.status != 200:
                        await message.edit_text(f"❌ Failed to fetch inbox. Status: {resp.status}")
                        return
                    data = await resp.json()
                    messages = data.get("hydra:member", data) if isinstance(data, dict) else data

            if not messages:
                await message.edit_text(f"📭 **Inbox Empty**\n\n📧 `{email}`")
                return

            text = f"📥 **Inbox** — `{email}`\n\n"
            for i, msg in enumerate(messages[:10], 1):
                sender = msg.get("from", {}).get("address", "Unknown")
                subject = msg.get("subject", "No Subject")
                msg_id = msg.get("id", "")
                created = msg.get("createdAt", "")[:16].replace("T", " ")
                text += f"**{i}.** `{msg_id[:8]}`\n"
                text += f"├ **From:** {sender}\n"
                text += f"├ **Subject:** {subject}\n"
                text += f"└ **Date:** {created}\n\n"

            text += f"Use `.mail read <id>` to read a message."
            await message.edit_text(text[:4000])

        # ─── .mail read [id] ───
        elif sub_cmd == "read":
            if chat_id not in mail_sessions:
                await message.edit_text("⚠️ No active mail session. Use `.mail new` first.")
                return

            token = mail_sessions[chat_id]["token"]

            # Get message ID
            msg_id = args[2] if len(args) > 2 else None

            async with aiohttp.ClientSession() as session:
                if not msg_id:
                    # Get latest message
                    async with session.get(
                        "https://api.mail.tm/messages",
                        headers={"Authorization": f"Bearer {token}"}
                    ) as resp:
                        if resp.status != 200:
                            await message.edit_text("❌ Failed to fetch inbox.")
                            return
                        data = await resp.json()
                        messages = data.get("hydra:member", data) if isinstance(data, dict) else data
                        if not messages:
                            await message.edit_text("📭 No messages to read.")
                            return
                        msg_id = messages[0]["id"]

                # Fetch full message
                async with session.get(
                    f"https://api.mail.tm/messages/{msg_id}",
                    headers={"Authorization": f"Bearer {token}"}
                ) as resp:
                    if resp.status != 200:
                        await message.edit_text(f"❌ Failed to read message. Status: {resp.status}")
                        return
                    msg_data = await resp.json()

            sender = msg_data.get("from", {}).get("address", "Unknown")
            subject = msg_data.get("subject", "No Subject")
            created = msg_data.get("createdAt", "")[:16].replace("T", " ")
            body = msg_data.get("text", "") or ""

            # Strip HTML tags if text is empty but html exists
            if not body.strip():
                html_body = msg_data.get("html", "") or ""
                if html_body:
                    body = re.sub(r'<[^>]+>', '', html_body)
                    body = re.sub(r'\s+', ' ', body).strip()

            text = (
                f"📨 **Email:**\n\n"
                f"├ **From:** {sender}\n"
                f"├ **Subject:** {subject}\n"
                f"├ **Date:** {created}\n"
                f"└ **ID:** `{msg_id}`\n\n"
                f"**Body:**\n{body[:3500]}"
            )
            await message.edit_text(text[:4000])

        # ─── .mail otp ───
        elif sub_cmd == "otp":
            if chat_id not in mail_sessions:
                await message.edit_text("⚠️ No active mail session. Use `.mail new` first.")
                return

            token = mail_sessions[chat_id]["token"]
            await message.edit_text("🔍 Searching for OTP...")

            async with aiohttp.ClientSession() as session:
                # Get latest message
                async with session.get(
                    "https://api.mail.tm/messages",
                    headers={"Authorization": f"Bearer {token}"}
                ) as resp:
                    if resp.status != 200:
                        await message.edit_text("❌ Failed to fetch inbox.")
                        return
                    data = await resp.json()
                    messages = data.get("hydra:member", data) if isinstance(data, dict) else data
                    if not messages:
                        await message.edit_text("📭 No messages. OTP not found.")
                        return

                # Read latest message
                msg_id = messages[0]["id"]
                async with session.get(
                    f"https://api.mail.tm/messages/{msg_id}",
                    headers={"Authorization": f"Bearer {token}"}
                ) as resp:
                    if resp.status != 200:
                        await message.edit_text("❌ Failed to read message.")
                        return
                    msg_data = await resp.json()

            body = msg_data.get("text", "") or ""
            if not body.strip():
                html_body = msg_data.get("html", "") or ""
                body = re.sub(r'<[^>]+>', '', html_body)

            # Search for 4-8 digit OTP
            otp_matches = re.findall(r'\b(\d{4,8})\b', body)
            subject = msg_data.get("subject", "")
            otp_in_subject = re.findall(r'\b(\d{4,8})\b', subject)

            all_otps = otp_in_subject + otp_matches

            if all_otps:
                otp = all_otps[0]
                await message.edit_text(
                    f"🔑 **OTP Found!**\n\n"
                    f"├ **OTP:** `{otp}`\n"
                    f"├ **From:** {msg_data.get('from', {}).get('address', 'Unknown')}\n"
                    f"└ **Subject:** {msg_data.get('subject', 'N/A')}"
                )
            else:
                await message.edit_text("⚠️ No OTP (4-8 digit code) found in latest email.")

        # ─── .mail watch [seconds] ───
        elif sub_cmd == "watch":
            if chat_id not in mail_sessions:
                await message.edit_text("⚠️ No active mail session. Use `.mail new` first.")
                return

            token = mail_sessions[chat_id]["token"]
            duration = int(args[2]) if len(args) > 2 else 60
            duration = min(duration, 300)  # Max 5 minutes

            await message.edit_text(f"👁️ Watching inbox for **{duration}s**...")

            # Get current message count
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.mail.tm/messages",
                    headers={"Authorization": f"Bearer {token}"}
                ) as resp:
                    data = await resp.json()
                    messages = data.get("hydra:member", data) if isinstance(data, dict) else data
                    known_ids = {m["id"] for m in messages} if messages else set()

            start_time = time.time()
            checked = 0

            while time.time() - start_time < duration:
                await asyncio.sleep(5)
                checked += 1
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://api.mail.tm/messages",
                        headers={"Authorization": f"Bearer {token}"}
                    ) as resp:
                        if resp.status != 200:
                            continue
                        data = await resp.json()
                        messages = data.get("hydra:member", data) if isinstance(data, dict) else data

                if messages:
                    for msg in messages:
                        if msg["id"] not in known_ids:
                            known_ids.add(msg["id"])
                            sender = msg.get("from", {}).get("address", "Unknown")
                            subject = msg.get("subject", "No Subject")
                            await message.edit_text(
                                f"🔔 **New Email Received!**\n\n"
                                f"├ **From:** {sender}\n"
                                f"├ **Subject:** {subject}\n"
                                f"├ **ID:** `{msg['id'][:8]}`\n"
                                f"└ **Time:** {elapsed}s into watch\n\n"
                                f"Use `.mail read {msg['id']}` to read."
                            )
                            return

                # Update countdown every 15s
                if checked % 3 == 0:
                    try:
                        await message.edit_text(f"👁️ Watching inbox... **{remaining}s** remaining")
                    except:
                        pass

            await message.edit_text(f"⏱️ Watch ended after **{duration}s**. No new emails received.")

        # ─── .mail delete ───
        elif sub_cmd == "delete":
            if chat_id not in mail_sessions:
                await message.edit_text("⚠️ No active mail session.")
                return

            token = mail_sessions[chat_id]["token"]
            account_id = mail_sessions[chat_id].get("account_id", "")
            email = mail_sessions[chat_id]["email"]

            if account_id:
                async with aiohttp.ClientSession() as session:
                    async with session.delete(
                        f"https://api.mail.tm/accounts/{account_id}",
                        headers={"Authorization": f"Bearer {token}"}
                    ) as resp:
                        pass  # 204 = success, but we clear session regardless

            del mail_sessions[chat_id]
            await message.edit_text(f"🗑️ **Email Deleted:** `{email}`\n\nSession cleared.")

        # ─── .mail domains ───
        elif sub_cmd == "domains":
            await message.edit_text("🌐 Fetching available domains...")
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.mail.tm/domains") as resp:
                    if resp.status != 200:
                        await message.edit_text("❌ Failed to fetch domains.")
                        return
                    data = await resp.json()
                    domains = data.get("hydra:member", data) if isinstance(data, dict) else data

            if not domains:
                await message.edit_text("⚠️ No domains available.")
                return

            text = "🌐 **Available Domains:**\n\n"
            for i, d in enumerate(domains, 1):
                text += f"**{i}.** `@{d['domain']}`\n"
            await message.edit_text(text)

        # ─── .mail chatpdf ───
        elif sub_cmd == "chatpdf":
            await message.edit_text("🤖 Generating ChatPDF account via temp mail...")

            async with aiohttp.ClientSession() as session:
                # Step 1: Create temp email
                async with session.get("https://api.mail.tm/domains") as resp:
                    if resp.status != 200:
                        await message.edit_text("❌ Failed to fetch domains.")
                        return
                    data = await resp.json()
                    domains = data.get("hydra:member", data) if isinstance(data, dict) else data
                    if not domains:
                        await message.edit_text("❌ No domains available.")
                        return
                    domain = domains[0]["domain"]

                username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                email = f"{username}@{domain}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

                # Create mail.tm account
                async with session.post(
                    "https://api.mail.tm/accounts",
                    json={"address": email, "password": password},
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status not in (200, 201):
                        await message.edit_text("❌ Failed to create temp email for ChatPDF.")
                        return
                    acc_data = await resp.json()
                    account_id = acc_data.get("id", "")

                # Get token
                async with session.post(
                    "https://api.mail.tm/token",
                    json={"address": email, "password": password},
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status != 200:
                        await message.edit_text("❌ Failed to get mail token.")
                        return
                    token_data = await resp.json()
                    mail_token = token_data.get("token", "")

                await message.edit_text("🤖 Generating ChatPDF checkout...")

                # ChatPDF via VPS3 API
                try:
                    import requests as _req
                    r_api = _req.get("http://155.103.70.111:5000/api/chatgpt/gen", timeout=90)
                    api_data = r_api.json()
                    if api_data.get("status") == "ok":
                        checkout_url = api_data.get("url", "N/A")
                        acc_email = api_data.get("email", email)
                        acc_pass = api_data.get("password", "Daxx@2026#")
                        mail_sessions[chat_id] = {"email": acc_email, "password": acc_pass, "token": mail_token, "account_id": account_id}
                        await message.edit_text(
                            f"✅ **ChatPDF Generated!**\n\n"
                            f"📧 **Email:** `{acc_email}`\n"
                            f"🔑 **Password:** `{acc_pass}`\n"
                            f"💳 **Checkout:** `{checkout_url}`"
                        )
                    else:
                        await message.edit_text("❌ ChatPDF error: " + str(api_data.get("message","Unknown"))[:100])
                except Exception as cp_err:
                    await message.edit_text(f"❌ ChatPDF error: `{str(cp_err)[:100]}`")

    except Exception as e:
        try:
            await message.edit_text(f"❌ Mail error: `{str(e)[:100]}`")
        except:
            pass



# ==========================================
# 🔐 1VPN CHECKOUT GENERATOR
# ==========================================

@app.on_message(filters.me & filters.command("1vpn", prefixes="."))
async def vpn_gen_cmd(client, message: Message):
    try:
        import requests as _req, re, random, string
        from bs4 import BeautifulSoup as _BS

        args = message.text.split(None, 1)
        plan = args[1].strip().lower() if len(args) > 1 else "yearly"
        if plan not in ["yearly", "monthly", "free"]:
            await message.edit_text("⚠️ **Usage:** `.1vpn yearly` or `.1vpn monthly`")
            return

        await message.edit_text("⚙️ Generating 1VPN checkout...")

        _headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
            "Accept": "text/html,*/*",
        }
        s = _req.Session()

        # Temp email
        r_d = _req.get("https://api.mail.tm/domains", timeout=10)
        domain = r_d.json()["hydra:member"][0]["domain"]
        user = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = f"{user}@{domain}"
        password = "Daxx@2026#"
        _req.post("https://api.mail.tm/accounts", json={"address": email, "password": password}, timeout=10)

        # Signup
        r = s.get("https://1vpn.org/signup/", headers=_headers, timeout=15)
        soup = _BS(r.text, "html.parser")
        csrf = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        s.post("https://1vpn.org/signup/",
            headers={**_headers, "Referer": "https://1vpn.org/signup/", "Origin": "https://1vpn.org"},
            data={"csrfmiddlewaretoken": csrf, "email": email, "password1": password},
            timeout=15, allow_redirects=True)

        # Plan page
        r2 = s.get("https://1vpn.org/select-plan/", headers=_headers, timeout=15)
        csrf2 = _BS(r2.text, "html.parser").find("input", {"name": "csrfmiddlewaretoken"})["value"]

        # Submit checkout
        r3 = s.post("https://1vpn.org/payments/select_method/",
            headers={**_headers, "Referer": "https://1vpn.org/select-plan/", "Origin": "https://1vpn.org"},
            data={"csrfmiddlewaretoken": csrf2, "plan": plan, "payment_method": "stripe"},
            timeout=20, allow_redirects=True)

        checkout_url = r3.url if "stripe" in r3.url.lower() or "pay.1vpn" in r3.url.lower() else None

        if checkout_url:
            await message.edit_text(
                f"✅ **1VPN Checkout Generated!**\n\n"
                f"📧 **Email:** `{email}`\n"
                f"🔑 **Password:** `{password}`\n"
                f"📦 **Plan:** `{plan}`\n"
                f"💳 **Checkout:** `{checkout_url}`"
            )
        else:
            await message.edit_text(
                f"⚠️ Account created but no checkout URL.\n\n"
                f"📧 **Email:** `{email}`\n"
                f"🔑 **Password:** `{password}`\n"
                f"🌐 Login: https://1vpn.org/select-plan/"
            )

    except Exception as e:
        await message.edit_text(f"❌ 1VPN error: `{str(e)[:100]}`")



# ==========================================
# 🛡️ GROUP ADMIN COMMANDS
# ==========================================

@app.on_message(filters.me & filters.command("promote", prefixes="."))
async def promote_cmd(client, message: Message):
    try:
        from pyrogram.types import ChatAdministratorRights
        reply = message.reply_to_message
        if not reply:
            await message.edit_text("⚠️ Reply to a user to promote!")
            return
        user_id = reply.from_user.id
        user_name = reply.from_user.first_name
        await client.promote_chat_member(
            message.chat.id, user_id,
            privileges=ChatAdministratorRights(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
            )
        )
        await message.edit_text(f"✅ **{user_name}** promoted to Admin!")
    except Exception as e:
        await message.edit_text(f"❌ Promote error: `{str(e)[:100]}`")

@app.on_message(filters.me & filters.command("demote", prefixes="."))
async def demote_cmd(client, message: Message):
    try:
        from pyrogram.types import ChatAdministratorRights
        reply = message.reply_to_message
        if not reply:
            await message.edit_text("⚠️ Reply to a user to demote!")
            return
        user_id = reply.from_user.id
        user_name = reply.from_user.first_name
        await client.promote_chat_member(
            message.chat.id, user_id,
            privileges=ChatAdministratorRights(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            )
        )
        await message.edit_text(f"⬇️ **{user_name}** demoted from Admin!")
    except Exception as e:
        await message.edit_text(f"❌ Demote error: `{str(e)[:100]}`")

@app.on_message(filters.me & filters.command("title", prefixes="."))
async def title_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        reply = message.reply_to_message
        if not reply or len(args) < 2:
            await message.edit_text("⚠️ Reply to admin + `.title New Title`")
            return
        user_id = reply.from_user.id
        user_name = reply.from_user.first_name
        title = args[1].strip()[:16]
        await client.set_administrator_title(message.chat.id, user_id, title)
        await message.edit_text(f"✅ **{user_name}** ka title: `{title}`")
    except Exception as e:
        await message.edit_text(f"❌ Title error: `{str(e)[:100]}`")

@app.on_message(filters.me & filters.command("tmute", prefixes="."))
async def tmute_cmd(client, message: Message):
    try:
        from pyrogram.types import ChatPermissions
        from datetime import datetime, timedelta
        args = message.text.split(None, 1)
        reply = message.reply_to_message
        if not reply:
            await message.edit_text("⚠️ `.tmute 10m` | `.tmute 2h` | `.tmute 1d`")
            return
        user_id = reply.from_user.id
        user_name = reply.from_user.first_name
        duration = 60
        if len(args) > 1:
            t = args[1].strip()
            if t.endswith("m"): duration = int(t[:-1]) * 60
            elif t.endswith("h"): duration = int(t[:-1]) * 3600
            elif t.endswith("d"): duration = int(t[:-1]) * 86400
        until = datetime.utcnow() + timedelta(seconds=duration)
        await client.restrict_chat_member(
            message.chat.id, user_id,
            ChatPermissions(all_perms=False),
            until_date=until
        )
        dur_text = f"{duration//60}m" if duration < 3600 else f"{duration//3600}h"
        await message.edit_text(f"🔇 **{user_name}** muted for `{dur_text}`")
    except Exception as e:
        await message.edit_text(f"❌ TMute error: `{str(e)[:100]}`")

@app.on_message(filters.me & filters.command("warn", prefixes="."))
async def warn_cmd(client, message: Message):
    try:
        reply = message.reply_to_message
        if not reply:
            await message.edit_text("⚠️ Reply to a user to warn!")
            return
        user_id = reply.from_user.id
        user_name = reply.from_user.first_name
        args = message.text.split(None, 1)
        reason = args[1] if len(args) > 1 else "No reason"
        key = f"{message.chat.id}_{user_id}"
        if not hasattr(warn_cmd, "warns"):
            warn_cmd.warns = {}
        warn_cmd.warns[key] = warn_cmd.warns.get(key, 0) + 1
        count = warn_cmd.warns[key]
        await message.edit_text(f"⚠️ **{user_name}** warned! (`{count}/3`)\n**Reason:** {reason}")
        if count >= 3:
            await client.ban_chat_member(message.chat.id, user_id)
            await message.reply(f"🚫 **{user_name}** banned after 3 warnings!")
            warn_cmd.warns[key] = 0
    except Exception as e:
        await message.edit_text(f"❌ Warn error: `{str(e)[:100]}`")

@app.on_message(filters.me & filters.command("unwarn", prefixes="."))
async def unwarn_cmd(client, message: Message):
    try:
        reply = message.reply_to_message
        if not reply:
            await message.edit_text("⚠️ Reply to a user!")
            return
        user_id = reply.from_user.id
        user_name = reply.from_user.first_name
        key = f"{message.chat.id}_{user_id}"
        if hasattr(warn_cmd, "warns"):
            warn_cmd.warns[key] = max(0, warn_cmd.warns.get(key, 1) - 1)
        await message.edit_text(f"✅ **{user_name}** ka 1 warn remove!")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{str(e)[:100]}`")

@app.on_message(filters.me & filters.command("unban", prefixes="."))
async def unban_cmd(client, message: Message):
    try:
        reply = message.reply_to_message
        if not reply:
            await message.edit_text("⚠️ Reply to a user!")
            return
        user_id = reply.from_user.id
        user_name = reply.from_user.first_name
        await client.unban_chat_member(message.chat.id, user_id)
        await message.edit_text(f"✅ **{user_name}** unbanned!")
    except Exception as e:
        await message.edit_text(f"❌ Unban error: `{str(e)[:100]}`")



@app.on_message(filters.me & filters.command("freecad", prefixes="."))
async def freecad_cmd(client, message: Message):
    try:
        import requests as _req
        args = message.text.split(None, 1)
        amount = args[1].strip() if len(args) > 1 else "1"
        try: float(amount)
        except: amount = "1"
        await message.edit_text(f"⚙️ Generating FreeCAD checkout (${amount})...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) Chrome/150.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,*/*",
            "Referer": "https://www.freecad.org/",
        }
        r = _req.get("https://www.freecad.org/stripe-checkout-session.php",
            params={"amount": amount, "currency": "usd"},
            headers=headers, timeout=20, allow_redirects=True)
        if "checkout.stripe.com" in r.url or "pay/" in r.url:
            await message.edit_text(
                f"✅ **FreeCAD Checkout!**\n\n"
                f"💰 **Amount:** `${amount} USD`\n"
                f"⚡ **Gateway:** Stripe\n\n"
                f"💳 **URL:** `{r.url}`",
                disable_web_page_preview=True
            )
        else:
            await message.edit_text("❌ Could not generate checkout.")
    except Exception as e:
        await message.edit_text(f"❌ FreeCAD error: `{str(e)[:100]}`")



# ==========================================
# 💳 STRIPE CHECKOUT GENERATOR
# ==========================================

_sk_store = {}  # chat_id -> sk_key

@app.on_message(filters.me & filters.command("setsk", prefixes="."))
async def setsk_cmd(client, message: Message):
    try:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.edit_text("⚠️ **Usage:** `.setsk sk_live_xxxxx`")
            return
        sk = args[1].strip()
        if not sk.startswith("sk_"):
            await message.edit_text("❌ Invalid SK key! Must start with `sk_live_` or `sk_test_`")
            return
        _sk_store["global"] = sk  # Global — works in all chats
        masked = sk[:12] + "..." + sk[-4:]
        await message.edit_text(f"✅ **Stripe SK saved!**\n`{masked}`")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{str(e)[:100]}`")

@app.on_message(filters.me & filters.command("ch", prefixes="."))
async def ch_cmd(client, message: Message):
    try:
        import requests as _req

        # Get SK from store or default
        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        args = message.text.split(None, 1)
        try:
            amount = float(args[1].strip()) if len(args) > 1 else 1.0
        except:
            amount = 1.0
        amount_cents = int(amount * 100)

        await message.edit_text(f"⚙️ Generating ${amount:.2f} checkout...")

        r = _req.post(
            "https://api.stripe.com/v1/checkout/sessions",
            auth=(sk, ""),
            data={
                "mode": "payment",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
                "line_items[0][price_data][currency]": "usd",
                "line_items[0][price_data][product_data][name]": "Payment",
                "line_items[0][price_data][unit_amount]": str(amount_cents),
                "line_items[0][quantity]": "1",
            },
            timeout=15
        )

        data = r.json()
        if r.status_code == 200:
            session_id = data.get("id", "")
            url = data.get("url", "")
            await message.edit_text(
                f"✅ **Stripe Checkout Generated!**\n\n"
                f"💰 **Amount:** `${amount:.2f} USD`\n"
                f"🔑 **Session:** `{session_id[:30]}...`\n\n"
                f"💳 **Checkout URL:**\n`{url}`",
                disable_web_page_preview=True
            )
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Stripe error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ Error: `{str(e)[:100]}`")



@app.on_message(filters.me & filters.command("inb", prefixes="."))
async def inb_cmd(client, message: Message):
    try:
        import requests as _req

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        args = message.text.split(None, 1)
        try:
            amount = float(args[1].strip()) if len(args) > 1 else 1.0
        except:
            amount = 1.0
        amount_cents = int(amount * 100)

        await message.edit_text(f"⚙️ Generating ${amount:.2f} invoice...")

        # Step 1: Create customer
        r_cust = _req.post("https://api.stripe.com/v1/customers",
            auth=(sk, ""),
            data={"email": "customer@example.com", "name": "Customer"},
            timeout=15)
        customer_id = r_cust.json().get("id", "")

        # Step 2: Create invoice item
        _req.post("https://api.stripe.com/v1/invoiceitems",
            auth=(sk, ""),
            data={
                "customer": customer_id,
                "amount": str(amount_cents),
                "currency": "usd",
                "description": f"Invoice ${amount:.2f}",
            },
            timeout=15)

        # Step 3: Create invoice
        r_inv = _req.post("https://api.stripe.com/v1/invoices",
            auth=(sk, ""),
            data={
                "customer": customer_id,
                "collection_method": "send_invoice",
                "days_until_due": "7",
            },
            timeout=15)
        inv_data = r_inv.json()
        inv_id = inv_data.get("id", "")

        # Step 4: Finalize invoice
        _req.post(f"https://api.stripe.com/v1/invoices/{inv_id}/finalize",
            auth=(sk, ""), timeout=15)

        # Step 5: Get invoice URL
        r_final = _req.get(f"https://api.stripe.com/v1/invoices/{inv_id}",
            auth=(sk, ""), timeout=15)
        final = r_final.json()
        inv_url = final.get("hosted_invoice_url", "N/A")
        inv_pdf = final.get("invoice_pdf", "N/A")
        inv_num = final.get("number", inv_id[:15])

        await message.edit_text(
            f"✅ **Invoice Generated!**\n\n"
            f"💰 **Amount:** `${amount:.2f} USD`\n"
            f"📋 **Invoice #:** `{inv_num}`\n"
            f"👤 **Customer:** `{customer_id}`\n\n"
            f"🌐 **Invoice URL:**\n`{inv_url}`\n\n"
            f"📄 **PDF:**\n`{inv_pdf}`",
            disable_web_page_preview=True
        )

    except Exception as e:
        await message.edit_text(f"❌ Invoice error: `{str(e)[:100]}`")


# ==========================================
# 💳 STRIPE SK COMMANDS (Advanced)
# ==========================================

# Command: .pi [amount] — Payment Intent
@app.on_message(filters.me & filters.command("pi", prefixes="."))
async def pi_cmd(client, message: Message):
    try:
        import requests as _req

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        args = message.text.split(None, 1)
        try:
            amount = float(args[1].strip()) if len(args) > 1 else 1.0
        except:
            amount = 1.0
        amount_cents = int(amount * 100)

        await message.edit_text(f"⚙️ Creating ${amount:.2f} Payment Intent...")

        r = _req.post(
            "https://api.stripe.com/v1/payment_intents",
            auth=(sk, ""),
            data={
                "amount": str(amount_cents),
                "currency": "usd",
                "payment_method_types[]": "card",
            },
            timeout=15
        )

        data = r.json()
        if r.status_code == 200:
            pi_id = data.get("id", "")
            client_secret = data.get("client_secret", "")
            status = data.get("status", "")
            await message.edit_text(
                f"✅ **Payment Intent Created!**\n\n"
                f"💰 **Amount:** `${amount:.2f} USD`\n"
                f"🔑 **PI ID:** `{pi_id}`\n"
                f"📋 **Status:** `{status}`\n"
                f"🔐 **Client Secret:** `{client_secret}`"
            )
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Stripe error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ PI error: `{str(e)[:100]}`")


# Command: .skinfo — Show Stripe account info
@app.on_message(filters.me & filters.command("skinfo", prefixes="."))
async def skinfo_cmd(client, message: Message):
    try:
        import requests as _req

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        await message.edit_text("⚙️ Fetching account info...")

        r = _req.get("https://api.stripe.com/v1/account", auth=(sk, ""), timeout=15)
        data = r.json()

        if r.status_code == 200:
            biz_name = data.get("business_profile", {}).get("name") or data.get("settings", {}).get("dashboard", {}).get("display_name") or "N/A"
            email = data.get("email", "N/A")
            country = data.get("country", "N/A")
            currency = data.get("default_currency", "N/A")
            mode = "🟢 LIVE" if sk.startswith("sk_live_") else "🟡 TEST"
            charges = "✅" if data.get("charges_enabled") else "❌"
            payouts = "✅" if data.get("payouts_enabled") else "❌"

            await message.edit_text(
                f"🔐 **Stripe Account Info**\n\n"
                f"├ **Business:** {biz_name}\n"
                f"├ **Email:** `{email}`\n"
                f"├ **Country:** {country}\n"
                f"├ **Currency:** {currency.upper()}\n"
                f"├ **Mode:** {mode}\n"
                f"├ **Charges:** {charges}\n"
                f"└ **Payouts:** {payouts}"
            )
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Stripe error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ SKInfo error: `{str(e)[:100]}`")


# Command: .balance — Show Stripe account balance
@app.on_message(filters.me & filters.command("balance", prefixes="."))
async def balance_cmd(client, message: Message):
    try:
        import requests as _req

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        await message.edit_text("⚙️ Fetching balance...")

        r = _req.get("https://api.stripe.com/v1/balance", auth=(sk, ""), timeout=15)
        data = r.json()

        if r.status_code == 200:
            text = "💰 **Stripe Account Balance**\n\n"

            available = data.get("available", [])
            if available:
                text += "**Available:**\n"
                for bal in available:
                    amt = bal.get("amount", 0) / 100
                    cur = bal.get("currency", "usd").upper()
                    text += f"├ `{amt:.2f} {cur}`\n"

            pending = data.get("pending", [])
            if pending:
                text += "\n**Pending:**\n"
                for bal in pending:
                    amt = bal.get("amount", 0) / 100
                    cur = bal.get("currency", "usd").upper()
                    text += f"├ `{amt:.2f} {cur}`\n"

            if not available and not pending:
                text += "No balance data found."

            await message.edit_text(text)
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Stripe error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ Balance error: `{str(e)[:100]}`")


# Command: .charges [n] — List last N charges
@app.on_message(filters.me & filters.command("charges", prefixes="."))
async def charges_cmd(client, message: Message):
    try:
        import requests as _req
        from datetime import datetime

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        args = message.text.split(None, 1)
        try:
            limit = int(args[1].strip()) if len(args) > 1 else 5
        except:
            limit = 5
        limit = min(max(limit, 1), 20)

        await message.edit_text(f"⚙️ Fetching last {limit} charges...")

        r = _req.get(
            f"https://api.stripe.com/v1/charges?limit={limit}",
            auth=(sk, ""), timeout=15
        )
        data = r.json()

        if r.status_code == 200:
            charges = data.get("data", [])
            if not charges:
                await message.edit_text("ℹ️ No charges found.")
                return

            text = f"💳 **Last {len(charges)} Charges:**\n\n"
            for ch in charges:
                ch_id = ch.get("id", "N/A")[:20]
                amt = ch.get("amount", 0) / 100
                cur = ch.get("currency", "usd").upper()
                status = ch.get("status", "N/A")
                card = ch.get("payment_method_details", {}).get("card", {})
                last4 = card.get("last4", "****")
                desc = ch.get("description", "No desc")
                created = datetime.fromtimestamp(ch.get("created", 0)).strftime("%d/%m %H:%M")
                status_icon = "✅" if status == "succeeded" else "❌" if status == "failed" else "⏳"

                text += (
                    f"{status_icon} `{ch_id}`\n"
                    f"├ **{amt:.2f} {cur}** | Card: `*{last4}`\n"
                    f"├ {desc[:30]} | {created}\n\n"
                )

            await message.edit_text(text[:4000])
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Stripe error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ Charges error: `{str(e)[:100]}`")


# Command: .customers [n] — List last N customers
@app.on_message(filters.me & filters.command("customers", prefixes="."))
async def customers_cmd(client, message: Message):
    try:
        import requests as _req
        from datetime import datetime

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        args = message.text.split(None, 1)
        try:
            limit = int(args[1].strip()) if len(args) > 1 else 5
        except:
            limit = 5
        limit = min(max(limit, 1), 20)

        await message.edit_text(f"⚙️ Fetching last {limit} customers...")

        r = _req.get(
            f"https://api.stripe.com/v1/customers?limit={limit}",
            auth=(sk, ""), timeout=15
        )
        data = r.json()

        if r.status_code == 200:
            customers = data.get("data", [])
            if not customers:
                await message.edit_text("ℹ️ No customers found.")
                return

            text = f"👥 **Last {len(customers)} Customers:**\n\n"
            for cust in customers:
                cust_id = cust.get("id", "N/A")[:20]
                email = cust.get("email", "N/A") or "N/A"
                name = cust.get("name", "N/A") or "N/A"
                created = datetime.fromtimestamp(cust.get("created", 0)).strftime("%d/%m/%Y")

                text += (
                    f"👤 `{cust_id}`\n"
                    f"├ **Name:** {name}\n"
                    f"├ **Email:** {email}\n"
                    f"├ **Created:** {created}\n\n"
                )

            await message.edit_text(text[:4000])
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Stripe error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ Customers error: `{str(e)[:100]}`")


# Command: .pl [amount] — Create Payment Link
@app.on_message(filters.me & filters.command("pl", prefixes="."))
async def pl_cmd(client, message: Message):
    try:
        import requests as _req

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        args = message.text.split(None, 1)
        try:
            amount = float(args[1].strip()) if len(args) > 1 else 1.0
        except:
            amount = 1.0
        amount_cents = int(amount * 100)

        await message.edit_text(f"⚙️ Creating ${amount:.2f} Payment Link...")

        # Step 1: Create Price
        r_price = _req.post(
            "https://api.stripe.com/v1/prices",
            auth=(sk, ""),
            data={
                "product_data[name]": f"Payment ${amount:.2f}",
                "unit_amount": str(amount_cents),
                "currency": "usd",
            },
            timeout=15
        )
        price_data = r_price.json()
        if r_price.status_code != 200:
            err = price_data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Price error: `{err}`")
            return

        price_id = price_data.get("id", "")

        # Step 2: Create Payment Link
        r_link = _req.post(
            "https://api.stripe.com/v1/payment_links",
            auth=(sk, ""),
            data={
                "line_items[0][price]": price_id,
                "line_items[0][quantity]": "1",
            },
            timeout=15
        )
        link_data = r_link.json()

        if r_link.status_code == 200:
            link_url = link_data.get("url", "N/A")
            link_id = link_data.get("id", "N/A")
            await message.edit_text(
                f"✅ **Payment Link Created!**\n\n"
                f"💰 **Amount:** `${amount:.2f} USD`\n"
                f"🔗 **Link:** `{link_url}`\n"
                f"🆔 **ID:** `{link_id}`",
                disable_web_page_preview=True
            )
        else:
            err = link_data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Link error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ PL error: `{str(e)[:100]}`")


# Command: .refund [payment_intent_id] — Refund a payment
@app.on_message(filters.me & filters.command("refund", prefixes="."))
async def refund_cmd(client, message: Message):
    try:
        import requests as _req
        import re

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        pi_id = None

        # Check for argument
        args = message.text.split(None, 1)
        if len(args) > 1:
            pi_id = args[1].strip()
        elif message.reply_to_message and message.reply_to_message.text:
            # Extract pi_xxx from replied message
            match = re.search(r'(pi_[A-Za-z0-9]+)', message.reply_to_message.text)
            if match:
                pi_id = match.group(1)

        if not pi_id:
            await message.edit_text("⚠️ **Usage:** `.refund pi_xxxxx` or reply to a message containing pi_xxx")
            return

        await message.edit_text(f"⚙️ Refunding `{pi_id}`...")

        r = _req.post(
            "https://api.stripe.com/v1/refunds",
            auth=(sk, ""),
            data={"payment_intent": pi_id},
            timeout=15
        )
        data = r.json()

        if r.status_code == 200:
            ref_id = data.get("id", "N/A")
            amount = data.get("amount", 0) / 100
            cur = data.get("currency", "usd").upper()
            status = data.get("status", "N/A")
            await message.edit_text(
                f"✅ **Refund Successful!**\n\n"
                f"🔙 **Refund ID:** `{ref_id}`\n"
                f"💰 **Amount:** `{amount:.2f} {cur}`\n"
                f"📋 **Status:** `{status}`\n"
                f"🎯 **PI:** `{pi_id}`"
            )
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Refund error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ Refund error: `{str(e)[:100]}`")


# Command: .coupon [percent] — Create discount coupon
@app.on_message(filters.me & filters.command("coupon", prefixes="."))
async def coupon_cmd(client, message: Message):
    try:
        import requests as _req

        sk = _sk_store.get("global")
        if not sk:
            await message.edit_text("⚠️ Set SK first: `.setsk sk_live_xxxxx`")
            return

        args = message.text.split(None, 1)
        try:
            percent = int(args[1].strip()) if len(args) > 1 else 10
        except:
            percent = 10
        percent = min(max(percent, 1), 100)

        await message.edit_text(f"⚙️ Creating {percent}% coupon...")

        r = _req.post(
            "https://api.stripe.com/v1/coupons",
            auth=(sk, ""),
            data={
                "percent_off": str(percent),
                "duration": "once",
            },
            timeout=15
        )
        data = r.json()

        if r.status_code == 200:
            coupon_id = data.get("id", "N/A")
            pct = data.get("percent_off", percent)
            dur = data.get("duration", "once")
            await message.edit_text(
                f"✅ **Coupon Created!**\n\n"
                f"🏷️ **Code:** `{coupon_id}`\n"
                f"💯 **Discount:** `{pct}%`\n"
                f"⏱ **Duration:** `{dur}`"
            )
        else:
            err = data.get("error", {}).get("message", "Unknown error")
            await message.edit_text(f"❌ Coupon error: `{err}`")

    except Exception as e:
        await message.edit_text(f"❌ Coupon error: `{str(e)[:100]}`")




if __name__ == "__main__":
    print("Starting userbot...")
    app.run()
