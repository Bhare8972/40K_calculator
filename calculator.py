#!/usr/bin/env python3

import numpy as np

from inspect import getsourcefile
from os.path import abspath, dirname, join, isfile
from os import listdir
from scipy.stats import chisquare
import traceback


def string_to_dice(value_string):
	"""given a string like, 5, 2D6, or D3+2, return: number_of_dice, max_value_of_dice,  constant
	if number_of_dice is 0, then max_value_of_dice is None"""

	Dsplit_data = value_string.strip().split('D')

	if len(Dsplit_data)==1:
		return 0, None, int(Dsplit_data[0])
	elif len(Dsplit_data)==2:

		num_dice = Dsplit_data[0]
		afterD = Dsplit_data[1]

		if len(num_dice)==0:
			num_dice = 1
		else:
			num_dice = int(num_dice)


		PlusSplit_data = afterD.split('+')
		if len(PlusSplit_data)==1:
			max_dice = int(PlusSplit_data[0])
			constant = 0
		elif len(PlusSplit_data)==2:
			max_dice = int(PlusSplit_data[0])
			constant = int(PlusSplit_data[1])

		return num_dice, max_dice, constant

	else:
		print("ERROR in string_to_dice")
		quit()


class modifier_cls:
	all_mods_dict = {}

	def __init__(self, name, priority, description):  ## higher priority means happens later
		self.name = name
		self.priority = priority
		self.description = description

	def apply( self, calculator):
		"""apply this affect to a calculator"""
		print('WARNING: effect', self.name, 'is not implented.')

	def string( self, calculator):
		"""apply this affect to a calculator"""
		print('WARNING: effect', self.name, 'is not implented.')

	def preference( self, B):
		"""If have two effects of same name, return better of the two"""
		print('WARNING: effect', self.name, 'preference is not implented.')
		return self

	def exclusiveName(self):
		"""name by which only one can be applied. (same as name for most modiferes. only differ for anti)"""
		return self.name




class anti_modifier(modifier_cls):
	name = "anti"
	description = "anti kw x : crit wound on at least x if keyword kw is in defender keywords"

	def __init__(self, values):

		super().__init__(anti_modifier.name, 0, anti_modifier.description)

		if len(values) != 2:
			print('warning, anti modifier has wrong num arguments', values)
			quit()

		self.keyword = values[0]
		self.value = int(values[1])

	def preference(self, B):

		if B.value < self.value:
			return B

		else:
			return self

	def exclusiveName(self):
		return "anti-"+self.keyword

	def string(self):
		return 'anti '+self.keyword+' '+str(self.value)

	def apply( self, calculator):

		if self.keyword in calculator.defender_keywords:
			if calculator.crit_wound > self.value:
				calculator.crit_wound = self.value
modifier_cls.all_mods_dict['anti'] = anti_modifier





class singleVal_modifier(modifier_cls):
	def __init__(self, name, priority, description, values, mode=1): ## if mode is 1, higher is better, if mode is 2 lower is better
		super().__init__(name, priority,description)

		if len(values) != 1:
			print(name, 'has wrong num values')
			quit()

		self.val = int(values[0])

		if mode not in [1,2]:
			print("Error in singleVal_modifier constructor" )
			quit()

		self.mode = mode

	def preference( self, B):
		"""If have two effects of same name, return better of the two"""
		if B.name != self.name:
			print("ERROR in singleVal_modifier.preference")
			quit()

		if B.val == self.val:
			return self
		elif B.val < self.val:
			if self.mode == 1:
				return self
			else:
				return [B]

	def string(self):
		return self.name +" "+str(self.val)


class sustainedHits( singleVal_modifier ):
	name = "sustainedHits"
	description = "sustainedHits x : add x additional hits for every critical hit"

	def __init__(self, values):
		super().__init__(sustainedHits.name, 0, 
			sustainedHits.description,
			values)

	def apply(self, calculator):
		calculator.critHit_to_normHits_multiplier += self.val
modifier_cls.all_mods_dict['sustainedHits'] = sustainedHits


class melta( singleVal_modifier ):
	name = "melta"
	description = "melta x : add x additional damage for each wound if halfRange is also applied."

	def __init__(self, values):
		super().__init__(melta.name, 0, 
			melta.description,
			values)

	def apply(self, calculator):
		if 'halfRange' in calculator.unique_modifiers:
			calculator.additional_damage += self.val
modifier_cls.all_mods_dict['melta'] = melta

class rapidFire( singleVal_modifier ):
	name = "rapidFire"
	description = "rapidFire x : add x additional attack if halfRange is also applied."

	def __init__(self, values):
		super().__init__(rapidFire.name, 0, 
			rapidFire.description,
			values)

	def apply(self, calculator):
		if 'halfRange' in calculator.unique_modifiers:
			calculator.extra_initial_attacks += self.val
modifier_cls.all_mods_dict['rapidFire'] = rapidFire

class modHits( singleVal_modifier ):
	name = "modHits"
	description = "modHits x : add x to the hit roll."

	def __init__(self, values):
		super().__init__(modHits.name, 0, 
			modHits.description,
			values)

	def apply(self, calculator):
		calculator.hitRoll_modifier += self.val
modifier_cls.all_mods_dict['modHits'] = modHits

class modAttacks( singleVal_modifier ):
	name = "modAttacks"
	description = "modAttacks x : add x number of attacks"

	def __init__(self, values):
		super().__init__(modAttacks.name, 0, 
			modAttacks.description,
			values)

	def apply(self, calculator):
		calculator.extra_initial_attacks += self.val
modifier_cls.all_mods_dict['modAttacks'] = modAttacks

class modDamage( singleVal_modifier ):
	name = "modDamage"
	description = "modDamage x : add x extra damage per attack"

	def __init__(self, values):
		super().__init__(modDamage.name, 0, 
			modDamage.description,
			values)

	def apply(self, calculator):
		calculator.additional_damage += self.val
modifier_cls.all_mods_dict['modDamage'] = modDamage

class modSave( singleVal_modifier ):
	name = "modSave"
	description = "modSave x : add x to save rol"

	def __init__(self, values):
		super().__init__(modSave.name, 0, 
			modSave.description,
			values)

	def apply(self, calculator):
		calculator.save_modifier += self.val
modifier_cls.all_mods_dict['modSave'] = modSave

class modWound( singleVal_modifier ):
	name = "modWound"
	description = "modWound x : add x to the wound roll."

	def __init__(self, values):
		super().__init__(modWound.name, 0, 
			modWound.description,
			values)

	def apply(self, calculator):
		calculator.woundRoll_modifier += self.val
modifier_cls.all_mods_dict['modWound'] = modWound

class modCritHit( singleVal_modifier ):
	name = "modCritHit"
	description = "modCritHit x : set critical hit to x."

	def __init__(self, values):
		super().__init__(modCritHit.name, 0, 
			modCritHit.description,
			values)

	def apply(self, calculator):
		calculator.crit_hit = self.val
