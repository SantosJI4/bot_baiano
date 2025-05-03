import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import random  # Para gerar EXP aleatório

DATA_FILE = "./src/data/economy.json"

def load_data():
    """Carrega os dados do banco de dados JSON."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}, "profissoes": {}}, f, indent=4)
        return {"users": {}, "profissoes": {}}
    
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # Garante que o campo "profissoes" exista
    if "profissoes" not in data:
        data["profissoes"] = {}
        save_data(data)

    return data
def save_data(data):
    """Salva os dados no banco de dados JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class WorkSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                "ultimo_trabalho": None
            }
            save_data(data)
        return data["users"][str(user_id)]

    def update_user_data(self, user_id, key, value):
        """Atualiza os dados de um usuário."""
        data = load_data()
        data["users"][str(user_id)][key] = value
        save_data(data)

    def promover_usuario(self, user_id, user_data):
        """Promove o usuário automaticamente ao atingir o nível necessário."""
        data = load_data()
        nivel_atual = user_data["nivel"]
        emprego_atual = user_data["emprego"]

        for cargo, requisitos in data["profissoes"].items():
            if requisitos["nivel_minimo"] <= nivel_atual and cargo != emprego_atual:
                user_data["emprego"] = cargo
                self.update_user_data(user_id, "emprego", cargo)
                return cargo  # Retorna o novo cargo
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ganha EXP ao interagir no chat."""
        if message.author.bot:
            return  # Ignora mensagens de bots

        user_id = message.author.id
        user_data = self.get_user_data(user_id)

        # Gera EXP aleatório entre 5 e 10 (mais difícil)
        exp_ganho = random.randint(5, 10)
        user_data["exp"] += exp_ganho

        # Verifica se o usuário subiu de nível
        nivel_atual = user_data["nivel"]
        exp_para_proximo_nivel = 150 + (nivel_atual - 1) * 75  # Aumenta a dificuldade

        if user_data["exp"] >= exp_para_proximo_nivel:
            user_data["nivel"] += 1
            user_data["exp"] -= exp_para_proximo_nivel
            self.update_user_data(user_id, "nivel", user_data["nivel"])
            self.update_user_data(user_id, "exp", user_data["exp"])

            # Promove o usuário automaticamente
            novo_cargo = self.promover_usuario(user_id, user_data)
            if novo_cargo:
                await message.channel.send(
                    f"🎉 Parabéns, {message.author.mention}! Você subiu para o nível {user_data['nivel']} e foi promovido para **{novo_cargo}**!"
                )
            else:
                await message.channel.send(
                    f"🎉 Parabéns, {message.author.mention}! Você subiu para o nível {user_data['nivel']}!"
                )

        # Atualiza os dados do usuário
        self.update_user_data(user_id, "exp", user_data["exp"])

    @commands.command(name="trabalhar")
    async def trabalhar(self, ctx):
        """Permite que o usuário trabalhe e receba um salário."""
        user_id = ctx.author.id
        user_data = self.get_user_data(user_id)
        data = load_data()

        emprego = user_data["emprego"]
        if emprego == "Desempregado":
            await ctx.send("❌ Você está desempregado! Suba de nível para desbloquear empregos.")
            return

        profissao = data["profissoes"].get(emprego)
        if not profissao:
            await ctx.send("❌ Ocorreu um erro ao encontrar sua profissão. Contate um administrador.")
            return

        agora = datetime.now()
        ultimo_trabalho = user_data["ultimo_trabalho"]

        if ultimo_trabalho:
            diferenca = agora - datetime.fromisoformat(ultimo_trabalho)
            if diferenca < timedelta(hours=8):
                tempo_restante = timedelta(hours=8) - diferenca
                horas, resto = divmod(tempo_restante.seconds, 3600)
                minutos, _ = divmod(resto, 60)
                await ctx.send(
                    f"❌ {ctx.author.mention}, você já trabalhou recentemente! Tente novamente em {horas} horas e {minutos} minutos."
                )
                return

        # Calcula o salário e adiciona ao saldo do usuário
        salario = profissao["salario"]
        user_data["carteira"] += salario
        user_data["ultimo_trabalho"] = agora.isoformat()
        self.update_user_data(user_id, "carteira", user_data["carteira"])
        self.update_user_data(user_id, "ultimo_trabalho", user_data["ultimo_trabalho"])

        await ctx.send(f"💼 {ctx.author.mention}, você trabalhou como **{emprego}** e ganhou R$ {salario}!")

    @commands.command(name="nivel")
    async def nivel(self, ctx):
        """Exibe o nível e a experiência do usuário."""
        user_id = ctx.author.id
        user_data = self.get_user_data(user_id)

        nivel = user_data["nivel"]
        exp = user_data["exp"]
        exp_para_proximo_nivel = 150 + (nivel - 1) * 75  # Aumenta a dificuldade

        embed = discord.Embed(
            title=f"📊 Status de {ctx.author.name}",
            description=f"**Nível:** {nivel}\n**EXP:** {exp}/{exp_para_proximo_nivel}\n**Emprego:** {user_data['emprego']}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(WorkSystem(bot))