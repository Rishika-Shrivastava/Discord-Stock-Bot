# s_bot.py

#IMPORTS
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import pandas as pd
import plotly.express as px
import yfinance as yf
import datetime

#------------------------------------------------------

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


bot = commands.Bot(command_prefix='!')


#gets the stock updates for the day and returns a dataframe
def get_stock_df(stock):

    print('Enter get stock function')

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)

    print(yesterday)

    stock_df = yf.download(stock,
                           start=yesterday.strftime('%Y-%m-%d'),
                           end=today.strftime('%Y-%m-%d'),
                           period='1d',
                           progress=False)

    print('return stock values')

    return stock_df


#create a channel stock channel if it doesn't exist to get updates
@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='stock-channel'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        await guild.create_text_channel(channel_name, reason='need a new channel')
        #print('Channel created')


# Sends stock updates to channel. Uses get_stock_df function
@bot.command(name='get-stock-update')
async def send_eod_update(ctx, stock='TSLA', channel_name='stock-channel'):

    # print('Enter eod')
    #data transformation
    df = get_stock_df(stock)

    open_val = round(df.iloc[0][0], 6)
    high_val = round(df.iloc[0][1], 6)
    low_val = round(df.iloc[0][2], 6)
    close_val = round(df.iloc[0][3], 6)

    #establish connection and send stock update
    guild = ctx.guild
    channel = discord.utils.get(guild.channels, name=channel_name)

    print('Connection established')
    if not channel:
        await ctx.send('Channel doesn\'t exist')
    else:
        channel_id = channel.id
        await channel.send(f'Stock updates for {stock} are: \nOpen: {open_val},\nHigh: {high_val},\nLow: {low_val},'
                           f'\nClose: {close_val}')

        print(channel_id)


#get a plot for a particular stock (temporary code)
@bot.command(name='get-stock-fig')
async def generate_figure(ctx, stock='TSLA', channel_name='stock-channel'):
    #data transformation
    df = get_stock_df(stock)

    csv_val = pd.read_csv('stock_csv.csv')

    fig = px.line(csv_val, x='Datetime', y='Close', title='Closing over Datetime')
    fig.write_image('send_fig.png')

    # establish connection and send stock update
    guild = ctx.guild
    channel = discord.utils.get(guild.channels, name=channel_name)

    if not channel:
        await ctx.send('Channel doesn\'t exist')
    else:
        channel_id = channel.id
        await channel.send(file=discord.File('E:/Projects/Python/Discord Stock Bot/send_fig.png'))


#if role is not admin
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


bot.run(TOKEN)
