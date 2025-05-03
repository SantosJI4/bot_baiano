import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import io
import json
import aiohttp

DATA_FILE = "./src/data/economy.json"  # Caminho para o arquivo JSON

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self):
        """Carrega os dados do arquivo JSON."""
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({"users": {}}, f, indent=4)
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(self, data):
        """Salva os dados no arquivo JSON."""
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get_user_data(self, user_id):
        """Obtém os dados do usuário ou cria um novo registro."""
        data = self.load_data()
        if str(user_id) not in data["users"]:
            data["users"][str(user_id)] = {
                "nivel": 1,
                "exp": 0,
                "carteira": 0,
                "banco": 0,
                "emprego": "Desempregado",
                "respeito": 0,
                "casado_com": None,
                "background": None
            }
            self.save_data(data)
        return data["users"][str(user_id)]

    def calcular_exp_para_proximo_nivel(self, nivel):
        """Calcula a quantidade de EXP necessária para o próximo nível."""
        return 100 + (nivel * 50)

    @commands.command(name="perfil")
    async def perfil(self, ctx, member: discord.Member = None):
        """Gera a imagem de perfil do usuário."""
        try:
            if member is None:
                member = ctx.author  # Usa o autor do comando se nenhum membro for mencionado

            user_id = member.id
            user_data = self.get_user_data(user_id)

            # Carrega os dados do usuário
            nivel = user_data["nivel"]
            exp = user_data["exp"]
            exp_para_proximo_nivel = self.calcular_exp_para_proximo_nivel(nivel)
            emprego = user_data["emprego"]
            saldo_mao = user_data["carteira"]
            saldo_banco = user_data["banco"]
            respeito = user_data["respeito"]
            casado_com = user_data["casado_com"]

            # Verifica se o usuário está casado
            if casado_com is not None:
                parceiro = await self.bot.fetch_user(casado_com)
                status_casamento = f"💍 Casado com {parceiro.name}"
            else:
                status_casamento = "💔 Solteiro"

            # Cria a imagem do perfil
            largura, altura = 1000, 600

            # Verifica se há um fundo personalizado
            fundo_path = user_data.get("background", None)
            if fundo_path and os.path.exists(fundo_path):
                imagem = Image.open(fundo_path).resize((largura, altura))
            else:
                imagem = Image.new("RGB", (largura, altura), (20, 20, 20))  # Fundo cinza escuro
                draw = ImageDraw.Draw(imagem)
                for i in range(altura):  # Gradiente de fundo
                    cor = (20 + i // 10, 20 + i // 15, 50 + i // 20)
                    draw.line([(0, i), (largura, i)], fill=cor)

            draw = ImageDraw.Draw(imagem)
            try:
                fonte_titulo = ImageFont.truetype("./assets/fonts/DejaVuSans.ttf", 60)
                fonte_texto = ImageFont.truetype("./assets/fonts/DejaVuSans.ttf", 40)
                fonte_destaque = ImageFont.truetype("./assets/fonts/DejaVuSans.ttf", 50)
            except OSError:
                # Fallback para a fonte padrão embutida
                fonte_titulo = ImageFont.load_default()
                fonte_texto = ImageFont.load_default()
                fonte_destaque = ImageFont.load_default()

            # Adiciona o título
            draw.text((30, 30), f"Perfil de {member.name}", font=fonte_titulo, fill=(255, 255, 255))

            # Adiciona as informações do perfil
            draw.text((30, 120), f"Nível: {nivel}", font=fonte_destaque, fill=(255, 215, 0))
            draw.text((30, 180), f"EXP: {exp}/{exp_para_proximo_nivel}", font=fonte_texto, fill=(255, 255, 255))
            draw.text((30, 240), f"Emprego: {emprego}", font=fonte_texto, fill=(255, 255, 255))
            draw.text((30, 300), f"Saldo em Mãos: R$ {saldo_mao}", font=fonte_texto, fill=(0, 255, 0))
            draw.text((30, 360), f"Saldo no Banco: R$ {saldo_banco}", font=fonte_texto, fill=(0, 255, 255))
            draw.text((30, 420), f"Respeito: {respeito}", font=fonte_texto, fill=(255, 255, 255))
            draw.text((30, 480), f"Status: {status_casamento}", font=fonte_texto, fill=(255, 255, 255))

            # Adiciona uma moldura para o avatar
            avatar_url = member.display_avatar.replace(size=256).url  # Obtém a URL do avatar
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as response:
                    avatar_bytes = await response.read()
                    avatar = Image.open(io.BytesIO(avatar_bytes)).resize((200, 200))
                    avatar = ImageOps.fit(avatar, (200, 200), centering=(0.5, 0.5))
                    mask = Image.new("L", avatar.size, 0)
                    draw_mask = ImageDraw.Draw(mask)
                    draw_mask.ellipse((0, 0, 200, 200), fill=255)
                    avatar.putalpha(mask)
                    imagem.paste(avatar, (750, 50), avatar)

            # Adiciona uma barra de progresso para o EXP
            barra_x = 30
            barra_y = 540
            barra_largura = 900
            barra_altura = 40
            progresso = int((exp / exp_para_proximo_nivel) * barra_largura)

            # Fundo da barra
            draw.rectangle(
                [barra_x, barra_y, barra_x + barra_largura, barra_y + barra_altura],
                fill=(50, 50, 50),
            )
            # Progresso da barra
            draw.rectangle(
                [barra_x, barra_y, barra_x + progresso, barra_y + barra_altura],
                fill=(0, 200, 0),
            )
            # Texto da barra
            draw.text(
                (barra_x + barra_largura // 2, barra_y - 10),
                f"{exp}/{exp_para_proximo_nivel} EXP",
                font=fonte_texto,
                fill=(255, 255, 255),
                anchor="ms",
            )

            # Salva a imagem em um buffer
            buffer = io.BytesIO()
            imagem.save(buffer, format="PNG")
            buffer.seek(0)

            # Envia a imagem no Discord
            await ctx.send(file=discord.File(fp=buffer, filename="perfil.png"))
        except Exception as e:
            print(f"❌ Erro ao gerar perfil: {e}")
            await ctx.send("❌ Ocorreu um erro ao gerar o perfil.")

    @commands.command(name="setbackground")
    async def set_background(self, ctx):
        """Permite que o usuário envie uma imagem para personalizar o fundo do perfil."""
        try:
            # Verifica se há anexos na mensagem
            if not ctx.message.attachments:
                await ctx.send("❌ Por favor, envie uma imagem junto com o comando.")
                return

            # Obtém o primeiro anexo
            attachment = ctx.message.attachments[0]

            # Verifica se o anexo é uma imagem válida
            if not attachment.filename.lower().endswith(("png", "jpg", "jpeg")):
                await ctx.send("❌ O arquivo deve ser uma imagem (PNG, JPG ou JPEG).")
                return

            user_id = ctx.author.id
            fundo_path = f"./backgrounds/{user_id}.png"

            # Baixa e salva a imagem
            await attachment.save(fundo_path)

            # Atualiza o caminho do fundo no banco de dados
            data = self.load_data()
            data["users"][str(user_id)]["background"] = fundo_path
            self.save_data(data)

            await ctx.send("✅ Seu fundo personalizado foi configurado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao configurar o fundo personalizado: {e}")
            await ctx.send("❌ Ocorreu um erro ao configurar o fundo personalizado.")
# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(Profile(bot))
    print("✅ Cog 'Profile' carregado com sucesso.")