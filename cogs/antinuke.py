import discord
from discord.ext import commands
from collections import defaultdict, deque
import time
import config

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.nuke_history = defaultdict(deque)
        self.ban_history = defaultdict(deque)
        self.webhook_history = defaultdict(deque)

    async def strip_all_roles(self, guild, user_id, reason):
        member = guild.get_member(user_id)
        if member:
            roles_to_keep = [r for r in member.roles if r.is_default() or r.managed]
            try:
                await member.edit(roles=roles_to_keep, reason=reason)
                print(f"[PUNISHMENT] Stripped all roles from {member}: {reason}")
            except discord.Forbidden:
                print(f"[ERROR] Bot role too low to strip roles from {member}.")

    async def check_deletion(self, guild, action_type):
        async for entry in guild.audit_logs(limit=1, action=action_type):
            user = entry.user
            if not user or user.bot or user.id == guild.owner_id:
                return

            now = time.time()
            actions = self.nuke_history[(guild.id, user.id)]
            actions.append(now)

            while actions and now - actions[0] > config.NUKE_WINDOW:
                actions.popleft()

            if len(actions) > config.NUKE_LIMIT:
                actions.clear()
                await self.strip_all_roles(guild, user.id, "Anti-Nuke: Mass deletion of channels or roles.")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.check_deletion(channel.guild, discord.AuditLogAction.channel_delete)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.check_deletion(role.guild, discord.AuditLogAction.role_delete)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        guild = after.guild
        dangerous = (
            (not before.permissions.administrator and after.permissions.administrator) or
            (not before.permissions.ban_members and after.permissions.ban_members) or
            (not before.permissions.kick_members and after.permissions.kick_members) or
            (not before.permissions.manage_guild and after.permissions.manage_guild) or
            (not before.permissions.manage_roles and after.permissions.manage_roles)
        )
        if dangerous:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
                if entry.target.id != after.id:
                    continue
                executor = entry.user
                if not executor or executor.bot or executor.id == guild.owner_id:
                    return
                try:
                    await after.edit(permissions=before.permissions, reason="Anti-Admin: Unauthorized dangerous permission blocked.")
                except discord.Forbidden:
                    pass
                await self.strip_all_roles(guild, executor.id, "Anti-Admin: Attempted to grant Administrator/Staff permissions.")

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        guild = channel.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_create):
            executor = entry.user
            if not executor or executor.bot or executor.id == guild.owner_id:
                return

            now = time.time()
            webhooks = self.webhook_history[(guild.id, executor.id)]
            webhooks.append(now)

            while webhooks and now - webhooks[0] > config.WEBHOOK_WINDOW:
                webhooks.popleft()

            if len(webhooks) > config.WEBHOOK_LIMIT:
                try:
                    for wh in await channel.webhooks():
                        if wh.id == entry.target.id:
                            await wh.delete(reason="Anti-Webhook: Exceeded 1 webhook per 3 hours limit.")
                except discord.Forbidden:
                    pass
                await self.strip_all_roles(guild, executor.id, "Anti-Webhook: Created more than 1 webhook within 3 hours.")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id != user.id:
                continue
            executor = entry.user
            if not executor or executor.bot or executor.id == guild.owner_id:
                return

            now = time.time()
            bans = self.ban_history[(guild.id, executor.id)]
            bans.append(now)

            while bans and now - bans[0] > config.BAN_WINDOW:
                bans.popleft()

            if len(bans) > config.BAN_LIMIT:
                bans.clear()
                await self.strip_all_roles(guild, executor.id, "Anti-Mass Ban: Exceeded 5 bans within 24 hours.")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
