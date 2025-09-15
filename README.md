# Fictive

A state-machine based interactive fiction tool.

I'm sure what the world truly needs is a new engine for making text adventures that is more stripped down and limited than previous engines, but offers an approach that is both more complicated than simple Choose-Your type games, more limited than Inform-type games, and entirely (and stubbornly) text-based only.

## Key Features
* Develop games in a simple, declarative syntax
* Allow for code-reuse within a game
* Support complex commands and interactions
* Give the game "memory" with a state bag and a templating system
* Ensure games can be easily tested with a simple script

## Current Status
* Simple library loader lets you interact with a collection of games
* Games support states, nested sub-states, a variety of transition types
* Game dev syntax is pretty much solidified
* Testing scripts for validating games
* Game dev *tools* still need some work

## Setup
This uses `uv`, so you should be able to do a `uv sync` to get up and running.

## Running
`uv run python -m fictive <path to game folder>` runs the game UI in a terminal. The game folder should be a folder containing one or more Fictive games.

`uv run textual serve fictive <path to game folder>` runs the game engine in a web server, instead, allowing you to host games on the web.

The supplied `example` game represents a simple example game with a handful of states to navigate through. It uses substates, the statebag, and basically demos the core things you can do with Fictive.

In addition to that game, there is also a `tutorial` game, which is both an example game, *and* an interactive instructional guide to working with Fictive. If you want to learn to write Fictives, this is a good starting point.

You can also run the unit tests: `uv run python -m unittest fictive.tests`. The unit tests are currently quite incomplete.

If you want to learn about writing Fictives, check out the [Dev Guide](DevGuide.md)

# An Example Play: game.yaml
```
You are in a mysterious room. It's hard to say what's so mysterious about it.
That is what's so mysterious.

There is a switch here. It is in the off position.

> go
In this room, there is a large archway. You can easily walk through it, but
nothing happens. Large cables run to the archway. It seems to need power.

> back
You are in a mysterious room. It's hard to say what's so mysterious about it.
That is what's so mysterious.

There is a switch here. It is in the off position.

> switch
You are in a mysterious room. It's hard to say what's so mysterious about it.
That is what's so mysterious.

The switch is on. You hear a faint humming sound.

> go
The cables hum with the power coursing through them. The archway crackles,  its
energy forming a hazy portal within it.

> check power
You remember turning the switch on.
> go
You have stepped through the archway. Every atom in your body is disassembled
and reassembled. You are dead. You live on. Are you the same person? You do not
know. You have exited the maze.

Game Over!
```
