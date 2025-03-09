

REQUIREMENTS 

This program uses Python3 and numpy.
It is a commandline program. Thus, when running one should see a terminal with a "cmd>>" showing. One then types in commands.

For those not used to python, I recomend installing the "Anaconda" distribution. It will come with all needed things. (Just google "python Anaconda" and follow install instructions)



BASIC USAGE / QUICK START


The program reads-in information about Warhammer 40K units from the "units" folder. These files are text files and should be easy to edit. More info about this is below. A few Chaos Space Marine units are provided.

One can then type commands to test how much damage one unit can do to anouther. It is also to type the commands into a text file and have the program read the text file. More info is given later
For example, one can type:

fight CSM_F? CSM_Ha?

And the program will print the following table:

Forgefiend vs Havocs
 weapon     | N  | P% D>0 | first quartile | ave. dam. | third quartile |
------------------------------------------------------------------------
 Ectoplasma |   1|   82.4 |            1.2 |       2.8 |            3.6 |
 Autocannon |   1|   77.0 |            1.1 |       2.6 |            3.5 |
 Limbs      |   1|   27.0 |            0.0 |       0.6 |            1.1 |
 Jaws       |   1|   54.6 |            0.0 |       1.5 |            1.8 |
------------------------------------------------------------------------

The program guessed that "CSM_F?" meant CSM_Forgefiend, and "CSM_Ha?" meant CSM_Havoks. In many commands, the arguments can end with a question-mark to make the program guess what you mean. This saves typing. Note that typing "CSM_H?" would not work, as the program would not know if you meant Havoks or Hellbrute.

This table shows a list of possible weapons that the first unit can use to damage the second unit. This list includes both ranged and melee weapons. The first collumn is name of the weapon, second collumn is number of weapons shot. In this case, the program is only considering one instance of each weapon. This is important to note, as a Forgefiend will never actually have only one Autocannon (for instance). This number can be adjusted in the unit files. 

The third collumn ("P% D>0") shows the probability, in percent, that the weapon will do 1 or more damage. For example, the Ectoplasma cannon has 82% chance of doing 1 or more damage. The fourth collumn "first quartile", that is, 25% of the time the weapon will do less than this damage. This number will be zero most of the time, and only nonzero if "P% D>0" is greader than 75%.  The fifth collumn ""ave. dam." is the average damage over many shots. The sixth collumn is "third quartile", that is, 25% of the time the weapon will apply more damage than this number.

The numbers "P% D>0",  "first quartile" and "third quartile" are useful for assesing how swingy or consistent a weapon is.

One can also view the actuall probability distribution. For example, type:

showWeap E? 

The program will guess you want to see results of the Ectoplasma, and print:

 wounds |   % |
-----------------
      0 | 17.6|===========
      1 |  0.0|
      2 | 39.7|=========================
      3 |  0.0|
      4 | 31.1|===================
      5 |  0.0|
      6 | 10.2|======
      7 |  0.0|
      8 |  1.5|
      
For example, this table shows that 31% of the time the Ectoplasma will do 4 damage to Havoks (and thus kill the models). Note that the "showWeap" command always refers to the previous "fight" command. Thus, can only be called if "fight" has been called.

Also note that the Ectoplasma ought to do 3 damage per shot, but this table shows that each shot is only doing two damage. This is becouse the program accounts for the fact that damage per shot does not carry from one model to anouther (and Havoks only have 2 wounds per model).

Finally, note that this program uses a Monte-Carlo technique. That is, it simulates rolling the dice many times to create this distribution, the same way a person might. By default, the weapon is rolled 5000 times. However, it does mean that the results are slightly different everytime the "fight" command is called. 

all available units can be shown with:

printUnit

This command can also show the details of a specific unit. EG:

printUnit CSM_F?

will show the details of a forgefiend:

unit: Forgefiend ; 1 models
  T= 10 , S= 3 , invuln= 5 , FNP -
  keywords: ['vehicle', 'walker', 'chaos', 'daemon', 'forgefiend']
  weapons:
    Ectoplasma range= 36 , A= D3 , skill= 3 , S= 10 , AP= -3 , D= 3
    mods:blast ,
    Autocannon range= 36 , A= 6 , skill= 3 , S= 8 , AP= -1 , D= 2
    Limbs range= - , A= 2 , skill= 3 , S= 6 , AP= 0 , D= 2
    Jaws range= - , A= 5 , skill= 3 , S= 7 , AP= 0 , D= 2
    
