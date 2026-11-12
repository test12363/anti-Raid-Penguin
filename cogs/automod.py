import discord
from discord.ext import commands, tasks
from collections import defaultdict, deque
from datetime import timedelta
import time
import re
import config

URL_REGEX = re.compile(r"(https?://\S+|www\.\S+|discord\.gg/\S+|discord\.com/invite/\S+)", re.IGNORECASE)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_history = defaultdict(deque)
        self.image_history = defaultdict(deque)
        self.last_messages = defaultdict(lambda: deque(maxlen=3))
        
        self.everyone_strikes = defaultdict(int)
        self.mention_strikes = defaultdict(int)
        self.global_warnings = defaultdict(int)
        
        self.reset_warnings_task.start()

    def cog_unload(self):
        self.reset_warnings_task.cancel()

    @tasks.loop(hours=24)
    async def reset_warnings_task(self):
        self.everyone_strikes.clear()
        self.mention_strikes.clear()
        self.global_warnings.clear()
        print("[SYSTEM] All warning counters have been reset (24h cycle).")

    async def add_warning(self, guild, channel, member, reason):
        key = (guild.id, member.id)
        self.global_warnings[key] += 1
        warns = self.global_warnings[key]

        if warns >= config.MAX_WARNINGS:
            try:
                await member.ban(reason=f"Auto-Blacklist: Reached {config.MAX_WARNINGS} warnings ({reason}).")
                await channel.send(f"🔨 **{member}** has been **blacklisted (banned)** after reaching **{config.MAX_WARNINGS} warnings**.", delete_after=8)
            except discord.Forbidden:
                pass
        else:
            await channel.send(f"⚠️ **{member.mention}**, {reason} (**Warning {warns}/{config.MAX_WARNINGS}** before blacklist).", delete_after=6)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if message.author.guild_permissions.administrator:
            return

        key = (message.guild.id, message.author.id)
        now = time.time()

        # 1. Anti-@everyone / @here (1: Delete -> 2: Kick -> 3: Blacklist)
        if message.mention_everyone or "@everyone" in message.content or "@here" in message.content:
            try:
                await message.delete()
            except discord.Forbidden:
                pass

            self.everyone_strikes[key] += 1
            strike = self.everyone_strikes[key]
            try:
                if strike == 1:
                    await message.channel.send(f"⚠️ **{message.author.mention}**, `@everyone` and `@here` are forbidden. Next time: **Kick**.", delete_after=8)
                elif strike == 2:
                    await message.author.kick(reason="Anti-Mention: 2nd attempt of @everyone/@here.")
                    await message.channel.send(f"👢 **{message.author}** has been kicked for repeating `@everyone`/`@here`.", delete_after=8)
                else:
                    await message.author.ban(reason="Blacklist: 3rd attempt of @everyone/@here.")
                    await message.channel.send(f"🔨 **{message.author}** has been **blacklisted (banned)** for abusing `@everyone`/`@here`.", delete_after=8)
            except discord.Forbidden:
                pass
            return

        # 2. Max 2 mentions (@) per message (1: Delete -> 2: Kick -> 3: Ban)
        if (len(message.mentions) + len(message.role_mentions)) > 2:
            try:
                await message.delete()
            except discord.Forbidden:
                pass

            self.mention_strikes[key] += 1
            strike = self.mention_strikes[key]
            try:
                if strike == 1:
                    await message.channel.send(f"⚠️ **{message.author.mention}**, maximum **2 mentions** allowed per message. Next time: **Kick**.", delete_after=8)
                elif strike == 2:
                    await message.author.kick(reason="Anti-Mention: 2nd violation of max 2 mentions.")
                    await message.channel.send(f"👢 **{message.author}** has been kicked for mention spam.", delete_after=8)
                else:
                    await message.author.ban(reason="Anti-Mention: 3rd violation of max 2 mentions.")
                    await message.channel.send(f"🔨 **{message.author}** has been **banned** for repeated mention spam.", delete_after=8)
            except discord.Forbidden:
                pass
            return

        # 3. Anti-Links (Delete + 30m Mute)
        if URL_REGEX.search(message.content):
            try:
                await message.delete()
                await message.author.timeout(timedelta(minutes=config.LINK_MUTE_MINUTES), reason="Anti-Link: Posted an unauthorized link.")
                await message.channel.send(f"🔗 **{message.author.mention}**, links are not allowed here (Muted for **30 minutes**).", delete_after=8)
            except discord.Forbidden:
                pass
            return

        # 4. Anti-Images / Attachments (Max 1 file every 3 seconds)
        if message.attachments:
            imgs = self.image_history[key]
            while imgs and now - imgs[0] > config.IMAGE_WINDOW:
                imgs.popleft()

            if len(message.attachments) > 1 or len(imgs) >= 1:
                try:
                    await message.delete()
                    await self.add_warning(message.guild, message.channel, message.author, "maximum 1 image/file every 3 seconds")
                except discord.Forbidden:
                    pass
                return
            else:
                imgs.append(now)

        # 5. Anti-Copy/Paste (3 identical messages in a row)
        clean_text = message.content.strip().lower()
        if len(clean_text) > 0:
            txt_hist = self.last_messages[key]
            txt_hist.append(clean_text)
            if len(txt_hist) == 3 and txt_hist[0] == txt_hist[1] == txt_hist[2]:
                txt_hist.clear()
                try:
                    await message.delete()
                    await self.add_warning(message.guild, message.channel, message.author, "repeating the exact same message")
                except discord.Forbidden:
                    pass
                return

        # 6. Anti-Text Spam (Max 4 messages in 5s -> 5th triggers 2h Mute)
        msgs = self.message_history[key]
        msgs.append(now)
        while msgs and now - msgs[0] > config.MESSAGE_WINDOW:
            msgs.popleft()

        if len(msgs) > config.MAX_MESSAGES_ALLOWED:
            msgs.clear()
            try:
                await message.author.timeout(timedelta(hours=config.SPAM_MUTE_HOURS), reason="Anti-Spam: 5 messages within 5 seconds.")
                await message.channel.purge(limit=10, check=lambda m: m.author == message.author)
                await message.channel.send(f"🛡️ **{message.author.mention}** has been muted for **2 hours** for spamming.", delete_after=8)
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
