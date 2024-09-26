import os
import discord
from discord.ext import commands, tasks
from llm.respond import respond_to_channel
from config.settings import SYSTEM_PROMPT, AI_CHANNEL_ID, IS_HEROKU_APP
import django_rq
from rq.job import Job
import json
from channels.models import Channel, Message
from asgiref.sync import sync_to_async, async_to_sync
from ai_agents.models import AIAgent
from rq.serializers import JSONSerializer
import asyncio
import signal
import sys
import time

bots = []

def handle_message(message_data):
    channel = Channel.objects.get(channel_name=message_data['channel'])
    print(f"Handling message: {message_data['content']} in channel {channel}")
    response_text = respond_to_channel(message_data['content'], channel.channel_id)
    print(bots[0])
    return {
        "channel": message_data['channel'],
        "channel_id": channel.channel_id,
        "content": response_text,
    }

class DiscordBot(commands.Bot):
    def __init__(self, ai_agent):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(
            command_prefix='$',
            description='A multi-instance Discord bot',
            intents=intents
        )
        
        self.ai_agent = ai_agent
        
    async def setup_hook(self):
        self.background_loop.start()
    
    @tasks.loop(seconds=5.0)
    async def background_loop(self):
        message_queue = django_rq.get_queue('default')
        for job_id in message_queue.finished_job_registry.get_job_ids():
            job = Job.fetch(job_id, connection=message_queue.connection)
            message_queue.finished_job_registry.remove(job.id)
            result_data = job.latest_result().return_value
            print(result_data)
            channel = self.get_channel(int(result_data['channel_id']))
            if channel:
                await channel.send(result_data['content'])
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
    
    async def on_message(self, message):
        print(f'{message.author}: {message.content} {message.channel}')
        if message.author.bot:
            print(f'Bot {message.author.bot}')
            return
        elif message.content.startswith('$'):
            await self.process_commands(message)
            return
        elif message.content.startswith('ai'):
            await message.channel.send('Ok.')
            queue = django_rq.get_queue('default')
            queue.enqueue(
                handle_message,
                {
                    "content": message.content,
                    "author": str(message.author),
                    "channel": str(message.channel)
                },
            )

async def run_bot(ai_agent):
    bot = DiscordBot(ai_agent)

    try:
        await bot.start(ai_agent.bot_token)
    except asyncio.CancelledError:
        print(f"Bot {ai_agent.name} was cancelled")
    except Exception as e:
        print(f"Error in bot {ai_agent.name}: {e}")
    finally:
        await bot.shutdown()

def run_discord_bot():
    ai_agents = AIAgent.objects.filter(is_active=True)[:1]

    if IS_HEROKU_APP:
        loop = asyncio.get_event_loop()
        # bots = [DiscordBot(ai_agent) for ai_agent in ai_agents]
        bot_tasks = [asyncio.ensure_future(run_bot(ai_agent)) for ai_agent in ai_agents]

        def force_exit():
            print("Forcing exit...")
            os._exit(1)

        def signal_handler():
            print("Received shutdown signal, closing bots...")
            for task in bot_tasks:
                task.cancel()
            
            # Schedule force exit after 5 seconds
            loop.call_later(5, force_exit)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        try:
            loop.run_until_complete(asyncio.gather(*bot_tasks))
        except asyncio.CancelledError:
            pass
        finally:
            pending = asyncio.all_tasks(loop=loop)
            for task in pending:
                task.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()
            sys.exit(0)
    else:
        bot = DiscordBot(ai_agents[0])
        bot.run(ai_agents[0].bot_token)

        # @commands.has_permissions(manage_messages=True)
        # @bot.command()
        # async def clear(ctx):
        #     """Clears the specified number of messages from the channel."""
        #     print('Clearing messages...')
        #     await ctx.channel.purge(limit=10)
        #     print('Messages cleared.')
        # bot.run(ai_agents[0].bot_token)
        