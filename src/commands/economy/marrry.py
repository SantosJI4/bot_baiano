import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import os
import json
from datetime import datetime

DATA_FILE = "./src/data/economy.json"

def load_data():
    """Carrega os dados do banco de dados JSON."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f, indent=4)
        return {"users": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Salva os dados no banco de dados JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class MarriageSystem(commands.Cog):
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
                "itens": {},
                "casado_com": None,
                "ultimo_trabalho": None
            }
            save_data(data)
        return data["users"][str(user_id)]

    def update_user_data(self, user_id, key, value):
        """Atualiza os dados de um usuário."""
        data = load_data()
        data["users"][str(user_id)][key] = value
        save_data(data)

    @commands.command(name="casar")
    async def casar(self, ctx, member: discord.Member):
        """Permite que um usuário peça outro em casamento."""
        user_id = ctx.author.id
        target_id = member.id

        if user_id == target_id:
            await ctx.send("❌ Você não pode se casar consigo mesmo!")
            return

        user_data = self.get_user_data(user_id)
        target_data = self.get_user_data(target_id)

        # Verifica se o usuário já está casado
        if user_data["casado_com"] is not None:
            await ctx.send("❌ Você já está casado!")
            return

        if target_data["casado_com"] is not None:
            await ctx.send(f"❌ {member.mention} já está casado!")
            return

        # Verifica se o usuário tem pelo menos 2 anéis
        if user_data["itens"].get("Alumínio", 0) < 2:
            await ctx.send("❌ Você precisa de pelo menos 2 anéis no inventário para pedir alguém em casamento.")
            return

        # Envia o pedido de casamento
        embed = discord.Embed(
            title="💍 Pedido de Casamento",
            description=f"{ctx.author.mention} pediu {member.mention} em casamento! 💕\n\nReaja com ✅ para aceitar ou ❌ para recusar.",
            color=discord.Color.pink()
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == member and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "✅":
                # Atualiza os dados de casamento
                user_data["casado_com"] = target_id
                target_data["casado_com"] = user_id
                self.update_user_data(user_id, "casado_com", target_id)
                self.update_user_data(target_id, "casado_com", user_id)

                # Remove os anéis do inventário
                user_data["itens"]["Alumínio"] -= 2
                self.update_user_data(user_id, "itens", user_data["itens"])

                # Gera a imagem do casamento
                await self.gerar_imagem_casamento(ctx.author, member)

                await ctx.send(f"🎉 Parabéns, {ctx.author.mention} e {member.mention}! Vocês agora estão casados! 💕")
            else:
                await ctx.send(f"❌ {member.mention} recusou o pedido de casamento de {ctx.author.mention}.")
        except discord.TimeoutError:
            await ctx.send("⏰ O tempo para responder ao pedido de casamento acabou.")

    async def gerar_imagem_casamento(self, user1, user2):
        """Gera uma imagem personalizada para o casamento."""
        # Baixa os avatares dos usuários
        avatar1 = Image.open(await user1.avatar.url.read()).resize((150, 150))
        avatar2 = Image.open(await user2.avatar.url.read()).resize((150, 150))

        # Cria a imagem base
        base = Image.new("RGB", (500, 300), "white")
        draw = ImageDraw.Draw(base)

        # Adiciona os avatares
        base.paste(avatar1, (50, 75))
        base.paste(avatar2, (300, 75))

        # Adiciona um coração no meio
        heart = Image.open("./src/assets/heart.png").resize((100, 100))
        base.paste(heart, (200, 100), heart)

        # Adiciona texto
        font = ImageFont.truetype("./src/assets/font.ttf", 20)
        draw.text((50, 250), f"{user1.name} ❤️ {user2.name}", fill="black", font=font)
        draw.text((50, 270), f"Data: {datetime.now().strftime('%d/%m/%Y')}", fill="black", font=font)

        # Salva a imagem
        image_path = f"./src/assets/casamento_{user1.id}_{user2.id}.png"
        base.save(image_path)

        # Envia a imagem no canal
        await user1.send(file=discord.File(image_path))
        await user2.send(file=discord.File(image_path))

@commands.command(name="testar_casamento")
async def testar_casamento(self, ctx):
    """Comando de teste para verificar o sistema de casamento."""
    # Usuários fictícios para teste
    user1 = ctx.author
    user2 = ctx.guild.get_member(ctx.author.id)  # Simula o autor como o segundo usuário também

    # Simula os dados no banco de dados
    user1_data = self.get_user_data(user1.id)
    user2_data = self.get_user_data(user2.id)

    # Adiciona anéis ao inventário do usuário 1 para o teste
    user1_data["itens"]["Alumínio"] = 2
    self.update_user_data(user1.id, "itens", user1_data["itens"])

    # Simula o pedido de casamento
    await ctx.send(f"💍 Simulando pedido de casamento entre {user1.mention} e {user2.mention}...")
    user1_data["casado_com"] = user2.id
    user2_data["casado_com"] = user1.id
    self.update_user_data(user1.id, "casado_com", user2.id)
    self.update_user_data(user2.id, "casado_com", user1.id)

    # Gera a imagem de casamento
    await self.gerar_imagem_casamento(user1, user2)

    await ctx.send(f"🎉 Teste concluído! {user1.mention} e {user2.mention} agora estão casados (simulado).")

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(MarriageSystem(bot))