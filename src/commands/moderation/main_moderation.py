import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "./config.json"

class ModerationMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()

    def load_config(self):
        """Carrega as configurações do arquivo JSON."""
        if not os.path.exists(CONFIG_FILE):
            return {"welcome_channel": None, "event_channel": None, "prefix": "!"}
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_config(self):
        """Salva as configurações no arquivo JSON."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    @commands.group(name="config", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        """Comando principal para configurar o bot."""
        embed = discord.Embed(
            title="Configuração do Bot",
            description="Use os subcomandos abaixo para configurar o bot:",
            color=discord.Color.blue()
        )
        embed.add_field(name="`config welcome_channel <#canal>`", value="Define o canal de boas-vindas.", inline=False)
        embed.add_field(name="`config event_channel <#canal>`", value="Define o canal de eventos.", inline=False)
        embed.add_field(name="`config prefix <novo_prefixo>`", value="Altera o prefixo do bot.", inline=False)
        await ctx.send(embed=embed)

    @config.command(name="welcome_channel")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """Define o canal de boas-vindas."""
        self.config["welcome_channel"] = channel.id
        self.save_config()
        await ctx.send(f"✅ Canal de boas-vindas definido para {channel.mention}.")

    @config.command(name="event_channel")
    @commands.has_permissions(administrator=True)
    async def set_event_channel(self, ctx, channel: discord.TextChannel):
        """Define o canal de eventos."""
        self.config["event_channel"] = channel.id
        self.save_config()
        await ctx.send(f"✅ Canal de eventos definido para {channel.mention}.")

    @config.command(name="prefix")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        """Altera o prefixo do bot."""
        self.config["prefix"] = prefix
        self.save_config()
        await ctx.send(f"✅ Prefixo do bot alterado para `{prefix}`.")

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int):
        """Limpa uma quantidade específica de mensagens no canal."""
        if amount <= 0:
            await ctx.send("❌ O número de mensagens a ser excluído deve ser maior que 0.")
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"✅ {len(deleted)} mensagens foram excluídas.", delete_after=5)
        
async def setup(bot):
    await bot.add_cog(ModerationMain(bot))