import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "./config.json"

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()

    def load_config(self):
        """Carrega as configurações do arquivo JSON."""
        if not os.path.exists(CONFIG_FILE):
            return {"welcome_settings": {}}
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_config(self):
        """Salva as configurações no arquivo JSON."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    @commands.command(name="welcome_test")
    @commands.has_permissions(administrator=True)
    async def welcome_test(self, ctx):
        """Testa a mensagem de boas-vindas."""
        settings = self.config.get("welcome_settings", {})
        channel = ctx.channel
        text = settings.get("text", "🎉 **Bem-vindo ao nosso servidor!**\n\nEstamos muito felizes em ter você aqui! Aproveite sua estadia. 😊")
        banner = settings.get("banner", "https://wallpapercave.com/wp/wp6081414.jpg")  # Banner padrão
        show_server_icon = settings.get("show_server_icon", True)

        embed = discord.Embed(
            title="🎊 Bem-vindo! 🎊",
            description=text,
            color=discord.Color.green()
        )
        embed.set_footer(text="Estamos felizes em ter você aqui! 🎉")
        if banner:
            embed.set_image(url=banner)
        if show_server_icon and ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Envia a mensagem de boas-vindas quando um novo membro entra no servidor."""
        settings = self.config.get("welcome_settings", {})
        channel_id = settings.get("channel")
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return

        text = settings.get("text", "🎉 **Bem-vindo ao nosso servidor!**\n\nEstamos muito felizes em ter você aqui! Aproveite sua estadia. 😊")
        banner = settings.get("banner", "https://wallpapercave.com/wp/wp6081414.jpg")  # Banner padrão
        show_server_icon = settings.get("show_server_icon", True)

        embed = discord.Embed(
            title="🎊 Bem-vindo! 🎊",
            description=f"{text}\n\n👋 {member.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Estamos felizes em ter você aqui! 🎉")
        if banner:
            embed.set_image(url=banner)
        if show_server_icon and member.guild.icon:
            embed.set_thumbnail(url=member.guild.icon.url)

        await channel.send(embed=embed)

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(Welcome(bot))