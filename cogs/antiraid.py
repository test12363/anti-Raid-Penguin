import discord
from discord.ext import commands
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
import time
import config

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_history = defaultdict(deque)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        now_dt = datetime.now(timezone.utc)
        if (now_dt - member.created_at) < timedelta(days=config.MIN_ACCOUNT_AGE_DAYS):
            try:
                await member.kick(reason=f"Anti-Raid: Account younger than {config.MIN_ACCOUNT_AGE_DAYS} days.")
                return
            except discord.Forbidden:
                pass

        now = time.time()
        joins = self.join_history[member.guild.id]
        joins.append(now)

        while joins and now - joins[0] > config.JOIN_WINDOW:
            joins.popleft()

        if len(joins) >= config.MAX_JOINS:
            try:
                await member.kick(reason="Anti-Raid: Mass join detected (10+ members in 10s).")
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