modifier_cls.all_mods_dict['modCritHit'] = modCritHit

class modCritWound( singleVal_modifier ):
	name = "modCritWound"
	description = "modCritWound x : set critical wound to x."

	def __init__(self, values):
		super().__init__(modCritWound.name, 0, 
			modCritWound.description,
			values)

	def apply(self, calculator):
		calculator.crit_wound = self.val
modifier_cls.all_mods_dict['modCritWound'] = modCritWound

class reRollHits( singleVal_modifier ):
	name = "reRollHits"
	description = "reRollHits x: re-roll failed hit rolls that are x or lower (set x=6 to reroll all failed)"

	def __init__(self, values):
		super().__init__(reRollHits.name, 0, 
			reRollHits.description,
			values)

	def apply(self, calculator):
		calculator.reRoll_hit_roll = self.val
modifier_cls.all_mods_dict['reRollHits'] = reRollHits

class reRollWounds( singleVal_modifier ):
	name = "reRollWounds"
	description = "reRollWounds x: re-roll failed wounds rolls that are x or lower (set x=6 to reroll all failed)"

	def __init__(self, values):
		super().__init__(reRollWounds.name, 0, 
			reRollWounds.description,
			values)

	def apply(self, calculator):
		calculator.reRoll_wound_roll = self.val
modifier_cls.all_mods_dict['reRollWounds'] = reRollWounds







class noVal_modifier(modifier_cls):
	def __init__(self, name, priority, description, values):
		super().__init__(name, priority, description)

		if len(values) != 0:
			print(name, 'has wrong num values')
			quit()

	def preference( self, B):
		"""If have two effects of same name, return better of the two"""
		return self ## they are the same

	def string(self):
		return self.name

class blast( noVal_modifier ):
	name = "blast"
	description = "blast : add 1 additional attack per five models."

	def __init__(self, values):
		super().__init__(blast.name, 0, 
			blast.description,
			values)

	def apply(self, calculator):
		numModels = int(calculator.defender.num_models)

		if "blastNum" in calculator.unique_modifiers:
			numModels = calculator.unique_modifiers["blastNum"].numModels

		numFives = int(numModels/5)

		calculator.extra_initial_attacks += numFives
modifier_cls.all_mods_dict['blast'] = blast


class twinLinked( noVal_modifier ):
	name = "twinLinked"
	description = "twinLinked : re-roll all failed wound rolls."

	def __init__(self, values):
		super().__init__(twinLinked.name, 0, 
			twinLinked.description,
			values)

	def apply(self, calculator):
		calculator.reRoll_wound_roll = True
modifier_cls.all_mods_dict['twinLinked'] = twinLinked

class devastatingWounds( noVal_modifier ):
	name = "devastatingWounds"
	description = "devastatingWounds : Every critical wound is a false mortal wound"

	def __init__(self, values):
		super().__init__(devastatingWounds.name, 0, 
			devastatingWounds.description,
			values)

	def apply(self, calculator):
		calculator.critWound_to_normWounds_multiplier -= 1
		calculator.critWounds_to_devWounds_multiplier += 1
modifier_cls.all_mods_dict['devastatingWounds'] = devastatingWounds

class lethalHits( noVal_modifier ):
	name = "lethalHits"
	description = "lethalHits : Every critical hit ignores the wound roll"

	def __init__(self, values):
		super().__init__(lethalHits.name, 0, 
			lethalHits.description,
			values)

	def apply(self, calculator):
		calculator.critHit_to_normHits_multiplier -= 1
		calculator.critHit_to_lethalHits_multiplier += 1
modifier_cls.all_mods_dict['lethalHits'] = lethalHits


class heavy( noVal_modifier ):
	name = "heavy"
	description = "heavy : if noMove is active, than add 1 to hit roll"

	def __init__(self, values):
		super().__init__(heavy.name, 0, 
			heavy.description,
			values)

	def apply(self, calculator):
		if "noMove" in calculator.unique_modifiers:
			calculator.hitRoll_modifier += 1
modifier_cls.all_mods_dict['heavy'] = heavy








### unused modifier
class torrent( noVal_modifier ):
	name = "torrent"
	description = "torrent : skips hit roll"
	isNoted=False

	def __init__(self, values):
		super().__init__(torrent.name, 0, 
			torrent.description,
			values)

		if not torrent.isNoted:
			print("torrent note: torrent keyword not really used. a '-' in hit value is what is used")
			torrent.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['torrent'] = torrent

class hazardous( noVal_modifier ):
	name = "hazardous"
	description = "hazardous : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(hazardous.name, 0, 
			hazardous.description,
			values)

		if not hazardous.isNoted:
			print("hazardous note: harzardous is not used")
			hazardous.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['hazardous'] = hazardous

class pistol( noVal_modifier ):
	name = "pistol"
	description = "pistol : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(pistol.name, 0, 
			pistol.description,
			values)

		if not pistol.isNoted:
			print("pistol note: pistol is not used")
			pistol.isNoted = True
		
	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['pistol'] = pistol

class assault( noVal_modifier ):
	name = "assault"
	description = "assault : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(assault.name, 0, 
			assault.description,
			values)

		if not assault.isNoted:
			print("assault note: assault is not used")
			assault.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['assault'] = assault

class ignoresCover( noVal_modifier ):
	name = "ignoresCover"
	description = "ignoresCover : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(ignoresCover.name, 0, 
			ignoresCover.description,
			values)

		if not ignoresCover.isNoted:
			print("ignoresCover note: ignoresCover is not used")
			ignoresCover.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['ignoresCover'] = ignoresCover

class lance( noVal_modifier ):
	name = "lance"
	description = "lance : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(lance.name, 0, 
			lance.description,
			values)

		if not lance.isNoted:
			print("lance note: lance is not used")
			lance.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['lance'] = lance

class ignoreCover( noVal_modifier ):
	name = "ignoreCover"
	description = "ignoreCover : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(ignoreCover.name, 0, 
			ignoreCover.description,
			values)

		if not ignoreCover.isNoted:
			print("ignoreCover note: ignoreCover is not used")
			ignoreCover.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['ignoreCover'] = ignoreCover

class precision( noVal_modifier ):
	name = "precision"
	description = "precision : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(precision.name, 0, 
			precision.description,
			values)

		if not precision.isNoted:
			print("precision note: precision is not used")
			precision.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['precision'] = precision

class extraAttacks( noVal_modifier ):
	name = "extraAttacks"
	description = "extraAttacks : not used"
	isNoted=False

	def __init__(self, values):
		super().__init__(extraAttacks.name, 0, 
			extraAttacks.description,
			values)

		if not extraAttacks.isNoted:
			print("extraAttacks note: extraAttacks is not used")
			extraAttacks.isNoted = True

	def apply(self, calculator):
		pass
modifier_cls.all_mods_dict['extraAttacks'] = extraAttacks












