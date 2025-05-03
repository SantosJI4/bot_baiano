import discord
import random
import asyncio
import json
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime

class SlotMachine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = {}
        self.economy_file = "economy.json"

    def load_economy_data(self):
        try:
            with open(self.economy_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_economy_data(self, data):
        with open(self.economy_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_user_balance(self, user_id):
        economy_data = self.load_economy_data()
        return economy_data.get(str(user_id), {}).get("saldo", 1000)

    def update_user_balance(self, user_id, amount):
        economy_data = self.load_economy_data()
        user_id_str = str(user_id)

        if user_id_str not in economy_data:
            economy_data[user_id_str] = {"saldo": 1000}

        economy_data[user_id_str]["saldo"] += amount
        self.save_economy_data(economy_data)

    def add_to_history(self, user_id, amount):
        if user_id not in self.user_data:
            self.user_data[user_id] = {"aposta": 100, "historico": []}
        self.user_data[user_id]["historico"].append(amount)
        if len(self.user_data[user_id]["historico"]) > 5:
            self.user_data[user_id]["historico"].pop(0)

    @commands.command(name="slot")
    async def slot_machine(self, ctx):
        user_id = ctx.author.id

        if user_id not in self.user_data:
            self.user_data[user_id] = {"aposta": 100, "historico": []}

        async def update_embed(embed, saldo, aposta, historico):
            embed.clear_fields()
            embed.add_field(name="💰 Saldo", value=f"R$ {saldo}", inline=True)
            embed.add_field(name="🎲 Aposta", value=f"R$ {aposta}", inline=True)
            embed.add_field(name="🕒 Horário", value=f"{datetime.now().strftime('%H:%M:%S')}", inline=True)
            if historico:
                embed.add_field(name="📜 Histórico de Ganhos", value="\n".join([f"R$ {h}" for h in historico]), inline=False)
            else:
                embed.add_field(name="📜 Histórico de Ganhos", value="Nenhum ganho registrado.", inline=False)

        async def spin_slots():
            symbols = ["🍒", "🍋", "🍉", "⭐", "💎", "🔔", "🍇", "🍓", "🍍"]
            return [random.choice(symbols) for _ in range(9)]

        async def animate_slots(embed, msg):
            symbols = ["🍒", "🍋", "🍉", "⭐", "💎", "🔔", "🍇", "🍓", "🍍"]
            for _ in range(10):
                temp_roll = [random.choice(symbols) for _ in range(9)]
                embed.description = (
                    f"{temp_roll[0]} | {temp_roll[1]} | {temp_roll[2]}\n"
                    f"{temp_roll[3]} | {temp_roll[4]} | {temp_roll[5]}\n"
                    f"{temp_roll[6]} | {temp_roll[7]} | {temp_roll[8]}"
                )
                await msg.edit(embed=embed)
                await asyncio.sleep(0.2)

        async def play_game(interaction):
            saldo = self.get_user_balance(user_id)
            aposta = self.user_data[user_id]["aposta"]

            if saldo < aposta:
                await interaction.response.send_message("❌ Você não tem saldo suficiente para apostar!", ephemeral=True)
                return

            self.update_user_balance(user_id, -aposta)

            await animate_slots(embed, msg)

            slots = await spin_slots()
            embed.description = (
                f"{slots[0]} | {slots[1]} | {slots[2]}\n"
                f"{slots[3]} | {slots[4]} | {slots[5]}\n"
                f"{slots[6]} | {slots[7]} | {slots[8]}"
            )

            # Algoritmo de vitória/perda
            if slots[0] == slots[1] == slots[2] or slots[3] == slots[4] == slots[5] or slots[6] == slots[7] == slots[8]:
                premio = aposta * random.randint(5, 15)  # Super ganhos
                self.update_user_balance(user_id, premio)
                self.add_to_history(user_id, premio)
                resultado = f"🎉 Você ganhou R$ {premio} com {slots[4]}!"
            else:
                resultado = "😢 Você perdeu! Tente novamente."

            # Feedback visual
            embed.color = discord.Color.green() if "ganhou" in resultado else discord.Color.red()

            saldo_atual = self.get_user_balance(user_id)
            historico = self.user_data[user_id]["historico"]
            embed.add_field(name="Resultado", value=resultado, inline=False)
            await update_embed(embed, saldo_atual, aposta, historico)
            await interaction.response.edit_message(embed=embed, view=view)

        async def increase_bet(interaction):
            self.user_data[user_id]["aposta"] += 50
            aposta = self.user_data[user_id]["aposta"]
            saldo = self.get_user_balance(user_id)
            historico = self.user_data[user_id]["historico"]
            await update_embed(embed, saldo, aposta, historico)
            await interaction.response.edit_message(embed=embed, view=view)

        async def reset_game(interaction):
            self.update_user_balance(user_id, 1000 - self.get_user_balance(user_id))
            self.user_data[user_id] = {"aposta": 100, "historico": []}
            saldo = self.get_user_balance(user_id)
            aposta = self.user_data[user_id]["aposta"]
            historico = self.user_data[user_id]["historico"]
            embed.description = "🎰 Bem-vindo ao Slot Machine! Clique em **Girar** para começar."
            await update_embed(embed, saldo, aposta, historico)
            await interaction.response.edit_message(embed=embed, view=view)

        async def cancel_game(interaction):
            await interaction.response.send_message("❌ Jogo cancelado.", ephemeral=True)
            await interaction.message.delete()

        view = View()
        view.add_item(Button(label="Girar", style=discord.ButtonStyle.green, custom_id="spin"))
        view.add_item(Button(label="Aumentar Aposta", style=discord.ButtonStyle.blurple, custom_id="increase_bet"))
        view.add_item(Button(label="Reiniciar", style=discord.ButtonStyle.gray, custom_id="reset"))
        view.add_item(Button(label="Cancelar", style=discord.ButtonStyle.red, custom_id="cancel"))

        view.children[0].callback = play_game
        view.children[1].callback = increase_bet
        view.children[2].callback = reset_game
        view.children[3].callback = cancel_game

        embed = discord.Embed(
            title="🎰 Slot Machine",
            description="🎰 Bem-vindo ao Slot Machine! Clique em **Girar** para começar.",
            color=discord.Color.gold()
        )
        saldo = self.get_user_balance(user_id)
        aposta = self.user_data[user_id]["aposta"]
        historico = self.user_data[user_id]["historico"]
        await update_embed(embed, saldo, aposta, historico)

        msg = await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(SlotMachine(bot))