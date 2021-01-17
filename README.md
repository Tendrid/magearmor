# magearmor
Python plugin system for magearmor.com minecraft server
/gamerule doFireTick false

# Battles:Modified
Every damage event in the game now has a set of carrier damages, which means when a weapon does 5 damage, it can be "piercing" damage (such as an arrow).  A weapon strike can have one, or no carrier types from one of each of the following damage classes:

###### Physical
* Bludgeoning
* Hacking
* Slashing
* Piercing

###### Elemental
* Acid
* Fire
* Cold
* Energy

###### Magic
* Necrotic
* Divine
* Arcane

All armor items now have modifiers built in, which means they can react to each carrier strike differently.  This means a piece of armor with high defence against piercing damage will take far less damage from an arrow than a piece of armor with low (or possibly even negative) defence.  Mobs in the game also have a natural armor.  This means, if you try to fight a monster with high piercing defence (such as a skeleton, because, you know, they're just bones, right?) then your arrows will do very little damage, however, if you were to attack them with a "Bludgeoning" item, it would be very effective.



# Towns

Players have the ability to claim plots (Minecraft chunks) in the game, as long as the plots are adjacent.  By default, players can claim up to 9 plots, however, the more they build in their town, the more xp they gain, which allows them to claim more plots, and in time, "outpost" plots, which let them claim a non adjacent plot, to start a new settlement.

You can invite other players to join your town, and then assign them a rank.  The default ranks are Peasant, Citizen, and Lord, but you can rename them.  Each rank can then be granted permissions in your town.  The currently supported permissions are:

* pve: Killing animals in town
* build: placing or breaking blocks
* doors: open doors and hatches
* chests: open chests and add/remove items
* buttons: click buttons
* switches: flip switches
* plates: use pressure plates

All players can have their own town, as well as be a member of any number of other towns.
