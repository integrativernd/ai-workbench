from discord.ext import commands, tasks
import discord
from llm.respond import respond, tool_registry
import django_rq
from rq.job import Job
from asgiref.sync import sync_to_async
from llm.anthropic_integration import stream_to_discord, get_basic_message
from llm.response_types import get_response_type_for_message, ResponseType
from temporal_app.run_workflow import get_temporal_client
from temporalio.client import WorkflowExecutionStatus


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
    
    @sync_to_async
    def save_workflow_result(self, result):
        if not result:
            return

        self.ai_agent.add_job(result.id)
        print(f"Saving result id: {result.id}")
        return result

    @sync_to_async
    def remove_job(self, job_id):
        if not job_id:
            return

        self.ai_agent.remove_job(job_id)
        print(f"Saving result id: {job_id}")
        return job_id

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
    
    
    @sync_to_async
    def refresh_ai_agent(self):
        self.ai_agent.refresh_from_db()
    
    @tasks.loop(seconds=3)
    async def background_loop(self):
        """
        A background task that runs every 5 seconds.
        It processes finished jobs from the message queue and sends the results to the appropriate Discord channel.
        """
        if not self.is_active:
            await self.close()
            return

        channel = self.get_channel(1286417414669602878)
        if not channel:
            return

        await self.refresh_ai_agent()

        job_ids = self.ai_agent.job_ids
        if len(job_ids) == 0:
            return
        
        print(f"I have jobs to process: {job_ids}")
        temporal_client = await get_temporal_client()

        for job_id in job_ids:
            print(f"Processing workflow: {job_id}")
            workflow = None
            result = None
            try:
                workflow = temporal_client.get_workflow_handle(job_id)
                print(f"Workflow: {workflow}")
                description = await workflow.describe()
                if description.status == WorkflowExecutionStatus.COMPLETED:
                    result = await workflow.result()
                    print(f"Workflow result: {result}")
                    await channel.send(str(result))
                    await self.remove_job(job_id)
                elif description.status == WorkflowExecutionStatus.TERMINATED:
                    print(f"Workflow terminated: {job_id}")
                    await self.remove_job(job_id)
                elif description.status == WorkflowExecutionStatus.FAILED:
                    print(f"Workflow failed: {job_id}")
                    await self.remove_job(job_id)
            except Exception as e:
                print(f"Error getting workflow result: {job_id}")
                await self.remove_job(job_id)
               
            # Check if the workflow is still running
            # if workflow:
            #     description = await workflow.describe()
            #     print(f"Workflow description: {description}")
            #     print(f"Workflow: {workflow}")
            #     try:
            #         result = await workflow.result()
            #         print(f"Workflow result: {result}")
            #     except Exception as e:
            #         print(f"Error getting workflow result: {e}")
            # # Check if the workflow has finished
            # if result:
            #     print(f"Result: {result}")
            #     # print(f"Channel: {channel}")
            #     await channel.send(result)
            #     # Remove the job from the queue
            #     await self.remove_job(job_id)
            print("\n")
    
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

        print(f'channel: {message.channel} - {message.channel.id}')
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

            response = None
            try:
                response = get_response_type_for_message(self.ai_agent, message.content)
            except Exception as e:
                print(f"Error processing message: {e}")
                await message.channel.send(f"Error processing message: {str(e)}")
                return

            if not response:
                # NOTE: This really would only happen if the base LLM provider is
                # is having an issue. We should log this and alert the user.
                await message.channel.send(f"Sorry, I don't understand that command.")
                return
            
            if response and response.type == ResponseType.MESSAGE:
                await message.channel.send('DEBUG: STREAM FROM BASE LLM')
                await stream_to_discord(self.ai_agent, message)
                return

            if response and response.type == ResponseType.TOOL:
                await message.channel.send('DEBUG: USE TOOL')
                response_text = await respond(self.ai_agent, message)
                await message.channel.send(response_text)
                return