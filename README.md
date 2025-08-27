# Fictive

A state-machine based interactive fiction tool. Still in an early draft state, not usable by anyone else. Everything is likely to change.

Also: I'm sure what the world truly needs is a new engine for making text adventures that is more stripped down and limited than previous engines.

## Current Status
Parses a collection of YAML files into a state machine. Then provides an interactive prompt where users provide textual input, which gets evaluated and causes the state machine to transition to new states. 

## Setup
This uses `uv`, so you should be able to do a `uv sync` to get up and running.

## Running
`uv run python -m fictive <path to game folder>`

The supplied `example` folder represents a simple example game with a handful of states to navigate through. It uses substates, the statebag, and basically demos the core things you can do with Fictive.

You can also run the unit tests: `uv run python -m unittest fictive.tests`. The unit tests are currently quite incomplete.

## Why YAML?
Look, the worst feature of YAML is its incredibly complex way of handling links. But for something like this, being able to define things in one place, and then link to those definitions? REALLY COOL. Really useful.


# The Fictive YAML Syntax
A Fictive YAML file MUST be a YAML array. Before we get into the details, there are two core ways to organize your YAML.

## File Structure
### The Single File Approach
You can build your entire game into a single YAML file. As these files will tend to get long, it may not be the easiest or cleanest way to do it, but it's certainly a good way to get started.

### The Directory Approach
To make it easier to modularize your game, you can also use a directory. Inside this directory, you will have multiple files which describe your game, and you **must** have a `manifest.yaml`. This file must be an array, and each entry contains the relative path to those files. The order you place the files in the manifest matters, as the game will be loaded in that sequence.

## Making Fictive Games

When designing a YAML game, there are a few key concepts.

The first is the state machine. This is the various things that can happen in the game. States don't have a direct mapping to anything concrete- they're not rooms or pages or scenes. They're best thought of as important points in the fiction, where the story can branch.

The second is the state bag. The state bag is a collection of key/value pairs that can be modified as the game progresses. This can be used to represent things which don't map neatly to a state machine, like a character's inventory, or whether they flipped a switch earlier in the game. It's an arbitrary set of global variables, essentially.

Finally, the game loop is important. States only transition in reaction to user input. The loop goes thus:

* We output the description of the current state and substates
* The user types a command and hits enter
* We check to see if that input causes a transition to a new state
* If it does, we transition to that new state

## A Machine
A machine contains states and transitions.

### States
States are defined thus:
```yaml
state:
    tag: myTag
    description: some descriptive text
    on_enter: someFunction
    on_exit: someFunction
    sub_machine: someMachine
```

`tag` and `description` are required. `on_*` is optional. `sub_machine` is optional. Se later sections for how to use those fields.

`tag` is the handle that will be used to refer to states when performing transitions.

### Transitions
Transitions are defined thus:

```yaml
transition:
    from: originStateTag
    to: destStateTag
    condition: someFunction
```

When we are on the `from` state, and the condition evaluates to true, the game will transition to the `to` state.

### Functions
Functions, broadly, are meant for two purposes. One is to control transitions. The other is to change the state_bag or other flow elements as part of an `on_*` event.

#### Condition Functions
The game supports the following condition functions:

```yaml
condition:
    on_match:
        matcher: regexHere
```

This transitions if a user's input matches the regex.

```yaml
condition:
    on_key:
        key: keyName
        value: value
```

This transitions if the state bag contains a key that equals that value.

```yaml
condition:
    - on_gt:
        key: keyName
        value: value
    - on_lt:
        key: otherKeyName
        value: otherValue
```

The `on_gt` and `on_lt` functions permit a transition when a greater than/less than comparison passes. Should be used with the `inc`/`dec` functions. Attempts to do a numeric comprarison first, but failing that does a textual comparison. The key should exist, or this will fail.

```yaml
condition: always
```

This transitions all the time, regardless of user input.

You can have an array of checks inside of a `condition`. All the checks must pass for the `condition` to cause a transition.

For example:

```yaml
condition:
    - on_match:
        matcher: someRegex
    - on_key:
        key: keyName
        value: value
```

If the input matches the regex, and the state bag contains a key equal to that value, we transition to the next state.

#### Event functions
Stase also have `on_enter` and `on_exit` events. These events permit the invocation of some functions as well.

```yaml
on_enter: revert
```

This will enter the new state, print its result, and then immediately revert back to the previous state. This is useful for creating states which represent health screens, or inventory screens, for example.

```yaml
on_enter:
    set_key:
        key: keyName
        value: value
```

This sets a key (which can then be checked by the `on_key` transition function).

```yaml
on_enter:
    inc:
        key: keyName
on_exit:
    dec:
        key: keyName
```

The `inc` and `dec` functions will increment or decrement a counter. You should initialize the counter as part of your statebag.

Much like transition functions, event functions can also be combined, so a single `on_enter` or `on_exit` event can have multiple entries, e.g.:

```yaml
on_exit:
    - set_key:
        key: keyName
        value: value
    - set_key:
        key: otherKey
        value: otherValue
    - revert
```

### Defining a Machine
With all this, we can now define a machine.

The basic outline of the YAML is:

```yaml
machine:
    startTag: someStateTag # we start the game in this state
    endTag: endStateTag # this represents a game over screen; we exit on this state
    states:
        # a list of states goes here
    transitions:
        # a list of transitions goes here
    global_transitions:
        # a list of transitions goes here
```

### Defining the Game
There are two YAML entries which define the game. The first is `execute` which wraps a machine, e.g.:

```yaml
- execute:
    machine:
        # machine definition here
```

This tells Fictive which specific state machine represents the main game (as you may have sub-state machines; more on that in a moment).

You may also have a `state_bag: tag, which allows you to initialize your state bag to a certain set of key/value pairs, e.g.:

```yaml
- state_bag:
    key: value
    otherKey: otherValue
```

All in all, this means a full game could be defined thus:

```yaml
- execute:
    machine:
        # machine definition here
- state_bag:
    someKey: defaultValue
```

### Organizing Your File with YAML Links
Writing a game that way would be absolutely cumbersome. It's better to organize your file using YAML links. So, for example, you may do this instead:

```yaml
- myMainMachine:
    - machine: &main
        # machine definition here
-execute: *main
```

In YAML, when you tag a key with `&label`, that creates an anchor. You can reference that anchor using `*label`, which is roughly equivalent to copy/pasting the information from that anchor.

This means that you can define various states elsewhere in your file, and then embed them into your machine using links, e.g.:

```yaml
- coreStates:
    - state: &entry
        tag: entry
        description: The game has started.
- machine: &main
    states:
        *entry
    startTag: entry
```

The best way to organize your files is up to you, and will likely be different for every game. The supplied `game.yaml` shows some examples of how to do this.

# Notes
Again, this is wildly unfinished. I make no promises that the syntax is fixed. I make no promises about which features will remain and which will be changed. I intend to completely gut the current game loop at some point.

# An Example Play: game.yaml
```
╰─➤  python -m fictive game.yaml
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
