This is a game where people play Marco Polo with a bat

**Installation** 
1. Pip install discord.py
2. Create a bot at https://discordapp.com/developers/docs/intro
3. Download this github
4. Create botData.txt
  4a. First line is the token from discordapp
  4b. The channel ID where you want to play
  4c. The number of bats you're trying to track down
  4d. The percentage of time the bats do something random, so you can't just keep calling !mango and waiting for it to charge you.
  (currently unimplemented)
5. Run with python batBot.py

*Commands*
Help - Print this dialogue
Start - after everyone has joined type !start in the main channel
Join - type !join in the main channel
Restart - type !restart in the main channel
Get the Map - !house in a DM
Move - !move [1. North, 2. South, 3. West, 4. East], so !move 1 will move north, in a DM
Catch - !catch attempts to catch the bat, in the main channel
Attract bat - !mango in the main channel

*Objective*
Catch the bat or bats
Avoid them stealing your mangos.  
