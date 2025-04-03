# A teljes Vikibot funkciókat visszahozó és kibővítő verzió
import discord
from discord.ext import commands, tasks
import openai
import os
import sqlite3
import random
import aiohttp
import feedparser
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_AUTH_TOKEN = os.getenv("TWITCH_AUTH_TOKEN")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Itt folytatódik a kódod az RPG funkciókkal együtt...
# === TOVÁBBI PARANCSOK BEILLESZTÉSE ===

@bot.command()
async def vikihelp(ctx):
    help_text = (
        "🆘 **VikiBot Parancsok**:\n"
        "!kaland – Napi RPG eseményed, XP-vel és rangokkal\n"
        "!profil – Megmutatja az XP-det és a rangodat\n"
        "!ranglista – Top 10 játékos XP szerint\n"
        "!kocka k10 / k100 / 2k10 – Kockadobás szerepjátékhoz\n"
        "!vikirajzol [utasítás] – Viki rajzol neked képet ✨\n"
        "!chat [üzenet] – Beszélgetés Vikivel, AI módra 🤖\n"
    )
    await ctx.send(help_text)

@bot.command()
async def profil(ctx):
    c.execute("SELECT xp, rank FROM users WHERE id=?", (ctx.author.id,))
    user = c.fetchone()
    if user:
        xp, rank = user
        await ctx.send(f"📊 **Profilod** – XP: {xp}, Rang: {rank}")
    else:
        await ctx.send("Nincs még profilod. Indíts egy kalandot a `!kaland` paranccsal!")

@bot.command()
async def ranglista(ctx):
    c.execute("SELECT name, xp FROM users ORDER BY xp DESC LIMIT 10")
    top = c.fetchall()
    msg = "🏆 **Top 10 játékos**:\n"
    for i, (name, xp) in enumerate(top, 1):
        msg += f"{i}. {name} – {xp} XP\n"
    await ctx.send(msg)

@bot.command()
async def kocka(ctx, dob: str):
    try:
        if "k" in dob:
            db, meret = dob.lower().split("k")
            db = int(db) if db else 1
            meret = int(meret)
            dobasok = [random.randint(1, meret) for _ in range(db)]
            await ctx.send(f"🎲 Dobásaid: {', '.join(map(str, dobasok))} (összesen: {sum(dobasok)})")
        else:
            await ctx.send("Használat: !kocka k10 vagy 2k6 stb.")
    except:
        await ctx.send("Hibás formátum! Példa: !kocka 3k10")

import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@bot.command()
async def chat(ctx, *, uzenet):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Te egy barátságos, humoros, vörös hajú nő vagy Viktória, azaz Viki néven. Előszeretettel adsz csípkelődő váalszokat és viccesen beszólsz mindenkinek, de emellett kedves vagy"},
                {"role": "user", "content": uzenet}
            ]
        )
        await ctx.send(response.choices[0].message.content)
    except Exception as e:
        print(f"[HIBA a !chat parancsnál]: {e}")
        await ctx.send("🥺 Hoppá, VikiBot beszédképessége átmenetileg elveszett!")

@bot.command()
async def vikirajzol(ctx, *, prompt):
    try:
        print(f"Kép generálás indítva a következő prompttal: {prompt}")  # Debug üzenet
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        print(f"Generált kép URL: {image_url}")  # Debug üzenet
        await ctx.send(f"🎨 Kép készül: `{prompt}` – Viki küldi hamarosan...")
        await ctx.send(image_url)
    except openai.Error as e:  # Frissített hiba kezelés
        print(f"[HIBA az OpenAI API hívásnál]: {e}")  # Tovább részletes hibaüzenet
        await ctx.send(f"🥺 Bocs, Kis-Haver, valami elromlott a kép generálásnál... {e}")
    except Exception as e:
        print(f"[Általános HIBA]: {e}")  # Egyéb hiba
        await ctx.send(f"🥺 Bocs, Kis-Haver, valami elromlott a kép generálásnál...")

# A meglévő RPG funkciók megmaradnak

# === AJÁNLÓK ===
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

