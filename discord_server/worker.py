import os
import discord
from discord.ext import commands, tasks
from llm.respond import get_response
from config.settings import SYSTEM_PROMPT, AI_CHANNEL_ID, IS_HEROKU_APP
import django_rq
from rq.job import Job
import json
from channels.models import Channel, Message
from asgiref.sync import sync_to_async, async_to_sync
from ai_agents.models import AIAgent

description = '''
An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.
'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', description=description, intents=intents)

# BOT_ID = os.getenv('BOT_ID')

AI_CHANNELS = ['ai-workbench']

def run_message_creation(message_data):
    message_data = json.loads(message_data)
    channel = Channel.objects.get(channel_name=message_data['channel'])
    message = Message(
        channel=channel,
        content=message_data['content'],
        author=message_data['author']
    )
    message.save()

# This loop will run in the background and send messages to the AI channel.
@tasks.loop(seconds=5.0)
async def background_loop():
    print('background_loop')
    # channel = bot.get_channel(AI_CHANNEL_ID)
    # message_queue = django_rq.get_queue('default')
    # for job_id in message_queue.finished_job_registry.get_job_ids():
    #     job = Job.fetch(job_id, connection=message_queue.connection)
    #     message_queue.finished_job_registry.remove(job.id)
    #     result = job.latest_result()
    #     await channel.send(result.return_value)
        # queue = django_rq.get_queue('low')
        # queue.enqueue(run_message_creation, data)

@commands.has_permissions(manage_messages=True)
@bot.command()
async def clear(ctx):
    """Clears the specified number of messages from the channel."""
    print('Clearing messages...')
    await ctx.channel.purge(limit=10)
    print('Messages cleared.')
    # await ctx.channel.send(f'Cleared {amount} messages.', delete_after=5)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    # channel = bot.get_channel(AI_CHANNEL_ID)
    # await channel.send("I'm back!")
    # background_loop.start()

# This listener will respond to messages in the AI channel.
@bot.event
async def on_message(message):
    print(f'{message.author}: {message.content} {message.channel}')
    # Don't respond to messages from the bot itself.
    if message.author.bot:
        return
    elif message.content.startswith('$'):
        await bot.process_commands(message)
    else:
        response_text = get_response(message.content)
        await message.channel.send(response_text)

    message_data = json.dumps({
        "content": message.content,
        "author": str(message.author),
        "channel": str(message.channel)
    })
    queue = django_rq.get_queue('low')
    queue.enqueue(run_message_creation, message_data)

def run_discord_bot():
    ai_agents = AIAgent.objects.filter(is_active=True)
    
    for ai_agent in ai_agents:
        bot.run(ai_agent.bot_token)
    