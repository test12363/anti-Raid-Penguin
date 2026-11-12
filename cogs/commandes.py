import discord
from discord import app_commands
from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lockdown", description="Locks all text channels on the server (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def lockdown(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        default_role = interaction.guild.default_role
        count = 0

        for channel in interaction.guild.text_channels:
            overwrite = channel.overwrites_for(default_role)
            if overwrite.send_messages is not False:
                overwrite.send_messages = False
                try:
                    await channel.set_permissions(default_role, overwrite=overwrite, reason=f"Lockdown initiated by {interaction.user}")
                    count += 1
                except discord.Forbidden:
                    pass

        await interaction.followup.send(f"🔒 **Server locked** ({count} channels locked).", ephemeral=True)
        await interaction.channel.send("🚨 **ALERT:** The server has been temporarily locked by an administrator.")

    @app_commands.command(name="unlock", description="Unlocks all text channels on the server (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        default_role = interaction.guild.default_role
        count = 0

        for channel in interaction.guild.text_channels:
            overwrite = channel.overwrites_for(default_role)
            if overwrite.send_messages is False:
                overwrite.send_messages = None
                try:
                    await channel.set_permissions(default_role, overwrite=overwrite, reason=f"Unlock initiated by {interaction.user}")
                    count += 1
                except discord.Forbidden:
                    pass

        await interaction.followup.send(f"🔓 **Server unlocked** ({count} channels reopened).", ephemeral=True)
        await interaction.channel.send("✅ **ALERT OVER:** All text channels are now open again.")

    @lockdown.error
    @unlock.error
    async def admin_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Only members with **Administrator** permission can use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
