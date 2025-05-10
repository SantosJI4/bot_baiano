import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

class Pedido(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pedidos = []  # Lista para armazenar pedidos (pode ser substituída por um banco de dados)
        self.suporte_channel_id = None  # ID do canal de suporte (configurável)
        self.verificar_pedidos.start()  # Inicia a tarefa de verificação de pedidos

    @commands.command(name="set_suporte_channel")
    @commands.has_permissions(administrator=True)
    async def set_suporte_channel(self, ctx, channel: discord.TextChannel):
        """Define o canal de suporte para notificações."""
        self.suporte_channel_id = channel.id
        await ctx.send(f"✅ Canal de suporte definido para {channel.mention}.")

    @commands.command(name="pedido")
    async def pedido(self, ctx, id_jogador: str, produto: str):
        """Registra um pedido e notifica a equipe de suporte."""
        if not self.suporte_channel_id:
            await ctx.send("❌ O canal de suporte não foi configurado. Use `!set_suporte_channel` para configurá-lo.")
            return

        # Registra o pedido
        pedido = {
            "cliente": ctx.author.id,
            "id_jogador": id_jogador,
            "produto": produto,
            "status": "pendente",
            "criado_em": datetime.utcnow(),
            "prazo": datetime.utcnow() + timedelta(hours=24)
        }
        self.pedidos.append(pedido)

        # Notifica a equipe de suporte
        suporte_channel = self.bot.get_channel(self.suporte_channel_id)
        if suporte_channel:
            embed = discord.Embed(
                title="📦 Novo Pedido",
                description=f"Um novo pedido foi registrado!",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Cliente", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="ID do Jogador", value=id_jogador, inline=True)
            embed.add_field(name="Produto", value=produto, inline=True)
            embed.add_field(name="Prazo", value="24 horas", inline=True)
            embed.set_footer(text="Equipe de Suporte")
            await suporte_channel.send(embed=embed)

        await ctx.send("✅ Pedido registrado com sucesso! A equipe de suporte foi notificada.")

    @commands.command(name="concluir")
    @commands.has_permissions(administrator=True)
    async def concluir(self, ctx, numero: int):
        """Marca um pedido como concluído."""
        if numero <= 0 or numero > len(self.pedidos):
            await ctx.send("❌ Número do pedido inválido.")
            return

        pedido = self.pedidos[numero - 1]
        if pedido["status"] == "concluído":
            await ctx.send("❌ Este pedido já foi concluído.")
            return

        pedido["status"] = "concluído"
        await ctx.send(f"✅ Pedido #{numero} marcado como concluído.")

    @tasks.loop(minutes=10)
    async def verificar_pedidos(self):
        """Verifica os pedidos pendentes e envia lembretes se o prazo estiver próximo de expirar."""
        agora = datetime.utcnow()
        for i, pedido in enumerate(self.pedidos, start=1):
            if pedido["status"] == "pendente" and pedido["prazo"] - agora <= timedelta(hours=1):
                suporte_channel = self.bot.get_channel(self.suporte_channel_id)
                if suporte_channel:
                    embed = discord.Embed(
                        title="⏰ Lembrete de Pedido",
                        description=f"O prazo para o pedido #{i} está próximo de expirar!",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Cliente", value=f"<@{pedido['cliente']}>", inline=True)
                    embed.add_field(name="ID do Jogador", value=pedido["id_jogador"], inline=True)
                    embed.add_field(name="Produto", value=pedido["produto"], inline=True)
                    embed.add_field(name="Prazo", value=pedido["prazo"].strftime("%Y-%m-%d %H:%M:%S UTC"), inline=True)
                    embed.set_footer(text="Equipe de Suporte")
                    await suporte_channel.send(embed=embed)

    @verificar_pedidos.before_loop
    async def before_verificar_pedidos(self):
        """Aguarda o bot estar pronto antes de iniciar a tarefa."""
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Pedido(bot))