# 🤖 Imeshu Userbot

A powerful Telegram userbot with 105+ commands built with [Srigram](https://github.com/sriganesh/srigram).

## ✨ Features
- 105+ commands (fun, utility, admin, Stripe, Rebtel checker, and more)
- Easy deployment on Heroku, VPS, or Docker

## 🚀 Deploy on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

1. Click the button above
2. Fill in your `SESSION_STRING`, `API_ID`, `API_HASH`
3. Deploy!

## 🐳 Deploy with Docker

```bash
git clone https://github.com/DAXXTEAM/Userbot
cd Userbot
cp .env.example .env
# Edit .env with your credentials
docker-compose up -d
```

## 🖥️ Deploy on VPS

```bash
git clone https://github.com/DAXXTEAM/Userbot
cd Userbot
pip install -r requirements.txt
export SESSION_STRING="your_session_string"
export API_ID="your_api_id"
export API_HASH="your_api_hash"
python3 main.py
```

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `SESSION_STRING` | Your Telegram session string |
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash |

## 📝 Generate Session String

```python
pip install srigram
python3 -c "from srigram import Client; import asyncio
async def gen():
    async with Client('gen', api_id=YOUR_API_ID, api_hash='YOUR_API_HASH') as app:
        print(await app.export_session_string())
asyncio.run(gen())"
```

## 📜 License
MIT
