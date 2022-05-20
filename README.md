# protonDButility
A python script that lets you search the steam database for games and check their linux compatability using ProtonDB.

# Install
Just clone the script and either add it to your dotfiles as an alias, or build it into a binary.

# Usage
By default, the script comes with a handful of commands <br />
To run the script, simply do `python protonDButility.py` followed up by the potential arguments.<br />
By default, to search for a specific game, write the name of the game as an argument.<br />
`--help` - Prints a message showing the capabilites of protonDButility.<br />
--version` - Prints the version of the script.<br />
`--refresh` - Manually force a database refresh.<br />
`--database` - Displays the amount of entries in the current local steam database.<br />
`--search` - Search for a game with a partial name, displays all games matching the search term.<br />
`--installed` - Check the compatability of installed steam games.<br />

# Todo
I'll fix how the database formatting works, right now, `python protonDB.py --search` results in all lowercase text.