class enviromental_effect_cls:
	### things that affect modifiers

	all_environs_dict = {}

	def __init__(self, name):
		self.name = name

	def string(self):
		return self.name

class activateHeavyEnviron( enviromental_effect_cls ):
	name = 'activateHeavy'
	description = 'activateHeavy : activate heavy ability'

	def __init__(self, vals):
		super().__init__(activateHeavyEnviron.name)
		if len(vals)!=0:
			print('Warning, num arguments to activateHeavyEnviron is wrong. should be 0')
enviromental_effect_cls.all_environs_dict['activateHeavy'] = activateHeavyEnviron

class noMoveEnviron( enviromental_effect_cls ):
	name = 'noMove'
	description = 'noMove : activate all effects that require model to not move (heavy)'

	def __init__(self, vals):
		super().__init__(noMoveEnviron.name)
		if len(vals)!=0:
			print('Warning, num arguments to noMoveEnviron is wrong. should be 0')
enviromental_effect_cls.all_environs_dict['noMove'] = noMoveEnviron

# class ignoresCoverEnviron( enviromental_effect_cls ):
# 	name = "ignoresCover"
# 	description = "ignoresCover : modifier inCover is ignored."

# 	def __init__(self):
# 		super().__init__(ignoresCoverEnviron.name)
# enviromental_effect_cls.all_environs_dict['ignoresCover'] = ignoresCoverEnviron

class blastNumEnviron( enviromental_effect_cls ):
	name = "blastNum"
	description = "blastNum x: Set number of models for purpose of caluclating blast"

	def __init__(self, vals):
		super().__init__(blastNumEnviron.name)
		if len(vals)!=1:
			print('Warning, num arguments to blastNumEnviront is wrong. should be 0')
		self.numModels = int(vals[0])
enviromental_effect_cls.all_environs_dict['blastNum'] = blastNumEnviron





class weapon:
## these should all be strings mostly
	def __init__(self, name, range, attacks, skill, strength, AP, damage, number=1, modifiers=[]):
		self.name = name
		self.range = range
		self.attacks = attacks
		self.skill = skill
		self.strength = strength
		self.AP = AP
		self.damage = damage
		self.modifiers = modifiers
		self.number = int(number)

	def print(self):
		print(self.name, 'range=',self.range, ', A=',self.attacks, ', skill=',self.skill, ', S=',self.strength, ', AP=',self.AP, ', D=',self.damage)
		if self.number != 1:
			print('    number=', self.number)

		if len(self.modifiers)>0:
			print('    mods:',end='')
			for m in self.modifiers:
				print( m.string(),',',end='' )
			print()


class model:
## these should all be strings mostly
	def __init__(self, name, faction, faction_short, num_models, toughness, save, wounds, invuln_save='-', feel_no_pain='-', weapons={}, abilities=[], key_words=[]):
		self.name = name 
		self.faction = faction
		self.faction_short = faction_short
		self.num_models = num_models
		self.toughness = toughness
		self.save = save 
		self.wounds = wounds
		self.invuln_save = invuln_save
		self.feel_no_pain = feel_no_pain
		self.weapons = weapons
		self.key_words = key_words
		self.abilities = abilities

	def print(self):
		print("unit:", self.name, ';', self.num_models , 'models')
		print("  T=",self.toughness, ', S=',self.save, ', invuln=',self.invuln_save,', FNP',self.feel_no_pain)
		print("  keywords:", self.key_words)
		
		if len(self.abilities)>0:
			print('  abilities:',end='')
			for m in self.abilities:
				print( m.string,',',end='' )
			print()

		print("  weapons:")
		for w in self.weapons.values():
			print('    ',end='')
			w.print()

def readModel_from_file(fname):

	mode = 'normal' ## also readWeapons
	weaponList = []

	with open(fname,'r') as fin:
		for line in fin:

			if len(line)==0:
				continue

			lineData = line.split()

			if len(lineData)==0 or lineData[0][0]== '#':
				continue

			if mode == 'normal':
				if lineData[0]=='name':
					modelName = lineData[1]
				elif lineData[0] == 'faction':
					faction = ' '.join( lineData[1:] )
				elif lineData[0] == 'faction_short':
					faction_short = lineData[1]
				elif lineData[0] == 'num_models':
					num_models = lineData[1]
				elif lineData[0] == 'toughness':
					toughness = lineData[1]
				elif lineData[0] == 'save':
					save = lineData[1]
				elif lineData[0] == 'wounds':
					wounds = lineData[1]
				elif lineData[0] == 'invuln_save':
					invuln_save = lineData[1]
				elif lineData[0] == 'feel_no_pain':
					feel_no_pain = lineData[1]

				elif lineData[0] == 'key_words':
					key_words = lineData[1:]

				elif lineData[0] == 'abilities':
					abilities = lineData[1:]

					if len(abilities) > 0:
						print("WARNING: model abilities not yet implemented")

				elif lineData[0] == 'weapons':
					mode = 'readWeapons'

				else:
					print('WARNING UNKNOWN LINE:', lineData)

			elif mode == 'readWeapons':

				if lineData[0] == 'end_weapons':
					mode = 'normal'
					continue

				name = lineData[0]
				dataDict = dict(txt.split('=') for txt in lineData[1:])


				numberWeapons = 1
				if 'num' in dataDict:
					numberWeapons = dataDict['num']

				modList = []
				if 'mods' in dataDict:
					modList = dataDict['mods'].split(',')

				
				##turn modlist into real modeifers
				modifier_list = []
				for modTxt in modList:
					data = modTxt.split('_')
					modName = data[0]
					values = data[1:]

					if modName in modifier_cls.all_mods_dict:
						modifier_list.append(   modifier_cls.all_mods_dict[modName]( values )  )

					elif modName in enviromental_effect_cls.all_environs_dict:
						if len(values)>0:
							modifier_list.append(   enviromental_effect_cls.all_environs_dict[modName](values)  )
						else:
							modifier_list.append(   enviromental_effect_cls.all_environs_dict[modName]()  )

					else:
						print(modName, 'is not yet implemented')

				W = weapon(name, dataDict['range'], dataDict['A'], dataDict['skill'], dataDict['S'], dataDict['AP'], dataDict['D'], number=numberWeapons, modifiers=modifier_list)
				weaponList.append( W )

	if mode != 'normal':
		print('WARNING: file',fname,'did not end the weapon list')

## TODO: turn abilities into classes

	key_words = [kw.lower() for kw in key_words]
	weaponDict = {weapon.name:weapon for weapon in weaponList}

	return model(name=modelName, faction=faction, faction_short=faction_short, num_models=num_models,
		toughness=toughness, save=save, wounds=wounds, invuln_save=invuln_save, feel_no_pain=feel_no_pain, weapons=weaponDict, abilities=[], key_words=key_words)


			




