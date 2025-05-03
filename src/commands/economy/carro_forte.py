import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta
import json
import os

DATA_FILE = "./src/data/economy.json"
CHANNEL_ID = 1366432240065581167  # Substitua pelo ID do canal desejado
CARRO_FORTE_IMAGE = "./assets/carro_forte.png"  # Caminho para a imagem do carro-forte
FUGITIVO_ROLE_NAME = "Fugitivo"  # Nome do cargo temporário para fugitivos

def load_data():
    """Carrega os dados do banco de dados JSON."""
    try:
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({"users": {}}, f, indent=4)
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar o arquivo JSON: {e}")
        return {"users": {}}

def save_data(data):
    """Salva os dados no banco de dados JSON."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo JSON: {e}")
class CarroForte(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_active = False
        self.participants = []
        self.carro_type = None
        self.carro_rewards = {
            "Bronze": (500, 1000),
            "Ouro": (1000, 5000),
            "Diamante": (5000, 10000)
        }
        self.fugitivos = {}  # Dicionário para rastrear fugitivos e seus tempos
        self.start_event_loop.start()  # Inicia o loop do evento automaticamente
        print("✅ Loop do evento de carro-forte iniciado.")
        
    async def assign_fugitivo_role(self, member):
        """Atribui o cargo de Fugitivo ao usuário e remove após 10 minutos."""
        try:
            guild = member.guild
            fugitivo_role = discord.utils.get(guild.roles, name=FUGITIVO_ROLE_NAME)

            # Cria o cargo se ele não existir
            if not fugitivo_role:
                fugitivo_role = await guild.create_role(
                    name=FUGITIVO_ROLE_NAME,
                    color=discord.Color.light_grey(),
                    reason="Criado automaticamente para o sistema de carro-forte."
                )
                print(f"✅ Cargo '{FUGITIVO_ROLE_NAME}' criado no servidor {guild.name}.")

            # Atribui o cargo ao membro
            await member.add_roles(fugitivo_role)
            print(f"✅ Cargo '{FUGITIVO_ROLE_NAME}' atribuído a {member.name}.")

            # Remove o cargo após 10 minutos
            await asyncio.sleep(600)  # 10 minutos
            await member.remove_roles(fugitivo_role)
            print(f"✅ Cargo '{FUGITIVO_ROLE_NAME}' removido de {member.name}.")
        except Exception as e:
            print(f"❌ Erro ao atribuir/remover o cargo de Fugitivo: {e}")


    @tasks.loop(minutes=30)
    async def start_event_loop(self):
        """Inicia o evento de carro-forte automaticamente."""
        try:
            print("🔄 Aguardando para iniciar o próximo evento de carro-forte...")
            await asyncio.sleep(random.randint(10, 600))  # Espera entre 10 segundos e 10 minutos
            self.carro_type = random.choice(["Bronze", "Ouro", "Diamante"])
            self.event_active = True
            self.participants = []

            # Obtém o canal específico pelo ID
            channel = self.bot.get_channel(CHANNEL_ID)

            if channel and isinstance(channel, discord.TextChannel):
                embed = discord.Embed(
                    title=f"🚨 Carro-Forte de {self.carro_type} avistado!",
                    description=(
                        f"Use `-t furtar` para participar do roubo! Você precisa de pelo menos uma arma.\n\n"
                        f"💰 **Recompensas:**\n"
                        f"Bronze: R$ 500 - R$ 1.000\n"
                        f"Ouro: R$ 1.000 - R$ 5.000\n"
                        f"Diamante: R$ 5.000 - R$ 10.000"
                    ),
                    color=discord.Color.gold()
                )
                embed.set_image(url="attachment://carro_forte.png")
                embed.set_footer(text="O evento ficará ativo por 2 minutos. Não perca!")

                # Envia a mensagem com a imagem
                if os.path.exists(CARRO_FORTE_IMAGE):
                    with open(CARRO_FORTE_IMAGE, "rb") as img:
                        await channel.send(embed=embed, file=discord.File(img, "carro_forte.png"))
                else:
                    print(f"❌ Imagem do carro-forte não encontrada: {CARRO_FORTE_IMAGE}")
                    await channel.send(embed=embed)

                print(f"✅ Evento de carro-forte iniciado no canal {channel.name} com tipo {self.carro_type}.")
            else:
                print(f"❌ Canal com ID {CHANNEL_ID} não encontrado ou não é um canal de texto.")

            # O evento ficará ativo por 2 minutos
            await asyncio.sleep(120)
            if channel:
                await self.end_event(channel)
        except Exception as e:
            print(f"❌ Erro ao iniciar o evento de carro-forte: {e}")

    @start_event_loop.before_loop
    async def before_start_event_loop(self):
        """Aguarda o bot estar pronto antes de iniciar o loop."""
        print("⏳ Aguardando o bot estar pronto para iniciar o loop do evento de carro-forte...")
        await self.bot.wait_until_ready()
    async def end_event(self, channel):
            """Finaliza o evento de carro-forte e apaga as mensagens relacionadas."""
            try:
                if not self.participants:
                    await channel.send("🚨 O evento de carro-forte terminou, mas ninguém participou!")
                    print("🚨 O evento de carro-forte terminou sem participantes.")
                else:
                    rewards = {}
                    for user_id in self.participants:
                        user_data = self.get_user_data(user_id)
                        min_reward, max_reward = self.carro_rewards[self.carro_type]
                        reward = random.randint(min_reward, max_reward)
                        user_data["carteira"] += reward
                        self.update_user_data(user_id, "carteira", user_data["carteira"])
                        rewards[user_id] = reward

                        # Adiciona o cargo de fugitivo ao usuário
                        guild = channel.guild
                        member = guild.get_member(user_id)
                        if member:
                            await self.assign_fugitivo_role(member)

                    # Determina quem ganhou mais dinheiro
                    top_user_id = max(rewards, key=rewards.get)
                    top_reward = rewards[top_user_id]

                    # Envia o feedback
                    participants_mentions = ", ".join([f"<@{user_id}>" for user_id in self.participants])
                    await channel.send(
                        f"🚨 O evento de carro-forte terminou!\n\n"
                        f"Participantes: {participants_mentions}\n"
                        f"🏆 **<@{top_user_id}> ganhou mais dinheiro: R$ {top_reward}!**\n"
                        f"Os participantes agora são fugitivos! Policiais, usem `-t prender @usuário` para capturá-los."
                    )
                    print(f"✅ Evento de carro-forte finalizado. Participantes: {participants_mentions}")

                # Apaga as mensagens relacionadas ao evento
                def is_event_message(message):
                    """Filtra mensagens relacionadas ao evento."""
                    return (
                        message.author == self.bot.user or
                        "carro-forte" in message.content.lower() or
                        "furtar" in message.content.lower()
                    )

                deleted = await channel.purge(limit=100, check=is_event_message)
                print(f"✅ {len(deleted)} mensagens relacionadas ao evento foram apagadas.")
            except Exception as e:
                print(f"❌ Erro ao finalizar o evento de carro-forte: {e}")

            # Reseta o evento
            self.event_active = False
            self.participants = []
            self.carro_type = None
        
    def get_user_data(self, user_id):
        """Obtém os dados de um usuário ou cria um novo registro."""
        try:
            data = load_data()
            if str(user_id) not in data["users"]:
                data["users"][str(user_id)] = {
                    "carteira": 0,
                    "banco": 0,
                    "nivel": 1,
                    "exp": 0,
                    "emprego": "Desempregado",
                    "respeito": 0,
                    "itens": {},
                    "casado_com": None,
                    "ultimo_trabalho": None
                }
                save_data(data)
            return data["users"][str(user_id)]
        except Exception as e:
            print(f"❌ Erro ao obter os dados do usuário {user_id}: {e}")
            return None

    def update_user_data(self, user_id, key, value):
        """Atualiza os dados de um usuário."""
        try:
            data = load_data()
            data["users"][str(user_id)][key] = value
            save_data(data)
        except Exception as e:
            print(f"❌ Erro ao atualizar os dados do usuário {user_id}: {e}")
    @commands.command(name="furtar")
    async def furtar(self, ctx):
        """Permite que o usuário participe do evento de carro-forte."""
        try:
            # Verifica se há um evento ativo
            if not self.event_active:
                await ctx.send("❌ Não há nenhum evento de carro-forte ativo no momento.")
                return

            user_id = ctx.author.id
            user_data = self.get_user_data(user_id)

            if not user_data:
                await ctx.send("❌ Não foi possível carregar seus dados. Tente novamente mais tarde.")
                return

            # Verifica se o usuário tem pelo menos uma arma
            required_weapons = ["Faca", "Espingarda", "Pistola", "Calibre 12", "Submetralhadora", "Bazuca"]
            has_weapon = any(user_data["itens"].get(weapon, 0) > 0 for weapon in required_weapons)

            if not has_weapon:
                await ctx.send("❌ Você não pode participar do roubo! Você precisa ter pelo menos uma arma.")
                return

            # Adiciona o usuário à lista de participantes
            if user_id not in self.participants:
                self.participants.append(user_id)
                await ctx.send(f"✅ {ctx.author.mention}, você entrou no roubo do carro-forte de {self.carro_type}!")
                print(f"✅ {ctx.author.name} entrou no roubo do carro-forte.")
            else:
                await ctx.send(f"❌ {ctx.author.mention}, você já está participando do roubo!")
                print(f"❌ {ctx.author.name} já está participando do roubo.")
        except Exception as e:
            print(f"❌ Erro no comando 'furtar': {e}")
            await ctx.send("❌ Ocorreu um erro ao tentar participar do roubo. Tente novamente mais tarde.")

async def setup(bot):
    await bot.add_cog(CarroForte(bot))
    print("✅ Cog 'CarroForte' carregado com sucesso.")