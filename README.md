# protonDButility
A python script that lets you search the steam database for games and check their linux compatability using ProtonDB.

# Install
Just clone the script and either add it to your dotfiles as an alias, or build it into a binary.

# Usage
By default, the script comes with a handful of commands
To run the script, simply do `python protonDButility.py` followed up by the potential arguments.
By default, to search for a specific game, write the name of the game as an argument.
`--help` - Prints a message showing the capabilites of protonDButility
--version` - Prints the version of the script.
`--refresh` - Manually force a database refresh.
`--database` - Displays the amount of entries in the current local steam database.
`--search` - Search for a game with a partial name, displays all games matching the search term.
`--installed` - Check the compatability of installed steam games.

# Todo
I'll fix how the database formatting works, right now, `python protonDB.py --search` results in all lowercase text.