class weaponFight_paramaterCalculator:
	def __init__(self, weapon, attacker, defender, modifiers=[]):


		self.weapon = weapon
		self.attacker = attacker
		self.defender = defender
		self.modifiers = modifiers


	## number of attacks

		self.num_initial_attacks = str(self.weapon.attacks)
		self.extra_initial_attacks = 0


	## hit roll modifiers
		if self.weapon.skill == '-': ## torrent weapon
			self.weapon_skill = None
		else:
			self.weapon_skill = int(self.weapon.skill)

		self.hitRoll_modifier = 0
		self.crit_hit = 6
		self.critHit_to_normHits_multiplier = 1 ## a 1 means a crit hit is normal hit. 2 is "sustained 1"
		self.critHit_to_lethalHits_multiplier = 0 ## if 1, means "lethal 1" (also need to subtract one from critHit_to_normHits_multiplier)

		self.reRoll_hit_roll = 0

	## wound roll

		self.weapon_strength = int(self.weapon.strength)
		self.defender_toughness = int(self.defender.toughness)

		self.woundRoll_modifier = 0
		self.crit_wound = 6

		self.reRoll_wound_roll = 0

		self.critWound_to_normWounds_multiplier = 1
		self.critWounds_to_devWounds_multiplier = 0
		self.critWounds_to_mortalWounds_multiplier = 0


	## save throw

		self.defender_save = int(self.defender.save)
		self.defender_wounds = int(self.defender.wounds)
		self.save_modifier = 0

		if self.defender.invuln_save =='-':
			self.invuln_save = None
		else:
			self.invuln_save = int(self.defender.invuln_save)



	## feel no pain
		if self.defender.feel_no_pain == '-':
			self.defender_FNP = None
		else:
			self.defender_FNP = int(self.defender.feel_no_pain)

	## damage

		self.weapon_damage = str(self.weapon.damage)
		self.additional_damage = 0



#### now we calculate and apply modifiers  ####
		self.attacker_keywords = self.attacker.key_words
		self.defender_keywords = self.defender.key_words

		## step one is to put them all into one pot
		all_mods = modifiers + attacker.abilities + defender.abilities + weapon.modifiers

		## remove duplicates and pick better of two, and then put in dict
		self.unique_modifiers = {}
		for mod in all_mods:
			exName = mod.exclusiveName()

			## search for duplicates in current list
			if exName in self.unique_modifiers:
				## if we have a duplicate
				dupMod = self.unique_modifiers[exName]

				betterMod = mod.preference( dupMod ) ## get better of two
				self.unique_modifiers[exName] = betterMod

			else:
				self.unique_modifiers[exName] = mod

		## next sort the list by preference
		self.sorted_active_abilities = [mod for mod in self.unique_modifiers.values() if isinstance(mod, modifier_cls)]
		self.sorted_active_abilities.sort( key=lambda X: X.priority )

		## finally, apply the abilities
		for ab in self.sorted_active_abilities:
			ab.apply( self )





## Normalize hit roll

		if self.hitRoll_modifier < -1: ## a hit roll cannot be modified more or less than 1
			self.hitRoll_modifier = -1
		elif self.hitRoll_modifier > 1:
			self.hitRoll_modifier = 1

### Normalize wound roll

		if self.woundRoll_modifier < -1: ## a hit roll cannot be modified more or less than 1
			self.woundRoll_modifier = -1
		elif self.woundRoll_modifier > 1:
			self.woundRoll_modifier = 1

		if self.weapon_strength >= 2*self.defender_toughness:
			self.woundRoll_succses = 2
		elif self.weapon_strength > self.defender_toughness:
			self.woundRoll_succses = 3
		elif self.weapon_strength == self.defender_toughness:
			self.woundRoll_succses = 4
		elif self.weapon_strength <= 0.5*self.defender_toughness:
			self.woundRoll_succses = 6
		elif self.weapon_strength < self.defender_toughness:
			self.woundRoll_succses = 5

	
#### normalize Save roll mods

		self.save_modifier += int(self.weapon.AP)

		if self.save_modifier > 1:
			self.save_modifier = 1  ## can never improve more than one






#### Monte Carlo Technique