jatek_ajanlok = [
    "🎮 **Inscryption** – Ha szereted a pakliépítős pszichotripet, ez a te játszótered!",
    "🕹️ **Hades** – Roguelike pokoljárás, ahol a halál csak bemelegítés.",
    "💣 **Enter the Gungeon** – Lövöldözés, görgetés, görgetve lövöldözés!",
    "🐉 **Dragon's Dogma** – Ha a sárkányt nem hozod, hát elvisz!",
    "🧠 **The Talos Principle** – Agydaráló puzzle + filozófia koktélban.",
    "🚗 **My Summer Car** – Ha szerelnél, káromkodnál és finn lennél egyszerre.",
    "🌌 **No Man's Sky** – Fedezd fel az univerzumot... vagy bukj bele a menükbe.",
    "🛠️ **Factorio** – Addiktívabb, mint a kávé. És az is gépekkel készül.",
    "🏰 **Kingdom Two Crowns** – Oldschool pixelgrafika, modern frusztrációval.",
    "🐺 **The Witcher 3** – Geralt szexibb, mint te valaha leszel. Fogadd el.",
    "🎯 **Hitman 3** – Bújj bele egy csendes bérgyilkos cipőjébe... aztán dobj banánhéjat.",
    "🧟 **Project Zomboid** – Zombi apokalipszis, ahogy az valójában kinézne: bénázva.",
    "🪓 **Valheim** – Vikingek, sárkányok, faaprítás és valami troll is biztos.",
    "🔪 **Katana ZERO** – Neon, pixelvér és időlassítás. A tökéletes randi estére.",
    "🧙 **Divinity: Original Sin 2** – Ha barátokkal akarsz összeveszni egy varázslat miatt.",
    "🔍 **Return of the Obra Dinn** – Detektívkedés, ahol a pixelek hazudnak.",
    "🎢 **RollerCoaster Tycoon Classic** – Építs, csődölj, csukd be a vécéket bosszúból!",
    "🦁 **Zoo Tycoon** – Adj az oroszlánnak pizzát. Csak viccelek. Ne tedd.",
    "🚴 **Lonely Mountains: Downhill** – Egy hegy, egy bringa, sok zuhanás.",
    "🌃 **Cyberpunk 2077** – Ha már kijavították... egész élvezhető. Néha.",
    "🧩 **Baba is You** – Baba is confused. Baba is win. Baba is zseni.",
    "💀 **Dark Souls III** – Git gud vagy sírj a sarokban. Nincs középút.",
    "🎮 **Slay the Spire** – Kártyás mészárlás, ahol a torony csak a kezdet.",
    "💣 **Broforce** – Robbants, sikíts, ismételd! A szabadság nevében.",
    "🎻 **Arma 3** – Ultra-realisztikus katonai szimuláció. Meghalsz a fűben. Sokszor.",
    "🐓 **Untitled Goose Game** – Te vagy a gonosz. És liba is. Gonosz liba.",
    "🚀 **Kerbal Space Program** – Tudomány, humor és robbanás. Leginkább robbanás.",
    "🐸 **Frog Detective** – Ha szeretsz nyomozni... békaként. Mert miért ne?",
    "📦 **Unpacking** – Egy játék a kipakolásról. Mégis szíven üt. (!!!)",
    "🛠️ **Teardown** – Minden rombolható. MINDEN. Most már tetszik, mi?",
    "🚔 **This Is the Police** – Dönts erkölcsösen... vagy ne. Te vagy a rend.",
    "🪐 **Outer Wilds** – Időhurkos űrutazás. Lenyűgöző és kicsit ijesztő.",
    "🎮 **Risk of Rain 2** – Szép színes káosz. Egyre nehezebb. Egyre függőbb.",
    "🦍 **APE OUT** – Te vagy a gorilla. A dobok üvöltenek. Vér és művészet egyben.",
    "🧱 **Minecraft** – Ha épp nem életed menedzselsz, bányássz és építs helyette.",
    "🎨 **Okami HD** – Festett világ, farkasisten, japán mese. És te vagy a ceruza!",
    "📜 **Banner Saga** – Döntések, harc, rajzolt eposz. Ne öljetek meg, srácok...",
    "🕵️ **L.A. Noire** – Tedd fel a kérdést újra. A gyanúsított izzad. Ez jó jel.",
    "🚢 **Sea of Thieves** – Igyál rumot, dalolj, és süllyedj el stílusosan!"
]

