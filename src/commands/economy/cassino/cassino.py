import discord
import random
import asyncio
import json
import os
from discord.ext import commands

DATA_FILE = "./src/data/economy.json"

def load_data():
    """Carrega os dados do arquivo JSON."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f, indent=4)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Salva os dados no arquivo JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Cassino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # Rastreia jogos ativos para evitar conflitos

    def update_user_balance(self, user_id, key, amount):
        """Atualiza o saldo do usuário."""
        data = load_data()
        if str(user_id) not in data["users"]:
            data["users"][str(user_id)] = {"carteira": 0, "banco": 0}
        data["users"][str(user_id)][key] += amount
        save_data(data)

    def get_user_balance(self, user_id):
        """Obtém o saldo do usuário."""
        data = load_data()
        if str(user_id) not in data["users"]:
            return 0
        return data["users"][str(user_id)]["carteira"]

    @commands.command(name="minas")
    async def jogo_das_minas(self, ctx):
        """Jogo das Minas com opção de sacar."""
        if ctx.channel.id in self.active_games:
            await ctx.send("❌ Já existe um jogo ativo neste canal. Aguarde o término.")
            return

        self.active_games[ctx.channel.id] = True
        await ctx.send("💣 **Jogo das Minas Iniciado!** Escolha um número no quadro ou digite `sacar` para encerrar o jogo e coletar seus ganhos.")
        board = [f"🔲" for _ in range(9)]
        mine_index = random.randint(0, 8)
        multiplier = 1
        total_prize = 0

        embed = discord.Embed(
            title="💣 Jogo das Minas",
            description="Escolha um número no quadro abaixo ou digite `sacar` para encerrar o jogo.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Quadro", value="\n".join([" | ".join(board[i:i+3]) for i in range(0, 9, 3)]))
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(f"{ctx.author.mention}, quanto você quer apostar?")
        try:
            msg_bet = await self.bot.wait_for("message", check=check, timeout=30)
            bet = int(msg_bet.content)
            if bet <= 0:
                await ctx.send("❌ Aposta inválida!")
                del self.active_games[ctx.channel.id]
                return
        except (ValueError, asyncio.TimeoutError):
            await ctx.send("❌ Você não respondeu a tempo ou enviou um valor inválido.")
            del self.active_games[ctx.channel.id]
            return

        while True:
            await ctx.send(f"{ctx.author.mention}, escolha um número no quadro (1-9) ou digite `sacar` para encerrar o jogo.")
            try:
                msg_choice = await self.bot.wait_for("message", check=check, timeout=30)
                choice = msg_choice.content.lower()

                if choice == "sacar":
                    self.update_user_balance(ctx.author.id, "carteira", total_prize)
                    await ctx.send(f"💰 {ctx.author.mention}, você sacou R$ {total_prize}! Parabéns!")
                    break

                chosen_index = int(choice) - 1
                if chosen_index < 0 or chosen_index >= len(board):
                    await ctx.send("❌ Escolha inválida! Escolha um número entre 1 e 9.")
                    continue

                if board[chosen_index] != "🔲":
                    await ctx.send("❌ Este número já foi escolhido! Tente novamente.")
                    continue

                if chosen_index == mine_index:
                    board[mine_index] = "💥"
                    embed.description = "💥 Você encontrou a mina e perdeu tudo!"
                    embed.color = discord.Color.red()
                    embed.clear_fields()
                    embed.add_field(name="Quadro Final", value="\n".join([" | ".join(board[i:i+3]) for i in range(0, 9, 3)]))
                    await msg.edit(embed=embed)
                    await ctx.send(f"💣 {ctx.author.mention}, você perdeu R$ {bet}.")
                    break

                # Atualiza o quadro e os ganhos
                board[chosen_index] = "✅"
                multiplier += 0.5
                total_prize = int(bet * multiplier)
                embed.description = f"🎉 Você escapou da mina! Seus ganhos atuais: R$ {total_prize}."
                embed.color = discord.Color.green()
                embed.clear_fields()
                embed.add_field(name="Quadro Atualizado", value="\n".join([" | ".join(board[i:i+3]) for i in range(0, 9, 3)]))
                await msg.edit(embed=embed)

            except (ValueError, asyncio.TimeoutError):
                await ctx.send("❌ Você não respondeu a tempo.")
                break

        del self.active_games[ctx.channel.id]
        await ctx.send(f"💣 Deseja jogar novamente? Use o comando `-minas`!")

async def setup(bot):
    await bot.add_cog(Cassino(bot))