class fightEngine_MC:
	def __init__(self, num_runs, max_dice):
		self.max_dice = max_dice
		self.num_runs = num_runs

		self.workspace = np.empty(max_dice, dtype=int)


	def rollDice(self, number, minCut, maxCut):
		"""Roll number of D6. Return number below minCut, number between minCut (inclusive) and maxCut(exclusive), and number >= maxCut"""

		if number < 1:
			#raise ValueError('ODD ERROR, num dice rolls is too small: '+str(number))
			#quit()
			return 0,0,0
		elif number > self.max_dice:
			prevL, prevM, prevG = rollDice(number-self.max_dice, minCut, maxCut )
			number = self.max_dice
		else:
			prevL=0
			prevM=0
			prevG=0

		diceRolls = np.random.randint(low=1, high=6+1, size=number)
		L = np.sum( np.less(diceRolls, minCut, out=self.workspace[:number]) )
		G = np.sum( np.greater_equal(diceRolls, maxCut, out=self.workspace[:number]) )
		M = number -L -G

		return L+prevL, M+prevM, G+prevG

	def rollDice_3cut(self, number, minCut, midCut, maxCut):
		"""Roll number of D6. Return:
			 number <= minCut,  number between minCut (exclusive) and midCut(exclusive), number between midCut (inclusive) and maxCut (exclusive),  and number >= maxCut"""

		if number < 1:
			return 0,0,0,0
		elif number > self.max_dice:
			pA, pB, pC, pD = rollDice_3cut(number-self.max_dice, minCut, midCut, maxCut )
			number = self.max_dice
		else:
			pA = 0
			pB = 0
			pC = 0
			pD = 0

		diceRolls = np.random.randint(low=1, high=6+1, size=number)


		A = np.sum( np.less_equal(diceRolls, minCut, out=self.workspace[:number]) )

		BpA = np.sum( np.less(diceRolls, midCut, out=self.workspace[:number]) )
		B = BpA-A

		CpBpA = np.sum( np.less(diceRolls, maxCut, out=self.workspace[:number]) )
		C = CpBpA - BpA

		D = np.sum( np.greater_equal(diceRolls, maxCut, out=self.workspace[:number]) )

		return A+pA, B+pB, C+pC, D+pD

	def getFightDistribution(self, parameters):


		current_dist = [0]

		for runi in range(self.num_runs):

			one_roll_result = self._oneRoll(parameters)


			if one_roll_result > len(current_dist) - 1 :
				extra_amounts = one_roll_result - (len(current_dist) - 1)
				current_dist += [0]*extra_amounts

			current_dist[one_roll_result] += 1


		self.finalWoundsDistribution = distribution(0, len(current_dist)-1, current_dist)

		return self.finalWoundsDistribution


	def _oneRoll(self, parameters):

	#### caluclate number of attacks ####

		numDice, maxofDice, constant = string_to_dice(parameters.num_initial_attacks)

		dice_roll_result = 0
		if numDice>0:
			dice_roll_result = np.sum( np.random.randint(low=1, high=maxofDice+1, size=numDice) )

		attacks = dice_roll_result + constant + parameters.extra_initial_attacks



	### calc hit roll ###
		if parameters.weapon_skill is not None:

			### NORMALIZE HIT ROLL
			sucsessful_hit_rol = parameters.weapon_skill - parameters.hitRoll_modifier

			if sucsessful_hit_rol < 2:
				sucsessful_hit_rol = 2 ## unmodified of 1 always fails

			if sucsessful_hit_rol > parameters.crit_hit:
				sucsessful_hit_rol = parameters.crit_hit

			if parameters.reRoll_hit_roll >= sucsessful_hit_rol:
				reRoll = sucsessful_hit_rol - 1
			else:
				reRoll = parameters.reRoll_hit_roll


			### RULL HIT ROLL
			if reRoll>0:

				attacks, first_failedHitRolls, first_numHits, first_numHitCrits = self.rollDice_3cut(attacks,   reRoll,    sucsessful_hit_rol,   parameters.crit_hit)

			else:
				first_failedHitRolls = 0
				first_numHits = 0
				first_numHitCrits = 0

			failedHitRolls, num_hits, num_hitCrits = self.rollDice(attacks, sucsessful_hit_rol, parameters.crit_hit)

			failedHitRolls += first_failedHitRolls
			num_hits += first_numHits
			num_hitCrits += first_numHitCrits


			### FINAL CALCS
			num_hits += num_hitCrits*parameters.critHit_to_normHits_multiplier
			num_LethalHits = num_hitCrits*parameters.critHit_to_lethalHits_multiplier

		else:     ## TORRENT
			num_hits = attacks
			num_LethalHits = 0


	### calc wound roll ###

		## normalize wound roll
		sucsessful_wound_roll = parameters.woundRoll_succses - parameters.woundRoll_modifier

		if sucsessful_wound_roll > parameters.crit_wound:
			sucsessful_wound_roll = parameters.crit_wound

		reRoll = parameters.reRoll_wound_roll
		if reRoll >= sucsessful_wound_roll:
			reRoll = sucsessful_wound_roll - 1


		### ROLL WOULD ROLL
		if reRoll>0:

			num_hits, first_num_failed_wounds, first_num_wounds, first_num_woundCrits = self.rollDice_3cut(num_hits,   reRoll,    sucsessful_wound_roll,   parameters.crit_wound)

		else:
			first_num_failed_wounds = 0
			first_num_wounds = 0
			first_num_woundCrits = 0

		num_failed_wounds, num_wounds, num_woundCrits = self.rollDice(num_hits, sucsessful_wound_roll,   parameters.crit_wound)

		num_failed_wounds += first_num_failed_wounds
		num_wounds += first_num_wounds
		num_woundCrits += first_num_woundCrits
			

		# num_failed_wounds, num_wounds, num_woundCrits = self.rollDice(num_hits, sucsessful_wound_roll, parameters.crit_wound)

		# if parameters.reRoll_wound_roll:
		# 	num_failed_wounds, num_new_wounds, num_new_woundCrits = self.rollDice(num_failed_wounds, sucsessful_wound_roll, parameters.crit_wound)
		# 	num_wounds += num_new_wounds
		# 	num_woundCrits += num_new_woundCrits

		### FINAL CALUCLATION
		num_wounds += num_woundCrits*parameters.critWound_to_normWounds_multiplier
		devastating_wounds = num_woundCrits*parameters.critWounds_to_devWounds_multiplier
		mortal_wounds = num_woundCrits*parameters.critWounds_to_mortalWounds_multiplier


	### SAVES ###
		num_saves = num_wounds + num_LethalHits

		norm_save = parameters.defender_save - parameters.save_modifier
		if (parameters.invuln_save is not None) and (parameters.invuln_save<norm_save):
			save_to_use = parameters.invuln_save
		else:
			save_to_use = norm_save

		fail_saved, num_saved, _ = self.rollDice( num_saves, save_to_use, 7 )

		total_unsaved_wounds = fail_saved + devastating_wounds ## attacks whose damage is limited to one model per attack


	### damages ##

		numDice, maxofDice, constant = string_to_dice(parameters.weapon_damage)

		dice_roll_result = 0
		if numDice>0:
			dice_roll_result = np.sum( np.random.randint(low=1, high=maxofDice+1, size=numDice) )

		damage_factor = dice_roll_result + constant + parameters.additional_damage


		total_damages = mortal_wounds*damage_factor   ## true mortal wounds can carry to multiple models

		if damage_factor > parameters.defender_wounds:  ## most attackes have damage that cannot carry between models
			damage_factor = parameters.defender_wounds

		total_damages += total_unsaved_wounds*damage_factor



	### feel-no-pain ###
		if parameters.defender_FNP is not None:
			_, total_damages, _ = self.rollDice(total_damages, parameters.defender_FNP, 7)


		return total_damages




class multiFight:
	def __init__(self, fightEngine, attacker, defender, additionalModifiers=[]):
		self.fightEngine = fightEngine

		self.attacker = attacker
		self.defender = defender
		self.additionalModifiers = additionalModifiers

		self.weaponNames = list( attacker.weapons.keys() )

		self.weaponNumbers = { name:weapon.number for name,weapon in attacker.weapons.items() }

		self.weaponDistributions = {}
		for name in self.weaponNames:
			dist = self.fightEngine.getFightDistribution(weaponFight_paramaterCalculator(weapon=attacker.weapons[name], attacker=attacker, defender=defender, modifiers=additionalModifiers ))
			num = self.weaponNumbers[ name ]

			if num>1:
				OneWeaponDist = dist
				current_dist = dist

				for i in range(num-1):
					current_dist = summing_distribution_process(current_dist, OneWeaponDist)

				dist = current_dist

			self.weaponDistributions[name] = dist




		# self.weaponDistributions = { name: 
		# self.fightEngine.getFightDistribution(weaponFight_paramaterCalculator(weapon=attacker.weapons[name], attacker=attacker, defender=defender, modifiers=additionalModifiers ))
		# for name in self.weaponNames }

	def getWeaponNames(self):
		return self.weaponNames

	def getWeaponDistribution(self, weaponName):
		return self.weaponDistributions[weaponName]

	def printNiceTable(self):

		maxWeaponName = np.max( [len('weapon')] + [ len(wn) for wn in self.weaponNames if self.weaponNumbers[wn]!=0 ] )
		maxWeaponName += 2



