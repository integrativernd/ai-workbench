import asyncio
import signal
from contextlib import asynccontextmanager
from asgiref.sync import sync_to_async
from discord_server.chatbot import ChatBot
from config.settings import IS_HEROKU_APP
from ai_agents.models import AIAgent


class ChatBotManager:
    """
    A class to manage multiple Discord bots.
    It handles starting, stopping, and monitoring the status of bots.
    """

    def __init__(self):
        """
        Initialize the BotManager.
        """
        self.bots = {}
        self.shutdown_event = asyncio.Event()

    async def start_bot(self, ai_agent):
        """
        Start a new bot for the given AI agent.

        :param ai_agent: The AIAgent object for which to start a bot
        """
        if ai_agent.id in self.bots:
            print(f"Bot for agent {ai_agent.name} is already running.")
            return

        bot = ChatBot(ai_agent)
        self.bots[ai_agent.id] = bot

        try:
            await bot.start(ai_agent.bot_token)
        except asyncio.CancelledError:
            print(f"Bot {ai_agent.name} was cancelled")
        except Exception as e:
            print(f"Error in bot {ai_agent.name}: {e}")
        finally:
            await self.stop_bot(ai_agent.id)

    async def stop_bot(self, agent_id):
        """
        Stop the bot associated with the given agent ID.

        :param agent_id: The ID of the AI agent whose bot should be stopped
        """
        if agent_id in self.bots:
            bot = self.bots[agent_id]
            bot.is_active = False
            await bot.close()
            del self.bots[agent_id]
            print(f"Bot for agent {agent_id} has been stopped and removed.")

    async def stop_all_bots(self):
        """
        Stop all running bots.
        """
        tasks = [self.stop_bot(agent_id) for agent_id in list(self.bots.keys())]
        await asyncio.gather(*tasks)

    @sync_to_async
    def get_ai_agent(self, agent_id):
        """
        Asynchronously get the AIAgent object for the given agent ID.

        :param agent_id: The ID of the AI agent to retrieve
        :return: The AIAgent object
        """
        return AIAgent.objects.get(id=agent_id)
  
    @sync_to_async
    def get_ai_agent_by_name(self, agent_name):
        """
        Asynchronously get the AIAgent object for the given agent ID.

        :param agent_id: The ID of the AI agent to retrieve
        :return: The AIAgent object
        """
        return AIAgent.objects.get(name=agent_name)

    async def check_bot_status(self):
        """
        Periodically check the status of all bots and manage their lifecycle.
        This method runs until a shutdown is requested.
        """
        while not self.shutdown_event.is_set():
            for agent_id in list(self.bots.keys()):
                ai_agent = await self.get_ai_agent(agent_id)
                if not ai_agent.is_active:
                    await self.stop_bot(agent_id)
                else:
                    # Update the bot's ai_agent reference with the latest data
                    self.bots[agent_id].ai_agent = ai_agent
            
            # Check for new active agents
            active_agents = await sync_to_async(list)(AIAgent.objects.filter(is_active=True))
            for agent in active_agents:
                if agent.id not in self.bots:
                    await self.start_bot(agent)
            
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=60)
            except asyncio.TimeoutError:
                continue  # Continue to next iteration if no shutdown event

@asynccontextmanager
async def manage_bot_lifecycle():
    """
    An async context manager to handle the lifecycle of the BotManager and its bots.
    It sets up signal handlers for graceful shutdown and ensures all bots are properly closed on exit.
    """
    bot_manager = ChatBotManager()
    
    def signal_handler():
        print("Received shutdown signal, initiating graceful shutdown...")
        bot_manager.shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, signal_handler)

    ai_agents = await sync_to_async(list)(AIAgent.objects.filter(is_active=True))
    bot_tasks = [asyncio.create_task(bot_manager.start_bot(agent)) for agent in ai_agents]
    status_task = asyncio.create_task(bot_manager.check_bot_status())

    try:
        yield bot_manager
    finally:
        print("Shutting down all bots...")
        bot_manager.shutdown_event.set()
        await bot_manager.stop_all_bots()
        for task in bot_tasks + [status_task]:
            task.cancel()
        await asyncio.gather(*bot_tasks, status_task, return_exceptions=True)
        print("All bots have been shut down.")

async def start_manage_bot_lifecycle():
    """
    The main coroutine that sets up and runs the bot manager and all bots.
    """
    async with manage_bot_lifecycle() as bot_manager:
        await asyncio.gather(
            *[asyncio.create_task(bot_manager.start_bot(agent)) for agent in bot_manager.bots.values()],
            bot_manager.check_bot_status()
        )

def run_chatbot_manager():
    """
    The entry point of the script. It sets up Heroku-specific configurations if necessary
    and runs the main coroutine.
    """
    try:
        asyncio.run(start_manage_bot_lifecycle())
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt, shutting down...")
    finally:
        print("Discord bot has shut down.")