film_ajanlok = [
    "🎬 **Whiplash** – Ez nem jazz. Ez háború dobverőkkel.",
    "📺 **Peaky Blinders** – Ha a sapkád nem vág, nem vagy Shelby.",
    "🔪 **John Wick** – Kutya + bosszú + golyózápor. Klasszikus Viki-módi.",
    "🚬 **Sin City** – Fekete-fehér noir, vérrel és monológokkal nyakon öntve.",
    "🌌 **Interstellar** – Űr, idő, sírás. És sok kukorica.",
    "🧠 **Inception** – Álmodd meg, majd álmodd újra. Viki szerint ez normális.",
    "🎭 **Fight Club** – Az első szabály: ne mondd el, de ajánljuk.",
    "🦇 **The Batman** – Sötét, komor, és még mindig nem alszik.",
    "🐉 **House of the Dragon** – Mert sárkányokból sosem elég.",
    "👑 **The Crown** – Politika, korona, intrika. És teával oldják.",
    "🦾 **Ex Machina** – Mesterséges intelligencia + para + tánc. Viki approved.",
    "📽️ **The Lighthouse** – Két férfi, egy világítótorony, és sok madár.",
    "🧛 **What We Do in the Shadows** – Vámpírok, de viccesek. Meglepően.",
    "🍕 **The Bear** – Nem medve, hanem szakács. Mégis vad.",
    "🔫 **Barry** – Bérgyilkos próbál színészkedni. Meglepően nehéz.",
    "🔮 **The OA** – Ha nem érted... akkor pont jól csinálod.",
    "🕹️ **Black Mirror: Bandersnatch** – Te döntesz, aztán megbánod.",
    "💀 **Breaking Bad** – A kémiatanár elgurította. És mi örülünk neki.",
    "🧟 **The Last of Us** – Zombi + dráma + Ellie. Már most klasszikus.",
    "🎢 **Dark** – Német időutazás, ahol még a nagymama is gyanús.",
    "🪞 **Twin Peaks** – Kávé, fánk, és megmagyarázhatatlan fura arcok.",
    "📺 **Better Call Saul** – Jog, bűn, humor – és egy ügyvéd, aki jobban tudja.",
    "🎬 **Dune** – Homok, politika, fűszer. És sandworm szörf!",
    "👁️ **Arrival** – Űrlények nyelvórája. Viki imádja a betűket.",
    "🚪 **The Others** – Klasszikus kísértetmese, amiben te is benne vagy.",
    "🧙 **Harry Potter** – Tudjuk, hogy úgyis újranézed minden télen.",
    "🦾 **Love, Death & Robots** – Sci-fi rövidfilmek... beteg, gyönyörű és zseni.",
    "🎠 **Euphoria** – Ha még nem borultál ki eléggé. Most megteheted.",
    "🎭 **The Sopranos** – Mafia + terápia. Dráma deluxe.",
    "🎡 **Stranger Things** – '80-as évek nosztalgia + szörnyek + Synthwave.",
    "🧟 **Zombieland** – Kézikönyv az apokalipszis túléléséhez – rágóval.",
    "🎬 **Inglourious Basterds** – Tarantino stílus, nyelvleckékkel és baseballütőkkel.",
    "📽️ **The Grand Budapest Hotel** – Minden szimmetrikus. És gusztusos.",
    "👽 **District 9** – Idegenek, szegregáció, és egy kis testmódosítás.",
    "🧠 **Severance** – Munka és magánélet szétválasztva. Nagyon szó szerint.",
    "🎩 **The Prestige** – Illúzió, versengés, és egy macska kétszer.",
    "🧪 **Chernobyl** – Dráma, hidegrázás és ukrán akcentus.",
    "🦸 **The Boys** – Szuperhősök... de nem úgy. Egyáltalán nem úgy.",
    "🎬 **Everything Everywhere All At Once** – Multiverzum, kungfu, és egy rakás őrület."
]

