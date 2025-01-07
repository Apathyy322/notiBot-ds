import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
tk = os.getenv("token2")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

rms = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def pd(ds):
    h, m = 0, 0
    if 'h' in ds:
        p = ds.split('h')
        h = int(p[0])
        if len(p) > 1 and 'm' in p[1]:
            m = int(p[1].replace('m', ''))
    elif 'm' in ds:
        m = int(ds.replace('m', ''))
    return timedelta(hours=h, minutes=m)

@bot.command()
async def dm(ctx):
    if ctx.author == bot.user:
        return

    if ctx.message.content.lower().startswith("!dm"):
        pt = ctx.message.content.split(' ', 2)
        if len(pt) < 3:
            await ctx.message.channel.send("Usage: !dm <usrid> <msg>")
            return
        usrid = int(pt[1])
        msg = pt[2]
        usr = await bot.fetch_user(usrid)
        await usr.send(msg)
        await ctx.message.channel.send(f"Successfully sent message to {usr.name}!")

@bot.command()
async def remind(ctx):
    try:
        await ctx.send("⏰ Please specify the time (e.g., `2h15m` for 2 hours 15 minutes):")
        tm = await bot.wait_for(
            "message",
            timeout=60,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        wt = pd(tm.content)

        await ctx.send("📝 What should I remind you about?")
        tx = await bot.wait_for(
            "message",
            timeout=60,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        rt = tx.content

        tt = datetime.now() + wt
        rid = f"{ctx.author.id}-{len(rms)}"

        rms[rid] = {
            "usr": ctx.author,
            "txt": rt,
            "time": tt
        }

        await ctx.send(f"✅ Reminder scheduled for {tt.strftime('%Y-%m-%d %H:%M:%S')}! \n\nReminder ID: `{rid}`")
        asyncio.create_task(sr(ctx.author, rt, wt, rid))
    except asyncio.TimeoutError:
        await ctx.send("⏳ You took too long to respond. Please try again.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

async def sr(usr, rt, wt, rid):
    try:
        await asyncio.sleep(wt.total_seconds())
        if rid in rms:
            await usr.send(f"🔔 Reminder: {rt}")
            del rms[rid]
    except discord.Forbidden:
        print(f"Failed to DM {usr}.")
    except Exception as e:
        print(f"Error with reminder {rid}: {e}")

@bot.command()
async def listrems(ctx):
    ur = [r for r in rms.items() if r[1]["usr"] == ctx.author]
    if not ur:
        await ctx.send("📋 You have no active reminders.")
        return
    res = "📋 **Your Active Reminders:**\n"
    for rid, rm in ur:
        res += f"- **ID**: {rid}, **Time**: {rm['time'].strftime('%Y-%m-%d %H:%M:%S')}, **Text**: {rm['txt']}\n"
    await ctx.send(res)

@bot.command()
async def cancel(ctx, rid: str):
    try:
        if rid in rms:
            if rms[rid]["usr"] == ctx.author:
                del rms[rid]
                await ctx.send(f"❌ Reminder `{rid}` has been canceled.")
            else:
                await ctx.send("⚠️ You do not own this reminder.")
        else:
            await ctx.send(f"⚠️ No reminder found with ID `{rid}`.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred while canceling the reminder: {e}")

bot.run(tk)