# size: maxWeaponName, 4, 8, 16, 11, 16   (maxWeaponName + 60 total )
	#   weapon | N  | P% D>0 | first quartile | ave. dam. | third quartile |

		print( self.attacker.name, 'vs', self.defender.name )
		string = ' weapon'.ljust(maxWeaponName) + '| N  | P% D>0 | first quartile | ave. dam. | third quartile |'
		print(string)
		print('-'*(maxWeaponName+60) )

		for wn, dist in self.weaponDistributions.items():

			num = self.weaponNumbers[wn]
			if num == 0:
				continue


			ave, _ = dist.average()
			_, Po0 = dist.average(1)
			firstQ, median, thirdQ = dist.getQuartiles()

			string = ' '+wn.ljust(maxWeaponName-1) + '|'           # name
			string = string + " " +str(num).rjust(3) + '|'  #num
			string = string + f"{Po0*100:.1f}".rjust(7) + ' |'  #P% D>0 
			string = string + f"{firstQ:.1f}".rjust(15) + ' |'  #first quartile 
			string = string + f"{ave:.1f}".rjust(10) + ' |'  #average
			string = string + f"{thirdQ:.1f}".rjust(15) + ' |'  #third quartile
			print(string)

		print('-'*(maxWeaponName+60) )




##### DISTRIBUTION FUNCTIONS ######

class distribution:
	def __init__(self, minimum, maximum, dist):
		self._minimum = minimum
		self._maximum = maximum
		self._dist = np.array(dist, dtype=float)

		if len(self._dist) != self._maximum - self._minimum + 1:
			print('error in intilizing distsribution')
			quit()

		self.normalization = np.sum(self._dist)
		self._dist /= self.normalization

	def getMin(self):
		return self._minimum

	def getMax(self):
		return self._maximum

	def getValue(self, v):
		"""return PMF for value v"""
		if v < self._minimum:
			return 0.0
		if v > self._maximum:
			return 0.0

		return self._dist[v-self._minimum]

	def getNumber(self, v):
		"""return PMF * normalization"""
		return self.getValue(v)*self.normalization

	def drawSample(self, N):
		"""return 1D array of N samples drawn from this distribution"""

		draws = np.random.uniform(size=N)
		TEMP1 = np.empty(shape=N, dtype=bool)
		TEMP2 = np.empty(shape=N, dtype=bool)

		out = np.empty(shape=N, dtype=int)
		current_PMF = 0

		np.equal( draws, 0, out=TEMP1 )
		out[TEMP1] = self.getMin()


		for value in range(self.getMin(), self.getMax()+1):
			nextPMF = current_PMF + self.getValue( value )

			np.greater( draws, current_PMF, out=TEMP1 )
			np.less_equal( draws, nextPMF, out=TEMP2 )
			np.logical_and( TEMP1,TEMP2, out=TEMP1 )

			out[TEMP1] = value

			current_PMF = nextPMF

		return out




	def copy(self):
		return distribution(self._minimum, self._maximum, self._dist)



	## OUTPUT

	def print(self):
		for i in range(self._minimum, self._maximum+1):
			print( i, self.getValue(i)*100, '%' )

	def barPlot(self, width=40):

		##      8 char  5 char
		print(' wounds |   % |')
		print('-----------------')
		bar_width = width -8-5-2

		max_v = np.max(self._dist)

		for i in range(self._minimum, self._maximum+1):
			v = self.getValue(i)

			A = str(i).rjust(7)

			percent = f"{v*100:.1f}"
			percent = percent.rjust(5)

			num_pieces = int(v*bar_width/max_v)


			string_to_display = A+' |' + percent+'|'+'='*num_pieces



			print( string_to_display )






	### STATS
	def probGreatEqual(self, v):
		"""probability to get a value equal to or greater than v"""
		p_succses = 0
		for pv in range(self._minimum, self._maximum+1):
			if pv >= v:
				p_succses += getValue(pv)

		return p_succses

	def average(self, minValue=-np.inf):
		"""return average with a lower cut, and the probility to be above that lower cut"""

		numerator = 0 
		denominator = 0

		for i in range(self._minimum, self._maximum+1):

			if i >= minValue:
				p = self.getValue(i)

				numerator += p*i
				denominator += p

		return numerator/denominator, denominator

	def getQuartiles(self):

		previous_CMF = 0
		previous_CMF_X = None

		for i in range(self._minimum, self._maximum+1):

			new_CMF = previous_CMF + self.getValue(i) ## prob to get this value or lower

			# if new_CMF>0.25 and previous_CMF<=0.25:
			# 	firstQuartile = previous_CMF_X
			
			# if new_CMF>0.5 and previous_CMF<=0.5:
			# 	median = previous_CMF_X
			
			# if new_CMF>0.75 and previous_CMF<=0.75:
			# 	thirdQuartile = previous_CMF_X

			if new_CMF>=0.25 and previous_CMF<0.25:
				if previous_CMF_X is None:
					firstQuartile = i 
				else:
					f = (previous_CMF - 0.25)/( previous_CMF-new_CMF )
					firstQuartile = previous_CMF_X + f*( i-previous_CMF_X )

			if new_CMF>=0.5 and previous_CMF<0.5:
				if previous_CMF_X is None:
					median = i
				else:
					f = (previous_CMF - 0.5)/( previous_CMF-new_CMF )
					median = previous_CMF_X + f*( i-previous_CMF_X )

			if new_CMF>=0.75 and previous_CMF<0.75:
				if previous_CMF_X is None:
					thirdQuartile = i
				else:
					f = (previous_CMF - 0.75)/( previous_CMF-new_CMF )
					thirdQuartile = previous_CMF_X + f*( i-previous_CMF_X )


			previous_CMF_X = i
			previous_CMF = new_CMF

		return firstQuartile, median, thirdQuartile



 ## make some distributions ## 

# def singleDice_distribution():
# 	"""return a distribution representing a single D6"""

# 	return distribution(1,6,[1,1,1,1,1,1])

def flat_distribution(min_inclusive, max_inclusive):
	N = max_inclusive - min_inclusive + 1
	return distribution(min_inclusive, max_inclusive, np.ones(N))

def coinFlip_distribution( prob ):
	return distribution(0, 1, [1-prob, prob])

# def STR_to_dist(strDist):
# 	"""if a string is of three types:
# 	integer
# 	Dinteger
# 	or 
# 	Dinteger+intger 

# 	Return a distribution that it represents"""


# 	if strDist[0]=='D':
# 		v=strDist.split('+')
# 		numDice = int(v[0][1:])

# 		if len(v) == 1:
# 			additional = 0
# 		elif len(v)==2:
# 			additional = int(v[1])
# 		else:
# 			print('error in STR_to_dist:', strDist)
# 			quit()

# 		sixDice = singleDice_distribution()
# 		current_dist = sixDice
# 		for i in range(1,numDice):
# 			current_dist = summing_distribution_process(current_dist, sixDice)

# 		current_dist = addNum_to_distribution(current_dist, additional)

# 		return current_dist

# 	else:
# 		i = int(strDist)
# 		return distribution(i,i,[1])


 ## operations on distributions ##

def addNum_to_distribution(dist, num):
	"""if you take a number from a distribution and add a fixed num to it, this is the result"""

	copy = dist.copy()
	copy._minimum += num
	copy._maximum += num

	return copy