@tasks.loop(time=datetime.strptime("16:00", "%H:%M").time())
async def hetijatekajanlo():
    csatorna = bot.get_channel(int(os.getenv("GAME_CHANNEL_ID")))
    ajanlas = random.choice(jatek_ajanlok)
    await csatorna.send(f"@everyone 🔥 Heti játékajánló:\n{ajanlas}")

@tasks.loop(time=datetime.strptime("15:00", "%H:%M").time())
async def hetifilmajanlo():
    csatorna = bot.get_channel(int(os.getenv("MOVIE_CHANNEL_ID")))
    ajanlas = random.choice(film_ajanlok)
    await csatorna.send(f"@everyone 🍿 Heti filmajánló:\n{ajanlo}")

@bot.event
async def on_ready():
    scheduler.start()
    hetijatekajanlo.start()
    hetifilmajanlo.start()
    print(f"✅ Bejelentkezve mint: {bot.user}")

@bot.event
async def on_ready():
    scheduler.start()
    hetijatekajanlo.start()
    hetifilmajanlo.start()
    check_youtube.start()
    check_tiktok.start()
    check_twitch_live.start()
    print(f"✅ Bejelentkezve mint: {bot.user}")

# === YouTube RSS figyelés ===
@tasks.loop(minutes=5)
async def check_youtube():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(os.getenv("YOUTUBE_CHANNEL_ID")))
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCL3sW98H9R9Ks5dFNIFUtYg"
    feed = feedparser.parse(url)
    latest_entry = feed.entries[0]
    try:
        with open("last_video_id.txt", "r") as f:
            last_id = f.read().strip()
    except FileNotFoundError:
        last_id = ""
    if latest_entry.id != last_id:
        with open("last_video_id.txt", "w") as f:
            f.write(latest_entry.id)
        if channel:
            await channel.send(f"@everyone 📢 Új YouTube videó jelent\n meg: {latest_entry.title}\n{latest_entry.link}")


# === TikTok videó figyelés ===
@tasks.loop(minutes=5)
async def check_tiktok():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(os.getenv("TIKTOK_CHANNEL_ID")))
    url = "https://www.tiktok.com/@ddp44gaming"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                text = await resp.text()
                latest_url = text.split("https://www.tiktok.com/@ddp44gaming/video/")[1].split('"')[0]
                video_link = f"https://www.tiktok.com/@ddp44gaming/video/{latest_url}"
        try:
            with open("last_tiktok.txt", "r") as f:
                last_id = f.read().strip()
        except FileNotFoundError:
            last_id = ""
        if latest_url != last_id:
            with open("last_tiktok.txt", "w") as f:
                f.write(latest_url)
            await channel.send(f"@everyone 🎥 Új TikTok videó jelent meg: {video_link}")
    except Exception as e:
        print(f"[TikTok check error]: {e}")


# Hozzáadásra kerülnek: !chat, !vikihelp, !kocka, !vikirajzol, heti ajánlók, twitch/youtube figyelés

# === TWITCH ÉLŐ FIGYELÉS ===
@tasks.loop(minutes=2)
async def check_twitch_live():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(os.getenv("TWITCH_CHANNEL_ID")))
    streamer_login = os.getenv("TWITCH_STREAMER_LOGIN")
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_AUTH_TOKEN}"
    }
    url = f"https://api.twitch.tv/helix/streams?user_login={streamer_login}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data.get("data"):
                    if not hasattr(bot, "notified_twitch") or not bot.notified_twitch:
                        await channel.send(f"@everyone 🔴 **{streamer_login} élőben van Twitch-en!** Nézd most: https://twitch.tv/{streamer_login}")
                        bot.notified_twitch = True
                else:
                    bot.notified_twitch = False
    except Exception as e:
        print(f"[Twitch check error]: {e}")


