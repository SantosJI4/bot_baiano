import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import os
import json
from io import BytesIO

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

def fix_user_data():
    """Garante que todos os usuários tenham o campo respeito."""
    data = load_data()
    for user_id, user_data in data["users"].items():
        if "respeito" not in user_data:
            user_data["respeito"] = 0
    save_data(data)

# Chame esta função no início do bot
fix_user_data()

class Inventory(commands.Cog):
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
              "respeito": 0,  # Inicializa o campo respeito
              "itens": {},
              "casado_com": None,
              "ultimo_trabalho": None
          }
          save_data(data)
      else:
          # Garante que o campo respeito exista para usuários antigos
          if "respeito" not in data["users"][str(user_id)]:
              data["users"][str(user_id)]["respeito"] = 0
              save_data(data)
      return data["users"][str(user_id)]

    @commands.command(name="inventario")
    async def inventario(self, ctx):
      """Exibe o inventário do usuário."""
      print(f"Comando 'inventario' chamado por {ctx.author.name}")  # Log para depuração
      try:
          user_id = ctx.author.id
          user_data = self.get_user_data(user_id)

          # Dados do usuário
          carteira = user_data["carteira"]
          banco = user_data["banco"]
          emprego = user_data["emprego"]
          respeito = user_data["respeito"]
          itens = user_data["itens"]

          # Cria uma lista de itens formatada
          itens_formatados = "\n".join([f"**{item}**: {quantidade}" for item, quantidade in itens.items()])
          if not itens_formatados:
              itens_formatados = "Nenhum item no inventário."

          # Cria o embed
          embed = discord.Embed(
              title=f"🎒 Inventário de {ctx.author.name}",
              color=discord.Color.blue()
          )
          embed.set_thumbnail(url=ctx.author.display_avatar.url)
          embed.add_field(name="💰 Dinheiro na Carteira", value=f"R$ {carteira}", inline=True)
          embed.add_field(name="🏦 Dinheiro no Banco", value=f"R$ {banco}", inline=True)
          embed.add_field(name="💼 Profissão", value=emprego, inline=True)
          embed.add_field(name="⭐ Respeito", value=respeito, inline=True)
          embed.add_field(name="📦 Itens", value=itens_formatados, inline=False)
          embed.set_footer(text="Use seus recursos com sabedoria!")

          # Envia o embed
          await ctx.send(embed=embed)
          print("Embed enviado com sucesso.")  # Log para depuração
      except Exception as e:
          print(f"Erro no comando 'inventario': {e}")  # Log para depuração
          await ctx.send("❌ Ocorreu um erro ao tentar exibir seu inventário.")

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(Inventory(bot))