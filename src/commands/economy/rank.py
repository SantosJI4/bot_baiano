import discord
from discord.ext import commands
import json
import os

DATA_FILE = "./src/data/economy.json"

def load_data():
    """Carrega os dados do banco de dados JSON."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f, indent=4)
        return {"users": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

class RankSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ranking")
    async def ranking(self, ctx):
        """Exibe o ranking dos usuários mais ricos."""
        data = load_data()
        ranking = sorted(data["users"].items(), key=lambda x: x[1]["carteira"] + x[1]["banco"], reverse=True)

        embed = discord.Embed(
            title="🏆 Ranking dos Mais Ricos",
            color=discord.Color.gold()
        )
        for i, (user_id, user_data) in enumerate(ranking[:10], start=1):
            usuario = await self.bot.fetch_user(int(user_id))
            total = user_data["carteira"] + user_data["banco"]
            embed.add_field(name=f"{i}º {usuario.name}", value=f"R$ {total}", inline=False)

        await ctx.send(embed=embed)

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(RankSystem(bot))