def summing_distribution_process(distA, distB):
	"""givin a number pulled from distA, and a second number from distB, return distribution that is their sum"""

	final_dist = {}

	for va in range(distA.getMin(), distA.getMax()+1):
		pa = distA.getValue(va)

		for vb in range(distB.getMin(), distB.getMax()+1):
			pb = distB.getValue(vb)

			sumV = va+vb
			sumP = pa*pb

			if sumV in final_dist:
				final_dist[sumV] += sumP
			else: 
				final_dist[sumV] = sumP

	values = list(final_dist.keys())

	minV = np.min(values)
	maxV = np.max(values)

	dist = np.zeros(maxV-minV+1, dtype=float)
	for v in range(minV, maxV+1):
		if v in final_dist:
			dist[v-minV]=final_dist[v]

	return distribution(minV, maxV, dist)


##### INPUT STUFF

def searchStringList(list, string):
	output = []
	for l in list:
		if l.startswith(string):
			output.append( l )
	return output

class workplaceCls:
	"""hold info needed to run commands"""
	def __init__(self):

		self.filePath = dirname(abspath(getsourcefile(lambda:0)))
		self.unitsPath = join(self.filePath, 'units')

		self.loadModels()
		

		self.lastFight = None 
		self.fightEngine = fightEngine_MC(5000,100)

		self.activeMods =[]

	## get MC runs, set MC runs

	def loadModels(self):
		self.list_of_units = {}  
		for unitFname in listdir(self.unitsPath):
			if not unitFname.endswith('.unit'):
				continue

			fullUnitPath = join(self.unitsPath, unitFname)
			if not isfile(fullUnitPath):
				continue

			unitName = unitFname.split('.')[0]
			unitData = readModel_from_file( fullUnitPath )

			self.list_of_units[unitName] = unitData


	def availableWeapons(self):
		if self.lastFight is None:
			return []
		else:
			return self.lastFight.getWeaponNames()

class commandCLS:
	def __init__(self, name, helpStr, parameters, function, defaultArg=None, lists=[]):
		""" name = string that is name of command
			helpStr = a string to print in help menu
			parameters = list of strings. Each string is 'i', 's', or 'sl' to indicate type of parameter
			function = a function that takes two arguments: a) a workplace instance, a list of arguments
			defaultArg = if not None, is default value of last argument 
			lists = if argument type is sl, then this has list of available strings, in order of sl parameters
		"""

		self.fullName = name
		self.name = name.split()[0]
		self.helpStr = helpStr
		self.parameters = parameters
		self.function = function
		self.defaultArg = defaultArg
		self.lists = lists

	def getName(self):
		return self.name

	def getFullName(self):
		return self.fullName

	def getHelp(self):
		return self.helpStr

	def go(self, arguments, workspace):

		numModifier = 1 if self.defaultArg is not None else 0

		if len(arguments)+numModifier < len(self.parameters):
			print("ERROR: less arguments given than required")
			return 



		parsedArguments = []
		list_i = 0
		for argumentI, (typ, value) in enumerate(zip(self.parameters, arguments)):
			if typ == 'i':
				try: 
					val = int(value)
				except:
					print("for argument", argumentI+1, "expected integer, but could not parse:", value)
					return 
				parsedArguments.append(val)

			elif typ == 's':
				val = value.replace('|',' ')
				parsedArguments.append(val)

			elif typ == 'sl':
				list_i += 1

				if value[-1] == '?':
					value = value[:-1]

					availbilitiesItems = self.lists[list_i-1]
					if callable(availbilitiesItems):
						availbilitiesItems = availbilitiesItems()

					availbilities = searchStringList(availbilitiesItems, value)
					if len(availbilities)==0:
						print("for argument", argumentI+1, "no availble string matches:", value)
						return
					elif len(availbilities)==1:
						print("for argument", argumentI+1, "exactly one string matches (is good):", availbilities[0])
						value = availbilities[0]
					elif len(availbilities)>1:
						print("for argument", argumentI+1, "too many strings match:", availbilities)
						return 

				parsedArguments.append(value)

		if (len(arguments) == len(self.parameters)-1) and self.defaultArg is not None :
			parsedArguments.append(self.defaultArg)

		self.function( parsedArguments, workspace )


### TODO: replace lists argument with functions. 
class inputControler:
	def __init__(self):
		self.workspace = workplaceCls()
		self.readingFile = False

		commands = [
		commandCLS('quit', 'exit the program', [], function=lambda cmds,wk:quit() ),
		commandCLS('help', 'print all commands', [], function=self.help ),
		commandCLS('printUnit (x[sl])', 'print info about unit named x. If name is not given, then print names of all units', ['sl'], function=printUnit,
			defaultArg = '-',
			 lists=[list(self.workspace.list_of_units.keys())] ),

		commandCLS('printMods', 'print all modifiers', [], function=printModifierInfo ),

		commandCLS('printActiveMods', 'print list of active modifiers', [], function=printActiveMods ),
		commandCLS('addMod x[s]', 'add a modifer (x) to list of active modifiers. x should be a string with no spaces. arguments should be seperated with a "_", e.g. anti_infantry_3', ['s'], function=addMod ),
		commandCLS('clearMods', 'set list of active modifiers to be empty', [], function=clearMods ),

		commandCLS('fight x[sl] y[sl]', 'fight unit x against unit y and print results', ['sl','sl'], function=fight,
			 lists=[list(self.workspace.list_of_units.keys()), list(self.workspace.list_of_units.keys())]    ),

		commandCLS('showWeap x[sl]', 'plot the actual PMF of damage for weapon x of previous fight command', ['sl'], function=showWeap,
			 lists=[self.workspace.availableWeapons]  ),

		commandCLS('statTest x[sl]', 'Compare results to hand-rolled results. See readme', ['sl'], function=statTest,
			 lists=[self.workspace.availableWeapons]  ),

		commandCLS('readCmdsFile', 'Read list of commands from cmds.txt. See readme', [], function=self.readFile,
			 lists=[]  ),

		commandCLS('rcf', 'shortcut for readCmdsFile', [], function=self.readFile,
			 lists=[]  ),

		commandCLS('reloadModels', 're-load all model files.', [], function=reload_Models,
			 lists=[]  ),
		]

		self.commands = { cmd.getName():cmd for cmd in commands }

	def stdIn_loop(self):
		while True:
			print()
			txt = input('cmd>> ')
			self.parseText(txt)

	def parseText(self, text):
		words = text.split()
		cmd = words[0]
		if cmd in self.commands:

			try:
			    self.commands[cmd].go(words[1:], self.workspace)
			except Exception:
			    traceback.print_exc()

		else:
			print('no cmd of name:', cmd)
			print('type "help" if desired')

	def help(self, args, workspace):

		print()
		print('help menu / list of commands:')
		print()

		for name, cmd in self.commands.items():
			print(cmd.getFullName())
			print(cmd.getHelp())
			print()

	def readFile(self, arguments, workspace):
		if self.readingFile:
			print("Not reading file again! Would make an infinite loop!")
			return

		self.readingFile = True

		fname = join(workspace.filePath, 'cmds.txt')
		lineNum = 1
		for line in open(fname, 'r'):
			f = line.split()[0][0]
			if f =='#':
				continue

			self.parseText( line )

		self.readingFile = False



