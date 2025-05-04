import discord
from discord.ext import commands
import random

class Tapa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tapa")
    async def tapa(self, ctx, membro: discord.Member):
        """Dá um tapa em outro membro com um GIF aleatório."""
        if membro == ctx.author:
            await ctx.send("❌ Você não pode dar um tapa em si mesmo!")
            return

        # Lista de GIFs de tapa
        gifs = [
            "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
            "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
            "https://media.giphy.com/media/l3YSimA8CV1k41b1u/giphy.gif",
            "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif",
            "https://media.giphy.com/media/mEtSQlxqBtWWA/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="💥 Tapa!",
            description=f"{ctx.author.mention} deu um tapa em {membro.mention}!",
            color=discord.Color.red()
        )
        embed.set_image(url=gif)

        # Botão para retribuir o tapa
        view = TapaView(ctx.author, membro)
        await ctx.send(embed=embed, view=view)


class TapaView(discord.ui.View):
    def __init__(self, autor, alvo):
        super().__init__(timeout=60)  # O botão ficará ativo por 60 segundos
        self.autor = autor
        self.alvo = alvo

    @discord.ui.button(label="Retribuir", style=discord.ButtonStyle.red, emoji="🔄")
    async def retribuir(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retribui o tapa."""
        if interaction.user != self.alvo:
            await interaction.response.send_message("❌ Apenas quem recebeu o tapa pode retribuir!", ephemeral=True)
            return

        # Lista de GIFs de tapa
        gifs = [
            "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
            "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
            "https://media.giphy.com/media/l3YSimA8CV1k41b1u/giphy.gif",
            "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif",
            "https://media.giphy.com/media/mEtSQlxqBtWWA/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="💥 Retribuição!",
            description=f"{self.alvo.mention} retribuiu o tapa em {self.autor.mention}!",
            color=discord.Color.red()
        )
        embed.set_image(url=gif)

        await interaction.response.send_message(embed=embed)
        self.stop()  # Desativa os botões após a interação


async def setup(bot):
    await bot.add_cog(Tapa(bot))