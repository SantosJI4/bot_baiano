import discord
from discord.ext import commands
import openai
import os

# Carrega a chave da API do OpenAI do arquivo .env
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chat")
    async def chat(self, ctx, *, prompt):
        """Conversa com o ChatGPT usando a API do OpenAI."""
        await ctx.send("🤖 Processando sua mensagem...")
        try:
            # Envia a mensagem para a API do ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Modelo usado
                messages=[
                    {"role": "system", "content": "Você é um assistente útil e amigável."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            # Resposta do ChatGPT
            reply = response["choices"][0]["message"]["content"]
            await ctx.send(f"💬 {reply}")
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao processar sua mensagem: {e}")
    @commands.command(name="image")
    async def generate_image(self, ctx, *, prompt):
      """Gera uma imagem usando a API DALL·E da OpenAI."""
      await ctx.send("🎨 Gerando sua imagem...")

      try:
          # Envia a solicitação para a API DALL·E
          response = openai.Image.create(
              prompt=prompt,
              n=1,  # Número de imagens a serem geradas
              size="256x256"
          )

          # Obtém o URL da imagem gerada
          image_url = response["data"][0]["url"]
          await ctx.send(f"🖼️ Aqui está sua imagem: {image_url}")
      except openai.error.OpenAIError as e:
          if e.http_status == 500:
              await ctx.send("❌ O servidor da OpenAI encontrou um erro ao processar sua solicitação. Tente novamente mais tarde.")
          else:
              await ctx.send(f"❌ Ocorreu um erro: {e}")
          
async def setup(bot):
    await bot.add_cog(ChatAI(bot))