### functions to run
def printUnit(arguments, workspace):

	if arguments[0]== '-':
		print( list(workspace.list_of_units.keys()) )

	else:
		unitName = arguments[0]
		print('unit info:', unitName)
		workspace.list_of_units[unitName].print()


def printModifierInfo(arguments, workspace):

	#if arguments[0]== '-':

	for mod in modifier_cls.all_mods_dict.values():
		print(mod.description)
		print()

	for environ in enviromental_effect_cls.all_environs_dict.values():
		print(environ.description)
		print()

def printActiveMods(arguments, workspace):
	for mod in workspace.activeMods:
		print(mod.string())

def addMod(arguments, workspace):
	if len(arguments)!= 1:
		print('wrong num argumetns!:', arguments)
	words = arguments[0].split('_')
	modName = words[0]
	modArgs = words[1:]

	if modName in modifier_cls.all_mods_dict:
		mod = modifier_cls.all_mods_dict[modName]
		workspace.activeMods.append( mod(modArgs) )

	elif modName in enviromental_effect_cls.all_environs_dict:
		mod = enviromental_effect_cls.all_environs_dict[modName]
		workspace.activeMods.append( mod(modArgs) )

	else:
		print('unknown mod name', modName)

def clearMods(arguments, workspace):
	workspace.activeMods = []


def fight(arguments, workspace):
	unit1_name = arguments[0]
	unit2_name = arguments[1]

	if unit1_name in workspace.list_of_units:
		unit1 = workspace.list_of_units[unit1_name]
	else:
		print('no unit:', unit1_name)
		return

	if unit2_name in workspace.list_of_units:
		unit2 = workspace.list_of_units[unit2_name]
	else:
		print('no unit:', unit2_name)
		return

	print()
	print()
	workspace.lastFight = multiFight(workspace.fightEngine, unit1, unit2, additionalModifiers=workspace.activeMods)
	workspace.lastFight.printNiceTable()

def showWeap(arguments, workspace):
	weapon = arguments[0]
	weapDist = workspace.lastFight.getWeaponDistribution( weapon )
	weapDist.barPlot()



def statTest(arguments, workspace):

## get weapon distribution
	weapon = arguments[0]
	weapDist = workspace.lastFight.getWeaponDistribution( weapon )
	print('w', weapDist.drawSample(10)  )


### first, we open the file and make a distribution ###
	fname = join(workspace.filePath, 'fightStats.txt')
	fileDist = [0]
	lineNum = 1
	for line in open(fname, 'r'):
		data = line.split()
		if len(data) == 0:
			continue
		if data[0][0] == '#':
			continue

		if len(data)>1:
			print('ERROR on line', lineNum, 'in file fightStats.txt')
			return

		try:
			value = int(data[0])
		except:
			print('ERROR on line', lineNum, 'in file fightStats.txt')
			return

		if (value+1)>len(fileDist):
			fileDist += [0]*( value+1-len(fileDist))

		fileDist[ value ] += 1

		lineNum += 1

	fileDist = distribution(0, len(fileDist)-1, fileDist)


## flatten both to same range
	minVal = min( weapDist.getMin(), fileDist.getMin() )
	maxVal = min( weapDist.getMax(), fileDist.getMax() )

	flattenedWeapon_dist = np.zeros(shape=maxVal-minVal+1, dtype=int)
	flattenedMeasured_dist = np.zeros(shape=maxVal-minVal+1, dtype=int)

	for v in range(minVal, maxVal+1):
		flattenedWeapon_dist[ v-minVal ] = weapDist.getNumber( v )
		flattenedMeasured_dist[ v-minVal ] = fileDist.getNumber( v )

	total = np.empty( shape=maxVal-minVal+1, dtype=float)
	total[:] = flattenedWeapon_dist
	total += flattenedMeasured_dist
	total[ np.equal(total,0) ] = 0.00000000000001 ## to avoid nans

## perform two T-tests
	## weapon:
	total /= np.sum(total)
	total *= np.sum( flattenedWeapon_dist )
	weapTestResult = chisquare(f_obs=flattenedWeapon_dist, f_exp=total)

## measured
	total /= np.sum(total)
	total *= np.sum( flattenedMeasured_dist )
	measTestResult = chisquare(f_obs=flattenedMeasured_dist, f_exp=total)

	print()
	print()
 
	print('pvalue A:', weapTestResult.pvalue, 'pvalue B:', measTestResult.pvalue)

	if (weapTestResult.pvalue<0.1) or (measTestResult.pvalue<0.1):
		print('RESULT: the two distributions are statistcally DIFFERENT')
	else:
		print('RESULT: the two distributions are statistcally SAME')


def reload_Models(arguments, workspace):
	workspace.loadModels()







## todo, print weapon stats	

## todo, set MC runs?







if __name__ == '__main__':

	IC = inputControler()
	IC.stdIn_loop()


	# for c in modifier_cls.all_mods_dict.values():
	# 	print( c.name)
	# 	print( c.description)

	# Havocs = readModel_from_file('./units/CSM_Havocs.txt')
	# Terminators = readModel_from_file('./units/CSM_Terminators.txt')
	# Helbrute = readModel_from_file('./units/CSM_Helbrute.txt')

	# modifiers = [halfRangeEnviron()]

	# FE = fightEngine_MC(5000,100)

	# # M = multiFight(FE, Helbrute, Terminators, additionalModifiers=[])
	# # M.printNiceTable()
	# # print()
	# # print()

	# # M = multiFight(FE, Helbrute, Havocs, additionalModifiers=[])
	# # M.printNiceTable()
	# # print()
	# # print()

	# # M = multiFight(FE, Helbrute, Helbrute, additionalModifiers=[])
	# # M.printNiceTable()
	# # print()
	# # print()


	# M = multiFight(FE, Terminators, Terminators, additionalModifiers=modifiers)
	# M.printNiceTable()
	# print()
	# print()

	# M = multiFight(FE, Terminators, Havocs, additionalModifiers=modifiers)
	# M.printNiceTable()
	# print()
	# print()

	# M = multiFight(FE, Terminators, Helbrute, additionalModifiers=modifiers)
	# M.printNiceTable()
	# print()
	# print()



	#M = multiFight(FE, Havocs, Terminators, additionalModifiers=[])
	#M.printNiceTable()
	#print()
	#print()

	# print()
	# print()
	# M = multiFight(FE, Havocs, Havocs, additionalModifiers=[])
	# M.printNiceTable()
	# print()
	# print()

	# M = multiFight(FE, Havocs, Helbrute, additionalModifiers=[])
	# M.printNiceTable()
	# print()
	# print()