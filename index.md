# Magearmor Minecraft Overview

Magearmor.com is a community minecraft server for the [Tinakitten](https://www.twitch.tv/tinakitten) discord. 

## Plugins

### Towns
The towns plugin allows everyone to protect their build area.  Once you create a town, you can add plots to it (each plot is a minecraft chunk, 16x16 blocks).  All towns start with 9 plots they can claim, but you can gain more in the future.  All plots must be adjacent to a plot already claimed.

`/towns-create`
This command will create a town for you, but it will not claim any spaces.  Its simply where you get started

`/towns-name <town name>`
All towns start with the name "Village".  To rename your town, use `/towns-name My New Name`, which would rename your town to "My New Name".  You can do this as often as you'd like.

`/towns-claim`
When you use this command, it will immediately claim the chunk in which you are standing.  If the chunk is not adjacent to a chunk already claimed, you will see an error message, and the chunk will not be claimed.

`/towns-unclaim`
using this will unclaim a plot in your town.

`/towns-permissions (<permission_name> <rank_name>)`
This command, when typed on its own, will list your towns current permission settings.  If you provide this command with a permission name, and a new rank, the permission will change.

`/towns-ranks (<rank_name> <new_rank_name>)`
This command, when types on its own, will list your towns current ranks.  If you provide this command with a rank name, and a new name, it will change that ranks name.

`/towns-member-add <playername>`
using this command will add the player to your town.

`/towns-member-remove <playername>`
remove a player from your town

`/towns-member-rank (<playername>) (<rankname>)`
This sets the players rank in your town, which defines what they can and cannot do.  If you use this command without the playername or rank, you'll get a help message letting you know which ranks you can use.  If you use it with just the playername, you will see the players current rank.
