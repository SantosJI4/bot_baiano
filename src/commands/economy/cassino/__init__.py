from .roleta import setup as setup_roleta
from .cassino import setup as setup_cassino
from .blackjack import setup as setup_blackjack
from .slot_machine import setup as setup_slot_machine
from .dados_de_guerra import setup as setup_dados_de_guerra
from .loteria import setup as setup_loteria


async def setup(bot):
    await setup_roleta(bot)
    await setup_cassino(bot)
    await setup_blackjack(bot)
    await setup_slot_machine(bot)
    await setup_dados_de_guerra(bot)
    await setup_loteria(bot)