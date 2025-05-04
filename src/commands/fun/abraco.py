import discord
from discord.ext import commands
import random

class Abraco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="abraco")
    async def abraco(self, ctx, membro: discord.Member):
        """Dá um abraço em outro membro com um GIF aleatório."""
        if membro == ctx.author:
            await ctx.send("❌ Você não pode abraçar a si mesmo!")
            return

        # Lista de GIFs de abraço
        gifs = [
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
            "https://media.giphy.com/media/lrr9rHuoJOE0w/giphy.gif",
            "https://media.giphy.com/media/143v0Z4767T15e/giphy.gif",
            "https://media.giphy.com/media/3ZnBrkqoaI2hq/giphy.gif",
            "https://media.giphy.com/media/49mdjsMrH7oze/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="🤗 Abraço!",
            description=f"{ctx.author.mention} deu um abraço em {membro.mention}!",
            color=discord.Color.green()
        )
        embed.set_image(url=gif)

        # Botão para retribuir o abraço
        view = AbracoView(ctx.author, membro)
        await ctx.send(embed=embed, view=view)


class AbracoView(discord.ui.View):
    def __init__(self, autor, alvo):
        super().__init__(timeout=60)  # O botão ficará ativo por 60 segundos
        self.autor = autor
        self.alvo = alvo

    @discord.ui.button(label="Retribuir", style=discord.ButtonStyle.green, emoji="🔄")
    async def retribuir(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retribui o abraço."""
        if interaction.user != self.alvo:
            await interaction.response.send_message("❌ Apenas quem recebeu o abraço pode retribuir!", ephemeral=True)
            return

        # Lista de GIFs de abraço
        gifs = [
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
            "https://media.giphy.com/media/lrr9rHuoJOE0w/giphy.gif",
            "https://media.giphy.com/media/143v0Z4767T15e/giphy.gif",
            "https://media.giphy.com/media/3ZnBrkqoaI2hq/giphy.gif",
            "https://media.giphy.com/media/49mdjsMrH7oze/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="🤗 Retribuição!",
            description=f"{self.alvo.mention} retribuiu o abraço em {self.autor.mention}!",
            color=discord.Color.green()
        )
        embed.set_image(url=gif)

        await interaction.response.send_message(embed=embed)
        self.stop()  # Desativa os botões após a interação


async def setup(bot):
    await bot.add_cog(Abraco(bot))