# === MINI RPG JÁTÉK ===
conn = sqlite3.connect("vikibot.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, 
    name TEXT, 
    xp INTEGER, 
    rank TEXT, 
    kaland_count INTEGER, 
    last_kaland TEXT
)
""")

ranks = ["Rabszolga", "Paraszt", "Városlakó", "Lovag", "Hadúr", "Félisten", "Atyaúristen!"]

rpg_events = [
    "🥚 Egy rejtélyes aranytojást találtál – senki sem tudja, honnan jött. (+50 XP)",
    "🦄 Megpillantottál egy unikornist, és az megérintette a homlokod. Kapsz egy extra napot holnapra! (+0 XP, de misztikus előny)",
    "🌫️ Egy árnylény megérintette a lelked – a nap további részére elvesztettél minden kalandlehetőséget! (0 XP, nap vége)",
    "🔒 Egy elátkozott labirintus csapdájába estél – ma már nem szabadulsz! (0 XP, nap vége)",
    "🌪️ Megpróbáltál elcsábítani egy ork hercegnőt. Nem jött be... (-20 XP)",
    "🐔 Tyúklopáson kaptak a piacon! De legalább futottál egy jót. (+10 XP)",
    "🦴 Csontvázak közé tévedtél – de azt hitted, flashmob van. (-15 XP)",
    "🛡️ Részt vettél egy lovagi tornán... nézőként. (+5 XP)",
    "🧊 Befagyott a varázsgömböd – új jövendölés jövő héten! (0 XP)",
    "🪄 Egy mágikus pergamen további kalandot ad neked a mai napra! (+1 lehetőség)",
    "🕳️ Egy lidérc kiszívott belőled egy kis lelkesedést... (-1 lehetőség)",
    "🐉 Egy sárkány olyan hálás volt a simogatásért, hogy megajándékozott egy extra próbálkozással! (+1 lehetőség)",
    "🦴 Egy csapda aktiválódott – elvesztettél egy kalandlehetőséget! (-1 lehetőség)",
    "🧅 Megkóstoltad a Trollhagyma-leveset... rossz ötlet volt. (-10 XP)",
    "🦉 Egy bagoly súgott valamit – sajnos nem értetted. (0 XP)",
    "🪙 Találtál egy varázsérmét – beváltottad egy XP-re! (+20 XP)",
    "🐍 Megcsípett egy kobracsiga. Furcsa, de túl lehet élni. (-5 XP)",
    "🧚 Egy tündér megdicsérte a frizurád. Hát... legyen! (+5 XP)",
    "🪓 Váratlanul szétvágtad a napod: túl sok küldetés, kevés XP. (+2 XP)",
    "🏹 Egy íjászversenyen eltaláltad a nézőteret. Nem dicsőség, de XP jár. (+8 XP)",
    "🦴 Egy animált csontváz meghívott táncolni. Elfogadtad. (+6 XP)",
    "🥔 Megpróbáltál megjósolni egy krumpli sorsát. Haszontalan, de érdekes. (+1 XP)",
    "👻 Kísérteties hangokat hallottál... saját gyomrodból. (-2 XP)",
    "🧠 Egy bölcs idézett neked... de TikTokról. (0 XP)",
    "🔥 Felgyújtottad a saját sátrad. Legközelebb nem varázsolj álmomban. (-25 XP)",
    "⚗️ Véletlenül feltaláltál valamit. A nevedről nevezik el. (+15 XP)",
    "🕷️ Beleléptél egy mágikus pók hálójába – most minden ragad. (-10 XP)",
    "🌈 Egy szivárvány végén nem arany volt... hanem egy kobold szendvicse. (+3 XP)",
    "🎲 Fogadtál egy démonnal. Vesztettél. (-18 XP)",
    "🐇 Követtél egy nyulat egy lyukba. Nem volt ott más, csak egy másik nyúl. (-1 XP)",
    "🍄 Megkóstoltál egy gombát. Most minden színesebb. (+12 XP)",
    "🐢 Egy teknőssel versenyeztél. Kikaptál. (-5 XP)",
    "👑 Megálmodtad, hogy király vagy... aztán felébredtél. (0 XP)",
    "🐀 Egy patkánycsapdából mentettél ki egy rágcsálót. Most ő követ. (+4 XP)",
    "💤 Elaludtál egy mágikus tanácskozáson. Még pont nem vették észre. (0 XP)",
    "🕶️ Egy sötételf eladott neked napszemüveget. Most stílusos vagy. (+5 XP)",
    "🧼 Elcsúsztál egy varázsszappanon. Hasznos XP nem volt. (-3 XP)",
    "🎉 Rész vettél egy kobold bulin. Eléggé vad volt. (+7 XP)",
    "📚 Megtanultál egy új szót: Flabbergasted. (+1 XP)",
    "🪵 Egy fa beszélt hozzád... aztán ráültél. Most morcos. (-6 XP)",
    "🔔 Egy harang megszólalt – és hallottad benne a sorsod. (+10 XP)",
    "👃 Megszagoltál egy alkimista fiolát. Hiba volt. (-12 XP)",
    "🎁 Találtál egy ajándékot – benne egy jegyzet: 'XP jár érte!' (+9 XP)",
    "🦆 Egy beszélő kacsa megjósolta a jövőd. Még nem jött be. (0 XP)",
    "🎭 Egy bűvész trükkjét leleplezted. Most mindenki utál. (-8 XP)",
    "🧵 Elakadtál egy pókhálóban – de kiszabadultál! (+4 XP)",
    "🚪 Átléptél egy mágikus portált – és vissza is estél. (0 XP)",
    "🍰 Ettél egy varázstortát – most beszélsz sárkányul. (+13 XP)",
    "🌪️ Egy vihar sodort el... a szomszéd faluba. (-10 XP)",
    "🔮 Megláttad a jövőd – és az XP-vel teli volt! (+18 XP)",
    "🐸 Megcsókoltál egy békát... béka maradt. (-4 XP)",
    "📦 Egy dobozban XP-t találtál – megérte! (+20 XP)",
    "🧟 Egy zombi megpróbált megharapni... de csak udvarolt. (+6 XP)",
    "🧨 Ráléptél egy bűvös robbanó kacsára. Tanulságos. (-9 XP)"
]

@bot.command()
async def kaland(ctx):
    now = datetime.utcnow()
    c.execute("SELECT kaland_count, last_kaland, xp, rank FROM users WHERE id=?", (ctx.author.id,))
    data = c.fetchone()

    if data:
        kaland_count, last_kaland_str, xp, rank = data
        last_kaland = datetime.strptime(last_kaland_str, "%Y-%m-%d") if last_kaland_str else now - timedelta(days=1)

        if last_kaland.date() < now.date():
            kaland_count = 0

        if kaland_count >= 5:
            await ctx.send("🧊 Befagyott a kalandlehetőséged mára, Kis-Haver! Holnap újra próbálkozhatsz. ❄️")
            return
    else:
        xp = 0
        rank = ranks[0]
        kaland_count = 0
        last_kaland = now
        c.execute("INSERT INTO users (id, name, xp, rank, kaland_count, last_kaland) VALUES (?, ?, ?, ?, ?, ?)",
                  (ctx.author.id, ctx.author.name, xp, rank, kaland_count, last_kaland.strftime("%Y-%m-%d")))

    event = random.choice(rpg_events)
    xp_change = int(event.split("(")[1].split(" XP")[0].replace("+", "").replace("-", "-")) if "XP" in event else 0

    if "Befagyott a varázsgömböd" in event:
        kaland_count = 5
    elif "+1 lehetőség" in event:
        kaland_count = max(0, kaland_count - 1)
    elif "-1 lehetőség" in event:
        kaland_count = min(5, kaland_count + 1)
    elif "elvesztettél minden kalandlehetőséget" in event or "ma már nem szabadulsz" in event:
        kaland_count = 5
    else:
        xp += xp_change
        rank = ranks[min(xp // 100, len(ranks)-1)]
        kaland_count += 1

    c.execute("UPDATE users SET xp=?, rank=?, kaland_count=?, last_kaland=? WHERE id=?",
              (xp, rank, kaland_count, now.strftime("%Y-%m-%d"), ctx.author.id))
    conn.commit()
    await ctx.send(f"{event}\nJelenlegi XP-d: {xp}, Rangod: {rank}")
bot.run(DISCORD_BOT_TOKEN)

