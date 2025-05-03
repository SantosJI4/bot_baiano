import discord
import random
import asyncio
from discord.ext import commands, tasks

class Loteria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_lottery = None  # Dados do evento de loteria atual
        self.participants = {}  # Armazena os participantes e seus números únicos
        self.lottery_task = self.generate_random_lottery.start()  # Tarefa para criar eventos aleatórios

    def cog_unload(self):
        self.lottery_task.cancel()

    @commands.command(name="criar_loteria")
    @commands.has_permissions(administrator=True)
    async def criar_loteria(self, ctx, nome: str, premio: int, canal: discord.TextChannel, duracao: int):
        """Comando para o administrador criar um evento de loteria."""
        if self.current_lottery:
            await ctx.send("❌ Já existe uma loteria em andamento!")
            return

        self.current_lottery = {
            "nome": nome,
            "premio": premio,
            "canal": canal,
            "duracao": duracao,
            "fim": discord.utils.utcnow().timestamp() + duracao * 60
        }
        self.participants = {}

        await canal.send(
            f"🎟️ **Loteria Criada!**\n"
            f"**Nome:** {nome}\n"
            f"**Prêmio:** R$ {premio}\n"
            f"**Duração:** {duracao} minutos\n"
            f"Digite `/entrar_loteria` para participar!"
        )

        # Finaliza a loteria após o tempo especificado
        await asyncio.sleep(duracao * 60)
        await self.finalizar_loteria()

    @commands.command(name="entrar_loteria")
    async def entrar_loteria(self, ctx):
        """Permite que o usuário entre na loteria."""
        if not self.current_lottery:
            await ctx.send("❌ Não há nenhuma loteria em andamento no momento.")
            return

        if ctx.author.id in self.participants:
            await ctx.send("❌ Você já está participando desta loteria!")
            return

        # Gera um número único para o participante
        numero = random.randint(1, 1000)
        while numero in self.participants.values():
            numero = random.randint(1, 1000)

        self.participants[ctx.author.id] = numero
        await ctx.send(f"✅ Você entrou na loteria **{self.current_lottery['nome']}** com o número **{numero}**!")

    async def finalizar_loteria(self):
        """Finaliza a loteria e anuncia o vencedor."""
        if not self.current_lottery:
            return

        canal = self.current_lottery["canal"]
        if not self.participants:
            await canal.send("❌ A loteria foi encerrada, mas ninguém participou.")
        else:
            vencedor_id = random.choice(list(self.participants.keys()))
            vencedor_numero = self.participants[vencedor_id]
            vencedor = self.bot.get_user(vencedor_id)

            await canal.send(
                f"🎉 **Loteria Encerrada!**\n"
                f"**Nome:** {self.current_lottery['nome']}\n"
                f"**Prêmio:** R$ {self.current_lottery['premio']}\n"
                f"**Vencedor:** {vencedor.mention} com o número **{vencedor_numero}**!"
            )

        # Reseta os dados da loteria
        self.current_lottery = None
        self.participants = {}

    @tasks.loop(hours=1)
    async def generate_random_lottery(self):
        """Gera eventos de loteria aleatórios."""
        await self.bot.wait_until_ready()

        if self.current_lottery:
            return  # Não cria uma nova loteria se já houver uma em andamento

        canal = random.choice(self.bot.get_all_channels())
        if not isinstance(canal, discord.TextChannel):
            return

        nome = f"Loteria Aleatória #{random.randint(1, 100)}"
        premio = random.randint(500, 5000)
        duracao = random.randint(5, 15)  # Duração entre 5 e 15 minutos

        self.current_lottery = {
            "nome": nome,
            "premio": premio,
            "canal": canal,
            "duracao": duracao,
            "fim": discord.utils.utcnow().timestamp() + duracao * 60
        }
        self.participants = {}

        await canal.send(
            f"🎟️ **Loteria Aleatória!**\n"
            f"**Nome:** {nome}\n"
            f"**Prêmio:** R$ {premio}\n"
            f"**Duração:** {duracao} minutos\n"
            f"Digite `/entrar_loteria` para participar!"
        )

        # Finaliza a loteria após o tempo especificado
        await asyncio.sleep(duracao * 60)
        await self.finalizar_loteria()

async def setup(bot):
    await bot.add_cog(Loteria(bot))