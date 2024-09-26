import os
import discord
from discord.ext import commands, tasks
from llm.respond import respond_to_channel
from config.settings import SYSTEM_PROMPT, AI_CHANNEL_ID, IS_HEROKU_APP
import django_rq
from rq.job import Job
from channels.models import Channel
from ai_agents.models import AIAgent

def handle_message(message_data):
    """
    Handle a message by generating a response using an AI model.

    :param message_data: A dictionary containing message details
    :return: A dictionary with the response details
    """
    channel = Channel.objects.get(channel_name=message_data['channel'])
    ai_agent = AIAgent.objects.get(name=message_data['ai_agent_name'])
    print(f"Handling message: {message_data['content']} in channel {channel}")
    print(f"{ai_agent.name} is processing...")
    immediate_response_content = respond_to_channel({
        "channel_id": channel.channel_id,
        "ai_agent_name": message_data['ai_agent_name'],
        "channel": message_data['channel'],
        "content": message_data['content'],
        "system": ai_agent.description,
    })
    return {
        "ai_agent_name": message_data['ai_agent_name'],
        "channel": message_data['channel'],
        "channel_id": channel.channel_id,
        "content": immediate_response_content,
    }

class ChatBot(commands.Bot):
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
        self.is_active = ai_agent.is_active
        
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
            result_data = job.latest_result().return_value
            channel = self.get_channel(int(result_data['channel_id']))
            # print(f"{result_data['ai_agent_name']} finished processing.")
            # print(self.ai_agent.name)
            if channel and self.ai_agent.name == result_data['ai_agent_name']:
                message_queue.finished_job_registry.remove(job.id)
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
        # Ignore messages from the bot itself
        if not self.is_active:
            return

        # print(f'{message.author}: {message.content} {message.channel}')

        ai_agent_name = self.ai_agent.name.lower()
        if message.author.bot:
            print(f'Bot {message.author.bot}')
            return
        elif message.content.startswith('$'):
            await self.process_commands(message)
            return
        elif message.content.startswith(f"@{ai_agent_name}"):
            # await message.channel.send('Ok.')
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