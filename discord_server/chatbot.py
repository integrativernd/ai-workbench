from discord.ext import commands, tasks
import discord
from llm.respond import respond, tool_registry
import django_rq
from rq.job import Job
from channels.models import Channel
from asgiref.sync import sync_to_async
from llm.anthropic_integration import anthropic_client, stream_to_discord
from llm.response_types import get_response_type_for_message, ResponseType
from temporal_app.run_workflow import run_workflow

# @sync_to_async
# def get_ai_agent_response(ai_agent, message):
#     """
#     Handle a message by generating a response using an AI model.

#     :param message_data: A dictionary containing message details
#     :return: A dictionary with the response details
#     """
#     # channel = Channel.objects.get(channel_name=str(message.channel))
#     # channel_id = channel_object.channel_id
#     # ai_agent = AIAgent.objects.get(name=message_data['ai_agent_name'])

#                 #     {
#                 # "ai_agent_name": self.ai_agent.name,
#                 # "channel_name": str(message.channel),
#                 # "content": message.content,
#                 # "author": str(message.author),
#                 # "channel": str(message.channel),

#     # {
#     #     "ai_agent_name": ai_agent.name,
#     #     "channel_id": channel.channel_id,
#     #     "content": message_data['content'],
#     #     "author": message_data['author'],
#     #     "ai_agent_system_prompt": ai_agent.description,
#     # }
#     return respond(ai_agent, message, channel)

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

    async def list_messages(self, channel):
        """
        List all messages in the message queue.
        """
        try:
            channel_messages = []
            async for message in channel.history(limit=3):
                channel_messages.append(f"{message.author}: {message.content} {message.id}")
            summary = "\n".join(channel_messages)
            print(summary)
            await channel.send(summary)
        except Exception as e:
            print(f"Error listing messages: {e}")
            return
        
    async def clear_channel(self, channel):
        """
        Clear the message queue.
        """
        await channel.purge(limit=1000)

    @sync_to_async
    def handle_tool_use(self, result_data):
        return tool_registry.handle_tool_use(self.ai_agent, result_data)

    async def handle_background_process(self, result_data, channel):
        try:
            result_data['tool'] = result_data['tool_sequence'][0]
            result_data['tool_sequence'] = result_data['tool_sequence'][1:]
            # print(f"Processing tool: {result_data['tool']}")
            # print(f"Tool sequence: {result_data['tool_sequence']}")
            await self.handle_tool_use(result_data)
            # await channel.send(tool_result)
        except Exception as e:
            print(f"Error processing tool: {e}")
            await channel.send(f"Error processing tool: {str(e)}")
    
    @tasks.loop(seconds=2)
    async def background_loop(self):
        """
        A background task that runs every 5 seconds.
        It processes finished jobs from the message queue and sends the results to the appropriate Discord channel.
        """
        if not self.is_active:
            await self.close()
            return

        job_ids = self.message_queue.finished_job_registry.get_job_ids()
        if len(job_ids) == 0:
            return

        # TODO: Query by AIAgent#job_ids
        jobs = Job.fetch_many(job_ids, connection=self.message_queue.connection)
        for job in jobs:
            try:
                print(f"Processing job: {job.id}")
                result_data = job.latest_result().return_value
                channel = self.get_channel(int(result_data['channel_id']))
                if channel and self.ai_agent.id == result_data['ai_agent_id']:
                    if len(result_data['tool_sequence']) > 0:
                        await channel.send(result_data['tool_sequence'][0].name)
                        await self.handle_background_process(result_data, channel)
                    else:
                        await channel.send(result_data['content'])
                self.message_queue.finished_job_registry.remove(job.id)
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
        """
        We use the bot's name as a handle to trigger commands.
        """
        return f"@{self.ai_agent.name.lower()}"
    
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
                print(message.channel.id)
                await message.channel.send('pong')
                return
            
            if message.content == f"{self.discord_handle} clear":
                await self.clear_channel(message.channel)
                return

            if message.content == f"{self.discord_handle} history":
                print('Asking for history')
                await self.list_messages(message.channel)
                return

            if message.content == f"{self.discord_handle} temporal":
                print('test')
                result = await run_workflow()
                await message.channel.send(f"Result: {result}")
                return

            response = get_response_type_for_message(self.ai_agent, message.content)
            if response.type == ResponseType.MESSAGE:
                await stream_to_discord(self.ai_agent, message)
            elif response.type == ResponseType.TOOL:
                response_text = await respond(self.ai_agent, message)
                await message.channel.send(response_text)