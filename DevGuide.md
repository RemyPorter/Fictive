# Writing Fictive Games
## Introduction
First, launch the game library and play the Tutorial game, which teaches you the basics of writing a Fictive.

## The Big Ideas
### State Machines
Fictive views your interactive fiction game as a state machine. Think of a Choose-Your style book: each page in that book is a "state", and from that page, you can "transition" to other states.

Fictive is slightly different, in that the user types in their choices, which may be expressed in terms of commands you make up. This allows a lot more flexibility in both design and interaction.

### YAML
You will define your state machine as a set of YAML files. YAML is a simple markup language with some powerful features that makes it an ideal choice for this kind of thing. [Wikipedia](https://en.wikipedia.org/wiki/YAML) is a good starting point for learning more about YAML.

### Regular Expressions
When defining commands the user can enter, you will need to use regular expressions (regex). The [theory](https://en.wikipedia.org/wiki/Regular_expression) is useful, as is the specifics on [Python regex](https://docs.python.org/3/howto/regex.html#regex-howto). 

## Getting Started
To start writing a Fictive, you must do the following:
* Create a folder inside of a game directory
* Create a `manifest.yaml` file
* Create at least one other `yaml` file which is where you'll define your game.

E.g:

```
games/
    my_new_game/
        manifest.yaml
        game.yaml
```

### The Manifest
The Manifest provides a set of metadata about your game. It is a YAML dictionary. It should contain these keys:

```yaml
title: The Title of Your Game
author: This is you!
slug: A quick synopsis of your game
files:
    - a list
    - of the files
    - in this game
    - order matters!
tests:
    - a list
    - of files
    - containing tests
```

### Game Files
The game files will be merged into a single file, and then parsed. This is to better support YAML references across files. More on that later.

Inside of those files, you need to have an `execute` key, which will contain the state machine that drives your game. You may also have a `state_bag` key, which lets you initialize your state bag variables.

### A Simple Game
A game is made up of states and transitions. 

#### States (the basics)
States must have a `tag` and a `description`.

You could define a series of states like so:

```yaml
my_game_states: &my_game_states # this is a YAML reference, it lets us refer to this section later
    - state:
        tag: start
        description: The start of a game
    - state:
        tag: end
        description: The end of a game
```

#### Transitions (the basics)
Transitions define how we move `from` each state `to` the next. Transitions have a `condition` key, which lets us define under what conditions a transition may fire. The one you'll use the most is the `match` condition, which uses a regex to parse user input. For example:

```yaml
my_game_trans: &my_game_trans
    - transition:
        from: start
        to: end
        condition:
            match: (next|go|leave)
```

#### Putting it Together
Create a folder `test` under `games`. In that folder, create a `manifest.yaml`, and put the following:

```yaml
title: My Simple Game
author: <Your Name>
slug: A simple game to learn Fictive
files:
    - main.yaml
```

In the same folder, add `main.yaml`

Copy the `my_game_states` and `my_game_trans` into it. Then add:

```yaml
main_machine: &main # define your machine
    startTag: start # specify where this state machine starts
    endTag: end # optionally, specify where it ends
    states:
        - *my_game_states
    transitions:
        - *my_game_trans
execute: *main # tell Fictive to start the game by executing it
```

Launch Fictive and you should see your game in the menu. Load it and play.

If for some reason, your game doesn't work as expected- it gives you an error when you try and load the game- don't fret.

Run `uv python -m fictive games -t test`. That will at least give you some errors about what went wrong. The errors are not, at this time, very good. I'm sorry.

## Advanced Fictive
### Triggers and the State Bag
The state bag gives your game memory. User input can be recalled in future states, and we can create counters and other variables. For example, let's say you have a lever in your game. You wish to track if the user has pulled the lever or not.

```yaml
lever_states: &lever_states
    - state:
        tag: lever_up
        description: |
            There is a lever here. It is up in the "on" position.
        on_enter:
            set:
                key: lever
                value: on
    - state:
        tag: lever_down
        description: |
            There is a lever here. It is in the "off" position.
        on_enter:
            set:
                key: lever
                value: off
```

The `on_enter` trigger allows you to manipulate the state bag. Here you see the use of `set`.

#### Printing Statebag Entries
You can include state bag entries in your `description` (or any where else you control text output). To do so, simply reference the key in a future state.

```yaml
- state:
    tag: seen_lever
    description: You remember putting the lever in the {lever} position.
    on_enter: revert # more on this later
```

#### Transitions and the State Bag
Once you've set a key in an `on_enter`, you can check that key as part of a transition. For example, if in another state, a secret door is only available.

```yaml
- transition:
    from: big_room
    to: secret_door
    condition:
        eq:
            key: lever
            value: on
```

If the user is in the big room and they hit enter, it will move them to the secret door. Otherwise, some other transition may fire.

The `match` condition can also add state bag entries using regex capture groups.

```yaml
- transition:
    from: pick_weapon
    to: weapon_picked
    condition:
        match: 
            matcher: (get|take|use) (axe|sword|whip)
            keys: [_, player.weapon]
```

Each capture group can be saved as a key. The `_` key is for values we don't actually want to capture. Depending on what the user entered, "axe", "sword", or "whip" will be stored in "player.weapon". Future states and transitions will be able to leverage that.

You can have an array of functions in your `condition` (notated in YAML by putting a `- ` at the start of each line).

```yaml
condition:
    - eq:
        key: key
        value: value
    - match: user input
```

All conditions must pass for the condition to pass. This is an `and` operation, not an `or`.

##### Condition Reference
###### Always
Using `condition: always` creates a transition which will always fire when the user hits enter. Useful for breaking up text across multiple screens, and moving through game sections with no meaningful choices.

Good games use this sparingly!
###### Match
The match condition can be executed with a single parameter, thusly: `match: some regex`

Or it accepts two parameters. The `matcher` and the `keys`. This allows you to save user input into your state bag.

```yaml
match:
    matcher: some regex (with capture)
    keys: [captured values]
```

###### Eq
Compares a key against a value, or two keys, and allows a transition to pass only if they're equal.

```yaml
eq: # compare a key against a value
    key: someKey
    value: someValue
# or
eq: # compare a key against another key
    key: someKey
    other: someOtherkey
```

###### Gt, Gte, Lt, Lte
In addition to `eq`, there are `gt` (greater than), `gte` (greater than or equal), `lt` (less than) and `lte` (less than or equal) functions. They operate the same way as `eq`, but do what the name suggests.

All comparsions will do a numeric comparison if you've stored a numeric value in the key, otherwise it's a lexical (text based) comparison.


#### Trigger Reference
##### Revert
`revert` takes no parameters. When use in an `on_enter`, this state will become a "transient"- it will print a message, but not otherwise update the game.

Example:

```yaml
- state:
    tag: help
    description: This is a help message
    on_enter: revert
```

##### Set
`set` takes two parameters: the key to set, and the value. 

```yaml
set:
    key: someKey
    value: someValue
```

##### Inc/Dec
`inc` and `dec` can increment or decrement a single key. They only take one parameter, and can be invoked thus:

```yaml
inc: someNumericKey
```

These only work on numeric values. They combine well with the comparison conditions in transitions to make flexible transitions.

##### (Sub|Trans)?Banner
There are three banner functions, which control the banner displayed on the various screen areas. `banner` sets the text on the main state pane. `subbanner` sets the text on the substate pane, only visible in states with substates. Finally, `transbanner` sets the banner on transient states- states which were `revert`ed. These states act as pop-up messages, useful for displaying help.

```yaml
banner: My banner text
```

These functions do support templates, so you can access state bag variables.

```yaml
banner: You Have a {player.weapon}
```

### Sub States
You can create multiple machines in your game. For example here's a simple machine:

```yaml
lever_machine: &lever_machine
    states:
        - state:
             tag: lever_on
             description: The lever is on.
             on_enter:
                set:
                    key: lever
                    value: on
        - state:
            tag: lever_of
            description: The lever is off.
            on_enter:
                set:
                    key: lever
                    value: off
    transitions:
        - transition:
            from: lever_on
            to: lever_off
            condition:
                match: (flip|switch|lever)
        - transition:
            from: lever_off
            to: lever_on
            condition:
                match: (flip|switch|lever)
    startTag: lever_on
```

Now, we could have another state, in another machine, that might look like this:

```yaml
- state:
    tag: lever_room
    description: In the center of this room is a gigantic lever.
    sub_machine: *lever_machine
```

This will display both the main state description and the sub state description. If you type `flip`, the lever will change positions. The main state may have its own transition commands.

This allows you to create mini-games and puzzles within your main game. Sub-state machines can behave just like full state machines. They just are attached to a single state. Think of it like a Choose-Your book *inside* a single page of a Choose-Your book.

NB: Sub-state machines and state machines share the same statebag. Be careful when naming keys, as you may end up in situations where two different parts of your game use the same keys.


### Organizing
It's best to split your game across multiple files, and then reference the files in your `manifest.yaml`. The important fact here is that those files are loaded in order, and references have to be declared (`&some_name` declares a reference) before they're used (`*some_name` links a reference).

### Testing
Testing your game is important! You can create simple test scripts in YAML like so:

```yaml
my_test:
    - input: Some simulated user input
    - assert: 
        - tag: some_state_tag
        - eq:
            key: someKey
            value: someValue
```

A test starts with a key (`my_test`, above) and then is an array of statements. You can have any number of test files alongside your game files in your game folder.

In your manifest, add a `tests` key, and specify where your test files are loaded:

```yaml
tests:
    - tests/file1.yaml
    - tests/file2.yaml
```

You can have as many test scripts as you like in a single file- the key value you use (`my_test` above) will differentiate between them.

To run your tests, run:

```bash
uv run python -m fictive path_to_games -t your_game_folder
```

It's also helpful to use this command even if you haven't written any tests, because if you have errors in your YAML, this will provide better and more useful output.

# Conclusion
This covers everything you need to know about writing Fictive games. Check the `example` and `tutorial` games out to see how they were implemented. 

