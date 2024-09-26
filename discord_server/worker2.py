import os
import discord
from discord.ext import commands, tasks
from llm.respond import respond_to_channel
from config.settings import SYSTEM_PROMPT, AI_CHANNEL_ID, IS_HEROKU_APP
import django_rq
from rq.job import Job
from channels.models import Channel
from ai_agents.models import AIAgent
import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from asgiref.sync import sync_to_async

class DiscordBot(commands.Bot):
    """
    A custom Discord bot class that extends commands.Bot.
    This bot can handle messages, run background tasks, and manage its own lifecycle.
    """

    def __init__(self, ai_agent):
        """
        Initialize the Discord bot with custom settings.

        :param ai_agent: The AIAgent object associated with this bot
        """
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(
            command_prefix='$',
            description='A multi-instance Discord bot',
            intents=intents
        )
        
        self.ai_agent = ai_agent
        self.is_active = True
        
    async def setup_hook(self):
        """
        A coroutine called to do setup after the bot is logged in but before it has connected to the Websocket.
        Here, we start the background loop.
        """
        self.background_loop.start()
    
    @tasks.loop(seconds=5.0)
    async def background_loop(self):
        """
        A background task that runs every 5 seconds.
        It processes finished jobs from the message queue and sends the results to the appropriate Discord channel.
        """
        if not self.is_active:
            await self.close()
            return

        message_queue = django_rq.get_queue('default')
        for job_id in message_queue.finished_job_registry.get_job_ids():
            job = Job.fetch(job_id, connection=message_queue.connection)
            message_queue.finished_job_registry.remove(job.id)
            result_data = job.latest_result().return_value
            channel = self.get_channel(int(result_data['channel_id']))
            print(self.ai_agent.name)
            print(result_data['ai_agent_name'])
            if channel and self.ai_agent.name == result_data['ai_agent_name']:
                await channel.send(result_data['content'])
    
    async def on_ready(self):
        """
        Event listener for when the bot has successfully connected to Discord.
        """
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
    
    async def on_message(self, message):
        """
        Event listener for when a message is sent in a channel the bot can see.
        
        :param message: The message object representing the received message
        """
        if not self.is_active:
            return

        print(f'{message.author}: {message.content} {message.channel}')

        ai_agent_name = self.ai_agent.name.lower()
        if message.author.bot:
            print(f'Bot {message.author.bot}')
            return
        elif message.content.startswith('$'):
            await self.process_commands(message)
            return
        elif message.content.startswith(f"@{ai_agent_name}"):
            await message.channel.send('Ok.')
            queue = django_rq.get_queue('default')
            queue.enqueue(
                handle_message,
                {
                    "ai_agent_name": ai_agent_name,
                    "content": message.content,
                    "author": str(message.author),
                    "channel": str(message.channel)
                },
            )

def handle_message(message_data):
    """
    Handle a message by generating a response using an AI model.

    :param message_data: A dictionary containing message details
    :return: A dictionary with the response details
    """
    channel = Channel.objects.get(channel_name=message_data['channel'])
    print(f"Handling message: {message_data['content']} in channel {channel}")
    immediate_response_content = respond_to_channel({
        "channel_id": channel.channel_id,
        "ai_agent_name": message_data['ai_agent_name'],
        "channel": message_data['channel'],
        "content": message_data['content'],
    })
    return {
        "ai_agent_name": message_data['ai_agent_name'],
        "channel": message_data['channel'],
        "channel_id": channel.channel_id,
        "content": immediate_response_content,
    }

class BotManager:
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

        bot = DiscordBot(ai_agent)
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
    bot_manager = BotManager()
    
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

async def main():
    """
    The main coroutine that sets up and runs the bot manager and all bots.
    """
    async with manage_bot_lifecycle() as bot_manager:
        await asyncio.gather(
            *[asyncio.create_task(bot_manager.start_bot(agent)) for agent in bot_manager.bots.values()],
            bot_manager.check_bot_status()
        )

def run_discord_bot():
    """
    The entry point of the script. It sets up Heroku-specific configurations if necessary
    and runs the main coroutine.
    """
    if IS_HEROKU_APP:
        print('Running on Heroku...')

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt, shutting down...")
    finally:
        print("Discord bot has shut down.")

if __name__ == "__main__":
    run_discord_bot()