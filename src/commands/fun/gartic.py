import discord
from discord.ext import commands
import random
from PIL import Image, ImageDraw, ImageFont
import os

class GarticGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_word = None
        self.game_active = False

    @commands.command(name="gartic_start")
    async def start_gartic(self, ctx):
        """Inicia o jogo de Gartic com imagens."""
        if self.game_active:
            await ctx.send("🎮 Um jogo já está em andamento! Termine o jogo atual antes de iniciar outro.")
            return

        # Lista de palavras para o jogo
        words = ["cachorro", "gato", "carro", "avião", "árvore", "computador", "banana", "futebol", "praia", "montanha"]
        self.current_word = random.choice(words)
        self.game_active = True

        # Gera a imagem da palavra
        image_path = self.generate_image(self.current_word)

        # Envia a imagem no canal
        await ctx.send("🎨 Tente adivinhar o que está sendo desenhado!")
        await ctx.send(file=discord.File(image_path))

        # Remove a imagem após o envio
        os.remove(image_path)

    @commands.command(name="gartic_guess")
    async def guess_gartic(self, ctx, *, guess):
        """Permite que os usuários façam uma tentativa de adivinhar a palavra."""
        if not self.game_active:
            await ctx.send("❌ Nenhum jogo está em andamento. Use `!gartic_start` para iniciar um jogo.")
            return

        if guess.lower() == self.current_word.lower():
            self.game_active = False
            await ctx.send(f"🎉 Parabéns, {ctx.author.mention}! Você acertou a palavra: **{self.current_word}**!")
            self.current_word = None
        else:
            await ctx.send(f"❌ {ctx.author.mention}, essa não é a palavra correta. Tente novamente!")

    @commands.command(name="gartic_end")
    async def end_gartic(self, ctx):
        """Encerra o jogo atual."""
        if not self.game_active:
            await ctx.send("❌ Nenhum jogo está em andamento.")
            return

        self.game_active = False
        await ctx.send(f"🛑 O jogo foi encerrado! A palavra era: **{self.current_word}**.")
        self.current_word = None

    def generate_image(self, word):
        """Gera uma imagem simples representando a palavra."""
        # Configurações da imagem
        width, height = 400, 200
        background_color = (255, 255, 255)  # Branco
        text_color = (0, 0, 0)  # Preto
        font_path = "arial.ttf"  # Certifique-se de que a fonte está disponível no sistema
        font_size = 40

        # Cria a imagem
        image = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(image)

        # Carrega a fonte
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # Adiciona o texto (embaralhado)
        scrambled_word = "".join(random.sample(word, len(word)))
        text_width, text_height = draw.textsize(scrambled_word, font=font)
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        draw.text((text_x, text_y), scrambled_word, fill=text_color, font=font)

        # Salva a imagem temporariamente
        image_path = f"{word}.png"
        image.save(image_path)
        return image_path

async def setup(bot):
    await bot.add_cog(GarticGame(bot))