Note that the Ectoplasma weapon has the modifier (weapon ability) "blast". One can add additional weapon abilities. For example, the command:

addMod sustainedHits_1

will add the weapon ability sustained Hits 1. Now, if fight is called, all weapons will have sustained hits q.

Note the underscore between the ability name and argument. Becouse such modifiers can have arguments, the "?" does not work.

All active modifiers can be shown with the command:

printActiveMods

all available modifiers can be shown with the command:

printMods

and all active modifiers can be cleared with:

clearMods


finally, the command "quit" does what it says.



ADVANCED USAGE

typing "help" shows a list of all available commands.

For each command, the name of the command and possible arguments follows. Each argument has a name (e.g. x or y), and a type (e.g. [s] or [sl]). The second line gives a description of the command and what each argument is. If the argument is surrounded by parenthesis (e.g. "printUnit (x[sl])" ) than the argument is optional.  There are currently only two types of arguments: [s], which is any string (set of charectors), and [sl] which is a specific string from a known list. These strings can end with "?" and the program will try to guess what you mean. 

 
Typing commands in a command window can get annoying. Thus the command readCmdsFile will open the file "cmd.txt" and read each line and do each command. "rcf" is a shortcut. The cmd.txt file must be in the same folder as calculator.py. It should be noted that the mods added in a cmd.txt file are NOT erased after the file is run. Thus, if for example, one has "addMod sustainedHits_1" in cmds.txt, runs "rcf". Then, one changes sustainedHits to "lethalHits" and runs rcf again, then all weapons will have BOTH sustained and lethal hits. For this reason, the cmd.txt should likely always start (or end as desired) with a clearMods command. An example cmds.txt file is provided.


There is always the chance that I made a mistake in programming this calculator. Therefore, there is also a feature to test it. To do this, choose a particular profile and roll a number of weapon attack yourself. Place the number of wounds per weapon attack as a single collumn in fightStats.txt. Like cmd.txt, this file must be in same folder as calculator.py. Each line of fightStats.txt should contain a single integer. OR a line can start with a '#' and the program will ignore it. An example fightStats.txt is provided.

Next run a fight command with the exact same profile you rolled by-hand. In particular, pay attention to the "N" collumn, it ought to be "1" for this test (how to change it is below). Then run the command "statTest" with the argument of the weapon you want to test. E.G. "statTest Ectoplasma". The program will then perform a stats test (pearson chi-square for those of interest).

If the program prints "RESULT: the two distributions are statistcally DIFFERENT", then if means that you and the program rolled the weapon differently. In this case, please report to me exactly what you did (weapon profiles, how you rolled it, unit files, etc...) and I will investigate if the program or you are wrong.

If the program prints:  "RESULT: the two distributions are statistcally THE SAME".  It can mean one of three things:
1) You and the program both rolled the test correctly
2) You and the program made very similar mistakes
3) You rolled too-few times to have statistical significance

In short, you can't prove the program is correct, but at least you have no reason to belive it is wrong. Note, it is always impossible to prove that one has rolled enough statistics to argue that you can catch any problem, but I get the feeling that 20 rolls put in fightStats.txt are enough to catch significant errors.



EDITING UNIT FILES

The folder "units" contains unit files. They are relatively simple, one should simply open a few up to see the examples. The first few lines give basic stats of the unit. Faction names are currently not used. Number of models (num_models) is only used for calculating blast. Others should be obvious.

Empty lines are skipped.

Abilities can be added, but these are rarely useful since the program has a hard time taking enviromental factors into account (e.g. if a unit is alone, or in an aura, or whatever). Thus, unit abilities adn faction abilities should be typically accounted for using the "addMod" command.

Each weapon profile is a single line in between the "weapons" and "end_weapons" line. The weapon name must be a single word with no spaces. I like to show different weapon profiles with an underscore (e.g. "PlasmaGun_super"). However, the program treats weapon profiles as different weapons. The range, attacks, skill, strength and damage are then specified. 

Melee weapons have a range of "-". Otherwise Range is rarely used by the program.

Modifiers can be added. See the files for examples. These are same modifiers as listed by "printMods". The whole list of mods must have no spaces. Each mod is seperated by a comma (NO SPACE!), and the arguments of a mod are seperated by an underscore. (e.g. anti_infantry_4). 

If a unit has more than one weapon, this can be specified with "num". e.g. num=3. See CSM_Chosen for a good example. Note that if num=0, than that weapon will be ignored by the "fight" command. (It is actually calculated with num=1, but not printed in the table. So that showWeap command will still work). 

 











 









