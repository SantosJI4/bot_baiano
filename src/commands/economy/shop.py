import discord
from discord.ext import commands
import json
import os

DATA_FILE = "./src/data/economy.json"

def load_data():
    """Carrega os dados do banco de dados JSON."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}, "profissoes": {}, "itens": {}}, f, indent=4)
        return {"users": {}, "profissoes": {}, "itens": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Salva os dados no banco de dados JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class ShopSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categories = {
            "Aneis": [
                {"nome": "Alumínio", "preco": 100},
                {"nome": "Bronze", "preco": 250},
                {"nome": "Prata", "preco": 500},
                {"nome": "Ouro", "preco": 1000},
                {"nome": "Esmeralda", "preco": 2500},
                {"nome": "Diamante", "preco": 5000},
            ],
            "Armas": [
                {"nome": "Faca", "preco": 300},
                {"nome": "Espingarda", "preco": 1000},
                {"nome": "Pistola", "preco": 1500},
                {"nome": "Calibre 12", "preco": 3000},
                {"nome": "Submetralhadora", "preco": 5000},
                {"nome": "Bazuca", "preco": 10000},
                {"nome": "Dinamite", "preco": 2000},
            ],
        }

    def get_user_data(self, user_id):
        """Obtém os dados de um usuário ou cria um novo registro."""
        data = load_data()
        if str(user_id) not in data["users"]:
            data["users"][str(user_id)] = {
                "carteira": 0,
                "banco": 0,
                "nivel": 1,
                "exp": 0,
                "emprego": "Desempregado",
                "ultimo_trabalho": None,
                "itens": {}
            }
            save_data(data)
        return data["users"][str(user_id)]

    def update_user_data(self, user_id, key, value):
        """Atualiza os dados de um usuário."""
        data = load_data()
        data["users"][str(user_id)][key] = value
        save_data(data)

    @commands.command(name="loja")
    async def loja(self, ctx):
        """Exibe as categorias da loja."""
        embed = discord.Embed(
            title="🛒 Loja",
            description="Escolha uma categoria para ver os itens disponíveis ou feche a loja:",
            color=discord.Color.blue()
        )
        embed.add_field(name="💍 Aneis", value="Itens de luxo para exibir sua riqueza.", inline=False)
        embed.add_field(name="🔫 Armas", value="Itens para defesa ou ataque.", inline=False)
        embed.set_footer(text="Reaja com o emoji correspondente para escolher uma categoria ou fechar a loja.")

        message = await ctx.send(embed=embed)
        await message.add_reaction("💍")  # Emoji para Aneis
        await message.add_reaction("🔫")  # Emoji para Armas
        await message.add_reaction("❌")  # Emoji para fechar a loja

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["💍", "🔫", "❌"]

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "💍":
                await self.mostrar_categoria(ctx, "Aneis")
            elif str(reaction.emoji) == "🔫":
                await self.mostrar_categoria(ctx, "Armas")
            elif str(reaction.emoji) == "❌":
                await message.edit(embed=discord.Embed(
                    title="🛒 Loja",
                    description="A loja foi fechada. Volte sempre!",
                    color=discord.Color.red()
                ))
        except discord.TimeoutError:
            await ctx.send("⏰ Tempo esgotado! Tente novamente.")

    async def mostrar_categoria(self, ctx, categoria):
        """Exibe os itens de uma categoria."""
        if categoria not in self.categories:
            await ctx.send("❌ Categoria inválida.")
            return

        embed = discord.Embed(
            title=f"🛒 Loja - {categoria}",
            description="Escolha um item para comprar:",
            color=discord.Color.green()
        )
        for i, item in enumerate(self.categories[categoria], start=1):
            embed.add_field(name=f"{i}. {item['nome']}", value=f"Preço: R$ {item['preco']}", inline=False)
        embed.set_footer(text="Digite o número do item para comprá-lo.")

        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.content.isdigit()

        try:
            message = await self.bot.wait_for("message", timeout=60.0, check=check)
            escolha = int(message.content) - 1
            if 0 <= escolha < len(self.categories[categoria]):
                item = self.categories[categoria][escolha]
                await self.comprar_item(ctx, item)
            else:
                await ctx.send("❌ Escolha inválida.")
        except discord.TimeoutError:
            await ctx.send("⏰ Tempo esgotado! Tente novamente.")

    async def comprar_item(self, ctx, item):
        """Permite que o usuário compre um item."""
        user_id = ctx.author.id
        user_data = self.get_user_data(user_id)

        if user_data["carteira"] < item["preco"]:
            await ctx.send(f"❌ Você não tem dinheiro suficiente para comprar **{item['nome']}**.")
            return

        # Deduz o valor da carteira e adiciona o item ao inventário
        user_data["carteira"] -= item["preco"]
        if item["nome"] in user_data["itens"]:
            user_data["itens"][item["nome"]] += 1
        else:
            user_data["itens"][item["nome"]] = 1

        self.update_user_data(user_id, "carteira", user_data["carteira"])
        self.update_user_data(user_id, "itens", user_data["itens"])

        await ctx.send(f"✅ Você comprou **{item['nome']}** por R$ {item['preco']}!")

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(ShopSystem(bot))