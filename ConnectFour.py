# Connect Four Bot
# By: BentoBot02

import discord
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents(messages=True, reactions=True, invites=True, guilds=True, members=True, emojis=True)
bot = commands.Bot(command_prefix=['c4!', 'C4!'], case_insensitive=True, help_command=None, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(
    name="play",
    aliases=["p"])
async def start_command(ctx, *args):

    if len(args) == 0:
        await ctx.channel.send("<@" + str(ctx.author.id) + ">, you can't play by yourself.")
        return

    id = args[0]

    id = id.replace('<', '').replace('@', '').replace('!', '').replace('>', '')
    try:
        id = int(id)
        if ctx.guild.get_member(id) == None:
            raise ValueError
        elif id == ctx.author.id:
            await ctx.channel.send("<@" + str(ctx.author.id) + ">, you can't play against yourself.")
            return
    except ValueError:
        await ctx.channel.send("<@" + str(ctx.author.id) + ">, that user was not found.")
        return

    embedVar = discord.Embed(title="Connect Four", description="<@" + str(id) + ">, please accept or decline the game of Connect 4 with <@" + str(ctx.author.id) + "> to continue.") 
    message = await ctx.channel.send(content="<@" + str(id) + ">, would you like to play Connect Four with <@" + str(ctx.author.id) + ">", embed=embedVar)
    await message.add_reaction('❌')
    await message.add_reaction('✅')

    def acceptCheck(react, user):
        return react.message == message and (((user == ctx.author or user.id == id) and react.emoji == '❌') or (user.id == id and react.emoji == '✅'))

    try:
        reaction = await bot.wait_for('reaction_add', timeout=60, check=acceptCheck)
        reaction = reaction[0].emoji

        if reaction == '❌':
            await message.edit(embed=discord.Embed(title="Connect Four", description="Game declined.", color=discord.Color.red()))
            return

        def moveDurationCheck(m):
            return m.channel == ctx.channel and m.author == ctx.author

        await message.edit(embed=discord.Embed(title="Connect Four", description="<@" + str(ctx.author.id) + ">, input the max amount of time for each turn.\nMinimum: 5 seconds\nMaximum: 1 hour\nFormat: MM:SS"))
        
        duration = 0
        
        valid = False
        while not valid:
            message = await bot.wait_for('message', timeout=60, check=moveDurationCheck)
            messageList = message.content.split(':')
            
            try:
                minutes = int(messageList[0].strip())
                seconds = int(messageList[1].strip())
                total = minutes * 60 + seconds
                if total > 3600 or total < 5:
                    raise ValueError
                valid = True
                duration = total
            except ValueError:
                await ctx.channel.send("<@" + str(Ctx.author.id) + ">, please input a valid duration.")
                pass

        def firstCheck(react, user):
            return user.id == id and (react.emoji == '1️⃣' or react.emoji == '2️⃣')

        message = await ctx.channel.send(embed=discord.Embed(title="Connect Four", description="<@" + str(id) + ">, choose whether you will go first or second."))
        await message.add_reaction('1️⃣')
        await message.add_reaction('2️⃣')

        player1 = 0
        player2 = 0

        reaction = await bot.wait_for('reaction_add', timeout=60, check=firstCheck)
        reaction = reaction[0].emoji
        playerIDs = [0, 0]
        if reaction == '1️⃣':
            playerIDs = [id, ctx.author.id]
        else:
            playerIDs = [ctx.author.id, id]

        winnerExists = False
        #rowArray = ['🇦 ', '🇧 ', '🇨 ', '🇩 ', '🇪 ', '🇫 ', '🇬 ']
        height = 6
        width = 7
        bottomRow = "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣"
        gameBoard = [[0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]]

        playerTurn = 0

        result = 0
        firstPass = True
        while not winnerExists:
            
            playerStr = "🔴 <@" + str(playerIDs[0]) + ">\n🟡 <@" + str(playerIDs[1]) + ">"

            gameBoardStr = ""

            for row in range(0, len(gameBoard)):
                #gameBoardStr += rowArray[row]
                for column in range(0, len(gameBoard[row])):
                    if gameBoard[row][column] == 0:
                        gameBoardStr += "⚪ "
                    elif gameBoard[row][column] == 1:
                        gameBoardStr += "🔴 "
                    else:
                        gameBoardStr += "🟡 "
                gameBoardStr += "\n"
            gameBoardStr += bottomRow
            
            embedVar = discord.Embed(title="Connect Four", description=playerStr + "\n\n" + gameBoardStr)
            embedVar.set_footer(text="Input the column number to place a piece.")

            if firstPass:
                message = await ctx.channel.send(embed=embedVar)
            else:
                await message.edit(embed=embedVar)

            def playerCheck(m):
                return m.channel == ctx.channel and m.author.id == playerIDs[playerTurn]

            valid = False
            while not valid:
                try:
                    givenCoord = await bot.wait_for('message', timeout=duration, check=playerCheck)
                    givenCoord = givenCoord.content
                    givenColumn = int(givenCoord[0]) - 1
                    
                    if givenColumn < 0 or givenColumn > 6 or gameBoard[0][givenColumn] != 0:
                        raise ValueError
                    
                    if gameBoard[height - 1][givenColumn] == 0:
                        gameBoard[height - 1][givenColumn] = playerTurn + 1
                    else:
                        row = 0
                        while gameBoard[row][givenColumn] == 0:
                            row += 1
                        gameBoard[row - 1][givenColumn] = playerTurn + 1

                    valid = True

                except (IndexError, ValueError) as e:
                    pass

                except asyncio.TimeoutError:
                    playerStr = "<@" + str(playerIDs[(playerTurn + 1) % 2]) + "> won by timeout."
                    if playerIDs[(playerTurn + 1) % 2] == 0:
                        embedVar = discord.Embed(title="Connect Four", description=playerStr + "\n\n" + gameBoardStr, color=0xDD2E44)
                        embedVar.set_footer(text="Input the column number to place a piece.")
                        await message.edit(embed=embedVar)
                    else:
                        embedVar = discord.Embed(title="Connect Four", description=playerStr + "\n\n" + gameBoardStr, color=0xFDCB58)
                        embedVar.set_footer(text="Input the column number to place a piece.")
                        await message.edit(embed=embedVar)
                    return

            # check rows
            result = checkRows(gameBoard, height, width)
            if result != 0:
                break

            # check columns
            result = checkColumns(gameBoard, height, width)
            if result != 0:
                break

            # check diagonals
            result = checkDiagonals(gameBoard, height, width)
            if result != 0:
                break

            allFilled = True
            for column in range(0, width):
                if gameBoard[0][column] == 0:
                    allFilled = False
                    break

            if allFilled:
                break

            playerTurn = (playerTurn + 1) % 2

        gameBoardStr = ""
        for row in range(0, len(gameBoard)):
            #gameBoardStr += rowArray[row]
            for column in range(0, len(gameBoard[row])):
                if gameBoard[row][column] == 0:
                    gameBoardStr += "⚪ "
                elif gameBoard[row][column] == 1:
                    gameBoardStr += "🔴 "
                else:
                    gameBoardStr += "🟡 "
            gameBoardStr += "\n"
        gameBoardStr += bottomRow

        if result == 1:
            playerStr = "<@" + str(playerIDs[playerTurn]) + "> is the winner!"
            embedVar = discord.Embed(title="Connect Four", description=playerStr + "\n\n" + gameBoardStr, color=0xDD2E44)
            embedVar.set_footer(text="Input the column number to place a piece.")
            await ctx.channel.send(embed=embedVar)
            return

        elif result == 2:
            playerStr = "<@" + str(playerIDs[playerTurn]) + "> is the winner!"
            embedVar = discord.Embed(title="Connect Four", description=playerStr + "\n\n" + gameBoardStr, color=0xFDCB58)
            embedVar.set_footer(text="Input the column number to place a piece.")
            await ctx.channel.send(embed=embedVar)
            return

        else:
            playerStr = "<@" + str(ctx.author.id) + "> and <@" + str(id) + "> tied!"
            embedVar = discord.Embed(title="Connect Four", description=playerStr + "\n\n" + gameBoardStr, color=0xE6E7E8)
            embedVar.set_footer(text="Input the column number to place a piece.")
            await ctx.channel.send(embed=embedVar)
            return

    except asyncio.TimeoutError:
        await message.edit(embed=discord.Embed(title="Connect Four", description="Game expired.", color=discord.Color.red()))
        return


def checkRows(gameBoard, height, width):
    for row in range(0, height):
        player1Connect = 0
        player2Connect = 0
        for column in range(0, width):
            if gameBoard[row][column] == 0:
                player1Connect = 0
                player2Connect = 0
            elif gameBoard[row][column] == 1:
                player1Connect += 1
                player2Connect = 0
            else:
                player1Connect = 0
                player2Connect += 1
            if player1Connect >= 4:
                return 1
            elif player2Connect >= 4:
                return 2
    return 0

def checkColumns(gameBoard, height, width):
    for column in range(0, width):
        player1Connect = 0
        player2Connect = 0
        for row in range(0, height):
            if gameBoard[row][column] == 0:
                player1Connect = 0
                player2Connect = 0
            elif gameBoard[row][column] == 1:
                player1Connect += 1
                player2Connect = 0
            else:
                player1Connect = 0
                player2Connect += 1
            if player1Connect >= 4:
                return 1
            elif player2Connect >= 4:
                return 2
    return 0

def checkDiagonals(gameBoard, height, width):
    for row in range(0, height):
        player1Connect = 0
        player2Connect = 0
        diagonalColumn = 0
        diagonalRow = row
        while diagonalColumn < width and diagonalRow < height:
            if gameBoard[diagonalRow][diagonalColumn] == 0:
                player1Connect = 0
                player2Connect = 0
            elif gameBoard[diagonalRow][diagonalColumn] == 1:
                player1Connect += 1
                player2Connect = 0
            else:
                player1Connect = 0
                player2Connect += 1
            if player1Connect >= 4:
                return 1
            elif player2Connect >= 4:
                return 2
            diagonalRow += 1
            diagonalColumn += 1

    for row in range(0, height):
        player1Connect = 0
        player2Connect = 0
        diagonalColumn = 0
        diagonalRow = row
        while diagonalColumn < width and diagonalRow >= 0:
            if gameBoard[diagonalRow][diagonalColumn] == 0:
                player1Connect = 0
                player2Connect = 0
            elif gameBoard[diagonalRow][diagonalColumn] == 1:
                player1Connect += 1
                player2Connect = 0
            else:
                player1Connect = 0
                player2Connect += 1
            if player1Connect >= 4:
                return 1
            elif player2Connect >= 4:
                return 2
            diagonalRow -= 1
            diagonalColumn += 1

    for row in range(0, height):
        player1Connect = 0
        player2Connect = 0
        diagonalColumn = width - 1
        diagonalRow = row
        while diagonalColumn >= 0 and diagonalRow >= 0:
            if gameBoard[diagonalRow][diagonalColumn] == 0:
                player1Connect = 0
                player2Connect = 0
            elif gameBoard[diagonalRow][diagonalColumn] == 1:
                player1Connect += 1
                player2Connect = 0
            else:
                player1Connect = 0
                player2Connect += 1
            if player1Connect >= 4:
                return 1
            elif player2Connect >= 4:
                return 2
            diagonalRow -= 1
            diagonalColumn -= 1

    for row in range(0, height):
        player1Connect = 0
        player2Connect = 0
        diagonalColumn = width - 1
        diagonalRow = row
        while diagonalColumn < width and diagonalRow < height:
            if gameBoard[diagonalRow][diagonalColumn] == 0:
                player1Connect = 0
                player2Connect = 0
            elif gameBoard[diagonalRow][diagonalColumn] == 1:
                player1Connect += 1
                player2Connect = 0
            else:
                player1Connect = 0
                player2Connect += 1
            if player1Connect >= 4:
                return 1
            elif player2Connect >= 4:
                return 2
            diagonalRow += 1
            diagonalColumn -= 1
    return 0

bot.run(TOKEN)