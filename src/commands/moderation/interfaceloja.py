import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime, timedelta

class Loja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.produtos = {
            "1️⃣": {"nome": "Diamantes Free Fire", "quantidades": {100: 5, 500: 20, 1000: 35}},
            "2️⃣": {"nome": "Robux", "quantidades": {400: 10, 800: 18, 1700: 35}},
            "3️⃣": {"nome": "Fifa Coins", "quantidades": {10000: 15, 50000: 50, 100000: 90}},
            "4️⃣": {"nome": "PES Coins", "quantidades": {100: 5, 500: 20, 1000: 35}},
        }
        self.tickets = {}  # Armazena os tickets criados

    @commands.command(name="loja")
    async def loja(self, ctx):
        """Exibe a página inicial da loja."""
        embed = discord.Embed(
            title="🛒 Bem-vindo à Loja Virtual!",
            description="Escolha um dos produtos abaixo para continuar:\n\n"
                        "1️⃣ - Diamantes Free Fire\n"
                        "2️⃣ - Robux\n"
                        "3️⃣ - Fifa Coins\n"
                        "4️⃣ - PES Coins",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Reaja com o emoji correspondente para escolher um produto.")
        mensagem = await ctx.send(embed=embed)

        # Adiciona reações para seleção
        for emoji in self.produtos.keys():
            await mensagem.add_reaction(emoji)

        # Aguarda a reação do usuário
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in self.produtos

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            await self.mostrar_produto(ctx, reaction.emoji)
        except discord.TimeoutError:
            await ctx.send("⏰ Tempo esgotado. Use `!loja` para abrir a loja novamente.")

    async def mostrar_produto(self, ctx, emoji):
        """Mostra as opções de quantidades e preços para o produto selecionado."""
        produto = self.produtos[emoji]
        nome = produto["nome"]
        quantidades = produto["quantidades"]

        embed = discord.Embed(
            title=f"🛒 {nome}",
            description="Escolha uma das opções abaixo para continuar:",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        for i, (quantidade, preco) in enumerate(quantidades.items(), start=1):
            embed.add_field(name=f"{i}️⃣ {quantidade} unidades", value=f"💵 R$ {preco}", inline=False)
        embed.set_footer(text="Reaja com o número correspondente para escolher.")

        mensagem = await ctx.send(embed=embed)

        # Adiciona reações para seleção
        for i in range(1, len(quantidades) + 1):
            await mensagem.add_reaction(f"{i}️⃣")

        # Aguarda a reação do usuário
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [f"{i}️⃣" for i in range(1, len(quantidades) + 1)]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            indice = int(reaction.emoji[0]) - 1
            quantidade = list(quantidades.keys())[indice]
            preco = list(quantidades.values())[indice]
            await self.confirmar_pedido(ctx, nome, quantidade, preco)
        except discord.TimeoutError:
            await ctx.send("⏰ Tempo esgotado. Use `!loja` para abrir a loja novamente.")

    async def confirmar_pedido(self, ctx, produto, quantidade, preco):
        """Confirma o pedido e cria um ticket para suporte."""
        embed = discord.Embed(
            title="✅ Pedido Confirmado!",
            description=f"Produto: **{produto}**\nQuantidade: **{quantidade}**\nPreço: **R$ {preco}**",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Aguarde, um ticket foi criado para finalizar o pedido.")
        await ctx.send(embed=embed)

        # Cria um canal de ticket
        guild = ctx.guild
        categoria = get(guild.categories, name="Tickets") or await guild.create_category("Tickets")
        ticket_channel = await guild.create_text_channel(f"ticket-{ctx.author.name}", category=categoria)
        await ticket_channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
        suporte_role = get(guild.roles, name="Suporte")
        if suporte_role:
            await ticket_channel.set_permissions(suporte_role, read_messages=True, send_messages=True)

        # Envia mensagem no ticket
        embed = discord.Embed(
            title="🎫 Novo Ticket",
            description=f"Cliente: {ctx.author.mention}\nProduto: **{produto}**\nQuantidade: **{quantidade}**\nPreço: **R$ {preco}**",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Equipe de Suporte")
        await ticket_channel.send(embed=embed)

        # Adiciona o cliente ao cargo "Cliente"
        cliente_role = get(guild.roles, name="Cliente")
        if not cliente_role:
            cliente_role = await guild.create_role(name="Cliente", color=discord.Color.blue())
        await ctx.author.add_roles(cliente_role)

async def setup(bot):
    await bot.add_cog(Loja(bot))