import discord
from discord.ext import commands
from datetime import datetime

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ajuda", aliases=["comandos"])
    async def ajuda(self, ctx):
        """Exibe todos os comandos disponíveis, organizados por categorias."""
        embed = discord.Embed(
            title="📖 Ajuda - Lista de Comandos",
            description="Aqui estão todos os comandos disponíveis no bot, organizados por categorias:",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()  # Adiciona o horário atual
        )

        # Itera por todos os cogs e comandos
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            if commands_list:
                # Adiciona os comandos de cada categoria ao embed
                commands_description = "\n".join([f"`{cmd.name}` - {cmd.help}" for cmd in commands_list if not cmd.hidden])
                embed.add_field(name=f"**{cog_name}**", value=commands_description, inline=False)

        # Adiciona informações adicionais
        embed.set_footer(
            text=f"Solicitado por {ctx.author.name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))