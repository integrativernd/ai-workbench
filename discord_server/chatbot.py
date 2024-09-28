import os
from discord.ext import commands, tasks
import discord
from llm.respond import respond
from config.settings import SYSTEM_PROMPT, AI_CHANNEL_ID, PRODUCTION
import django_rq
from rq.job import Job
from channels.models import Channel
from ai_agents.models import AIAgent
import time

def handle_message(message_data):
    """
    Handle a message by generating a response using an AI model.

    :param message_data: A dictionary containing message details
    :return: A dictionary with the response details
    """
    channel = Channel.objects.get(channel_name=message_data['channel_name'])
    ai_agent = AIAgent.objects.get(name=message_data['ai_agent_name'])

    print(f"Handling message: {message_data['content']} in channel {channel}")
    print(f"{ai_agent.name} is processing...")

    immediate_response_content = respond(
        ai_agent,
        channel,
        {
            "ai_agent_name": ai_agent.name,
            "channel_id": channel.channel_id,
            "content": message_data['content'],
            "author": message_data['author'],
            "ai_agent_system_prompt": ai_agent.description,
        }
    )

    print(f"{ai_agent.name} my immediate response will be: {immediate_response_content}")

    return {
        "ai_agent_name": ai_agent.name,
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
        self.message_queue = django_rq.get_queue('default')
        
    async def setup_hook(self):
        """
        A coroutine called to do setup after the bot is logged in but before it has connected to the Websocket.
        Here, we start the background loop.
        """
        self.background_loop.start()
    
    async def add_job(self, job_id):
        """
        Add a job to the message queue for processing.

        :param job: The job object to add to the message queue
        """
        self.ai_agent.add_job(job_id)

    @tasks.loop(seconds=2)
    async def background_loop(self):
        """
        A background task that runs every 5 seconds.
        It processes finished jobs from the message queue and sends the results to the appropriate Discord channel.
        """

        if not self.is_active:
            await self.close()
            return
        else:
            print(f"{self.ai_agent.name}: I am active.")
        
        job_ids = self.message_queue.finished_job_registry.get_job_ids()
        print(f"{self.ai_agent.name}: I have {len(job_ids)} tasks to process.")

        if len(job_ids) == 0:
            return
        
        jobs = Job.fetch_many(job_ids, connection=self.message_queue.connection)
        for job in jobs:
            try:
                result_data = job.latest_result().return_value
                channel = self.get_channel(int(result_data['channel_id']))
                is_same_agent = self.ai_agent.name == result_data['ai_agent_name']
                if channel and is_same_agent:
                    self.message_queue.finished_job_registry.remove(job.id)
                    await channel.send(result_data['content'])
            except Exception as e:
                self.message_queue.finished_job_registry.remove(job.id)
                print(f"Error processing job: {job.id}")
                print(e)
    
    async def on_ready(self):
        """
        Event listener for when the bot has successfully connected to Discord.
        """
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @property
    def discord_handle(self):
        return f"@{self.ai_agent.name.lower()}"
    
    # async def enqueue_simple_background_process(self, request_data):
    #     job = self.message_queue.enqueue(simple_background_process, request_data)
    #     await self.add_job(job.id)

    async def enqueue_background_process(self, request_data):
        print(f"Enqueuing background process: {request_data}")
        job = self.message_queue.enqueue(handle_message, request_data)
        await self.add_job(job.id)
    
    async def on_message(self, message):
        """
        Event listener for when a message is sent in a channel the bot can see.
        
        :param message: The message object representing the received message
        """
        # Ignore messages from the bot itself
        if not self.is_active:
            return

        if message.author.bot:
            return

        print(f'channel: {message.channel}')
        print(f'{message.author}> {message.content}')

        if message.content.startswith(self.discord_handle):
            if message.content == f"{self.discord_handle} ping":
                await message.channel.send('pong')
                return

            await message.channel.send('Ok.')

            await self.enqueue_background_process({
                "ai_agent_name": self.ai_agent.name,
                "channel_name": str(message.channel),
                "content": message.content,
                "author": str(message.author),
                "channel": str(message.channel),
            })
