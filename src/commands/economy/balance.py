import discord
from discord.ext import commands
import json
import os

DATA_FILE = "./src/data/economy.json"

def load_data():
    """Carrega os dados do banco de dados JSON."""
    print("🔄 Carregando dados do arquivo JSON...")
    if not os.path.exists(DATA_FILE):
        print("⚠️ Arquivo JSON não encontrado. Criando um novo...")
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f, indent=4)
        return {"users": {}}
    with open(DATA_FILE, "r") as f:
        print("✅ Dados carregados com sucesso.")
        return json.load(f)

def save_data(data):
    """Salva os dados no banco de dados JSON."""
    print("💾 Salvando dados no arquivo JSON...")
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print("✅ Dados salvos com sucesso.")

class EconomyBalance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ Cog EconomyBalance inicializado.")

    def get_user_data(self, user_id):
        """Obtém os dados de um usuário ou cria um novo registro."""
        print(f"🔍 Obtendo dados do usuário {user_id}...")
        data = load_data()
        if str(user_id) not in data["users"]:
            print(f"⚠️ Usuário {user_id} não encontrado. Criando registro...")
            data["users"][str(user_id)] = {
                "carteira": 0,
                "banco": 0,
                "nivel": 1,
                "exp": 0,
                "emprego": "Desempregado",
                "itens": {},
                "casado_com": None,
                "ultimo_trabalho": None
            }
            save_data(data)
        else:
            print(f"✅ Dados do usuário {user_id} encontrados.")
        return data["users"][str(user_id)]

    def update_user_data(self, user_id, key, value):
        """Atualiza os dados de um usuário."""
        print(f"✏️ Atualizando dados do usuário {user_id}: {key} = {value}")
        data = load_data()
        data["users"][str(user_id)][key] = value
        save_data(data)
        print(f"✅ Dados do usuário {user_id} atualizados com sucesso.")

    @commands.command(name="saldo")
    async def saldo(self, ctx):
        """Exibe o saldo do usuário."""
        print(f"📊 Comando 'saldo' executado por {ctx.author.name} ({ctx.author.id})")
        user_data = self.get_user_data(ctx.author.id)
        carteira = user_data["carteira"]
        banco = user_data["banco"]

        embed = discord.Embed(
            title=f"💰 Saldo de {ctx.author.name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="🪙 Carteira", value=f"R$ {carteira}", inline=True)
        embed.add_field(name="🏦 Banco", value=f"R$ {banco}", inline=True)
        embed.set_footer(text="Use os comandos de economia para gerenciar seu dinheiro!")
        await ctx.send(embed=embed)
        print(f"✅ Saldo exibido para {ctx.author.name}.")

    @commands.command(name="depositar")
    async def depositar(self, ctx, quantia: str):
        """Deposita dinheiro no banco. Use 'all' para depositar tudo."""
        print(f"🏦 Comando 'depositar' executado por {ctx.author.name} ({ctx.author.id}) com quantia: {quantia}")
        user_data = self.get_user_data(ctx.author.id)

        if quantia.lower() in ["all", "tudo"]:
            quantia = user_data["carteira"]
        else:
            try:
                quantia = int(quantia)
            except ValueError:
                await ctx.send("❌ Por favor, insira um número válido ou use 'all' para depositar tudo.")
                return

        if quantia <= 0:
            print("❌ Quantia inválida para depósito.")
            await ctx.send("❌ Você não pode depositar uma quantia negativa ou zero.")
            return

        if user_data["carteira"] < quantia:
            print("❌ Saldo insuficiente na carteira para depósito.")
            await ctx.send("❌ Você não tem dinheiro suficiente na carteira para depositar.")
            return

        user_data["carteira"] -= quantia
        user_data["banco"] += quantia
        self.update_user_data(ctx.author.id, "carteira", user_data["carteira"])
        self.update_user_data(ctx.author.id, "banco", user_data["banco"])
        await ctx.send(f"🏦 {ctx.author.mention}, você depositou R$ {quantia} no banco!")
        print(f"✅ Depósito de R$ {quantia} realizado por {ctx.author.name}.")

    @commands.command(name="sacar")
    async def sacar(self, ctx, quantia: str):
        """Saca dinheiro do banco. Use 'all' para sacar tudo."""
        print(f"💸 Comando 'sacar' executado por {ctx.author.name} ({ctx.author.id}) com quantia: {quantia}")
        user_data = self.get_user_data(ctx.author.id)

        if quantia.lower() in ["all", "tudo"]:
            quantia = user_data["banco"]
        else:
            try:
                quantia = int(quantia)
            except ValueError:
                await ctx.send("❌ Por favor, insira um número válido ou use 'all' para sacar tudo.")
                return

        if quantia <= 0:
            print("❌ Quantia inválida para saque.")
            await ctx.send("❌ Você não pode sacar uma quantia negativa ou zero.")
            return

        if user_data["banco"] < quantia:
            print("❌ Saldo insuficiente no banco para saque.")
            await ctx.send("❌ Você não tem dinheiro suficiente no banco para sacar.")
            return

        user_data["banco"] -= quantia
        user_data["carteira"] += quantia
        self.update_user_data(ctx.author.id, "banco", user_data["banco"])
        self.update_user_data(ctx.author.id, "carteira", user_data["carteira"])
        await ctx.send(f"💸 {ctx.author.mention}, você sacou R$ {quantia} do banco!")
        print(f"✅ Saque de R$ {quantia} realizado por {ctx.author.name}.")

# Função obrigatória para carregar o cog
async def setup(bot):
    print("🔄 Carregando cog EconomyBalance...")
    await bot.add_cog(EconomyBalance(bot))
    print("✅ Cog EconomyBalance carregado com sucesso.")