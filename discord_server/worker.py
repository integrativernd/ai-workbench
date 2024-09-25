import os
import discord
from discord.ext import commands, tasks
from llm.respond import get_response
from config.settings import SYSTEM_PROMPT, AI_CHANNEL_ID
import django_rq
from rq.job import Job
from channels.models import Channel
from asgiref.sync import sync_to_async

description = '''
An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.
'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', description=description, intents=intents)

BOT_ID = os.getenv('BOT_ID')

AI_CHANNELS = ['ai-workbench']

# This loop will run in the background and send messages to the AI channel.
@tasks.loop(seconds=5.0)
async def background_loop():
    channel = bot.get_channel(AI_CHANNEL_ID)
    message_queue = django_rq.get_queue('default')
    for job_id in message_queue.finished_job_registry.get_job_ids():
        job = Job.fetch(job_id, connection=message_queue.connection)
        message_queue.finished_job_registry.remove(job.id)
        result = job.latest_result()
        await channel.send(result.return_value)

@commands.has_permissions(manage_messages=True)
@bot.command()
async def clear(ctx):
    """Clears the specified number of messages from the channel."""
    print('Clearing messages...')
    await ctx.channel.purge(limit=100)
    # await ctx.channel.send(f'Cleared {amount} messages.', delete_after=5)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    channel = bot.get_channel(AI_CHANNEL_ID)
    await channel.send("I'm back!")
    background_loop.start()

def run_ai_response(content):
    # response = get_message(
    #     "Simulate a useful response to the user's request as if you were able to complete this after processing in the background for an hour or so.",
    #     [
    #       {
    #           "role": "user",
    #           "content": content,
    #       }
    #     ]
    # )
    return "Background processing done"

# This listener will respond to messages in the AI channel.

@bot.event
async def on_message(message):
    print(f'{message.author}: {message.content}')

    # if message.channel.name not in active_channel_names: return
    # if message.channel.name not in AI_CHANNELS: return
    
    # Don't respond to messages from the bot itself.
    if message.author.bot: return
   
    if message.content.startswith('$'):
        await bot.process_commands(message)
    else:
        response_text = get_response(message.content)
        await message.channel.send(response_text)

def run_discord_bot():
    bot.run(os.getenv("BOT_RUN_TOKEN"))