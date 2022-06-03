import os
import uuid


# Debugging Functions
def print_hex(bytes):
    print("".join("%02x " % b for b in bytes).upper())

def find_all_instances(data_block, search_term, padding=0):
    cursor = 0
    while True:
        cursor = data_block.find(search_term, cursor)
        if cursor == -1:
            break
        end = cursor + len(search_term) + padding
        found = data_block[cursor:end]
        print(f'{hex(cursor)}:{found}')
        cursor += 1

import struct
def hex_to_float(bytes):
    if len(bytes) < 4:
        return 
    return struct.unpack('f', bytes)

def float_to_hex(value):
    return bytes(bytearray(struct.pack("f", value)))


''' Batch Editor for Save Files
# New size ONLY shows inside of breeding session and during sex
# Breaks animations with wild nephelyms
# Sexual interactions with wild nephelyms will soft lock game
# milking and harvesting animates will not play unless normal size
# Being in spirit form seems to ignore size so it doesn't cause issues
# disable wild sex or stay in spirit form if roaming with a new player size
# changing of the Main Breeder GUID breaks the save. Since the game looks for the GUID for the player data.
# fixed automatically in save function


### Important Headers: Ordered by position

## Header
GVAS - Infomation about the save. Leave unmodified
PlayerGuid - Guid of Nephelym that maps to the player character
PlayerWealth - Currecies of Player --ArrayProperty
PlayerBodyFluids - Nephelym Fluids --ArrayProperty


### Player monster
PlayerMonsters - Breeder and Nephelyms --ArrayProperty
    Nephelym
        name - nephelym name
        guid - unique identifier for nephelym
        variant - race and sex
        appearance - appearance and shape
        splatter - cum stains
        citargetvalue - idk
        cibuffer -idk
        cirate - idk
        cialpha - idk
        appliedscheme -idk
        stats - stats of nephelym.
        mother - mother nehpelym
        father - father nephelym
        traits - all the traits of the nephelym
        playertags - idk
        states - idk
        offspringid - Used to determine Child from OffspringBuffer
        lastmateid - guid of last mate
        lastmatesexcount - count of sex with last mate
OffspringBuffer - same as PlayerMonster, holds nephelyms for currently pregnant Nephelyms. Mapped with GUID
PlayerSexPositions - Sex Positions unlocked --ArrayProperty
PlayerSpirit - Player Spirit Energy --IntProperty
PlayerSpiritForm - Spirit Properties --StructProperty
    guid - guid, doesn't seem to affect anything
    variant - race and sex. might not be part of save
    appearance - the appearance/shape of spirit form
    appliedscheme - idk
    mother - parent mother
    father - parent father
    remain - trailing data

PlayerObtainedVariants - Obtained Nephelym races. probably for spirit form --ArrayProperty
PlayerSeenVariants - Seen Nephelym races. probably for spirit form --ArrayProperty
GameFlags - Flags for the game --StructProperty
WorldState - state for the game, Includes breeding tasks --StructProperty
BreederStatProgress - IDK or care --StructProperty



### Monster and Breeder Data Structure
MAIN HEADER
4 BYTE Number of Breeder + Nephelyms    will need to be updated if Nephelyms are added or dropped
\x0F + PlayerMonsters                   for list name
\x0F + StructProperty.                  for list type
8 BYTE Total data in list               !Looks like it can be ignored without issue
\x0E + CharacterData                    StructureType?
\x00 padding?
\x00*16 (Null GUID)


### Observations
# Houseing Max is 4096. Barn menu breaks after this. 12-bits.
# Max Breeding Center is 4096, including Breeder
# Max Nephelyms+Breeder is 12998 before save not recognized/ Save would be 2 GB.
# 12998 is odd since it's not close to any power of 2. inbetween 13 and 14-bytes.
# expected max of 4-bytes, 2,147,483,647 Nephelyms+Breeder


# Intresting limitations to the game.
# >Barns have a max capacity of 4096 before they break. Breeding Yard has same limit, but for all Nephelym+Breeder.
# >Max number of Nephelyms+Breeder before game nolonger recognized saves was 12998. save file was 2GB
# >Can swap any Nephelym or breeder to a new race. This will result in using the animations for the new race.
# >i.e Change the Breeder to a Kestrel, will cause the Breeder to fly when moving. Doesn't affect idle pose
# >Duplicated Nephelyms/Breeder only will appear if given a new GUID
# >Can have multiple breeders but game crashes if the Nephelym in the second position is also of Breeder race and doesn't have a new guid
# >Can stack contradictory traits. Smaller sizes take have higher priority than larger.
# >i.e Foxen with Massive and Tiny size will appear Tiny
# >Changing main breeders size will cause soft locking with some sex scences on wild nephelyms.
# >Can stack the same trait multiple times but doesn't have a tangable effect
'''


'''Macros and Generic Functions'''
class DictMacros:
    '''Dictionary macros used by funcions'''
    ##Nephelym Stats
    STAT_RANK_LEVEL = {
        'S': b'\x06', # Common
        'A': b'\x05', # Legendary
        'B': b'\x04', # Unique
        'C': b'\x03', # Rare
        'D': b'\x02', # Uncommon
        'E': b'\x01', # Common
    }
    STAT_RANKS = {
        'strength' : b'StrengthRank\x00',
        'dexterity' : b'DexterityRank\x00',
        'willpower' : b'WillpowerRank\x00',
        'allure' : b'AllureRank\x00',
        'fertility' : b'FertilityRank\x00',
        'rarity' : b'Rarity\x00',
    }
    
    ##Nephelym Traits
    NEPHELYM_TRAITS = {}
    TRAITS_WITH_LEVELS = {}
    TRAITS_LEVEL = {
        '4': b'\x34\x00',
        '3': b'\x33\x00',
        '2': b'\x32\x00',
        '1': b'\x31\x00',
    }

    BODY_TYPES = {
        'meaty' : b'Trait.Stat.Meaty.',
        'slender' : b'Trait.Appearance.Slender.',
        'chubby' : b'Trait.Appearance.Chubby.',
    }
    TRAIT_SIZE = {
        'massive' : b'Trait.Size.Massive\x00',
        'huge' : b'Trait.Size.Huge\x00',
        'large' : b'Trait.Size.Large\x00',
        'normal' : b'Trait.Size.Normal\x00',
        'small' : b'Trait.Size.Small\x00',
        'tiny' : b'Trait.Size.Tiny\x00',
    }
    TRAIT_STAT = {
        'charmer' : b'Trait.Stat.Charmer.',
        'debauched' : b'Trait.Stat.Debauched.',
        'fertile' : b'Trait.Stat.Fertile.',
        'hornball' : b'Trait.Stat.Hornball.',
        'juicy' : b'Trait.Stat.Juicy.',
        'kindhearted' : b'Trait.Stat.Kindhearted.',
        'nurturing' : b'Trait.Stat.Nurturing.',
        'nymphomaniac' : b'Trait.Stat.Nymphomaniac.',
        'potent' : b'Trait.Stat.Potent.',
        'stoic' : b'Trait.Stat.Stoic.',
        'swift' : b'Trait.Stat.Swift.',
        'valuable' : b'Trait.Stat.Valuable.',
        'desire' : b'Trait.Stat.Desire.',
    }
    TRAIT_APPERANCE = {
        'busty' : b'Trait.Appearance.Busty.',
        'buxom' : b'Trait.Appearance.Buxom.',
        'hung' : b'Trait.Appearance.Hung.',
        'slick' : b'Trait.Appearance.Slick.',
    }
    TRAIT_STAT_MISC = {
        'wild' : b'Trait.Stat.Wild\x00',
        'domestic' : b'Trait.Stat.Domestic\x00',
        'surprise' : b'Trait.Stat.Surprise\x00',
    }
    TRAIT_APPERANCE_MISC = {
        'atypical' :  b'Trait.Appearance.Atypical\x00',
        'twin' :  b'Trait.Appearance.Twin\x00',
        'hybrid' :  b'Trait.Appearance.Hybrid\x00',
    }
    TRAIT_FORM = {
        'hominal' : b'Trait.Form.Hominal\x00',
        'feral' : b'Trait.Form.Feral\x00',
    }
    
    TRAIT_NEGATIVE = {
        'hedonist' : b'Trait.Stat.Hedonist.',
        'efficient' : b'Trait.Stat.Efficient.',
        'sterile' : b'Trait.Stat.Sterile\x00',
    }

    NEPHELYM_TRAITS.update(BODY_TYPES)
    NEPHELYM_TRAITS.update(TRAIT_SIZE)
    NEPHELYM_TRAITS.update(TRAIT_STAT)
    NEPHELYM_TRAITS.update(TRAIT_APPERANCE)
    NEPHELYM_TRAITS.update(TRAIT_STAT_MISC)
    NEPHELYM_TRAITS.update(TRAIT_APPERANCE_MISC)
    NEPHELYM_TRAITS.update(TRAIT_FORM)
    NEPHELYM_TRAITS.update(TRAIT_NEGATIVE)

    TRAITS_WITH_LEVELS.update(BODY_TYPES)
    TRAITS_WITH_LEVELS.update(TRAIT_STAT)
    TRAITS_WITH_LEVELS.update(TRAIT_APPERANCE)
    TRAITS_WITH_LEVELS['hedonist'] = TRAIT_NEGATIVE['hedonist']
    TRAITS_WITH_LEVELS['efficient'] = TRAIT_NEGATIVE['efficient']

    ## Nephelym Races and Sexes
    SEXES = {
        'female': b'Sex.Female\x00',
        'futa': b'Sex.Futa\x00',
        'male': b'Sex.Male\x00',
    }
    RACES = {}
    
    RACES_FEMININE = {
        'ayrshire' : b'Race.Bovaur.Ayrshire\x00',
        'minotaur' : b'Race.Bovaur.Minotaur\x00',
        'cambion' : b'Race.Demon.Cambion\x00',
        'succubus' : b'Race.Demon.Succubus\x00',
        'wyvern' : b'Race.Dragon.Wyvern\x00',
        'shark' : b'Race.Formurian.Shark\x00',
        'vulpuss' : b'Race.Foxen.Vulpuss\x00',
        'bat' : b'Race.Harpy.Bat\x00',
        'kestrel' : b'Race.Harpy.Kestrel\x00',
        'breeder' : b'Race.Human.Breeder\x00',
        'akabeko' : b'Race.Hybrid.Akabeko\x00',
        'amaru' : b'Race.Hybrid.Amaru\x00',
        'bakeneko' : b'Race.Hybrid.Bakeneko\x00',
        'basilisk' : b'Race.Hybrid.Basilisk\x00',
        'catsune' : b'Race.Hybrid.Catsune\x00',
        'daeva' : b'Race.Hybrid.Daeva\x00',
        'griffin' : b'Race.Hybrid.Griffin\x00',
        'hellhound' : b'Race.Hybrid.Hellhound\x00',
        'jabberwock' : b'Race.Hybrid.Jabberwock\x00',
        'kludde' : b'Race.Hybrid.Kludde\x00',
        'kujata' : b'Race.Hybrid.Kujata\x00',
        'kumiho' : b'Race.Hybrid.Kumiho\x00',
        'kusarikku' : b'Race.Hybrid.Kusarikku\x00',
        'lamassu' : b'Race.Hybrid.Lamassu\x00',
        'oni' : b'Race.Hybrid.Oni\x00',
        'ryu' : b'Race.Hybrid.Ryu\x00',
        'surabhi' : b'Race.Hybrid.Surabhi\x00',
        'tenko' : b'Race.Hybrid.Tenko\x00',
        'tabby' : b'Race.Neko.Tabby\x00',
        'bunny' : b'Race.Risu.Bunny\x00',
        'malakhim' : b'Race.Seraphim.Malakhim\x00',
        'elf' : b'Race.Sylvan.Elf\x00',
        'goblin' : b'Race.Sylvan.Goblin\x00',
        'oic' : b'Race.Sylvan.Orc\x00',
        'slime' : b'Race.Sylvan.Slime\x00',
        'bee' : b'Race.Thriae.Bee\x00',
        'colossus' : b'Race.Titan.Colossus\x00',
        'lykos' : b'Race.Vulwarg.Lykos\x00',
    }
    
    RACES_MALE = {
        'breeder' : b'Race.Human.Breeder\x00',
        'sionnach' : b'Race.Foxen.Sionnach\x00',
        'drake' : b'Race.Dragon.Drake\x00',
        'incubus' : b'Race.Demon.Incubus\x00',
        'bull' : b'Race.Bovaur.Bull\x00',
        'wulf' : b'Race.Vulwarg.Wulf\x00',
        'seeder' : b'Race.Starfallen.Seeder\x00',
    }
    
    RACES_FUTA = {
        'spore' : b'Race.Starfallen.Spore\x00',
    }
    
    RACES_FEMALE = {
        'carrier' : b'Race.Starfallen.Carrier\x00',
        #Crashes the game if impregnated or given feral trait.
        'fern' : b'Race.Alraune.Fern\x00',
        'fern2' : b'Race.Alraune.Fern.P2\x00',
        'blossom' : b'Race.Alraune.Blossom\x00',
    }
    
    #EVERY Race below is not a valid race for nephelyms
    RACES_NPC_FEMALE = {
        'amber' : b'Race.Bovaur.Shorthorn.Amber\x00',
        'autumn' : b'Race.Alraune.Dryad.Autumn\x00',
        'camilla' : b'Race.Sylvan.Goblin.Camilla\x00',
        'matriarch' : b'Race.Dragon.Wyvern.Matriarch\x00',
        'emissary' : b'Race.Seraphim.Archangel.Emissary\x00',
        'falene' : b'Race.Sylvan.Elf.Painted.Falene\x00',
        'fern3' : b'Race.Alraune.Fern.P3\x00',
        'fesssi' : b'Race.Lamia.Naga.Fesssi\x00',
        'kybele' : b'Race.Centaur.Kybele\x00',
        'leylanna' : b'Race.Foxen.Kitsune.Leylanna\x00',
        'megaSlime' : b'Race.Sylvan.Slime.MegaSlime\x00',
        'monarch' : b'Race.Thriae.Butterfly.Monarch\x00',
        'neela' : b'Race.Lamia.Liasis.Neela\x00',
        'parvati' : b'Race.Neko.Bengal.Parvati\x00',
        'petra' : b'Race.Risu.Bunny.Petra\x00',
        'queen' : b'Race.Thriae.Bee.Queen\x00',
        'reaper' : b'Race.Ghost.Reaper\x00',
        'romy' : b'Race.Formurian.Mermaid.Romy\x00',
        'sloth' : b'Race.Demon.MindFlayer.Sloth\x00',
        'widow' : b'Race.Thriae.Spider.Widow\x00',
        'yasmine' : b'Race.Formurian.Clam.Yasmine\x00',
    }
    
    RACES_NPC_FUTA = {
       'cassie' : b'Race.Neko.Cheshire.Cassie\x00',
       'chief' : b'Race.Sylvan.Orc.Chief\x00',
       'mirru' : b'Race.Formurian.Kraken.Mirru\x00',
    }
    
    RACES_OTHERS = {
        'mem' : b'Race.Alraune.Mushroom\x00',
        'mem' : b'Race.Bovaur.Shorthorn\x00',
        'mem' : b'Race.Demon.Gargoyle\x00',
        'mem' : b'Race.Demon.Imp\x00',
        'mem' : b'Race.Demon.Succubus.Lydia\x00',
        'mem' : b'Race.Demon.Succubus.Meredith\x00',
        'mem' : b'Race.Demon.Test\x00',
        'mem' : b'Race.Demon.Test.2\x00',
        'mem' : b'Race.Demon.Vampire\x00',
        'mem' : b'Race.Dragon.Lizard\x00',
        'mem' : b'Race.Formurian.Kraken\x00',
        'mem' : b'Race.Human.Test\x00',
        'mem' : b'Race.Hybrid.Amarok\x00',
        'mem' : b'Race.Hybrid.Aralez\x00',
        'mem' : b'Race.Hybrid.Archon\x00',
        'mem' : b'Race.Hybrid.Audumla\x00',
        'mem' : b'Race.Hybrid.Azazel\x00',
        'mem' : b'Race.Hybrid.Behemoth\x00',
        'mem' : b'Race.Hybrid.Bicorn\x00',
        'mem' : b'Race.Hybrid.Chamrosh\x00',
        'mem' : b'Race.Hybrid.Cherubim\x00',
        'mem' : b'Race.Hybrid.Hakutaku\x00',
        'mem' : b'Race.Hybrid.Huldra\x00',
        'mem' : b'Race.Hybrid.Itsumade\x00',
        'mem' : b'Race.Hybrid.Jackal\x00',
        'mem' : b'Race.Hybrid.Jinko\x00',
        'mem' : b'Race.Hybrid.Kumiho\x00',
        'mem' : b'Race.Hybrid.Kunoichi\x00',
        'mem' : b'Race.Hybrid.Kusarikku\x00',
        'mem' : b'Race.Hybrid.Lamassu\x00',
        'mem' : b'Race.Hybrid.Nandi\x00',
        'mem' : b'Race.Hybrid.Raiju\x00',
        'mem' : b'Race.Hybrid.Simargl\x00',
        'mem' : b'Race.Hybrid.Sphinx\x00',
        'mem' : b'Race.Hybrid.Tengu\x00',
        'mem' : b'Race.Hybrid.Tiamat\x00',
        'mem' : b'Race.Hybrid.Vishap\x00',
        'mem' : b'Race.Hybrid.Werecat\x00',
        'mem' : b'Race.Hybrid.Youko\x00',
        'mem' : b'Race.Lamia.Liasis\x00',
        'mem' : b'Race.Lamia.Naga\x00',
        'mem' : b'Race.Risu.Mouse\x00',
        'mem' : b'Race.Risu.Squirrel\x00',
        'mem' : b'Race.Satyr.Sheep\x00',
        'mem' : b'Race.Seraphim.Archangel\x00',
        'mem' : b'Race.Seraphim.Ophanim\x00',
        'mem' : b'Race.Sylvan.Drow\x00',
        'mem' : b'Race.Sylvan.Elf.Painted.Falene\x00',
        'mem' : b'Race.Thriae.Butterfly\x00',
        'mem' : b'Race.Thriae.Leech\x00',
        'mem' : b'Race.Thriae.Moth\x00',
        'mem' : b'Race.Thriae.Spider\x00',
        'mem' : b'Race.Titan.Behemoth\x00',
        'mem' : b'Race.Titan.Brute\x00',
        'mem' : b'Race.Titan.Jotun\x00',
        'mem' : b'Race.Titan.Ogre\x00',
        'mem' : b'Race.Titan.Ogre.Bryn\x00',
        'mem' : b'Race.Undead\x00',
        'mem' : b'Race.Undead.Ghost\x00',
        'mem' : b'Race.Undead.Oni\x00',
        'mem' : b'Race.Vulwarg.Anubis\x00',
        'mem' : b'Race.Vulwarg.Kobold\x00',
        'mem' : b'Race.Vulwarg.Wulf.Sigrun\x00',
    }
    
    RACES_FEMALE.update(RACES_FEMININE)
    RACES_FUTA.update(RACES_FEMININE)
    RACES.update(RACES_MALE)
    RACES.update(RACES_FUTA)
    RACES.update(RACES_FEMALE)
    RACES.update(RACES_NPC_FEMALE)
    RACES.update(RACES_NPC_FUTA)
    
    SEX_RACE = {
        SEXES['female'] : RACES_FEMALE,
        SEXES['futa'] : RACES_FUTA,
        SEXES['male'] : RACES_MALE,
    }

class ByteMacros:
    '''Bytecode macros used by functions'''
    ### UE Data Structures Byte representation
    ARRAY_PROPERTY = b'\x0E\x00\x00\x00\x41\x72\x72\x61\x79\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    STRUCT_PROPERTY = b'\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    INT_PROPERTY = b'\x0C\x00\x00\x00\x49\x6E\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    FLOAT_PROPERTY = b'\x0E\x00\x00\x00\x46\x6C\x6F\x61\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    _BYTE_PROPERTY = b'\x0D\x00\x00\x00\x42\x79\x74\x65\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    STRUCT_ARRAY_PROPERTY = STRUCT_PROPERTY + b'\x00'
    BYTE_PROPERTY = _BYTE_PROPERTY + b'\x01\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x4E\x6F\x6E\x65\x00\x00'
    NAME_PROPERTY = b'\x0D\x00\x00\x00\x4E\x61\x6D\x65\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    BOOL_PROPERTY = b'\x0D\x00\x00\x00\x42\x6F\x6F\x6C\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    MAP_PROPERTY = b'\x0C\x00\x00\x00\x4D\x61\x70\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    TEXT_PROPERTY = b'\x0D\x00\x00\x00\x54\x65\x78\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    
    MAP_PADDING = b'\x00\x00\x00\x00'
    STRUCT_PADDING = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    NONE = b'\x05\x00\x00\x00\x4E\x6F\x6E\x65\x00'
    GUID_PROP = b'\x05\x00\x00\x00\x47\x75\x69\x64\x00' + STRUCT_PADDING

    ### Save header macros
    GUID_HEADER = b'\x10\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x47\x75\x69\x64\x00' + STRUCT_PADDING
    PLAYER_UNIQUE_ID = b'\x0F\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x55\x6E\x69\x71\x75\x65\x49\x44\x00' + STRUCT_PROPERTY + GUID_HEADER
    PLAYERWEALTH = b'\x0D\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x57\x65\x61\x6C\x74\x68\x00'
    PLAYERBODYFLUIDS = b'\x11\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x42\x6F\x64\x79\x46\x6C\x75\x69\x64\x73\x00'
    TAGNAME = b'\x08\x00\x00\x00\x54\x61\x67\x4E\x61\x6D\x65\x00'
    #Nephelym/Breeder Block Headers
    PLAYERMONSTER = b'\x0F\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x4D\x6F\x6E\x73\x74\x65\x72\x73\x00'
    CHARACTER_DATA = b'\x0E\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x44\x61\x74\x61\x00' + STRUCT_PADDING

    ### Individual Nephelym Macros
    PLAYER_MONSTER_NAME = b'\x05\x00\x00\x00\x4E\x61\x6D\x65\x00\x0C\x00\x00\x00\x53\x74\x72\x50\x72\x6F\x70\x65\x72\x74\x79\x00'
    NEPHELYM_GUID = b'\x09\x00\x00\x00\x55\x6E\x69\x71\x75\x65\x49\x44\x00' + STRUCT_PROPERTY + GUID_HEADER
    
    VARIANT_STRUCT_PROP = b'\x08\x00\x00\x00\x56\x61\x72\x69\x61\x6E\x74\x00' + STRUCT_PROPERTY
    GAMEPLAY_TAG_CONTAINER = b'\x15\x00\x00\x00\x47\x61\x6D\x65\x70\x6C\x61\x79\x54\x61\x67\x43\x6F\x6E\x74\x61\x69\x6E\x65\x72\x00' + STRUCT_PADDING
    
    
    APPEARANCE_STRUCT_PROP = b'\x0B\x00\x00\x00\x41\x70\x70\x65\x61\x72\x61\x6E\x63\x65\x00' + STRUCT_PROPERTY
    CHARACTER_APPEARANCE = b'\x14\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x41\x70\x70\x65\x61\x72\x61\x6E\x63\x65\x00' + STRUCT_PADDING
    
    SPLATTER_STRUCT_PROP = b'\x09\x00\x00\x00\x53\x70\x6C\x61\x74\x74\x65\x72\x00' + STRUCT_PROPERTY
    FLUID_SPLATTER = b'\x0E\x00\x00\x00\x46\x6C\x75\x69\x64\x53\x70\x6C\x61\x74\x74\x65\x72\x00' + STRUCT_PADDING
    
    CITARGETVALUE_STRUCT_PROP = b'\x0E\x00\x00\x00\x43\x49\x54\x61\x72\x67\x65\x74\x56\x61\x6C\x75\x65\x00' + STRUCT_PROPERTY
    CIBUFFER_STRUCT_PROP = b'\x09\x00\x00\x00\x43\x49\x42\x75\x66\x66\x65\x72\x00' + STRUCT_PROPERTY
    CHARACTER_MORPH = b'\x0F\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x4D\x6F\x72\x70\x68\x00' + STRUCT_PADDING
    
    #FloatProp
    CIRATE  = b'\x07\x00\x00\x00\x43\x49\x52\x61\x74\x65\x00' + FLOAT_PROPERTY
    CIALPHA = b'\x08\x00\x00\x00\x43\x49\x41\x6C\x70\x68\x61\x00' + FLOAT_PROPERTY
    
    #StructProp
    APPLIEDSCHEME_STRUCT_PROP = b'\x0E\x00\x00\x00\x41\x70\x70\x6C\x69\x65\x64\x53\x63\x68\x65\x6D\x65\x00' + STRUCT_PROPERTY
    CHARACTER_APPLIED_SCHEME = b'\x17\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x41\x70\x70\x6C\x69\x65\x64\x53\x63\x68\x65\x6D\x65\x00' + STRUCT_PADDING
    STAT_STRUCT_PROP = b'\x06\x00\x00\x00\x53\x74\x61\x74\x73\x00' + STRUCT_PROPERTY
    CHARACTER_STATS = b'\x0F\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x53\x74\x61\x74\x73\x00' + STRUCT_PADDING
    
    #Parents
    MOTHER_STRUCT_PROP = b'\x07\x00\x00\x00\x4D\x6F\x74\x68\x65\x72\x00' + STRUCT_PROPERTY
    FATHER_STRUCT_PROP = b'\x07\x00\x00\x00\x46\x61\x74\x68\x65\x72\x00' + STRUCT_PROPERTY
    CHARACTER_PARENT_DATA = b'\x14\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x50\x61\x72\x65\x6E\x74\x44\x61\x74\x61\x00' + STRUCT_PADDING
    
    #Traits
    TRAITS_STRUCT_PROP = b'\x07\x00\x00\x00\x54\x72\x61\x69\x74\x73\x00' + STRUCT_PROPERTY
    PLAYERTAGS_STRUCT_PROP = b'\x0B\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x54\x61\x67\x73\x00' + STRUCT_PROPERTY
    STATES_STRUCT_PROP = b'\x07\x00\x00\x00\x53\x74\x61\x74\x65\x73\x00' + STRUCT_PROPERTY
    OFFSPRINGID_STRUCT_PROP = b'\x0C\x00\x00\x00\x4F\x66\x66\x73\x70\x72\x69\x6E\x67\x49\x44\x00' + STRUCT_PROPERTY
    LASTMATEID_STRUCT_PROP = b'\x0B\x00\x00\x00\x4C\x61\x73\x74\x4D\x61\x74\x65\x49\x44\x00' + STRUCT_PROPERTY
    LASTMATESEXCOUNT_BYTE_PROP = b'\x11\x00\x00\x00\x4C\x61\x73\x74\x4D\x61\x74\x65\x53\x65\x78\x43\x6F\x75\x6E\x74\x00' + BYTE_PROPERTY
    
    ### Offspring Macros
    OFFSPRINGBUFFER = b'\x10\x00\x00\x00\x4F\x66\x66\x73\x70\x72\x69\x6E\x67\x42\x75\x66\x66\x65\x72\x00'
    
    ### Spiritform Macros
    UNIQUEID = b'\x09\x00\x00\x00\x55\x6E\x69\x71\x75\x65\x49\x44\x00'
    SPIRITFORM_GUID = UNIQUEID + STRUCT_PROPERTY + GUID_HEADER
    PLAYERSPIRIT = b'\x0D\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x70\x69\x72\x69\x74\x00'
    PLAYERSPIRITFORM = b'\x11\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x70\x69\x72\x69\x74\x46\x6F\x72\x6D\x00'
    
    
    ### Footer Macros
    PLAYERSEXPOSITIONS = b'\x13\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x65\x78\x50\x6F\x73\x69\x74\x69\x6F\x6E\x73\x00'
    GAMEPLAY_TAG = b'\x0C\x00\x00\x00\x47\x61\x6D\x65\x70\x6C\x61\x79\x54\x61\x67\x00' + STRUCT_PADDING
    CHATACTER_DATA = b'\x0E\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x44\x61\x74\x61\x00' + STRUCT_PADDING
    PLAYEROBTAINEDVARIANTS = b'\x17\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x4F\x62\x74\x61\x69\x6E\x65\x64\x56\x61\x72\x69\x61\x6E\x74\x73\x00'
    PLAYEROBTAINEDVARIANTS_ARRAY_PROP = PLAYEROBTAINEDVARIANTS + ARRAY_PROPERTY
    PLAYERSEENVARIANTS = b'\x13\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x65\x65\x6E\x56\x61\x72\x69\x61\x6E\x74\x73\x00'
    GAMEFLAGS = b'\x0A\x00\x00\x00\x47\x61\x6D\x65\x46\x6C\x61\x67\x73\x00'
    WORLDSTATE = b'\x0B\x00\x00\x00\x57\x6F\x72\x6C\x64\x53\x74\x61\x74\x65\x00'
    SEXYWOLDSTATE = b'\x0F\x00\x00\x00\x53\x65\x78\x79\x57\x6F\x72\x6C\x64\x53\x74\x61\x74\x65\x00' + STRUCT_PADDING
    BREEDERSTATPROGRESS = b'\x14\x00\x00\x00\x42\x72\x65\x65\x64\x65\x72\x53\x74\x61\x74\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    BREEDERSTATRANKPROGRESS = b'\x18\x00\x00\x00\x42\x72\x65\x65\x64\x65\x72\x53\x74\x61\x74\x52\x61\x6E\x6B\x50\x72\x6F\x67\x72\x65\x73\x73\x00' + STRUCT_PADDING
    
    ### Preset Macros
    PRESETNAME = b'\x0B\x00\x00\x00\x50\x72\x65\x73\x65\x74\x4E\x61\x6D\x65\x00'
    PRESETNAME_NAME_PROP = PRESETNAME + NAME_PROPERTY
    SCHEME = b'\x07\x00\x00\x00\x53\x63\x68\x65\x6D\x65\x00'
    SCHEME_PROP_STRUCT = SCHEME + STRUCT_PROPERTY
    COMMON = b'\x00\x00\x00\x62\x43\x6F\x6D\x6D\x6F\x6E\x00'
    UNCOMMON = b'\x0A\x00\x00\x00\x62\x55\x6E\x63\x6F\x6D\x6D\x6F\x6E\x00'
    RARE = b'\x06\x00\x00\x00\x62\x52\x61\x72\x65\x00'
    UNIQUE = b'\x08\x00\x00\x00\x62\x55\x6E\x69\x71\x75\x65\x00'
    LEGENDARY = b'\x0B\x00\x00\x00\x62\x4C\x65\x67\x65\x6E\x64\x61\x72\x79\x00'
    RARITY_PADDING = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    RARITY_COMMON    = COMMON    + BOOL_PROPERTY + RARITY_PADDING
    RARITY_UNCOMMON  = UNCOMMON  + BOOL_PROPERTY + RARITY_PADDING
    RARITY_RARE      = RARE      + BOOL_PROPERTY + RARITY_PADDING
    RARITY_UNIQUE    = UNIQUE    + BOOL_PROPERTY + RARITY_PADDING
    RARITY_LEGENDARY = LEGENDARY + BOOL_PROPERTY + RARITY_PADDING
    
    RARITIES = [RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_UNIQUE, RARITY_LEGENDARY,]

class IO:
    '''Functions that deal with IO'''
    def load_save(self, save_name):
        with open(save_name, 'rb') as f:
            return f.read()

    def write_save(self, save_name, data_out):
        with open(save_name, 'wb') as f:
            chunk = 1024
            for bytes in [data_out[i:i+chunk] for i in range(0, len(data_out), chunk)]:
                f.write(bytes)

class GenericParsers(DictMacros, ByteMacros, IO):
    '''Generic function for parsing and reconstucting datablocks'''
    def _parse_float_property(self, float_bytes, float_macro):
        cursor = float_bytes.find(float_macro)
        if cursor == -1:
            raise Exception(f'Invalid Float: {float_macro}')
        length_start = cursor + len(float_macro)
        length_end = length_start + 8
        length_bytes = float_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        data_start = length_end + 1
        data_end = data_start + length
        return float_bytes[:cursor], float_bytes[data_start:data_end], float_bytes[data_end:]
    
    def _parse_struct_property(self, struct_bytes, struct_macro, child_macro):
        cursor = struct_bytes.find(struct_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {struct_macro}')
        length_start = cursor + len(struct_macro)
        length_end = length_start + 8
        length_bytes = struct_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        data_start = length_end + len(child_macro)
        data_end = data_start + length
        return struct_bytes[:cursor], struct_bytes[data_start:data_end], struct_bytes[data_end:]
    
    def _parse_array_property(self, array_bytes, array_macro, child_macro, child_data_size=None):
        '''Return entire array data or elements in the array if child supplied'''
        cursor = array_bytes.find(array_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {array_macro}')
        length_start = cursor + len(array_macro)
        length_end = length_start + 8
        length_bytes = array_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        child_macro += b'\x00'
        data_start = length_end + len(child_macro)
        data_end = data_start + length
        
        if child_data_size:
            data_out = [array_bytes[i:i+child_data_size] for i in range(data_start + 4, data_end, child_data_size)]
        else:
            data_out = array_bytes[data_start:data_start+length]
        return array_bytes[:cursor], data_out, array_bytes[data_start+length:]
    
    def _parse_int_property(self, int_bytes, int_macro):
        '''Return Int value in byte format'''
        cursor = int_bytes.find(int_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {int_macro}')
        length_start = cursor + len(int_macro)
        length_end = length_start + 8
        length_bytes = int_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        data_start = length_end + 1
        data_end = data_start + length
        return int_bytes[:cursor], int_bytes[data_start:data_end], int_bytes[data_end:]
    
    def _parse_name_property(self, name_bytes, name_macro):
        '''Return name value in byte format'''
        cursor = name_bytes.find(name_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {name_macro}')
        length_start = cursor + len(name_macro)
        length_end = length_start + 8
        length_bytes = name_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        data_start = length_end + 1
        data_end = data_start + length
        return name_bytes[:cursor], name_bytes[data_start+4:data_end], name_bytes[data_end:]
    
    def _parse_byte_property(self, byte_bytes, byte_macro):
        '''Return byte value in byte format'''
        cursor = byte_bytes.find(byte_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {byte_macro}')
        data_start = cursor + len(byte_macro)
        data_end = data_start + 1
        return byte_bytes[:cursor], byte_bytes[data_start:data_end], byte_bytes[data_end:]
    
    def _parse_guid(self, guid_bytes, guid_macro):
        '''Parses guid from datablock'''
        cursor = guid_bytes.find(guid_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {guid_macro}')
        guid_start = cursor + len(guid_macro)
        return guid_bytes[:cursor], guid_bytes[guid_start:guid_start + 16], guid_bytes[guid_start + 16:]
    
    def _parse_map_property(self, map_bytes, map_macro, child_macro):
        cursor = map_bytes.find(map_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {map_macro}')
        length_start = cursor + len(map_macro)
        length_end = length_start + 8
        length_bytes = map_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        child_macro += child_macro + b'\x00'
        data_start = length_end + len(child_macro)
        data_end = data_start + length
        
        data_out = map_bytes[data_start:data_start+length]
        return map_bytes[:cursor], data_out, map_bytes[data_start+length:]
    
    def _parse_array_struct_property(self, array_struct_bytes, array_macro, struct_macro, child_macro):
        # TODO Add multi-level search to ensure proper segment parsed
        cursor = array_struct_bytes.find(array_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {array_macro}')
        length_start = cursor + len(array_macro)
        length_end = length_start + 8
        length_bytes = array_struct_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        data_length_offset = 4 + len(struct_macro) + len(self.STRUCT_PROPERTY) + 8 + len(child_macro)
        data_offset = len(self.STRUCT_PROPERTY + b'\x00') + data_length_offset
        
        data_start = length_end + data_offset
        data_end = data_start + length - data_length_offset
        data_out = array_struct_bytes[data_start:data_end]
        
        return array_struct_bytes[:cursor], data_out, array_struct_bytes[data_end:]
    
    def _parse_text_property(self, text_bytes, text_macro):
        cursor = text_bytes.find(text_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {text_macro}')
        length_start = cursor + len(text_macro)
        length_end = length_start + 8
        length_bytes = text_bytes[length_start:length_end]
        length = int.from_bytes(length_bytes, 'little')
        
        data_start = length_end + 1
        data_end = data_start + length
        return text_bytes[:cursor], text_bytes[data_start:data_end], text_bytes[data_end:]
    
    
    def _get_float_property_bytes(self, float_bytes, float_macro):
        float_length = len(float_bytes)
        bytes_out = float_macro \
            + float_length.to_bytes(8, 'little') \
            + b'\x00' \
            + float_bytes
        return bytes_out
    
    def _get_struct_property_bytes(self, struct_bytes, struct_macro, child_macro):
        struct_length = len(struct_bytes)
        bytes_out = struct_macro \
            + struct_length.to_bytes(8, 'little') \
            + child_macro \
            + struct_bytes
        return bytes_out
    
    def _get_array_property_bytes(self, array_bytes, array_macro, child_macro, child_data_size=None):
        child_macro += b'\x00'
        if child_data_size:
            elements = len(array_bytes)
            array_bytes = elements.to_bytes(4, 'little') + self.list_to_bytes(array_bytes)
        array_length = len(array_bytes)
        
        bytes_out = array_macro \
            + array_length.to_bytes(8, 'little') \
            + child_macro \
            + array_bytes
        return bytes_out
    
    def _get_int_property_bytes(self, int_bytes, int_macro):
        int_length = len(int_bytes)
        bytes_out = int_macro \
            + int_length.to_bytes(8, 'little') \
            + b'\x00' \
            + int_bytes
        return bytes_out
    
    def _get_name_property_bytes(self, name_bytes, name_macro):
        name_length = len(name_bytes)
        name_full_length = name_length + 4
        bytes_out = name_macro \
            + name_full_length.to_bytes(8, 'little') \
            + b'\x00' \
            + name_length.to_bytes(4, 'little') \
            + name_bytes
        return bytes_out
    
    def _get_byte_property_bytes(self, byte_bytes, byte_macro):
        bytes_out = byte_macro \
            + byte_bytes
        return bytes_out
    
    def _get_guid_bytes(self, guid_bytes, guid_macro):
        '''Rebuild guid string'''
        return guid_macro + guid_bytes
    
    def _get_map_property_bytes(self, map_bytes, map_macro, child_macro):
        child_macro += child_macro + b'\x00'
        map_length = len(map_bytes)
        
        bytes_out = map_macro \
            + map_length.to_bytes(8, 'little') \
            + child_macro \
            + map_bytes
        return bytes_out
    
    def _get_array_struct_property_bytes(self, array_struct_bytes_list, array_macro, struct_macro, child_macro):
        bytes_out = []
        count = len(array_struct_bytes_list)
        array_struct_bytes_list_data = self.list_to_bytes([array_struct_bytes.get_data() for array_struct_bytes in array_struct_bytes_list])
        array_struct_bytes_list_data_length = len(array_struct_bytes_list_data)
        array_length = 4 + len(struct_macro) + len(self.STRUCT_PROPERTY) + 8 + len(child_macro) + array_struct_bytes_list_data_length
        
        bytes_out.append(array_macro)
        bytes_out.append(array_length.to_bytes(8, 'little'))
        bytes_out.append(self.STRUCT_PROPERTY + b'\x00')
        bytes_out.append(count.to_bytes(4, 'little'))
        bytes_out.append(struct_macro)
        bytes_out.append(self.STRUCT_PROPERTY)
        bytes_out.append(array_struct_bytes_list_data_length.to_bytes(8, 'little'))
        bytes_out.append(child_macro)
        bytes_out.append(array_struct_bytes_list_data)
        return self.list_to_bytes(bytes_out)
    
    def _get_text_property_bytes(self, text_bytes, text_macro):
        text_length = len(text_bytes)
        bytes_out = text_macro \
            + text_length.to_bytes(8, 'little') \
            + b'\x00' \
            + text_bytes
        return bytes_out
    
    
    def _try_parse_int_property(self, data_in, int_macro):
        int_macro += self.INT_PROPERTY
        try:
            pre_data, int_prop, data_in = self._parse_int_property(data_in, int_macro)
        except Exception as e:
            pre_data = b''
            int_prop = b''
        return pre_data, int_prop, data_in
    
    def _try_parse_float_property(self, data_in, float_macro):
        float_macro += self.FLOAT_PROPERTY
        try:
            pre_data, float_prop, data_in = self._parse_float_property(data_in, float_macro)
        except:
            pre_data = b''
            float_prop = b''
        return pre_data, float_prop, data_in
    
    def _try_parse_struct_property(self, data_in, struct_macro, child_macro):
        struct_macro += self.STRUCT_PROPERTY
        try:
            pre_data, struct_prop, data_in = self._parse_struct_property(data_in, struct_macro, child_macro)
        except:
            pre_data = b''
            struct_prop = b''
        return pre_data, struct_prop, data_in
    
    def _try_parse_array_property(self, data_in, array_macro, child_macro, child_data_size=None):
        array_macro += self.ARRAY_PROPERTY
        try:
            pre_data, array_prop, data_in = self._parse_array_property(data_in, array_macro, child_macro, child_data_size)
        except:
            pre_data = b''
            array_prop = b''
        return pre_data, array_prop, data_in
    
    def _try_parse_map_property(self, data_in, map_macro, child_macro):
        map_macro += self.MAP_PROPERTY
        try:
            pre_data, map_prop, data_in = self._parse_map_property(data_in, map_macro, child_macro)
        except:
            pre_data = b''
            map_prop = b''
        return pre_data, map_prop, data_in
    
    def _try_parse_name_property(self, data_in, name_macro):
        name_macro += self.NAME_PROPERTY
        try:
            pre_data, name_prop, data_in = self._parse_name_property(data_in, name_macro)
        except:
            pre_data = b''
            name_prop = b''
        return pre_data, name_prop, data_in
    
    def _try_parse_array_struct_property(self, data_in, array_macro, struct_macro, child_macro):
        array_macro += self.ARRAY_PROPERTY
        try:
            pre_data, array_struct_prop, data_in = self._parse_array_struct_property(data_in, array_macro, struct_macro, child_macro)
        except:
            pre_data = b''
            array_struct_prop = b''
        return pre_data, array_struct_prop, data_in
    
    def _try_parse_text_property(self, data_in, text_macro):
        text_macro += self.TEXT_PROPERTY
        try:
            pre_data, text_prop, data_in = self._parse_text_property(data_in, text_macro)
        except:
            pre_data = b''
            text_prop = b''
        return pre_data, text_prop, data_in
    
    
    def _try_get_int_property_bytes(self, data_in, int_macro):
        if data_in == b'':
            data = b''
        else:
            int_macro += self.INT_PROPERTY
            data = self._get_int_property_bytes(data_in, int_macro)
        return data
    
    def _try_get_float_property_bytes(self, data_in, float_macro):
        if data_in == b'':
            data = b''
        else:
            float_macro += self.FLOAT_PROPERTY
            data = self._get_float_property_bytes(data_in, float_macro)
        return data
    
    def _try_get_struct_property_bytes(self, data_in, struct_macro, child_macro):
        if data_in == b'':
            data = b''
        else:
            struct_macro += self.STRUCT_PROPERTY
            data = self._get_struct_property_bytes(data_in, struct_macro, child_macro)
        return data
    
    def _try_get_array_property_bytes(self, data_in, array_macro, child_macro, child_data_size=None):
        if data_in == b'':
            data = b''
        else:
            array_macro += self.ARRAY_PROPERTY
            data = self._get_array_property_bytes(data_in, array_macro, child_macro, child_data_size)
        return data
    
    def _try_get_map_property_bytes(self, data_in, map_macro, child_macro):
        if data_in == b'':
            data = b''
        else:
            map_macro += self.MAP_PROPERTY
            data = self._get_map_property_bytes(data_in, map_macro, child_macro)
        return data
    
    def _try_get_name_property_bytes(self, data_in, name_macro):
        if data_in == b'':
            data = b''
        else:
            name_macro += self.NAME_PROPERTY
            data = self._get_name_property_bytes(data_in, name_macro)
        return data
    
    def _try_get_array_struct_property_bytes(self, data_in, array_macro, struct_macro, child_macro):
        if data_in == []:
            data_out = b''
        else:
            array_macro += self.ARRAY_PROPERTY
            data_out = self._get_array_struct_property_bytes(data_in, array_macro, struct_macro, child_macro)
        return data_out
    
    def _try_get_text_property_bytes(self, data_in, text_macro):
        if data_in == b'':
            data_out = b''
        else:
            text_macro += self.TEXT_PROPERTY
            data_out = self._get_text_property_bytes(data_in, text_macro)
        return data_out
    
    
    def list_to_bytes(self, byte_list):
        '''
        convert list of bytes to bytes.
        Noticable speed up in get_data functions when large amount of data needs to be appended
        Byte array is multible so appending data is quick. Only one conversion is needed to convert to bytes
        bytes are immutible so many new instances of bytes are created to append all the small byte pieces
        '''
        out_array = bytearray()
        for x in byte_list:
            out_array.extend(x)
        return bytes(out_array)

    def split_byte_list(self, bytes_in):
        out_list = []
        if len(bytes_in) > 0:
            count = int.from_bytes(bytes_in[:4], 'little')
            bytes_in = bytes_in[4:]
            for _ in range(count):
                length = int.from_bytes(bytes_in[:4], 'little')
                data = bytes_in[:4+length]
                out_list.append(data)
                bytes_in = bytes_in[4+length:]
        return out_list, bytes_in


'''Header Classes'''
class Header(GenericParsers):
    '''Header Parser'''
    BODYFLUIDS = b'\x0B\x00\x00\x00\x42\x6F\x64\x79\x46\x6C\x75\x69\x64\x73\x00' + ByteMacros.STRUCT_PADDING
    def __init__(self, header_data):
        self._parse_header_data(header_data)
    
    def _parse_header_data(self, header_data):
        self.gvas,            header_data = self._parse_gvas(header_data)
        _, self.playerguid,   header_data = self._parse_guid(header_data, self.PLAYER_UNIQUE_ID)
        _, self.playerwealth, header_data = self._try_parse_array_property(header_data, self.PLAYERWEALTH, self.INT_PROPERTY, 4)
        _, playerbodyfluids,  header_data = self._try_parse_array_struct_property(header_data, self.PLAYERBODYFLUIDS, self.PLAYERBODYFLUIDS, self.BODYFLUIDS)
        self.remain = header_data
        
        self.playerbodyfluids = PlayerBodyFluids(playerbodyfluids)
    
    def _parse_gvas(self, header_data):
        cursor = header_data.find(self.PLAYER_UNIQUE_ID)
        if cursor == -1:
            raise Exception('Invalid Header: PLAYER_UNIQUE_ID')
        return header_data[:cursor], header_data[cursor:]
    
    def get_data(self):
        data_out = []
        data_out.append(self.gvas)
        data_out.append(self._get_guid_bytes(self.playerguid, self.PLAYER_UNIQUE_ID))
        data_out.append(self._try_get_array_property_bytes(self.playerwealth, self.PLAYERWEALTH, self.INT_PROPERTY, 4))
        data_out.append(self._try_get_array_struct_property_bytes(self.playerbodyfluids.get_data(), self.PLAYERBODYFLUIDS, self.PLAYERBODYFLUIDS, self.BODYFLUIDS))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class PlayerBodyFluids(GenericParsers):
    RACETAG = b'\x08\x00\x00\x00\x52\x61\x63\x65\x54\x61\x67\x00'
    MILKML = b'\x08\x00\x00\x00\x4D\x69\x6C\x6B\x5F\x6D\x6C\x00'
    SEMENML = b'\x09\x00\x00\x00\x53\x65\x6D\x65\x6E\x5F\x6D\x6C\x00'
    MAXMILKML = b'\x0B\x00\x00\x00\x4D\x61\x78\x4D\x69\x6C\x6B\x5F\x6D\x6C\x00'
    MAXSEMENML = b'\x0C\x00\x00\x00\x4D\x61\x78\x53\x65\x6D\x65\x6E\x5F\x6D\x6C\x00'
    def __init__(self, playerbodyfluids_data):
        self._parse_playerbodyfluids_data(playerbodyfluids_data)
    
    def _parse_playerbodyfluids_data(self, playerbodyfluids_data):
        self.bodyfluids = []
        while len(playerbodyfluids_data) > 0:
            _, racetag,    playerbodyfluids_data = self._try_parse_struct_property(playerbodyfluids_data, self.RACETAG, self.GAMEPLAY_TAG)
            _, milkml,     playerbodyfluids_data = self._try_parse_int_property(playerbodyfluids_data, self.MILKML)
            _, semenml,    playerbodyfluids_data = self._try_parse_int_property(playerbodyfluids_data, self.SEMENML)
            _, maxmilkml,  playerbodyfluids_data = self._try_parse_int_property(playerbodyfluids_data, self.MAXMILKML)
            _, maxsemenml, playerbodyfluids_data = self._try_parse_int_property(playerbodyfluids_data, self.MAXSEMENML)
            playerbodyfluids_data = playerbodyfluids_data[len(self.NONE):]
            self.bodyfluids.append(BodyFluid(racetag, milkml, semenml, maxmilkml, maxsemenml, self.NONE))
    
    def get_data(self):
        return self.bodyfluids

class BodyFluid(PlayerBodyFluids):
    def __init__(self, racetag, milkml, semenml, maxmilkml, maxsemenml, remain):
        _, self.racetag, _ = self._try_parse_name_property(racetag, self.TAGNAME)
        self.milkml = milkml
        self.semenml = semenml
        self.maxmilkml = maxmilkml
        self.maxsemenml = maxsemenml
        self.remain = remain
    
    def get_data(self):
        data_out = []
        racetag = self._try_get_name_property_bytes(self.racetag, self.TAGNAME) + self.NONE
        data_out.append(self._try_get_struct_property_bytes(racetag, self.RACETAG, self.GAMEPLAY_TAG))
        data_out.append(self._try_get_int_property_bytes(self.milkml, self.MILKML))
        data_out.append(self._try_get_int_property_bytes(self.semenml, self.SEMENML))
        data_out.append(self._try_get_int_property_bytes(self.maxmilkml, self.MAXMILKML))
        data_out.append(self._try_get_int_property_bytes(self.maxsemenml, self.MAXSEMENML))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


'''Base Nephelym Classes'''
class NephelymBase(GenericParsers):
    '''
    Base Data structure for Nephelyms.
    Used for parsing specific datablocks of a nephelym
    '''
    def __str__(self):
        return f'Nephelym\n{self.name} {self.sex} {self.race} {self.guid}'
    
    def __init__(self, nephelym_data):
        self._parse_nephelym_data(nephelym_data)
    
    def _parse_nephelym_data(self, nephelym_data):
        _, self.name,             nephelym_data = self._parse_name(nephelym_data)
        _, self.guid,             nephelym_data = self._parse_guid(nephelym_data, self.NEPHELYM_GUID)
        _, self.race, self.sex,   nephelym_data = self._parse_variant(nephelym_data)
        _, appearance,            nephelym_data = self._parse_struct_property(nephelym_data, self.APPEARANCE_STRUCT_PROP,    self.CHARACTER_APPEARANCE)
        _, self.splatter,         nephelym_data = self._parse_struct_property(nephelym_data, self.SPLATTER_STRUCT_PROP,      self.FLUID_SPLATTER)
        _, self.citargetvalue,    nephelym_data = self._parse_struct_property(nephelym_data, self.CITARGETVALUE_STRUCT_PROP, self.CHARACTER_MORPH)
        _, self.cibuffer,         nephelym_data = self._parse_struct_property(nephelym_data, self.CIBUFFER_STRUCT_PROP,      self.CHARACTER_MORPH)
        _, self.cirate,           nephelym_data = self._parse_float_property(nephelym_data,  self.CIRATE)
        _, self.cialpha,          nephelym_data = self._parse_float_property(nephelym_data,  self.CIALPHA)
        _, self.appliedscheme,    nephelym_data = self._parse_struct_property(nephelym_data, self.APPLIEDSCHEME_STRUCT_PROP, self.CHARACTER_APPLIED_SCHEME)
        _, self.stats,            nephelym_data = self._parse_struct_property(nephelym_data, self.STAT_STRUCT_PROP,          self.CHARACTER_STATS)
        _, self.mother,           nephelym_data = self._parse_struct_property(nephelym_data, self.MOTHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        _, self.father,           nephelym_data = self._parse_struct_property(nephelym_data, self.FATHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        _, self.traits,           nephelym_data = self._parse_traits(nephelym_data)
        _, self.playertags,       nephelym_data = self._parse_struct_property(nephelym_data, self.PLAYERTAGS_STRUCT_PROP,    self.GAMEPLAY_TAG_CONTAINER)
        _, self.states,           nephelym_data = self._parse_struct_property(nephelym_data, self.STATES_STRUCT_PROP,        self.GAMEPLAY_TAG_CONTAINER)
        _, self.offspringid,      nephelym_data = self._parse_struct_property(nephelym_data, self.OFFSPRINGID_STRUCT_PROP,   self.GUID_PROP)
        _, self.lastmateid,       nephelym_data = self._parse_struct_property(nephelym_data, self.LASTMATEID_STRUCT_PROP,    self.GUID_PROP)
        _, self.lastmatesexcount, nephelym_data = self._parse_byte_property(nephelym_data, self.LASTMATESEXCOUNT_BYTE_PROP)
        self.appearance = Appearance(appearance)
        self.remain = nephelym_data
    
    def _parse_traits(self, nephelym_data):
        cursor = nephelym_data.find(self.TRAITS_STRUCT_PROP)
        if cursor == -1:
            raise Exception('Invalid Nephelym: TRAITS_STRUCT_PROP')
        traits_index = cursor + len(self.TRAITS_STRUCT_PROP) + 8
        _, traits, post_block = self._parse_gameplaytags(nephelym_data[traits_index:])
        return nephelym_data[:cursor], traits, post_block
    
    def _parse_variant(self, nephelym_data):
        cursor = nephelym_data.find(self.VARIANT_STRUCT_PROP)
        if cursor == -1:
            raise Exception('Invalid Nephelym: VARIANT_STRUCT_PROP')
        tags_index = cursor + len(self.VARIANT_STRUCT_PROP) + 8
        _, tags, post_block = self._parse_gameplaytags(nephelym_data[tags_index:])
        return nephelym_data[:cursor], tags[0], tags[1], post_block
    
    def _parse_gameplaytags(self, nephelym_data):
        '''Parse Gameplay tag Containers'''
        cursor = nephelym_data.find(self.GAMEPLAY_TAG_CONTAINER)
        if cursor == -1:
            raise Exception('Invalid Nephelym: GAMEPLAY_TAG_CONTAINER')
        container_start = cursor + len(self.GAMEPLAY_TAG_CONTAINER)
        container_elements = int.from_bytes(nephelym_data[container_start:container_start + 4], 'little')
        data_index = container_start + 4
        tags = []
        for x in range(container_elements):
            tag_length = int.from_bytes(nephelym_data[data_index:data_index + 4], 'little')
            data_index += tag_length + 4
            tags.append(nephelym_data[data_index-tag_length:data_index])
        return nephelym_data[:cursor], tags, nephelym_data[data_index:]
    
    def _parse_name(self, nephelym_data):
        '''Parses name from datablock'''
        cursor = nephelym_data.find(self.PLAYER_MONSTER_NAME)
        if cursor == -1:
            raise Exception('Invalid Nephelym: Name Missing')
        name_length_start = cursor + len(self.PLAYER_MONSTER_NAME) + 9
        name_length_end = name_length_start + 4
        name_length_bytes = nephelym_data[name_length_start:name_length_end]
        name_length = int.from_bytes(name_length_bytes, 'little')
        return nephelym_data[:cursor], nephelym_data[name_length_end:name_length_end + name_length], nephelym_data[name_length_end + name_length:]
    
    def _get_traits_bytes(self, traits):
        gameplay_tags_bytes = self._get_gameplaytags(traits)
        tags_length = len(gameplay_tags_bytes) - len(self.GAMEPLAY_TAG_CONTAINER)
        bytes_out = self.TRAITS_STRUCT_PROP \
            + tags_length.to_bytes(8, 'little') \
            + gameplay_tags_bytes
        return bytes_out
    
    def _get_variant_bytes(self, tags):
        gameplay_tags_bytes = self._get_gameplaytags(tags)
        tags_length = len(gameplay_tags_bytes) - len(self.GAMEPLAY_TAG_CONTAINER)
        bytes_out = self.VARIANT_STRUCT_PROP \
            + tags_length.to_bytes(8, 'little') \
            + gameplay_tags_bytes
        return bytes_out
    
    def _get_gameplaytags(self, tags):
        '''Returns bytes for game_play_tags with input tags'''
        bytes_out = self.GAMEPLAY_TAG_CONTAINER + len(tags).to_bytes(4, 'little')
        for tag in tags:
            bytes_out += len(tag).to_bytes(4, 'little') + tag
        return bytes_out
    
    def _get_name_bytes(self, name):
        '''Rebuild name string'''
        name_length = len(name)
        name_bytes = self.PLAYER_MONSTER_NAME \
            + (name_length+4).to_bytes(8, 'little') \
            + b'\x00' \
            + name_length.to_bytes(4, 'little') \
            + name
        return name_bytes
    
    def _format_trait(self, trait, level):
        if trait in self.NEPHELYM_TRAITS:
            new_trait = self.NEPHELYM_TRAITS[trait]
        elif trait in self.NEPHELYM_TRAITS.values():
            new_trait = trait
        else:
            raise Exception(f'{trait} not a valid Trait')
        
        if new_trait in self.TRAITS_WITH_LEVELS.values():
            if level in self.TRAITS_LEVEL:
                new_trait += self.TRAITS_LEVEL[level]
            elif level in self.TRAITS_LEVEL.values():
                new_trait += level
            else:
                raise Exception(f'{level} not a valid level')
        return new_trait
    
    def _check_sex(self):
        '''Check if the new sex is a possibility for the race'''
        if self.race in self.SEX_RACE[self.sex].values():
            return
        else:
            for sex in self.SEXES:
                self.sex = self.SEXES[sex]
                if self.race in self.SEX_RACE[self.sex].values():
                    return
    
    def change_appearance(self, nephelym):
        self.appearance = nephelym.appearance
    
    def change_race(self, race):
        if race in self.RACES:
            self.race = self.RACES[race]
        elif race in self.RACES.values():
            self.race = race
        else:
            raise Exception(f'{race} not a valid race')
        self._check_sex()
    
    def change_sex(self, sex):
        if sex in self.SEXES:
            self.sex = self.SEXES[sex]
        elif sex in self.SEXES.values():
            self.sex = sex
        else:
            raise Exception(f'{sex} not a valid sex')
        self._check_sex()
    
    def get_data(self):
        '''
        Takes all the information in the Nephelym and returns a complete datablock in save format
        Order doesn't seem to matter, but comparison is easier.
        '''
        data_out = []
        data_out.append(self._get_name_bytes(self.name))
        data_out.append(self._get_guid_bytes(self.guid, self.NEPHELYM_GUID))
        data_out.append(self._get_variant_bytes([self.race, self.sex, ]))
        data_out.append(self._get_struct_property_bytes(self.appearance.get_data(), self.APPEARANCE_STRUCT_PROP, self.CHARACTER_APPEARANCE))
        data_out.append(self._get_struct_property_bytes(self.splatter, self.SPLATTER_STRUCT_PROP, self.FLUID_SPLATTER))
        data_out.append(self._get_struct_property_bytes(self.citargetvalue, self.CITARGETVALUE_STRUCT_PROP, self.CHARACTER_MORPH))
        data_out.append(self._get_struct_property_bytes(self.cibuffer, self.CIBUFFER_STRUCT_PROP, self.CHARACTER_MORPH))
        data_out.append(self._get_float_property_bytes(self.cirate, self.CIRATE))
        data_out.append(self._get_float_property_bytes(self.cialpha, self.CIALPHA))
        data_out.append(self._get_struct_property_bytes(self.appliedscheme, self.APPLIEDSCHEME_STRUCT_PROP, self.CHARACTER_APPLIED_SCHEME))
        data_out.append(self._get_struct_property_bytes(self.stats, self.STAT_STRUCT_PROP, self.CHARACTER_STATS))
        data_out.append(self._get_struct_property_bytes(self.mother, self.MOTHER_STRUCT_PROP, self.CHARACTER_PARENT_DATA))
        data_out.append(self._get_struct_property_bytes(self.father, self.FATHER_STRUCT_PROP, self.CHARACTER_PARENT_DATA))
        data_out.append(self._get_traits_bytes(self.traits))
        data_out.append(self._get_struct_property_bytes(self.playertags, self.PLAYERTAGS_STRUCT_PROP, self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._get_struct_property_bytes(self.states, self.STATES_STRUCT_PROP, self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._get_struct_property_bytes(self.offspringid, self.OFFSPRINGID_STRUCT_PROP, self.GUID_PROP))
        data_out.append(self._get_struct_property_bytes(self.lastmateid, self.LASTMATEID_STRUCT_PROP, self.GUID_PROP))
        data_out.append(self._get_byte_property_bytes(self.lastmatesexcount, self.LASTMATESEXCOUNT_BYTE_PROP))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)
    
    def copy(self):
        '''get an exact copy of current nephelym'''
        return self.__class__(self.get_data())

class Nephelym(NephelymBase):
    '''Class for Nephelyms inclused several functions for modifying a Nephelym'''
    def __init__(self, nephelym_data):
        super().__init__(nephelym_data)
    
    def new_guid(self, guid=None):
        '''Creates a new guid for the nephelym'''
        if guid is None:
            guid = bytes.fromhex(uuid.uuid4().hex)
        self.guid = guid
    
    def replace_parent_guid(self, parent_block, guid=None):
        '''Returns the input parent block with a new guid'''
        if guid is None:
            guid = bytes.fromhex(uuid.uuid4().hex)
        cursor = parent_block.find(self.NEPHELYM_GUID)
        if cursor == -1:
            raise Exception('Invalid Nephelym: GUID')
        guid_start = cursor + len(self.NEPHELYM_GUID)
        return parent_block[:guid_start] + guid + parent_block[guid_start + 16:]
    
    def replace_mother_guid(self, guid=None):
        self.mother = self.replace_parent_guid(self.mother, guid)
    
    def replace_father_guid(self, guid=None):
        self.father = self.replace_parent_guid(self.father, guid)
    
    def add_trait(self, trait, level='3'):
        self.traits.append(self._format_trait(trait, level))
    
    def all_positive_traits(self):
        for trait in self.NEPHELYM_TRAITS:
            if trait in self.TRAIT_NEGATIVE:
                continue
            if trait in self.TRAIT_SIZE:
                continue
            new_trait = self._format_trait(trait, '3')
            self.traits.append(new_trait)
    
    def all_traits(self):
        for trait in self.NEPHELYM_TRAITS:
            new_trait = self._format_trait(trait, '3')
            self.traits.append(new_trait)
    
    def remove_all_traits(self):
        self.traits = []
    
    def remove_trait(self, trait, level='3'):
        remove_trait = self._format_trait(trait, level)
        if remove_trait in self.traits:
            self.traits.remove(remove_trait)
    
    def change_name(self, name):
        if type(name) is str:
            self.name = name.encode('utf-8') + b'\x00'
        elif type(name) is bytes:
            if name[-1:] != b'\x00':
                name += b'\x00'
            self.name = name
        else:
            raise Exception(f'{name} is not a valid name')
    
    def change_size(self, size):
        if size in self.TRAIT_SIZE:
            new_size = self.TRAIT_SIZE[size]
        elif size in self.TRAIT_SIZE.values():
            new_size = size
        else:
            raise Exception(f'{race} not a valid race')
        for size in self.TRAIT_SIZE:
            self.remove_trait(size)
        self.add_trait(new_size)
    
    def change_stat_level(self, stat, level):
        '''Change the stats ranks'''
        if stat not in self.STAT_RANKS:
            raise Exception(f'Invalid stat {stat}')
        if level not in self.STAT_RANK_LEVEL:
            raise Exception(f'Invalid stat level{level}')
        
        stat_property = self.STAT_RANKS[stat] + self.BYTE_PROPERTY
        cursor = self.stats.find(stat_property)
        if cursor == -1:
            raise Exception('Invalid Nephelym: GUID')
        stat_rank_start = cursor + len(stat_property)
        
        self.stats = self.stats[:stat_rank_start] + self.STAT_RANK_LEVEL[level] + self.stats[stat_rank_start+1:]
    
    def replace_all_stat_levels(self, level):
        for stat in self.STAT_RANKS:
            self.change_stat_level(stat, level)
    
    def clone(self):
        clone = self.copy()
        clone.new_guid()
        clone.replace_mother_guid()
        clone.replace_father_guid()
        return clone

class NephelymPreset(NephelymBase):
    def __str__(self):
        return f'Preset\n{self.name} {self.sex} {self.race}'
    
    def __init__(self, preset_file):
        self.preset_file = preset_file
        preset_data = self.load_save(preset_file)
        self._parse_preset(preset_data)
    
    def _parse_preset(self, preset_data):
        self.gvas,              preset_data = self._parse_gvas(preset_data)
        _, self.name,           preset_data = self._parse_name_property(preset_data, self.PRESETNAME_NAME_PROP)
        _, self.race, self.sex, preset_data = self._parse_variant(preset_data)
        _, appearance,          preset_data = self._parse_struct_property(preset_data, self.SCHEME_PROP_STRUCT, self.CHARACTER_APPEARANCE)
        _, self.rarities,       preset_data = self._parse_rarities(preset_data)
        self.remain = preset_data
        self.appearance = Appearance(appearance)
    
    def _parse_gvas(self, preset_data):
        cursor = preset_data.find(self.PRESETNAME_NAME_PROP)
        if cursor == -1:
            raise Exception('Invalid Header: PRESETNAME_NAME_PROP')
        return preset_data[:cursor], preset_data[cursor:]
    
    def _parse_rarities(self, preset_data):
        rarities = []
        data_end = 0
        predata = 0
        first = True
        for rarity in self.RARITIES:
            cursor = preset_data.find(rarity)
            if cursor == -1:
                continue
            rarities.append(rarity)
            data_end = cursor + len(rarity)
            if first:
                first = False
                predata = cursor
        return preset_data[:predata], rarities, preset_data[data_end:]
    
    def _get_rarities(self, rarities):
        return self.list_to_bytes(rarities)
    
    def get_data(self):
        data_out = []
        data_out.append(self.gvas)
        data_out.append(self._get_name_property_bytes(self.name, self.PRESETNAME_NAME_PROP))
        data_out.append(self._get_variant_bytes([self.race, self.sex]))
        data_out.append(self._get_struct_property_bytes(self.appearance.get_data(), self.SCHEME_PROP_STRUCT, self.CHARACTER_APPEARANCE))
        return self.list_to_bytes(data_out)

class PlayerSpiritForm(NephelymBase):
    def __init__(self, spiritform_data):
        self._parse_spiritform_data(spiritform_data)
    
    def _parse_spiritform_data(self, spiritform_data):
        _, self.guid,           spiritform_data = self._parse_guid(spiritform_data, self.SPIRITFORM_GUID)
        _, self.race, self.sex, spiritform_data = self._parse_race_sex(spiritform_data)
        _, appearance,          spiritform_data = self._parse_struct_property(spiritform_data, self.APPEARANCE_STRUCT_PROP,    self.CHARACTER_APPEARANCE)
        _, self.appliedscheme,  spiritform_data = self._parse_struct_property(spiritform_data, self.APPLIEDSCHEME_STRUCT_PROP, self.CHARACTER_APPLIED_SCHEME)
        _, self.mother,         spiritform_data = self._parse_struct_property(spiritform_data, self.MOTHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        _, self.father,         spiritform_data = self._parse_struct_property(spiritform_data, self.FATHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        self.remain = spiritform_data
        self.appearance = Appearance(appearance)
    
    def _parse_race_sex(self, nephelym_data):
        '''Spiritform doesn't have variant block if using games default spiritform for female. Female Vulpuss'''
        try:
            pre_data, race, sex, nephelym_data = self._parse_variant(nephelym_data)
        except:
            race = self.RACES_FEMALE['vulpuss']
            sex = self.SEXES['female']
            pre_data = b''
        return pre_data, race, sex, nephelym_data
    
    def change_form(self, nephelym):
        '''Update spirit form to be incoming nephelym'''
        self.change_appearance(nephelym)
        self.change_sex(nephelym.sex)
        self.change_race(nephelym.race)
    
    def get_data(self):
        data_out = []
        data_out.append(self._get_guid_bytes(self.guid, self.SPIRITFORM_GUID))
        data_out.append(self._get_variant_bytes([self.race, self.sex, ]))
        data_out.append(self._get_struct_property_bytes(self.appearance.get_data(), self.APPEARANCE_STRUCT_PROP, self.CHARACTER_APPEARANCE))
        data_out.append(self._get_struct_property_bytes(self.appliedscheme, self.APPLIEDSCHEME_STRUCT_PROP, self.CHARACTER_APPLIED_SCHEME))
        data_out.append(self._get_struct_property_bytes(self.mother, self.MOTHER_STRUCT_PROP, self.CHARACTER_PARENT_DATA))
        data_out.append(self._get_struct_property_bytes(self.father, self.FATHER_STRUCT_PROP, self.CHARACTER_PARENT_DATA))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


'''Appearance Classes'''
class Appearance(GenericParsers):
    TAGS  = b'\x05\x00\x00\x00\x54\x61\x67\x73\x00'
    MORPH = b'\x06\x00\x00\x00\x4D\x6F\x72\x70\x68\x00'
    PHYSICS = b'\x08\x00\x00\x00\x50\x68\x79\x73\x69\x63\x73\x00'
    BASESHAPE = b'\x0A\x00\x00\x00\x42\x61\x73\x65\x53\x68\x61\x70\x65\x00'
    CHUBBYSHAPE = b'\x0C\x00\x00\x00\x43\x68\x75\x62\x62\x79\x53\x68\x61\x70\x65\x00'
    SLENDERSHAPE = b'\x0D\x00\x00\x00\x53\x6C\x65\x6E\x64\x65\x72\x53\x68\x61\x70\x65\x00'
    MEATYSHAPE = b'\x0B\x00\x00\x00\x4D\x65\x61\x74\x79\x53\x68\x61\x70\x65\x00'
    MATERIAL = b'\x09\x00\x00\x00\x4D\x61\x74\x65\x72\x69\x61\x6C\x00'
    EYERINDEX = b'\x0A\x00\x00\x00\x45\x79\x65\x52\x49\x6E\x64\x65\x78\x00'
    EYELINDEX = b'\x0A\x00\x00\x00\x45\x79\x65\x4C\x49\x6E\x64\x65\x78\x00'
    EYEBROWINDEX = b'\x0D\x00\x00\x00\x45\x79\x65\x62\x72\x6F\x77\x49\x6E\x64\x65\x78\x00'
    FACEDECORINDEX = b'\x0F\x00\x00\x00\x46\x61\x63\x65\x44\x65\x63\x6F\x72\x49\x6E\x64\x65\x78\x00'
    BODYDECORINDEX = b'\x0F\x00\x00\x00\x42\x6F\x64\x79\x44\x65\x63\x6F\x72\x49\x6E\x64\x65\x78\x00'
    BODYMARKSINDEX = b'\x0F\x00\x00\x00\x42\x6F\x64\x79\x4D\x61\x72\x6B\x73\x49\x6E\x64\x65\x78\x00'
    ADDITIONALMATERIALMASKINDEX = b'\x1C\x00\x00\x00\x41\x64\x64\x69\x74\x69\x6F\x6E\x61\x6C\x4D\x61\x74\x65\x72\x69\x61\x6C\x4D\x61\x73\x6B\x49\x6E\x64\x65\x78\x00'
    ADDITIONALMATERIALINDEX = b'\x18\x00\x00\x00\x41\x64\x64\x69\x74\x69\x6F\x6E\x61\x6C\x4D\x61\x74\x65\x72\x69\x61\x6C\x49\x6E\x64\x65\x78\x00'
    ATTACHMENTMATERIAL = b'\x13\x00\x00\x00\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x4D\x61\x74\x65\x72\x69\x61\x6C\x00'
    TORSOATTACHMENTINDEX = b'\x15\x00\x00\x00\x54\x6F\x72\x73\x6F\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    PUBICHAIRINDEX = b'\x0F\x00\x00\x00\x50\x75\x62\x69\x63\x48\x61\x69\x72\x49\x6E\x64\x65\x78\x00'
    HEADATTACHMENTINDEX = b'\x14\x00\x00\x00\x48\x65\x61\x64\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    HEADEXTRAATTACHMENTINDEX = b'\x19\x00\x00\x00\x48\x65\x61\x64\x45\x78\x74\x72\x61\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    LEGSATTACHMENTINDEX = b'\x14\x00\x00\x00\x4C\x65\x67\x73\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    ARMSATTACHMENTINDEX = b'\x14\x00\x00\x00\x41\x72\x6D\x73\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    TAILATTACHMENTINDEX = b'\x14\x00\x00\x00\x54\x61\x69\x6C\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    WINGATTACHMENTINDEX = b'\x14\x00\x00\x00\x57\x69\x6E\x67\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    EARSATTACHMENTINDEX = b'\x14\x00\x00\x00\x45\x61\x72\x73\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    HAIRATTACHMENTINDEX = b'\x14\x00\x00\x00\x48\x61\x69\x72\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    FACIALHAIRINDEX = b'\x10\x00\x00\x00\x46\x61\x63\x69\x61\x6C\x48\x61\x69\x72\x49\x6E\x64\x65\x78\x00'
    DICKATTACHMENTINDEX = b'\x14\x00\x00\x00\x44\x69\x63\x6B\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    ACCESSORYATTACHMENTINDEX = b'\x19\x00\x00\x00\x41\x63\x63\x65\x73\x73\x6F\x72\x79\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    COLLARATTACHMENTINDEX = b'\x16\x00\x00\x00\x43\x6F\x6C\x6C\x61\x72\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    AMBIENTPARTICLEATTACHMENTINDEX = b'\x1F\x00\x00\x00\x41\x6D\x62\x69\x65\x6E\x74\x50\x61\x72\x74\x69\x63\x6C\x65\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x49\x6E\x64\x65\x78\x00'
    UPPERCLOTHINGINDEX = b'\x13\x00\x00\x00\x55\x70\x70\x65\x72\x43\x6C\x6F\x74\x68\x69\x6E\x67\x49\x6E\x64\x65\x78\x00'
    LOWERCLOTHINGINDEX = b'\x13\x00\x00\x00\x4C\x6F\x77\x65\x72\x43\x6C\x6F\x74\x68\x69\x6E\x67\x49\x6E\x64\x65\x78\x00'
    UNDERWEARINDEX = b'\x0F\x00\x00\x00\x55\x6E\x64\x65\x72\x77\x65\x61\x72\x49\x6E\x64\x65\x78\x00'
    BOOTSINDEX = b'\x0B\x00\x00\x00\x42\x6F\x6F\x74\x73\x49\x6E\x64\x65\x78\x00'
    IDLEANIMATIONINDEX = b'\x13\x00\x00\x00\x49\x64\x6C\x65\x41\x6E\x69\x6D\x61\x74\x69\x6F\x6E\x49\x6E\x64\x65\x78\x00'
    
    BOUNCE_PHYSICS = b'\x0E\x00\x00\x00\x42\x6F\x75\x6E\x63\x65\x50\x68\x79\x73\x69\x63\x73\x00' + ByteMacros.STRUCT_PADDING
    BODY_SHAPE = b'\x0A\x00\x00\x00\x42\x6F\x64\x79\x53\x68\x61\x70\x65\x00' + ByteMacros.STRUCT_PADDING
    CHARACTER_MATERIAL = b'\x12\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x4D\x61\x74\x65\x72\x69\x61\x6C\x00' + ByteMacros.STRUCT_PADDING
    CHARACTER_ATTACHMENT_SCHEME = b'\x1A\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x53\x63\x68\x65\x6D\x65\x00' + ByteMacros.STRUCT_PADDING
    
    def __init__(self, appearance_data):
        self._parse_appearance_data(appearance_data)
    
    def _parse_appearance_data(self, appearance_data):
        _, tags,                                appearance_data = self._try_parse_struct_property(appearance_data, self.TAGS, self.GAMEPLAY_TAG_CONTAINER)
        _, morph,                               appearance_data = self._try_parse_struct_property(appearance_data, self.MORPH,       self.CHARACTER_MORPH)
        if appearance_data[:len(self.PHYSICS)] == self.PHYSICS:
            _, physics,                         appearance_data = self._try_parse_struct_property(appearance_data, self.PHYSICS, self.BOUNCE_PHYSICS)
            _, baseshape,                       appearance_data = self._try_parse_struct_property(appearance_data, self.BASESHAPE, self.BODY_SHAPE)
        else: #SpiritForm has physics after BaseShape
            _, baseshape,                       appearance_data = self._try_parse_struct_property(appearance_data, self.BASESHAPE, self.BODY_SHAPE)
            _, physics,                         appearance_data = self._try_parse_struct_property(appearance_data, self.PHYSICS, self.BOUNCE_PHYSICS)
        _, chubbyshape,                         appearance_data = self._try_parse_struct_property(appearance_data, self.CHUBBYSHAPE,       self.BODY_SHAPE)
        _, slendershape,                        appearance_data = self._try_parse_struct_property(appearance_data, self.SLENDERSHAPE,       self.BODY_SHAPE)
        _, meatyshape,                          appearance_data = self._try_parse_struct_property(appearance_data, self.MEATYSHAPE,       self.BODY_SHAPE)
        _, material,                            appearance_data = self._try_parse_struct_property(appearance_data, self.MATERIAL,       self.CHARACTER_MATERIAL)
        _, self.eyerindex,                      appearance_data = self._try_parse_int_property(appearance_data, self.EYERINDEX)
        _, self.eyelindex,                      appearance_data = self._try_parse_int_property(appearance_data, self.EYELINDEX)
        _, self.eyebrowindex,                   appearance_data = self._try_parse_int_property(appearance_data, self.EYEBROWINDEX)
        _, self.facedecorindex,                 appearance_data = self._try_parse_int_property(appearance_data, self.FACEDECORINDEX)
        _, self.bodydecorindex,                 appearance_data = self._try_parse_int_property(appearance_data, self.BODYDECORINDEX)
        _, self.bodymarksindex,                 appearance_data = self._try_parse_int_property(appearance_data, self.BODYMARKSINDEX)
        _, self.additionalmaterialmaskindex,    appearance_data = self._try_parse_int_property(appearance_data, self.ADDITIONALMATERIALMASKINDEX)
        _, self.additionalmaterialindex,        appearance_data = self._try_parse_int_property(appearance_data, self.ADDITIONALMATERIALINDEX)
        _, attachmentmaterial,                  appearance_data = self._try_parse_struct_property(appearance_data, self.ATTACHMENTMATERIAL, self.CHARACTER_ATTACHMENT_SCHEME)
        _, self.torsoattachmentindex,           appearance_data = self._try_parse_int_property(appearance_data, self.TORSOATTACHMENTINDEX)
        _, self.pubichairindex,                 appearance_data = self._try_parse_int_property(appearance_data, self.PUBICHAIRINDEX)
        _, self.headattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.HEADATTACHMENTINDEX)
        _, self.headextraattachmentindex,       appearance_data = self._try_parse_int_property(appearance_data, self.HEADEXTRAATTACHMENTINDEX)
        _, self.legsattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.LEGSATTACHMENTINDEX)
        _, self.armsattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.ARMSATTACHMENTINDEX)
        _, self.tailattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.TAILATTACHMENTINDEX)
        _, self.wingattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.WINGATTACHMENTINDEX)
        _, self.earsattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.EARSATTACHMENTINDEX)
        _, self.hairattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.HAIRATTACHMENTINDEX)
        _, self.facialhairindex,                appearance_data = self._try_parse_int_property(appearance_data, self.FACIALHAIRINDEX)
        _, self.dickattachmentindex,            appearance_data = self._try_parse_int_property(appearance_data, self.DICKATTACHMENTINDEX)
        _, self.accessoryattachmentindex,       appearance_data = self._try_parse_int_property(appearance_data, self.ACCESSORYATTACHMENTINDEX)
        _, self.collarattachmentindex,          appearance_data = self._try_parse_int_property(appearance_data, self.COLLARATTACHMENTINDEX)
        _, self.ambientparticleattachmentindex, appearance_data = self._try_parse_int_property(appearance_data, self.AMBIENTPARTICLEATTACHMENTINDEX)
        _, self.upperclothingindex,             appearance_data = self._try_parse_int_property(appearance_data, self.UPPERCLOTHINGINDEX)
        _, self.lowerclothingindex,             appearance_data = self._try_parse_int_property(appearance_data, self.LOWERCLOTHINGINDEX)
        _, self.underwearindex,                 appearance_data = self._try_parse_int_property(appearance_data, self.UNDERWEARINDEX)
        _, self.bootsindex,                     appearance_data = self._try_parse_int_property(appearance_data, self.BOOTSINDEX)
        _, self.idleanimationindex,             appearance_data = self._try_parse_int_property(appearance_data, self.IDLEANIMATIONINDEX)
        self.remain = appearance_data
        
        self.tags = GameplayTag(tags)
        self.morph = Morph(morph)
        self.physics = Physics(physics)
        self.material = Material(material)
        self.attachmentmaterial = AttachmentMaterial(attachmentmaterial)
        self.baseshape = BaseShape(baseshape)
        self.chubbyshape = BaseShape(chubbyshape)
        self.slendershape = BaseShape(slendershape)
        self.meatyshape = BaseShape(meatyshape)

    def get_data(self):
        data_out = []
        data_out.append(self._try_get_struct_property_bytes(self.tags.get_data(),               self.TAGS, self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._try_get_struct_property_bytes(self.morph.get_data(),              self.MORPH, self.CHARACTER_MORPH))
        data_out.append(self._try_get_struct_property_bytes(self.physics.get_data(),            self.PHYSICS, self.BOUNCE_PHYSICS))
        data_out.append(self._try_get_struct_property_bytes(self.baseshape.get_data(),          self.BASESHAPE, self.BODY_SHAPE))
        data_out.append(self._try_get_struct_property_bytes(self.chubbyshape.get_data(),        self.CHUBBYSHAPE, self.BODY_SHAPE))
        data_out.append(self._try_get_struct_property_bytes(self.slendershape.get_data(),       self.SLENDERSHAPE, self.BODY_SHAPE))
        data_out.append(self._try_get_struct_property_bytes(self.meatyshape.get_data(),         self.MEATYSHAPE, self.BODY_SHAPE))
        data_out.append(self._try_get_struct_property_bytes(self.material.get_data(),           self.MATERIAL, self.CHARACTER_MATERIAL))
        data_out.append(self._try_get_int_property_bytes(self.eyerindex,                        self.EYERINDEX))
        data_out.append(self._try_get_int_property_bytes(self.eyelindex,                        self.EYELINDEX))
        data_out.append(self._try_get_int_property_bytes(self.eyebrowindex,                     self.EYEBROWINDEX))
        data_out.append(self._try_get_int_property_bytes(self.facedecorindex,                   self.FACEDECORINDEX))
        data_out.append(self._try_get_int_property_bytes(self.bodydecorindex,                   self.BODYDECORINDEX))
        data_out.append(self._try_get_int_property_bytes(self.bodymarksindex,                   self.BODYMARKSINDEX))
        data_out.append(self._try_get_int_property_bytes(self.additionalmaterialmaskindex,      self.ADDITIONALMATERIALMASKINDEX))
        data_out.append(self._try_get_int_property_bytes(self.additionalmaterialindex,          self.ADDITIONALMATERIALINDEX))
        data_out.append(self._try_get_struct_property_bytes(self.attachmentmaterial.get_data(), self.ATTACHMENTMATERIAL, self.CHARACTER_ATTACHMENT_SCHEME))
        data_out.append(self._try_get_int_property_bytes(self.torsoattachmentindex,             self.TORSOATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.pubichairindex,                   self.PUBICHAIRINDEX))
        data_out.append(self._try_get_int_property_bytes(self.headattachmentindex,              self.HEADATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.headextraattachmentindex,         self.HEADEXTRAATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.legsattachmentindex,              self.LEGSATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.armsattachmentindex,              self.ARMSATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.tailattachmentindex,              self.TAILATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.wingattachmentindex,              self.WINGATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.earsattachmentindex,              self.EARSATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.hairattachmentindex,              self.HAIRATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.facialhairindex,                  self.FACIALHAIRINDEX))
        data_out.append(self._try_get_int_property_bytes(self.dickattachmentindex,              self.DICKATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.accessoryattachmentindex,         self.ACCESSORYATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.collarattachmentindex,            self.COLLARATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.ambientparticleattachmentindex,   self.AMBIENTPARTICLEATTACHMENTINDEX))
        data_out.append(self._try_get_int_property_bytes(self.upperclothingindex,               self.UPPERCLOTHINGINDEX))
        data_out.append(self._try_get_int_property_bytes(self.lowerclothingindex,               self.LOWERCLOTHINGINDEX))
        data_out.append(self._try_get_int_property_bytes(self.underwearindex,                   self.UNDERWEARINDEX))
        data_out.append(self._try_get_int_property_bytes(self.bootsindex,                       self.BOOTSINDEX))
        data_out.append(self._try_get_int_property_bytes(self.idleanimationindex,               self.IDLEANIMATIONINDEX))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class BaseShape(Appearance):
    MORPHBUSTY = b'\x0B\x00\x00\x00\x4D\x6F\x72\x70\x68\x42\x75\x73\x74\x79\x00'
    MORPHBUXOM = b'\x0B\x00\x00\x00\x4D\x6F\x72\x70\x68\x42\x75\x78\x6F\x6D\x00'
    MORPHPREGNANT = b'\x0E\x00\x00\x00\x4D\x6F\x72\x70\x68\x50\x72\x65\x67\x6E\x61\x6E\x74\x00'
    PHYSICSBUSTY = b'\x0D\x00\x00\x00\x50\x68\x79\x73\x69\x63\x73\x42\x75\x73\x74\x79\x00'
    PHYSICSBUXOM = b'\x0D\x00\x00\x00\x50\x68\x79\x73\x69\x63\x73\x42\x75\x78\x6F\x6D\x00'
    PHYSICSPREGNANT = b'\x10\x00\x00\x00\x50\x68\x79\x73\x69\x63\x73\x50\x72\x65\x67\x6E\x61\x6E\x74\x00'
    def __init__(self, shape_data):
        self._parse_shape_data(shape_data)
    
    def _parse_shape_data(self, shape_data):
        _, morph,           shape_data = self._try_parse_struct_property(shape_data, self.MORPH,           self.CHARACTER_MORPH)
        _, morphbusty,      shape_data = self._try_parse_struct_property(shape_data, self.MORPHBUSTY,      self.CHARACTER_MORPH)
        _, morphbuxom,      shape_data = self._try_parse_struct_property(shape_data, self.MORPHBUXOM,      self.CHARACTER_MORPH)
        _, morphpregnant,   shape_data = self._try_parse_struct_property(shape_data, self.MORPHPREGNANT,   self.CHARACTER_MORPH)
        _, physics,         shape_data = self._try_parse_struct_property(shape_data, self.PHYSICS,         self.BOUNCE_PHYSICS)
        _, physicsbusty,    shape_data = self._try_parse_struct_property(shape_data, self.PHYSICSBUSTY,    self.BOUNCE_PHYSICS)
        _, physicsbuxom,    shape_data = self._try_parse_struct_property(shape_data, self.PHYSICSBUXOM,    self.BOUNCE_PHYSICS)
        _, physicspregnant, shape_data = self._try_parse_struct_property(shape_data, self.PHYSICSPREGNANT, self.BOUNCE_PHYSICS)
        self.remain = shape_data
        
        self.morph = Morph(morph)
        self.morphbusty = Morph(morphbusty)
        self.morphbuxom = Morph(morphbuxom)
        self.morphpregnant = Morph(morphpregnant)
        self.physics = Physics(physics)
        self.physicsbusty = Physics(physicsbusty)
        self.physicsbuxom = Physics(physicsbuxom)
        self.physicspregnant = Physics(physicspregnant)
    
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_struct_property_bytes(self.morph.get_data(),           self.MORPH,           self.CHARACTER_MORPH))
        data_out.append(self._try_get_struct_property_bytes(self.morphbusty.get_data(),      self.MORPHBUSTY,      self.CHARACTER_MORPH))
        data_out.append(self._try_get_struct_property_bytes(self.morphbuxom.get_data(),      self.MORPHBUXOM,      self.CHARACTER_MORPH))
        data_out.append(self._try_get_struct_property_bytes(self.morphpregnant.get_data(),   self.MORPHPREGNANT,   self.CHARACTER_MORPH))
        data_out.append(self._try_get_struct_property_bytes(self.physics.get_data(),         self.PHYSICS,         self.BOUNCE_PHYSICS))
        data_out.append(self._try_get_struct_property_bytes(self.physicsbusty.get_data(),    self.PHYSICSBUSTY,    self.BOUNCE_PHYSICS))
        data_out.append(self._try_get_struct_property_bytes(self.physicsbuxom.get_data(),    self.PHYSICSBUXOM,    self.BOUNCE_PHYSICS))
        data_out.append(self._try_get_struct_property_bytes(self.physicspregnant.get_data(), self.PHYSICSPREGNANT, self.BOUNCE_PHYSICS))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class Morph(Appearance):
    FACEDEPTH = b'\x0A\x00\x00\x00\x46\x61\x63\x65\x44\x65\x70\x74\x68\x00'
    FACEWIDTH = b'\x0A\x00\x00\x00\x46\x61\x63\x65\x57\x69\x64\x74\x68\x00'
    EYESCLOSE = b'\x0A\x00\x00\x00\x45\x79\x65\x73\x43\x6C\x6F\x73\x65\x00'
    EYESVERTICAL = b'\x0D\x00\x00\x00\x45\x79\x65\x73\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    EYESDEPTH = b'\x0A\x00\x00\x00\x45\x79\x65\x73\x44\x65\x70\x74\x68\x00'
    EYESDISTANCE = b'\x0D\x00\x00\x00\x45\x79\x65\x73\x44\x69\x73\x74\x61\x6E\x63\x65\x00'
    EYESSIZE = b'\x09\x00\x00\x00\x45\x79\x65\x73\x53\x69\x7A\x65\x00'
    EYESANGLE = b'\x0A\x00\x00\x00\x45\x79\x65\x73\x41\x6E\x67\x6C\x65\x00'
    HUMANEARSIZE = b'\x0D\x00\x00\x00\x48\x75\x6D\x61\x6E\x45\x61\x72\x53\x69\x7A\x65\x00'
    HUMANEARPOINTEDA = b'\x11\x00\x00\x00\x48\x75\x6D\x61\x6E\x45\x61\x72\x50\x6F\x69\x6E\x74\x65\x64\x41\x00'
    HUMANEARPOINTEDB = b'\x11\x00\x00\x00\x48\x75\x6D\x61\x6E\x45\x61\x72\x50\x6F\x69\x6E\x74\x65\x64\x42\x00'
    HUMANEARPOINTEDC = b'\x11\x00\x00\x00\x48\x75\x6D\x61\x6E\x45\x61\x72\x50\x6F\x69\x6E\x74\x65\x64\x43\x00'
    ATTACHEDEARSIZE = b'\x10\x00\x00\x00\x41\x74\x74\x61\x63\x68\x65\x64\x45\x61\x72\x53\x69\x7A\x65\x00'
    HAIRSIZE = b'\x09\x00\x00\x00\x48\x61\x69\x72\x53\x69\x7A\x65\x00'
    HAIRBACK = b'\x09\x00\x00\x00\x48\x61\x69\x72\x42\x61\x63\x6B\x00'
    BROWVERTICAL = b'\x0D\x00\x00\x00\x42\x72\x6F\x77\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    BROWDEPTH = b'\x0A\x00\x00\x00\x42\x72\x6F\x77\x44\x65\x70\x74\x68\x00'
    BROWINNERVERTICAL = b'\x12\x00\x00\x00\x42\x72\x6F\x77\x49\x6E\x6E\x65\x72\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    NOSEBRIDGEWIDTH = b'\x10\x00\x00\x00\x4E\x6F\x73\x65\x42\x72\x69\x64\x67\x65\x57\x69\x64\x74\x68\x00'
    NOSEBRIDGEDEPTH = b'\x10\x00\x00\x00\x4E\x6F\x73\x65\x42\x72\x69\x64\x67\x65\x44\x65\x70\x74\x68\x00'
    NOSEWIDTH = b'\x0A\x00\x00\x00\x4E\x6F\x73\x65\x57\x69\x64\x74\x68\x00'
    NOSEDEPTH = b'\x0A\x00\x00\x00\x4E\x6F\x73\x65\x44\x65\x70\x74\x68\x00'
    NOSEVERTICAL = b'\x0D\x00\x00\x00\x4E\x6F\x73\x65\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    NOSEANGLE = b'\x0A\x00\x00\x00\x4E\x6F\x73\x65\x41\x6E\x67\x6C\x65\x00'
    CHEEKBONEDEPTH = b'\x0F\x00\x00\x00\x43\x68\x65\x65\x6B\x62\x6F\x6E\x65\x44\x65\x70\x74\x68\x00'
    CHEEKBONEVERTICAL = b'\x12\x00\x00\x00\x43\x68\x65\x65\x6B\x62\x6F\x6E\x65\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    CHEEKBONEWIDTH = b'\x0F\x00\x00\x00\x43\x68\x65\x65\x6B\x62\x6F\x6E\x65\x57\x69\x64\x74\x68\x00'
    CHEEKBONESIZE = b'\x0E\x00\x00\x00\x43\x68\x65\x65\x6B\x62\x6F\x6E\x65\x53\x69\x7A\x65\x00'
    CHEEKDEPTH = b'\x0B\x00\x00\x00\x43\x68\x65\x65\x6B\x44\x65\x70\x74\x68\x00'
    CHEEKWIDTH = b'\x0B\x00\x00\x00\x43\x68\x65\x65\x6B\x57\x69\x64\x74\x68\x00'
    MOUTHWIDTH = b'\x0B\x00\x00\x00\x4D\x6F\x75\x74\x68\x57\x69\x64\x74\x68\x00'
    MOUTHVERTICAL = b'\x0E\x00\x00\x00\x4D\x6F\x75\x74\x68\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    MOUTHDEPTH = b'\x0B\x00\x00\x00\x4D\x6F\x75\x74\x68\x44\x65\x70\x74\x68\x00'
    MOUTHOPEN = b'\x0A\x00\x00\x00\x4D\x6F\x75\x74\x68\x4F\x70\x65\x6E\x00'
    MOUTHCORNERSVERTICAL = b'\x15\x00\x00\x00\x4D\x6F\x75\x74\x68\x43\x6F\x72\x6E\x65\x72\x73\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    MOUTHCORNERSDEPTH = b'\x12\x00\x00\x00\x4D\x6F\x75\x74\x68\x43\x6F\x72\x6E\x65\x72\x73\x44\x65\x70\x74\x68\x00'
    LIPUPPERFAT = b'\x0C\x00\x00\x00\x4C\x69\x70\x55\x70\x70\x65\x72\x46\x61\x74\x00'
    LIPUPPERWIDTH = b'\x0E\x00\x00\x00\x4C\x69\x70\x55\x70\x70\x65\x72\x57\x69\x64\x74\x68\x00'
    LIPUPPERDEPTH = b'\x0E\x00\x00\x00\x4C\x69\x70\x55\x70\x70\x65\x72\x44\x65\x70\x74\x68\x00'
    LIPUPPERPEAKVERTICAL = b'\x15\x00\x00\x00\x4C\x69\x70\x55\x70\x70\x65\x72\x50\x65\x61\x6B\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    LIPLOWERFAT = b'\x0C\x00\x00\x00\x4C\x69\x70\x4C\x6F\x77\x65\x72\x46\x61\x74\x00'
    LIPLOWERWIDTH = b'\x0E\x00\x00\x00\x4C\x69\x70\x4C\x6F\x77\x65\x72\x57\x69\x64\x74\x68\x00'
    LIPLOWERDEPTH = b'\x0E\x00\x00\x00\x4C\x69\x70\x4C\x6F\x77\x65\x72\x44\x65\x70\x74\x68\x00'
    LIPCENTERVERTICAL = b'\x12\x00\x00\x00\x4C\x69\x70\x43\x65\x6E\x74\x65\x72\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    LIPCURVES = b'\x0A\x00\x00\x00\x4C\x69\x70\x43\x75\x72\x76\x65\x73\x00'
    JAWCORNERWIDTH = b'\x0F\x00\x00\x00\x4A\x61\x77\x43\x6F\x72\x6E\x65\x72\x57\x69\x64\x74\x68\x00'
    JAWCORNERVERTICAL = b'\x12\x00\x00\x00\x4A\x61\x77\x43\x6F\x72\x6E\x65\x72\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    JAWWIDTH = b'\x09\x00\x00\x00\x4A\x61\x77\x57\x69\x64\x74\x68\x00'
    JAWVERTICAL = b'\x0C\x00\x00\x00\x4A\x61\x77\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    CHINWIDTH = b'\x0A\x00\x00\x00\x43\x68\x69\x6E\x57\x69\x64\x74\x68\x00'
    CHINVERTICAL = b'\x0D\x00\x00\x00\x43\x68\x69\x6E\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    CHINDEPTH = b'\x0A\x00\x00\x00\x43\x68\x69\x6E\x44\x65\x70\x74\x68\x00'
    CHINFAT = b'\x08\x00\x00\x00\x43\x68\x69\x6E\x46\x61\x74\x00'
    NECKGIRTH = b'\x0A\x00\x00\x00\x4E\x65\x63\x6B\x47\x69\x72\x74\x68\x00'
    SHOULDERWIDTH = b'\x0E\x00\x00\x00\x53\x68\x6F\x75\x6C\x64\x65\x72\x57\x69\x64\x74\x68\x00'
    SHOULDERSPREAD = b'\x0F\x00\x00\x00\x53\x68\x6F\x75\x6C\x64\x65\x72\x53\x70\x72\x65\x61\x64\x00'
    SHOULDERHEIGHT = b'\x0F\x00\x00\x00\x53\x68\x6F\x75\x6C\x64\x65\x72\x48\x65\x69\x67\x68\x74\x00'
    SHOULDERFORWARD = b'\x10\x00\x00\x00\x53\x68\x6F\x75\x6C\x64\x65\x72\x46\x6F\x72\x77\x61\x72\x64\x00'
    UPPERARMGIRTH = b'\x0E\x00\x00\x00\x55\x70\x70\x65\x72\x61\x72\x6D\x47\x69\x72\x74\x68\x00'
    UPPERARMFIT = b'\x0C\x00\x00\x00\x55\x70\x70\x65\x72\x61\x72\x6D\x46\x69\x74\x00'
    UPPERBODYFIT = b'\x0D\x00\x00\x00\x55\x70\x70\x65\x72\x42\x6F\x64\x79\x46\x69\x74\x00'
    FOREARMGIRTH = b'\x0D\x00\x00\x00\x46\x6F\x72\x65\x61\x72\x6D\x47\x69\x72\x74\x68\x00'
    BREAST = b'\x08\x00\x00\x00\x42\x72\x65\x61\x73\x74\x73\x00'
    BREASTCLOTHED = b'\x0F\x00\x00\x00\x42\x72\x65\x61\x73\x74\x73\x43\x6C\x6F\x74\x68\x65\x64\x00'
    
    BELLYFAT = b'\x09\x00\x00\x00\x42\x65\x6C\x6C\x79\x46\x61\x74\x00'
    BELLYMEGA = b'\x0A\x00\x00\x00\x42\x65\x6C\x6C\x79\x4D\x65\x67\x61\x00'
    BELLYDEPTH = b'\x0B\x00\x00\x00\x42\x65\x6C\x6C\x79\x44\x65\x70\x74\x68\x00'
    BELLYWIDTH = b'\x0B\x00\x00\x00\x42\x65\x6C\x6C\x79\x57\x69\x64\x74\x68\x00'
    BELLYDEPTH2 = b'\x0C\x00\x00\x00\x42\x65\x6C\x6C\x79\x44\x65\x70\x74\x68\x32\x00'
    BELLYWIDTH2 = b'\x0C\x00\x00\x00\x42\x65\x6C\x6C\x79\x57\x69\x64\x74\x68\x32\x00'
    BELLYHEIGHT = b'\x0C\x00\x00\x00\x42\x65\x6C\x6C\x79\x48\x65\x69\x67\x68\x74\x00'
    BELLYVERTICAL = b'\x0E\x00\x00\x00\x42\x65\x6C\x6C\x79\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    BELLYPREGNANT = b'\x0E\x00\x00\x00\x42\x65\x6C\x6C\x79\x50\x72\x65\x67\x6E\x61\x6E\x74\x00'
    BELLYFIT = b'\x09\x00\x00\x00\x42\x65\x6C\x6C\x79\x46\x69\x74\x00'
    BELLYPELVISCREASE = b'\x12\x00\x00\x00\x42\x65\x6C\x6C\x79\x50\x65\x6C\x76\x69\x73\x43\x72\x65\x61\x73\x65\x00'
    BELLYSMOOTH = b'\x0C\x00\x00\x00\x42\x65\x6C\x6C\x79\x53\x6D\x6F\x6F\x74\x68\x00'
    NAVELWIDTH = b'\x0B\x00\x00\x00\x4E\x61\x76\x65\x6C\x57\x69\x64\x74\x68\x00'
    NAVELHEIGHT = b'\x0C\x00\x00\x00\x4E\x61\x76\x65\x6C\x48\x65\x69\x67\x68\x74\x00'
    NAVELVERTICAL = b'\x0E\x00\x00\x00\x4E\x61\x76\x65\x6C\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    NAVELDEPTH = b'\x0B\x00\x00\x00\x4E\x61\x76\x65\x6C\x44\x65\x70\x74\x68\x00'
    WAISTWIDTH = b'\x0B\x00\x00\x00\x57\x61\x69\x73\x74\x57\x69\x64\x74\x68\x00'
    HIPWIDTH = b'\x09\x00\x00\x00\x48\x69\x70\x57\x69\x64\x74\x68\x00'
    GROINGIRTH = b'\x0B\x00\x00\x00\x47\x72\x6F\x69\x6E\x47\x69\x72\x74\x68\x00'
    VAGINAFAT = b'\x0A\x00\x00\x00\x56\x61\x67\x69\x6E\x61\x46\x61\x74\x00'
    VAGINAOPEN = b'\x0B\x00\x00\x00\x56\x61\x67\x69\x6E\x61\x4F\x70\x65\x6E\x00'
    BUTTSIZE = b'\x09\x00\x00\x00\x42\x75\x74\x74\x53\x69\x7A\x65\x00'
    BUTTDEPTH = b'\x0A\x00\x00\x00\x42\x75\x74\x74\x44\x65\x70\x74\x68\x00'
    BUTTHEIGHT = b'\x0B\x00\x00\x00\x42\x75\x74\x74\x48\x65\x69\x67\x68\x74\x00'
    BUTTWIDTH = b'\x0A\x00\x00\x00\x42\x75\x74\x74\x57\x69\x64\x74\x68\x00'
    BUTTCLEAVAGE = b'\x0D\x00\x00\x00\x42\x75\x74\x74\x43\x6C\x65\x61\x76\x61\x67\x65\x00'
    BUTTVERTICAL = b'\x0D\x00\x00\x00\x42\x75\x74\x74\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    BUTTPROTRUDE = b'\x0D\x00\x00\x00\x42\x75\x74\x74\x50\x72\x6F\x74\x72\x75\x64\x65\x00'
    BUTTCREASE = b'\x0B\x00\x00\x00\x42\x75\x74\x74\x43\x72\x65\x61\x73\x65\x00'
    THIGHGIRTH = b'\x0B\x00\x00\x00\x54\x68\x69\x67\x68\x47\x69\x72\x74\x68\x00'
    THIGHFIT = b'\x09\x00\x00\x00\x54\x68\x69\x67\x68\x46\x69\x74\x00'
    CALFGIRTH = b'\x0A\x00\x00\x00\x43\x61\x6C\x66\x47\x69\x72\x74\x68\x00'
    DICKBLURSHEATHOFFSET = b'\x15\x00\x00\x00\x44\x69\x63\x6B\x42\x6C\x75\x72\x53\x68\x65\x61\x74\x68\x4F\x66\x66\x73\x65\x74\x00'
    DICKBLURSHEATHTAPERA = b'\x15\x00\x00\x00\x44\x69\x63\x6B\x42\x6C\x75\x72\x53\x68\x65\x61\x74\x68\x54\x61\x70\x65\x72\x41\x00'
    DICKBLURSHEATHTAPERB = b'\x15\x00\x00\x00\x44\x69\x63\x6B\x42\x6C\x75\x72\x53\x68\x65\x61\x74\x68\x54\x61\x70\x65\x72\x42\x00'
    DICKBLURSHEATHCONSTRICT = b'\x18\x00\x00\x00\x44\x69\x63\x6B\x42\x6C\x75\x72\x53\x68\x65\x61\x74\x68\x43\x6F\x6E\x73\x74\x72\x69\x63\x74\x00'
    DICKHEADGIRTH = b'\x0E\x00\x00\x00\x44\x69\x63\x6B\x48\x65\x61\x64\x47\x69\x72\x74\x68\x00'
    DICKLENGTH = b'\x0B\x00\x00\x00\x44\x69\x63\x6B\x4C\x65\x6E\x67\x74\x68\x00'
    DICKSHAFTGIRTH = b'\x0F\x00\x00\x00\x44\x69\x63\x6B\x53\x68\x61\x66\x74\x47\x69\x72\x74\x68\x00'
    DICKSIZE = b'\x09\x00\x00\x00\x44\x69\x63\x6B\x53\x69\x7A\x65\x00'
    SCROTUMSIZE = b'\x0C\x00\x00\x00\x53\x63\x72\x6F\x74\x75\x6D\x53\x69\x7A\x65\x00'
    TEETHSHARP = b'\x0B\x00\x00\x00\x54\x65\x65\x74\x68\x53\x68\x61\x72\x70\x00'
    TAILSIZE = b'\x09\x00\x00\x00\x54\x61\x69\x6C\x53\x69\x7A\x65\x00'
    WINGSSIZE = b'\x0A\x00\x00\x00\x57\x69\x6E\x67\x73\x53\x69\x7A\x65\x00'
    LEGSPREAD = b'\x0A\x00\x00\x00\x4C\x65\x67\x53\x70\x72\x65\x61\x64\x00'
    FULLBODYSTACKED = b'\x10\x00\x00\x00\x46\x75\x6C\x6C\x42\x6F\x64\x79\x53\x74\x61\x63\x6B\x65\x64\x00'
    FULLBODYBULK = b'\x0D\x00\x00\x00\x46\x75\x6C\x6C\x42\x6F\x64\x79\x42\x75\x6C\x6B\x00'
    FULLBODYCHUBBY = b'\x0F\x00\x00\x00\x46\x75\x6C\x6C\x42\x6F\x64\x79\x43\x68\x75\x62\x62\x79\x00'
    FULLBODYSLENDER = b'\x10\x00\x00\x00\x46\x75\x6C\x6C\x42\x6F\x64\x79\x53\x6C\x65\x6E\x64\x65\x72\x00'
    SPINEADJUST = b'\x0C\x00\x00\x00\x53\x70\x69\x6E\x65\x41\x64\x6A\x75\x73\x74\x00'
    HEADSIZE = b'\x09\x00\x00\x00\x48\x65\x61\x64\x53\x69\x7A\x65\x00'
    ARMSCALE_0 = b'\x0B\x00\x00\x00\x41\x72\x6D\x53\x63\x61\x6C\x65\x5F\x30\x00'
    ARMSCALE_1 = b'\x0B\x00\x00\x00\x41\x72\x6D\x53\x63\x61\x6C\x65\x5F\x31\x00'
    ARMSCALE_2 = b'\x0B\x00\x00\x00\x41\x72\x6D\x53\x63\x61\x6C\x65\x5F\x32\x00'
    ARMSCALE_3 = b'\x0B\x00\x00\x00\x41\x72\x6D\x53\x63\x61\x6C\x65\x5F\x33\x00'
    ARMSCALE_4 = b'\x0B\x00\x00\x00\x41\x72\x6D\x53\x63\x61\x6C\x65\x5F\x34\x00'
    ARMSCALE_5 = b'\x0B\x00\x00\x00\x41\x72\x6D\x53\x63\x61\x6C\x65\x5F\x35\x00'

    BREASTSHAPE = b'\x0C\x00\x00\x00\x42\x72\x65\x61\x73\x74\x53\x68\x61\x70\x65\x00' + ByteMacros.STRUCT_PADDING

    def __init__(self, morph_data):
        self._parse_morph_data(morph_data)
    
    def _parse_morph_data(self, morph_data):
        _, self.facedepth,               morph_data = self._try_parse_float_property(morph_data, self.FACEDEPTH)
        _, self.facewidth,               morph_data = self._try_parse_float_property(morph_data, self.FACEWIDTH)
        _, self.eyesclose,               morph_data = self._try_parse_float_property(morph_data, self.EYESCLOSE)
        _, self.eyesvertical,            morph_data = self._try_parse_float_property(morph_data, self.EYESVERTICAL)
        _, self.eyesdepth,               morph_data = self._try_parse_float_property(morph_data, self.EYESDEPTH)
        _, self.eyesdistance,            morph_data = self._try_parse_float_property(morph_data, self.EYESDISTANCE)
        _, self.eyessize,                morph_data = self._try_parse_float_property(morph_data, self.EYESSIZE)
        _, self.eyesangle,               morph_data = self._try_parse_float_property(morph_data, self.EYESANGLE)
        _, self.humanearsize,            morph_data = self._try_parse_float_property(morph_data, self.HUMANEARSIZE)
        _, self.humanearpointeda,        morph_data = self._try_parse_float_property(morph_data, self.HUMANEARPOINTEDA)
        _, self.humanearpointedb,        morph_data = self._try_parse_float_property(morph_data, self.HUMANEARPOINTEDB)
        _, self.humanearpointedc,        morph_data = self._try_parse_float_property(morph_data, self.HUMANEARPOINTEDC)
        _, self.attachedearsize,         morph_data = self._try_parse_float_property(morph_data, self.ATTACHEDEARSIZE)
        _, self.hairsize,                morph_data = self._try_parse_float_property(morph_data, self.HAIRSIZE)
        _, self.hairback,                morph_data = self._try_parse_float_property(morph_data, self.HAIRBACK)
        _, self.browvertical,            morph_data = self._try_parse_float_property(morph_data, self.BROWVERTICAL)
        _, self.browdepth,               morph_data = self._try_parse_float_property(morph_data, self.BROWDEPTH)
        _, self.browinnervertical,       morph_data = self._try_parse_float_property(morph_data, self.BROWINNERVERTICAL)
        _, self.nosebridgewidth,         morph_data = self._try_parse_float_property(morph_data, self.NOSEBRIDGEWIDTH)
        _, self.nosebridgedepth,         morph_data = self._try_parse_float_property(morph_data, self.NOSEBRIDGEDEPTH)
        _, self.nosewidth,               morph_data = self._try_parse_float_property(morph_data, self.NOSEWIDTH)
        _, self.nosedepth,               morph_data = self._try_parse_float_property(morph_data, self.NOSEDEPTH)
        _, self.nosevertical,            morph_data = self._try_parse_float_property(morph_data, self.NOSEVERTICAL)
        _, self.noseangle,               morph_data = self._try_parse_float_property(morph_data, self.NOSEANGLE)
        _, self.cheekbonedepth,          morph_data = self._try_parse_float_property(morph_data, self.CHEEKBONEDEPTH)
        _, self.cheekbonevertical,       morph_data = self._try_parse_float_property(morph_data, self.CHEEKBONEVERTICAL)
        _, self.cheekbonewidth,          morph_data = self._try_parse_float_property(morph_data, self.CHEEKBONEWIDTH)
        _, self.cheekbonesize,           morph_data = self._try_parse_float_property(morph_data, self.CHEEKBONESIZE)
        _, self.cheekdepth,              morph_data = self._try_parse_float_property(morph_data, self.CHEEKDEPTH)
        _, self.cheekwidth,              morph_data = self._try_parse_float_property(morph_data, self.CHEEKWIDTH)
        _, self.mouthwidth,              morph_data = self._try_parse_float_property(morph_data, self.MOUTHWIDTH)
        _, self.mouthvertical,           morph_data = self._try_parse_float_property(morph_data, self.MOUTHVERTICAL)
        _, self.mouthdepth,              morph_data = self._try_parse_float_property(morph_data, self.MOUTHDEPTH)
        _, self.mouthopen,               morph_data = self._try_parse_float_property(morph_data, self.MOUTHOPEN)
        _, self.mouthcornersvertical,    morph_data = self._try_parse_float_property(morph_data, self.MOUTHCORNERSVERTICAL)
        _, self.mouthcornersdepth,       morph_data = self._try_parse_float_property(morph_data, self.MOUTHCORNERSDEPTH)
        _, self.lipupperfat,             morph_data = self._try_parse_float_property(morph_data, self.LIPUPPERFAT)
        _, self.lipupperwidth,           morph_data = self._try_parse_float_property(morph_data, self.LIPUPPERWIDTH)
        _, self.lipupperdepth,           morph_data = self._try_parse_float_property(morph_data, self.LIPUPPERDEPTH)
        _, self.lipupperpeakvertical,    morph_data = self._try_parse_float_property(morph_data, self.LIPUPPERPEAKVERTICAL)
        _, self.liplowerfat,             morph_data = self._try_parse_float_property(morph_data, self.LIPLOWERFAT)
        _, self.liplowerwidth,           morph_data = self._try_parse_float_property(morph_data, self.LIPLOWERWIDTH)
        _, self.liplowerdepth,           morph_data = self._try_parse_float_property(morph_data, self.LIPLOWERDEPTH)
        _, self.lipcentervertical,       morph_data = self._try_parse_float_property(morph_data, self.LIPCENTERVERTICAL)
        _, self.lipcurves,               morph_data = self._try_parse_float_property(morph_data, self.LIPCURVES)
        _, self.jawcornerwidth,          morph_data = self._try_parse_float_property(morph_data, self.JAWCORNERWIDTH)
        _, self.jawcornervertical,       morph_data = self._try_parse_float_property(morph_data, self.JAWCORNERVERTICAL)
        _, self.jawwidth,                morph_data = self._try_parse_float_property(morph_data, self.JAWWIDTH)
        _, self.jawvertical,             morph_data = self._try_parse_float_property(morph_data, self.JAWVERTICAL)
        _, self.chinwidth,               morph_data = self._try_parse_float_property(morph_data, self.CHINWIDTH)
        _, self.chinvertical,            morph_data = self._try_parse_float_property(morph_data, self.CHINVERTICAL)
        _, self.chindepth,               morph_data = self._try_parse_float_property(morph_data, self.CHINDEPTH)
        _, self.chinfat,                 morph_data = self._try_parse_float_property(morph_data, self.CHINFAT)
        _, self.neckgirth,               morph_data = self._try_parse_float_property(morph_data, self.NECKGIRTH)
        _, self.shoulderwidth,           morph_data = self._try_parse_float_property(morph_data, self.SHOULDERWIDTH)
        _, self.shoulderspread,          morph_data = self._try_parse_float_property(morph_data, self.SHOULDERSPREAD)
        _, self.shoulderheight,          morph_data = self._try_parse_float_property(morph_data, self.SHOULDERHEIGHT)
        _, self.shoulderforward,         morph_data = self._try_parse_float_property(morph_data, self.SHOULDERFORWARD)
        _, self.upperarmgirth,           morph_data = self._try_parse_float_property(morph_data, self.UPPERARMGIRTH)
        _, self.upperarmfit,             morph_data = self._try_parse_float_property(morph_data, self.UPPERARMFIT)
        _, self.upperbodyfit,            morph_data = self._try_parse_float_property(morph_data, self.UPPERBODYFIT)
        _, self.forearmgirth,            morph_data = self._try_parse_float_property(morph_data, self.FOREARMGIRTH)
        
        _, breast,                       morph_data = self._try_parse_struct_property(morph_data, self.BREAST, self.BREASTSHAPE)
        _, breastclothed,                morph_data = self._try_parse_struct_property(morph_data, self.BREASTCLOTHED, self.BREASTSHAPE)
        
        _, self.bellyfat,                morph_data = self._try_parse_float_property(morph_data, self.BELLYFAT)
        _, self.bellymega,               morph_data = self._try_parse_float_property(morph_data, self.BELLYMEGA)
        _, self.bellydepth,              morph_data = self._try_parse_float_property(morph_data, self.BELLYDEPTH)
        _, self.bellywidth,              morph_data = self._try_parse_float_property(morph_data, self.BELLYWIDTH)
        _, self.bellydepth2,             morph_data = self._try_parse_float_property(morph_data, self.BELLYDEPTH2)
        _, self.bellywidth2,             morph_data = self._try_parse_float_property(morph_data, self.BELLYWIDTH2)
        _, self.bellyheight,             morph_data = self._try_parse_float_property(morph_data, self.BELLYHEIGHT)
        _, self.bellyvertical,           morph_data = self._try_parse_float_property(morph_data, self.BELLYVERTICAL)
        _, self.bellypregnant,           morph_data = self._try_parse_float_property(morph_data, self.BELLYPREGNANT)
        _, self.bellyfit,                morph_data = self._try_parse_float_property(morph_data, self.BELLYFIT)
        _, self.bellypelviscrease,       morph_data = self._try_parse_float_property(morph_data, self.BELLYPELVISCREASE)
        _, self.bellysmooth,             morph_data = self._try_parse_float_property(morph_data, self.BELLYSMOOTH)
        _, self.navelwidth,              morph_data = self._try_parse_float_property(morph_data, self.NAVELWIDTH)
        _, self.navelheight,             morph_data = self._try_parse_float_property(morph_data, self.NAVELHEIGHT)
        _, self.navelvertical,           morph_data = self._try_parse_float_property(morph_data, self.NAVELVERTICAL)
        _, self.naveldepth,              morph_data = self._try_parse_float_property(morph_data, self.NAVELDEPTH)
        _, self.waistwidth,              morph_data = self._try_parse_float_property(morph_data, self.WAISTWIDTH)
        _, self.hipwidth,                morph_data = self._try_parse_float_property(morph_data, self.HIPWIDTH)
        _, self.groingirth,              morph_data = self._try_parse_float_property(morph_data, self.GROINGIRTH)
        _, self.vaginafat,               morph_data = self._try_parse_float_property(morph_data, self.VAGINAFAT)
        _, self.vaginaopen,              morph_data = self._try_parse_float_property(morph_data, self.VAGINAOPEN)
        _, self.buttsize,                morph_data = self._try_parse_float_property(morph_data, self.BUTTSIZE)
        _, self.buttdepth,               morph_data = self._try_parse_float_property(morph_data, self.BUTTDEPTH)
        _, self.buttheight,              morph_data = self._try_parse_float_property(morph_data, self.BUTTHEIGHT)
        _, self.buttwidth,               morph_data = self._try_parse_float_property(morph_data, self.BUTTWIDTH)
        _, self.buttcleavage,            morph_data = self._try_parse_float_property(morph_data, self.BUTTCLEAVAGE)
        _, self.buttvertical,            morph_data = self._try_parse_float_property(morph_data, self.BUTTVERTICAL)
        _, self.buttprotrude,            morph_data = self._try_parse_float_property(morph_data, self.BUTTPROTRUDE)
        _, self.buttcrease,              morph_data = self._try_parse_float_property(morph_data, self.BUTTCREASE)
        _, self.thighgirth,              morph_data = self._try_parse_float_property(morph_data, self.THIGHGIRTH)
        _, self.thighfit,                morph_data = self._try_parse_float_property(morph_data, self.THIGHFIT)
        _, self.calfgirth,               morph_data = self._try_parse_float_property(morph_data, self.CALFGIRTH)
        _, self.dickblursheathoffset,    morph_data = self._try_parse_float_property(morph_data, self.DICKBLURSHEATHOFFSET)
        _, self.dickblursheathtapera,    morph_data = self._try_parse_float_property(morph_data, self.DICKBLURSHEATHTAPERA)
        _, self.dickblursheathtaperb,    morph_data = self._try_parse_float_property(morph_data, self.DICKBLURSHEATHTAPERB)
        _, self.dickblursheathconstrict, morph_data = self._try_parse_float_property(morph_data, self.DICKBLURSHEATHCONSTRICT)
        _, self.dickheadgirth,           morph_data = self._try_parse_float_property(morph_data, self.DICKHEADGIRTH)
        _, self.dicklength,              morph_data = self._try_parse_float_property(morph_data, self.DICKLENGTH)
        _, self.dickshaftgirth,          morph_data = self._try_parse_float_property(morph_data, self.DICKSHAFTGIRTH)
        _, self.dicksize,                morph_data = self._try_parse_float_property(morph_data, self.DICKSIZE)
        _, self.scrotumsize,             morph_data = self._try_parse_float_property(morph_data, self.SCROTUMSIZE)
        _, self.teethsharp,              morph_data = self._try_parse_float_property(morph_data, self.TEETHSHARP)
        _, self.tailsize,                morph_data = self._try_parse_float_property(morph_data, self.TAILSIZE)
        _, self.wingssize,               morph_data = self._try_parse_float_property(morph_data, self.WINGSSIZE)
        _, self.legspread,               morph_data = self._try_parse_float_property(morph_data, self.LEGSPREAD)
        _, self.fullbodystacked,         morph_data = self._try_parse_float_property(morph_data, self.FULLBODYSTACKED)
        _, self.fullbodybulk,            morph_data = self._try_parse_float_property(morph_data, self.FULLBODYBULK)
        _, self.fullbodychubby,          morph_data = self._try_parse_float_property(morph_data, self.FULLBODYCHUBBY)
        _, self.fullbodyslender,         morph_data = self._try_parse_float_property(morph_data, self.FULLBODYSLENDER)
        _, self.spineadjust,             morph_data = self._try_parse_float_property(morph_data, self.SPINEADJUST)
        _, self.headsize,                morph_data = self._try_parse_float_property(morph_data, self.HEADSIZE)
        _, self.armscale_0,              morph_data = self._try_parse_float_property(morph_data, self.ARMSCALE_0)
        _, self.armscale_1,              morph_data = self._try_parse_float_property(morph_data, self.ARMSCALE_1)
        _, self.armscale_2,              morph_data = self._try_parse_float_property(morph_data, self.ARMSCALE_2)
        _, self.armscale_3,              morph_data = self._try_parse_float_property(morph_data, self.ARMSCALE_3)
        _, self.armscale_4,              morph_data = self._try_parse_float_property(morph_data, self.ARMSCALE_4)
        _, self.armscale_5,              morph_data = self._try_parse_float_property(morph_data, self.ARMSCALE_5)
        self.remain = morph_data
        
        self.breast = Breast(breast)
        self.breastclothed = Breast(breastclothed)
    
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_float_property_bytes(self.facedepth, self.FACEDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.facewidth, self.FACEWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.eyesclose, self.EYESCLOSE))
        data_out.append(self._try_get_float_property_bytes(self.eyesvertical, self.EYESVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.eyesdepth, self.EYESDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.eyesdistance, self.EYESDISTANCE))
        data_out.append(self._try_get_float_property_bytes(self.eyessize, self.EYESSIZE))
        data_out.append(self._try_get_float_property_bytes(self.eyesangle, self.EYESANGLE))
        data_out.append(self._try_get_float_property_bytes(self.humanearsize, self.HUMANEARSIZE))
        data_out.append(self._try_get_float_property_bytes(self.humanearpointeda, self.HUMANEARPOINTEDA))
        data_out.append(self._try_get_float_property_bytes(self.humanearpointedb, self.HUMANEARPOINTEDB))
        data_out.append(self._try_get_float_property_bytes(self.humanearpointedc, self.HUMANEARPOINTEDC))
        data_out.append(self._try_get_float_property_bytes(self.attachedearsize, self.ATTACHEDEARSIZE))
        data_out.append(self._try_get_float_property_bytes(self.hairsize, self.HAIRSIZE))
        data_out.append(self._try_get_float_property_bytes(self.hairback, self.HAIRBACK))
        data_out.append(self._try_get_float_property_bytes(self.browvertical, self.BROWVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.browdepth, self.BROWDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.browinnervertical, self.BROWINNERVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.nosebridgewidth, self.NOSEBRIDGEWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.nosebridgedepth, self.NOSEBRIDGEDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.nosewidth, self.NOSEWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.nosedepth, self.NOSEDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.nosevertical, self.NOSEVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.noseangle, self.NOSEANGLE))
        data_out.append(self._try_get_float_property_bytes(self.cheekbonedepth, self.CHEEKBONEDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.cheekbonevertical, self.CHEEKBONEVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.cheekbonewidth, self.CHEEKBONEWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.cheekbonesize, self.CHEEKBONESIZE))
        data_out.append(self._try_get_float_property_bytes(self.cheekdepth, self.CHEEKDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.cheekwidth, self.CHEEKWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.mouthwidth, self.MOUTHWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.mouthvertical, self.MOUTHVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.mouthdepth, self.MOUTHDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.mouthopen, self.MOUTHOPEN))
        data_out.append(self._try_get_float_property_bytes(self.mouthcornersvertical, self.MOUTHCORNERSVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.mouthcornersdepth, self.MOUTHCORNERSDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.lipupperfat, self.LIPUPPERFAT))
        data_out.append(self._try_get_float_property_bytes(self.lipupperwidth, self.LIPUPPERWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.lipupperdepth, self.LIPUPPERDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.lipupperpeakvertical, self.LIPUPPERPEAKVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.liplowerfat, self.LIPLOWERFAT))
        data_out.append(self._try_get_float_property_bytes(self.liplowerwidth, self.LIPLOWERWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.liplowerdepth, self.LIPLOWERDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.lipcentervertical, self.LIPCENTERVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.lipcurves, self.LIPCURVES))
        data_out.append(self._try_get_float_property_bytes(self.jawcornerwidth, self.JAWCORNERWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.jawcornervertical, self.JAWCORNERVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.jawwidth, self.JAWWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.jawvertical, self.JAWVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.chinwidth, self.CHINWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.chinvertical, self.CHINVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.chindepth, self.CHINDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.chinfat, self.CHINFAT))
        data_out.append(self._try_get_float_property_bytes(self.neckgirth, self.NECKGIRTH))
        data_out.append(self._try_get_float_property_bytes(self.shoulderwidth, self.SHOULDERWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.shoulderspread, self.SHOULDERSPREAD))
        data_out.append(self._try_get_float_property_bytes(self.shoulderheight, self.SHOULDERHEIGHT))
        data_out.append(self._try_get_float_property_bytes(self.shoulderforward, self.SHOULDERFORWARD))
        data_out.append(self._try_get_float_property_bytes(self.upperarmgirth, self.UPPERARMGIRTH))
        data_out.append(self._try_get_float_property_bytes(self.upperarmfit, self.UPPERARMFIT))
        data_out.append(self._try_get_float_property_bytes(self.upperbodyfit, self.UPPERBODYFIT))
        data_out.append(self._try_get_float_property_bytes(self.forearmgirth, self.FOREARMGIRTH))

        data_out.append(self._try_get_struct_property_bytes(self.breast.get_data(), self.BREAST, self.BREASTSHAPE))
        data_out.append(self._try_get_struct_property_bytes(self.breastclothed.get_data(), self.BREASTCLOTHED, self.BREASTSHAPE))

        data_out.append(self._try_get_float_property_bytes(self.bellyfat, self.BELLYFAT))
        data_out.append(self._try_get_float_property_bytes(self.bellymega, self.BELLYMEGA))
        data_out.append(self._try_get_float_property_bytes(self.bellydepth, self.BELLYDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.bellywidth, self.BELLYWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.bellydepth2, self.BELLYDEPTH2))
        data_out.append(self._try_get_float_property_bytes(self.bellywidth2, self.BELLYWIDTH2))
        data_out.append(self._try_get_float_property_bytes(self.bellyheight, self.BELLYHEIGHT))
        data_out.append(self._try_get_float_property_bytes(self.bellyvertical, self.BELLYVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.bellypregnant, self.BELLYPREGNANT))
        data_out.append(self._try_get_float_property_bytes(self.bellyfit, self.BELLYFIT))
        data_out.append(self._try_get_float_property_bytes(self.bellypelviscrease, self.BELLYPELVISCREASE))
        data_out.append(self._try_get_float_property_bytes(self.bellysmooth, self.BELLYSMOOTH))
        data_out.append(self._try_get_float_property_bytes(self.navelwidth, self.NAVELWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.navelheight, self.NAVELHEIGHT))
        data_out.append(self._try_get_float_property_bytes(self.navelvertical, self.NAVELVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.naveldepth, self.NAVELDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.waistwidth, self.WAISTWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.hipwidth, self.HIPWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.groingirth, self.GROINGIRTH))
        data_out.append(self._try_get_float_property_bytes(self.vaginafat, self.VAGINAFAT))
        data_out.append(self._try_get_float_property_bytes(self.vaginaopen, self.VAGINAOPEN))
        data_out.append(self._try_get_float_property_bytes(self.buttsize, self.BUTTSIZE))
        data_out.append(self._try_get_float_property_bytes(self.buttdepth, self.BUTTDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.buttheight, self.BUTTHEIGHT))
        data_out.append(self._try_get_float_property_bytes(self.buttwidth, self.BUTTWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.buttcleavage, self.BUTTCLEAVAGE))
        data_out.append(self._try_get_float_property_bytes(self.buttvertical, self.BUTTVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.buttprotrude, self.BUTTPROTRUDE))
        data_out.append(self._try_get_float_property_bytes(self.buttcrease, self.BUTTCREASE))
        data_out.append(self._try_get_float_property_bytes(self.thighgirth, self.THIGHGIRTH))
        data_out.append(self._try_get_float_property_bytes(self.thighfit, self.THIGHFIT))
        data_out.append(self._try_get_float_property_bytes(self.calfgirth, self.CALFGIRTH))
        data_out.append(self._try_get_float_property_bytes(self.dickblursheathoffset, self.DICKBLURSHEATHOFFSET))
        data_out.append(self._try_get_float_property_bytes(self.dickblursheathtapera, self.DICKBLURSHEATHTAPERA))
        data_out.append(self._try_get_float_property_bytes(self.dickblursheathtaperb, self.DICKBLURSHEATHTAPERB))
        data_out.append(self._try_get_float_property_bytes(self.dickblursheathconstrict, self.DICKBLURSHEATHCONSTRICT))
        data_out.append(self._try_get_float_property_bytes(self.dickheadgirth, self.DICKHEADGIRTH))
        data_out.append(self._try_get_float_property_bytes(self.dicklength, self.DICKLENGTH))
        data_out.append(self._try_get_float_property_bytes(self.dickshaftgirth, self.DICKSHAFTGIRTH))
        data_out.append(self._try_get_float_property_bytes(self.dicksize, self.DICKSIZE))
        data_out.append(self._try_get_float_property_bytes(self.scrotumsize, self.SCROTUMSIZE))
        data_out.append(self._try_get_float_property_bytes(self.teethsharp, self.TEETHSHARP))
        data_out.append(self._try_get_float_property_bytes(self.tailsize, self.TAILSIZE))
        data_out.append(self._try_get_float_property_bytes(self.wingssize, self.WINGSSIZE))
        data_out.append(self._try_get_float_property_bytes(self.legspread, self.LEGSPREAD))
        data_out.append(self._try_get_float_property_bytes(self.fullbodystacked, self.FULLBODYSTACKED))
        data_out.append(self._try_get_float_property_bytes(self.fullbodybulk, self.FULLBODYBULK))
        data_out.append(self._try_get_float_property_bytes(self.fullbodychubby, self.FULLBODYCHUBBY))
        data_out.append(self._try_get_float_property_bytes(self.fullbodyslender, self.FULLBODYSLENDER))
        data_out.append(self._try_get_float_property_bytes(self.spineadjust, self.SPINEADJUST))
        data_out.append(self._try_get_float_property_bytes(self.headsize, self.HEADSIZE))
        data_out.append(self._try_get_float_property_bytes(self.armscale_0, self.ARMSCALE_0))
        data_out.append(self._try_get_float_property_bytes(self.armscale_1, self.ARMSCALE_1))
        data_out.append(self._try_get_float_property_bytes(self.armscale_2, self.ARMSCALE_2))
        data_out.append(self._try_get_float_property_bytes(self.armscale_3, self.ARMSCALE_3))
        data_out.append(self._try_get_float_property_bytes(self.armscale_4, self.ARMSCALE_4))
        data_out.append(self._try_get_float_property_bytes(self.armscale_5, self.ARMSCALE_5))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class Physics(Appearance):
    BELLYBOUNCE =  b'\x0C\x00\x00\x00\x42\x65\x6C\x6C\x79\x42\x6F\x75\x6E\x63\x65\x00'
    BREASTBOUNCE =  b'\x0D\x00\x00\x00\x42\x72\x65\x61\x73\x74\x42\x6F\x75\x6E\x63\x65\x00'
    BUTTBOUNCE =  b'\x0B\x00\x00\x00\x42\x75\x74\x74\x42\x6F\x75\x6E\x63\x65\x00'
    THIGHBOUNCE =  b'\x0C\x00\x00\x00\x54\x68\x69\x67\x68\x42\x6F\x75\x6E\x63\x65\x00'
    
    def __init__(self, physics_data):
        self._parse_physics_data(physics_data)
    
    def _parse_physics_data(self, physics_data):
        _, self.bellybounce,               physics_data = self._try_parse_float_property(physics_data, self.BELLYBOUNCE)
        _, self.breastbounce,               physics_data = self._try_parse_float_property(physics_data, self.BREASTBOUNCE)
        _, self.buttbounce,               physics_data = self._try_parse_float_property(physics_data, self.BUTTBOUNCE)
        _, self.thighbounce,               physics_data = self._try_parse_float_property(physics_data, self.THIGHBOUNCE)
        self.remain = physics_data
    
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_float_property_bytes(self.bellybounce, self.BELLYBOUNCE))
        data_out.append(self._try_get_float_property_bytes(self.breastbounce, self.BREASTBOUNCE))
        data_out.append(self._try_get_float_property_bytes(self.buttbounce, self.BUTTBOUNCE))
        data_out.append(self._try_get_float_property_bytes(self.thighbounce, self.THIGHBOUNCE))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class Breast(Appearance):
    BREASTSIZE = b'\x0B\x00\x00\x00\x42\x72\x65\x61\x73\x74\x53\x69\x7A\x65\x00'
    BREASTDEPTH = b'\x0C\x00\x00\x00\x42\x72\x65\x61\x73\x74\x44\x65\x70\x74\x68\x00'
    BREASTHEIGHT = b'\x0D\x00\x00\x00\x42\x72\x65\x61\x73\x74\x48\x65\x69\x67\x68\x74\x00'
    BREASTPROTRUDE = b'\x0F\x00\x00\x00\x42\x72\x65\x61\x73\x74\x50\x72\x6F\x74\x72\x75\x64\x65\x00'
    BREASTCLEAVAGE = b'\x0F\x00\x00\x00\x42\x72\x65\x61\x73\x74\x43\x6C\x65\x61\x76\x61\x67\x65\x00'
    BREASTVERTICAL = b'\x0F\x00\x00\x00\x42\x72\x65\x61\x73\x74\x56\x65\x72\x74\x69\x63\x61\x6C\x00'
    BREASTWIDTH = b'\x0C\x00\x00\x00\x42\x72\x65\x61\x73\x74\x57\x69\x64\x74\x68\x00'
    TINYTITTIES = b'\x0C\x00\x00\x00\x54\x69\x6E\x79\x54\x69\x74\x74\x69\x65\x73\x00'
    NIPPLERADIUS = b'\x0D\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x52\x61\x64\x69\x75\x73\x00'
    NIPPLEFAT = b'\x0A\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x46\x61\x74\x00'
    NIPPLEPERK = b'\x0B\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x50\x65\x72\x6B\x00'
    AREOLAERADIUS = b'\x0E\x00\x00\x00\x41\x72\x65\x6F\x6C\x61\x65\x52\x61\x64\x69\x75\x73\x00'
    AREOLAEFAT = b'\x0B\x00\x00\x00\x41\x72\x65\x6F\x6C\x61\x65\x46\x61\x74\x00'
    AREOLAEDEPTH = b'\x0D\x00\x00\x00\x41\x72\x65\x6F\x6C\x61\x65\x44\x65\x70\x74\x68\x00'
    
    def __init__(self, breast_data):
        self._parse_breast_data(breast_data)
    
    def _parse_breast_data(self, breast_data):
        _, self.breastsize,     breast_data = self._try_parse_float_property(breast_data, self.BREASTSIZE)
        _, self.breastdepth,    breast_data = self._try_parse_float_property(breast_data, self.BREASTDEPTH)
        _, self.breastheight,   breast_data = self._try_parse_float_property(breast_data, self.BREASTHEIGHT)
        _, self.breastprotrude, breast_data = self._try_parse_float_property(breast_data, self.BREASTPROTRUDE)
        _, self.breastcleavage, breast_data = self._try_parse_float_property(breast_data, self.BREASTCLEAVAGE)
        _, self.breastvertical, breast_data = self._try_parse_float_property(breast_data, self.BREASTVERTICAL)
        _, self.breastwidth,    breast_data = self._try_parse_float_property(breast_data, self.BREASTWIDTH)
        _, self.tinytitties,    breast_data = self._try_parse_float_property(breast_data, self.TINYTITTIES)
        _, self.nippleradius,   breast_data = self._try_parse_float_property(breast_data, self.NIPPLERADIUS)
        _, self.nipplefat,      breast_data = self._try_parse_float_property(breast_data, self.NIPPLEFAT)
        _, self.nippleperk,     breast_data = self._try_parse_float_property(breast_data, self.NIPPLEPERK)
        _, self.areolaeradius,  breast_data = self._try_parse_float_property(breast_data, self.AREOLAERADIUS)
        _, self.areolaefat,     breast_data = self._try_parse_float_property(breast_data, self.AREOLAEFAT)
        _, self.areolaedepth,   breast_data = self._try_parse_float_property(breast_data, self.AREOLAEDEPTH)
        self.remain = breast_data
        
        list_max = [
            self.breastsize,
            self.breastdepth,
            self.breastheight,
            self.breastprotrude,
            self.breastcleavage,
            self.breastvertical,
            self.breastwidth,
            self.tinytitties,
        ]
        list_range_5 = [
            self.tinytitties,
            self.nippleradius,
            self.nipplefat,
            self.nippleperk,
            self.areolaeradius,
            self.areolaefat,
            self.areolaedepth,
        ]
    
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_float_property_bytes(self.breastsize, self.BREASTSIZE))
        data_out.append(self._try_get_float_property_bytes(self.breastdepth, self.BREASTDEPTH))
        data_out.append(self._try_get_float_property_bytes(self.breastheight, self.BREASTHEIGHT))
        data_out.append(self._try_get_float_property_bytes(self.breastprotrude, self.BREASTPROTRUDE))
        data_out.append(self._try_get_float_property_bytes(self.breastcleavage, self.BREASTCLEAVAGE))
        data_out.append(self._try_get_float_property_bytes(self.breastvertical, self.BREASTVERTICAL))
        data_out.append(self._try_get_float_property_bytes(self.breastwidth, self.BREASTWIDTH))
        data_out.append(self._try_get_float_property_bytes(self.tinytitties, self.TINYTITTIES))
        data_out.append(self._try_get_float_property_bytes(self.nippleradius, self.NIPPLERADIUS))
        data_out.append(self._try_get_float_property_bytes(self.nipplefat, self.NIPPLEFAT))
        data_out.append(self._try_get_float_property_bytes(self.nippleperk, self.NIPPLEPERK))
        data_out.append(self._try_get_float_property_bytes(self.areolaeradius, self.AREOLAERADIUS))
        data_out.append(self._try_get_float_property_bytes(self.areolaefat, self.AREOLAEFAT))
        data_out.append(self._try_get_float_property_bytes(self.areolaedepth, self.AREOLAEDEPTH))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class Material(Appearance):
    LIGHTCOLOR = b'\x0B\x00\x00\x00\x4C\x69\x67\x68\x74\x43\x6F\x6C\x6F\x72\x00'
    LIGHTINTENSITY = b'\x0F\x00\x00\x00\x4C\x69\x67\x68\x74\x49\x6E\x74\x65\x6E\x73\x69\x74\x79\x00'
    EFFECTCOLOR = b'\x0C\x00\x00\x00\x45\x66\x66\x65\x63\x74\x43\x6F\x6C\x6F\x72\x00'
    EFFECTGLOW = b'\x0B\x00\x00\x00\x45\x66\x66\x65\x63\x74\x47\x6C\x6F\x77\x00'
    SKINCOLOR = b'\x0A\x00\x00\x00\x53\x6B\x69\x6E\x43\x6F\x6C\x6F\x72\x00'
    MUSCLEDETAILS = b'\x0E\x00\x00\x00\x4D\x75\x73\x63\x6C\x65\x44\x65\x74\x61\x69\x6C\x73\x00'
    SOFTDETAILS = b'\x0C\x00\x00\x00\x53\x6F\x66\x74\x44\x65\x74\x61\x69\x6C\x73\x00'
    BODYDETAILS = b'\x0C\x00\x00\x00\x42\x6F\x64\x79\x44\x65\x74\x61\x69\x6C\x73\x00'
    SKINFADECOLOR = b'\x0E\x00\x00\x00\x53\x6B\x69\x6E\x46\x61\x64\x65\x43\x6F\x6C\x6F\x72\x00'
    SKINROUGHNESS = b'\x0E\x00\x00\x00\x53\x6B\x69\x6E\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    SKINMETAL = b'\x0A\x00\x00\x00\x53\x6B\x69\x6E\x4D\x65\x74\x61\x6C\x00'
    SKINGLOW = b'\x09\x00\x00\x00\x53\x6B\x69\x6E\x47\x6C\x6F\x77\x00'
    SKINSSSCOLOR = b'\x0D\x00\x00\x00\x53\x6B\x69\x6E\x53\x53\x53\x43\x6F\x6C\x6F\x72\x00'
    SPECULAR = b'\x09\x00\x00\x00\x53\x70\x65\x63\x75\x6C\x61\x72\x00'
    SKINFADE = b'\x09\x00\x00\x00\x53\x6B\x69\x6E\x46\x61\x64\x65\x00'
    ANIMATEDGLOW = b'\x0D\x00\x00\x00\x41\x6E\x69\x6D\x61\x74\x65\x64\x47\x6C\x6F\x77\x00'
    NIPPLECOLOR = b'\x0C\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x43\x6F\x6C\x6F\x72\x00'
    NIPPLEROUGHNESS = b'\x10\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    NIPPLEMETAL = b'\x0C\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x4D\x65\x74\x61\x6C\x00'
    NIPPLEGLOW = b'\x0B\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x47\x6C\x6F\x77\x00'
    NIPPLEACCENTCOLOR = b'\x12\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x41\x63\x63\x65\x6E\x74\x43\x6F\x6C\x6F\x72\x00'
    NIPPLEACCENTROUGHNESS = b'\x16\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x41\x63\x63\x65\x6E\x74\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    NIPPLEACCENTMETAL = b'\x12\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x41\x63\x63\x65\x6E\x74\x4D\x65\x74\x61\x6C\x00'
    NIPPLEACCENTGLOW = b'\x11\x00\x00\x00\x4E\x69\x70\x70\x6C\x65\x41\x63\x63\x65\x6E\x74\x47\x6C\x6F\x77\x00'
    VAGINACOLOR = b'\x0C\x00\x00\x00\x56\x61\x67\x69\x6E\x61\x43\x6F\x6C\x6F\x72\x00'
    VAGINAROUGHNESS = b'\x10\x00\x00\x00\x56\x61\x67\x69\x6E\x61\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    VAGINAMETAL = b'\x0C\x00\x00\x00\x56\x61\x67\x69\x6E\x61\x4D\x65\x74\x61\x6C\x00'
    VAGINAGLOW = b'\x0B\x00\x00\x00\x56\x61\x67\x69\x6E\x61\x47\x6C\x6F\x77\x00'
    DICKBASECOLOR = b'\x0E\x00\x00\x00\x44\x69\x63\x6B\x42\x61\x73\x65\x43\x6F\x6C\x6F\x72\x00'
    DICKCOLOR = b'\x0A\x00\x00\x00\x44\x69\x63\x6B\x43\x6F\x6C\x6F\x72\x00'
    DICKROUGHNESS = b'\x0E\x00\x00\x00\x44\x69\x63\x6B\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    DICKMETAL = b'\x0A\x00\x00\x00\x44\x69\x63\x6B\x4D\x65\x74\x61\x6C\x00'
    DICKGLOW = b'\x09\x00\x00\x00\x44\x69\x63\x6B\x47\x6C\x6F\x77\x00'
    DICKTIPCOLOR = b'\x0D\x00\x00\x00\x44\x69\x63\x6B\x54\x69\x70\x43\x6F\x6C\x6F\x72\x00'
    DICKTIPROUGHNESS = b'\x11\x00\x00\x00\x44\x69\x63\x6B\x54\x69\x70\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    DICKTIPMETAL = b'\x0D\x00\x00\x00\x44\x69\x63\x6B\x54\x69\x70\x4D\x65\x74\x61\x6C\x00'
    DICKTIPGLOW = b'\x0C\x00\x00\x00\x44\x69\x63\x6B\x54\x69\x70\x47\x6C\x6F\x77\x00'
    SCROTUMCOLOR = b'\x0D\x00\x00\x00\x53\x63\x72\x6F\x74\x75\x6D\x43\x6F\x6C\x6F\x72\x00'
    SCROTUMROUGHNESS = b'\x11\x00\x00\x00\x53\x63\x72\x6F\x74\x75\x6D\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    SCROTUMMETAL = b'\x0D\x00\x00\x00\x53\x63\x72\x6F\x74\x75\x6D\x4D\x65\x74\x61\x6C\x00'
    SCROTUMGLOW = b'\x0C\x00\x00\x00\x53\x63\x72\x6F\x74\x75\x6D\x47\x6C\x6F\x77\x00'
    BLURSHEATHTINT = b'\x0F\x00\x00\x00\x42\x6C\x75\x72\x53\x68\x65\x61\x74\x68\x54\x69\x6E\x74\x00'
    ANUSCOLOR = b'\x0A\x00\x00\x00\x41\x6E\x75\x73\x43\x6F\x6C\x6F\x72\x00'
    ANUSROUGHNESS = b'\x0E\x00\x00\x00\x41\x6E\x75\x73\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    ANUSMETAL = b'\x0A\x00\x00\x00\x41\x6E\x75\x73\x4D\x65\x74\x61\x6C\x00'
    ANUSGLOW = b'\x09\x00\x00\x00\x41\x6E\x75\x73\x47\x6C\x6F\x77\x00'
    LIPSCOLOR = b'\x0A\x00\x00\x00\x4C\x69\x70\x73\x43\x6F\x6C\x6F\x72\x00'
    LIPSROUGHNESS = b'\x0E\x00\x00\x00\x4C\x69\x70\x73\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    LIPSMETAL = b'\x0A\x00\x00\x00\x4C\x69\x70\x73\x4D\x65\x74\x61\x6C\x00'
    LIPSGLOW = b'\x09\x00\x00\x00\x4C\x69\x70\x73\x47\x6C\x6F\x77\x00'
    EYESOCKETCOLOR = b'\x0F\x00\x00\x00\x45\x79\x65\x53\x6F\x63\x6B\x65\x74\x43\x6F\x6C\x6F\x72\x00'
    EYESOCKETSHADOW = b'\x10\x00\x00\x00\x45\x79\x65\x53\x6F\x63\x6B\x65\x74\x53\x68\x61\x64\x6F\x77\x00'
    EYERIMCOLOR = b'\x0C\x00\x00\x00\x45\x79\x65\x52\x69\x6D\x43\x6F\x6C\x6F\x72\x00'
    EYERIMGLOW = b'\x0B\x00\x00\x00\x45\x79\x65\x52\x69\x6D\x47\x6C\x6F\x77\x00'
    EYERIMMETAL = b'\x0C\x00\x00\x00\x45\x79\x65\x52\x69\x6D\x4D\x65\x74\x61\x6C\x00'
    EYERIMROUGHNESS = b'\x10\x00\x00\x00\x45\x79\x65\x52\x69\x6D\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    EYERCOLOR = b'\x0A\x00\x00\x00\x45\x79\x65\x52\x43\x6F\x6C\x6F\x72\x00'
    EYERGLOW = b'\x09\x00\x00\x00\x45\x79\x65\x52\x47\x6C\x6F\x77\x00'
    EYELCOLOR = b'\x0A\x00\x00\x00\x45\x79\x65\x4C\x43\x6F\x6C\x6F\x72\x00'
    EYELGLOW = b'\x09\x00\x00\x00\x45\x79\x65\x4C\x47\x6C\x6F\x77\x00'
    EYESCLERACOLOR = b'\x0F\x00\x00\x00\x45\x79\x65\x53\x63\x6C\x65\x72\x61\x43\x6F\x6C\x6F\x72\x00'
    EYESCLERAGLOW = b'\x0E\x00\x00\x00\x45\x79\x65\x53\x63\x6C\x65\x72\x61\x47\x6C\x6F\x77\x00'
    EYEROUGHNESS = b'\x0D\x00\x00\x00\x45\x79\x65\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    EYEMETAL = b'\x09\x00\x00\x00\x45\x79\x65\x4D\x65\x74\x61\x6C\x00'
    WHOLEEYEMETAL = b'\x0E\x00\x00\x00\x57\x68\x6F\x6C\x65\x45\x79\x65\x4D\x65\x74\x61\x6C\x00'
    WHOLEEYEGLOW = b'\x0D\x00\x00\x00\x57\x68\x6F\x6C\x65\x45\x79\x65\x47\x6C\x6F\x77\x00'
    HAIRCOLOR = b'\x0A\x00\x00\x00\x48\x61\x69\x72\x43\x6F\x6C\x6F\x72\x00'
    HAIRMETAL = b'\x0A\x00\x00\x00\x48\x61\x69\x72\x4D\x65\x74\x61\x6C\x00'
    HAIRROUGHNESSMIN = b'\x11\x00\x00\x00\x48\x61\x69\x72\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x4D\x69\x6E\x00'
    HAIRROUGHNESSMAX = b'\x11\x00\x00\x00\x48\x61\x69\x72\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x4D\x61\x78\x00'
    HAIRROOTCOLOR = b'\x0E\x00\x00\x00\x48\x61\x69\x72\x52\x6F\x6F\x74\x43\x6F\x6C\x6F\x72\x00'
    HAIRTIPCOLOR = b'\x0D\x00\x00\x00\x48\x61\x69\x72\x54\x69\x70\x43\x6F\x6C\x6F\x72\x00'
    HAIRGLOW = b'\x09\x00\x00\x00\x48\x61\x69\x72\x47\x6C\x6F\x77\x00'
    HAIRROUGHNESS = b'\x0E\x00\x00\x00\x48\x61\x69\x72\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    HAIRSCATTER = b'\x0C\x00\x00\x00\x48\x61\x69\x72\x53\x63\x61\x74\x74\x65\x72\x00'
    HAIRHUEVARIATION = b'\x11\x00\x00\x00\x48\x61\x69\x72\x48\x75\x65\x56\x61\x72\x69\x61\x74\x69\x6F\x6E\x00'
    HAIRVALUEVARIATION = b'\x13\x00\x00\x00\x48\x61\x69\x72\x56\x61\x6C\x75\x65\x56\x61\x72\x69\x61\x74\x69\x6F\x6E\x00'
    HAIREDGEMASKCONTRAST = b'\x15\x00\x00\x00\x48\x61\x69\x72\x45\x64\x67\x65\x4D\x61\x73\x6B\x43\x6F\x6E\x74\x72\x61\x73\x74\x00'
    HAIREDGEMASKMIN = b'\x10\x00\x00\x00\x48\x61\x69\x72\x45\x64\x67\x65\x4D\x61\x73\x6B\x4D\x69\x6E\x00'
    HAIRDEPTHCONTRAST = b'\x12\x00\x00\x00\x48\x61\x69\x72\x44\x65\x70\x74\x68\x43\x6F\x6E\x74\x72\x61\x73\x74\x00'
    HAIRDEPTHOFFSET = b'\x10\x00\x00\x00\x48\x61\x69\x72\x44\x65\x70\x74\x68\x4F\x66\x66\x73\x65\x74\x00'
    FACIALHAIRCOLOR = b'\x10\x00\x00\x00\x46\x61\x63\x69\x61\x6C\x48\x61\x69\x72\x43\x6F\x6C\x6F\x72\x00'
    EYEBROWCOLOR = b'\x0D\x00\x00\x00\x45\x79\x65\x62\x72\x6F\x77\x43\x6F\x6C\x6F\x72\x00'
    EYEBROWROUGHNESS = b'\x11\x00\x00\x00\x45\x79\x65\x62\x72\x6F\x77\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    EYEBROWMETAL = b'\x0D\x00\x00\x00\x45\x79\x65\x62\x72\x6F\x77\x4D\x65\x74\x61\x6C\x00'
    EYEBROWGLOW = b'\x0C\x00\x00\x00\x45\x79\x65\x62\x72\x6F\x77\x47\x6C\x6F\x77\x00'
    FACEDECORCOLOR = b'\x0F\x00\x00\x00\x46\x61\x63\x65\x44\x65\x63\x6F\x72\x43\x6F\x6C\x6F\x72\x00'
    FACEDECORROUGHNESS = b'\x13\x00\x00\x00\x46\x61\x63\x65\x44\x65\x63\x6F\x72\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    FACEDECORMETAL = b'\x0F\x00\x00\x00\x46\x61\x63\x65\x44\x65\x63\x6F\x72\x4D\x65\x74\x61\x6C\x00'
    FACEDECORGLOW = b'\x0E\x00\x00\x00\x46\x61\x63\x65\x44\x65\x63\x6F\x72\x47\x6C\x6F\x77\x00'
    BODYDECORCOLOR = b'\x0F\x00\x00\x00\x42\x6F\x64\x79\x44\x65\x63\x6F\x72\x43\x6F\x6C\x6F\x72\x00'
    BODYDECORROUGHNESS = b'\x13\x00\x00\x00\x42\x6F\x64\x79\x44\x65\x63\x6F\x72\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    BODYDECORMETAL = b'\x0F\x00\x00\x00\x42\x6F\x64\x79\x44\x65\x63\x6F\x72\x4D\x65\x74\x61\x6C\x00'
    BODYDECORGLOW = b'\x0E\x00\x00\x00\x42\x6F\x64\x79\x44\x65\x63\x6F\x72\x47\x6C\x6F\x77\x00'
    BODYMARKSCOLOR = b'\x0F\x00\x00\x00\x42\x6F\x64\x79\x4D\x61\x72\x6B\x73\x43\x6F\x6C\x6F\x72\x00'
    BODYMARKSROUGHNESS = b'\x13\x00\x00\x00\x42\x6F\x64\x79\x4D\x61\x72\x6B\x73\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x00'
    BODYMARKSMETAL = b'\x0F\x00\x00\x00\x42\x6F\x64\x79\x4D\x61\x72\x6B\x73\x4D\x65\x74\x61\x6C\x00'
    BODYMARKSGLOW = b'\x0E\x00\x00\x00\x42\x6F\x64\x79\x4D\x61\x72\x6B\x73\x47\x6C\x6F\x77\x00'
    NAILSCOLOR = b'\x0B\x00\x00\x00\x4E\x61\x69\x6C\x73\x43\x6F\x6C\x6F\x72\x00'
    NAILSGLOW = b'\x0A\x00\x00\x00\x4E\x61\x69\x6C\x73\x47\x6C\x6F\x77\x00'
    MAWCOLOR = b'\x09\x00\x00\x00\x4D\x61\x77\x43\x6F\x6C\x6F\x72\x00'
    MAWGLOW = b'\x08\x00\x00\x00\x4D\x61\x77\x47\x6C\x6F\x77\x00'
    TEETHCOLOR = b'\x0B\x00\x00\x00\x54\x65\x65\x74\x68\x43\x6F\x6C\x6F\x72\x00'
    FURCOLORA = b'\x0A\x00\x00\x00\x46\x75\x72\x43\x6F\x6C\x6F\x72\x41\x00'
    FURCOLORB = b'\x0A\x00\x00\x00\x46\x75\x72\x43\x6F\x6C\x6F\x72\x42\x00'
    FURCOLORC = b'\x0A\x00\x00\x00\x46\x75\x72\x43\x6F\x6C\x6F\x72\x43\x00'
    FURCOLORD = b'\x0A\x00\x00\x00\x46\x75\x72\x43\x6F\x6C\x6F\x72\x44\x00'
    FURTIPCOLOR = b'\x0C\x00\x00\x00\x46\x75\x72\x54\x69\x70\x43\x6F\x6C\x6F\x72\x00'
    PUBICFURCOLOR = b'\x0E\x00\x00\x00\x50\x75\x62\x69\x63\x46\x75\x72\x43\x6F\x6C\x6F\x72\x00'
    PUBICFURTIPCOLOR = b'\x11\x00\x00\x00\x50\x75\x62\x69\x63\x46\x75\x72\x54\x69\x70\x43\x6F\x6C\x6F\x72\x00'
    BODYATTACHMENTSCOLOR = b'\x15\x00\x00\x00\x42\x6F\x64\x79\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x73\x43\x6F\x6C\x6F\x72\x00'
    ADDITIONALMATERIALTILE = b'\x17\x00\x00\x00\x41\x64\x64\x69\x74\x69\x6F\x6E\x61\x6C\x4D\x61\x74\x65\x72\x69\x61\x6C\x54\x69\x6C\x65\x00'
    ADDITIONALMATERIALCOLOR = b'\x18\x00\x00\x00\x41\x64\x64\x69\x74\x69\x6F\x6E\x61\x6C\x4D\x61\x74\x65\x72\x69\x61\x6C\x43\x6F\x6C\x6F\x72\x00'
    ADDITIONALMATERIALGLOW = b'\x17\x00\x00\x00\x41\x64\x64\x69\x74\x69\x6F\x6E\x61\x6C\x4D\x61\x74\x65\x72\x69\x61\x6C\x47\x6C\x6F\x77\x00'
    ADDITIONALMATERIALUSEOFFSET = b'\x1C\x00\x00\x00\x41\x64\x64\x69\x74\x69\x6F\x6E\x61\x6C\x4D\x61\x74\x65\x72\x69\x61\x6C\x55\x73\x65\x4F\x66\x66\x73\x65\x74\x00'
    ADDITIONALMATERIALOFFSET = b'\x19\x00\x00\x00\x41\x64\x64\x69\x74\x69\x6F\x6E\x61\x6C\x4D\x61\x74\x65\x72\x69\x61\x6C\x4F\x66\x66\x73\x65\x74\x00'
    GLINT = b'\x06\x00\x00\x00\x47\x6C\x69\x6E\x74\x00'
    
    
    LINEARCOLOR = b'\x0C\x00\x00\x00\x4C\x69\x6E\x65\x61\x72\x43\x6F\x6C\x6F\x72\x00' + ByteMacros.STRUCT_PADDING
    CHARACTERATTACHMENTCOLOR = b'\x19\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x41\x74\x74\x61\x63\x68\x6D\x65\x6E\x74\x43\x6F\x6C\x6F\x72\x00' + ByteMacros.STRUCT_PADDING
    
    def __init__(self, material_data):
        self._parse_material_data(material_data)
    
    def _parse_material_data(self, material_data):
        _, lightcolor,                          material_data = self._try_parse_struct_property(material_data, self.LIGHTCOLOR, self.LINEARCOLOR)
        _, self.lightintensity,                 material_data = self._try_parse_float_property(material_data, self.LIGHTINTENSITY)
        _, effectcolor,                         material_data = self._try_parse_struct_property(material_data, self.EFFECTCOLOR, self.LINEARCOLOR)
        _, self.effectglow,                     material_data = self._try_parse_float_property(material_data, self.EFFECTGLOW)
        _, skincolor,                           material_data = self._try_parse_struct_property(material_data, self.SKINCOLOR, self.LINEARCOLOR)
        _, self.muscledetails,                  material_data = self._try_parse_float_property(material_data, self.MUSCLEDETAILS)
        _, self.softdetails,                    material_data = self._try_parse_float_property(material_data, self.SOFTDETAILS)
        _, self.bodydetails,                    material_data = self._try_parse_float_property(material_data, self.BODYDETAILS)
        _, skinfadecolor,                       material_data = self._try_parse_struct_property(material_data, self.SKINFADECOLOR, self.LINEARCOLOR)
        _, self.skinroughness,                  material_data = self._try_parse_float_property(material_data, self.SKINROUGHNESS)
        _, self.skinmetal,                      material_data = self._try_parse_float_property(material_data, self.SKINMETAL)
        _, skinglow,                            material_data = self._try_parse_struct_property(material_data, self.SKINGLOW, self.LINEARCOLOR)
        _, skinssscolor,                        material_data = self._try_parse_struct_property(material_data, self.SKINSSSCOLOR, self.LINEARCOLOR)
        _, self.specular,                       material_data = self._try_parse_float_property(material_data, self.SPECULAR)
        _, self.skinfade,                       material_data = self._try_parse_float_property(material_data, self.SKINFADE)
        _, self.animatedglow,                   material_data = self._try_parse_float_property(material_data, self.ANIMATEDGLOW)
        _, nipplecolor,                         material_data = self._try_parse_struct_property(material_data, self.NIPPLECOLOR, self.LINEARCOLOR)
        _, self.nippleroughness,                material_data = self._try_parse_float_property(material_data, self.NIPPLEROUGHNESS)
        _, self.nipplemetal,                    material_data = self._try_parse_float_property(material_data, self.NIPPLEMETAL)
        _, nippleglow,                          material_data = self._try_parse_struct_property(material_data, self.NIPPLEGLOW, self.LINEARCOLOR)
        _, nippleaccentcolor,                   material_data = self._try_parse_struct_property(material_data, self.NIPPLEACCENTCOLOR, self.LINEARCOLOR)
        _, self.nippleaccentroughness,          material_data = self._try_parse_float_property(material_data, self.NIPPLEACCENTROUGHNESS)
        _, self.nippleaccentmetal,              material_data = self._try_parse_float_property(material_data, self.NIPPLEACCENTMETAL)
        _, nippleaccentglow,                    material_data = self._try_parse_struct_property(material_data, self.NIPPLEACCENTGLOW, self.LINEARCOLOR)
        _, vaginacolor,                         material_data = self._try_parse_struct_property(material_data, self.VAGINACOLOR, self.LINEARCOLOR)
        _, self.vaginaroughness,                material_data = self._try_parse_float_property(material_data, self.VAGINAROUGHNESS)
        _, self.vaginametal,                    material_data = self._try_parse_float_property(material_data, self.VAGINAMETAL)
        _, vaginaglow,                          material_data = self._try_parse_struct_property(material_data, self.VAGINAGLOW, self.LINEARCOLOR)
        _, dickbasecolor,                       material_data = self._try_parse_struct_property(material_data, self.DICKBASECOLOR, self.LINEARCOLOR)
        _, dickcolor,                           material_data = self._try_parse_struct_property(material_data, self.DICKCOLOR, self.LINEARCOLOR)
        _, self.dickroughness,                  material_data = self._try_parse_float_property(material_data, self.DICKROUGHNESS)
        _, self.dickmetal,                      material_data = self._try_parse_float_property(material_data, self.DICKMETAL)
        _, dickglow,                            material_data = self._try_parse_struct_property(material_data, self.DICKGLOW, self.LINEARCOLOR)
        _, dicktipcolor,                        material_data = self._try_parse_struct_property(material_data, self.DICKTIPCOLOR, self.LINEARCOLOR)
        _, self.dicktiproughness,               material_data = self._try_parse_float_property(material_data, self.DICKTIPROUGHNESS)
        _, self.dicktipmetal,                   material_data = self._try_parse_float_property(material_data, self.DICKTIPMETAL)
        _, dicktipglow,                         material_data = self._try_parse_struct_property(material_data, self.DICKTIPGLOW, self.LINEARCOLOR)
        _, scrotumcolor,                        material_data = self._try_parse_struct_property(material_data, self.SCROTUMCOLOR, self.LINEARCOLOR)
        _, self.scrotumroughness,               material_data = self._try_parse_float_property(material_data, self.SCROTUMROUGHNESS)
        _, self.scrotummetal,                   material_data = self._try_parse_float_property(material_data, self.SCROTUMMETAL)
        _, scrotumglow,                         material_data = self._try_parse_struct_property(material_data, self.SCROTUMGLOW, self.LINEARCOLOR)
        _, blursheathtint,                      material_data = self._try_parse_struct_property(material_data, self.BLURSHEATHTINT, self.LINEARCOLOR)
        _, anuscolor,                           material_data = self._try_parse_struct_property(material_data, self.ANUSCOLOR, self.LINEARCOLOR)
        _, self.anusroughness,                  material_data = self._try_parse_float_property(material_data, self.ANUSROUGHNESS)
        _, self.anusmetal,                      material_data = self._try_parse_float_property(material_data, self.ANUSMETAL)
        _, anusglow,                            material_data = self._try_parse_struct_property(material_data, self.ANUSGLOW, self.LINEARCOLOR)
        _, lipscolor,                           material_data = self._try_parse_struct_property(material_data, self.LIPSCOLOR, self.LINEARCOLOR)
        _, self.lipsroughness,                  material_data = self._try_parse_float_property(material_data, self.LIPSROUGHNESS)
        _, self.lipsmetal,                      material_data = self._try_parse_float_property(material_data, self.LIPSMETAL)
        _, lipsglow,                            material_data = self._try_parse_struct_property(material_data, self.LIPSGLOW, self.LINEARCOLOR)
        _, eyesocketcolor,                      material_data = self._try_parse_struct_property(material_data, self.EYESOCKETCOLOR, self.LINEARCOLOR)
        _, self.eyesocketshadow,                material_data = self._try_parse_float_property(material_data, self.EYESOCKETSHADOW)
        _, eyerimcolor,                         material_data = self._try_parse_struct_property(material_data, self.EYERIMCOLOR, self.LINEARCOLOR)
        _, eyerimglow,                          material_data = self._try_parse_struct_property(material_data, self.EYERIMGLOW, self.LINEARCOLOR)
        _, self.eyerimmetal,                    material_data = self._try_parse_float_property(material_data, self.EYERIMMETAL)
        _, self.eyerimroughness,                material_data = self._try_parse_float_property(material_data, self.EYERIMROUGHNESS)
        _, eyercolor,                           material_data = self._try_parse_struct_property(material_data, self.EYERCOLOR, self.LINEARCOLOR)
        _, eyerglow,                            material_data = self._try_parse_struct_property(material_data, self.EYERGLOW, self.LINEARCOLOR)
        _, eyelcolor,                           material_data = self._try_parse_struct_property(material_data, self.EYELCOLOR, self.LINEARCOLOR)
        _, eyelglow,                            material_data = self._try_parse_struct_property(material_data, self.EYELGLOW, self.LINEARCOLOR)
        _, eyescleracolor,                      material_data = self._try_parse_struct_property(material_data, self.EYESCLERACOLOR, self.LINEARCOLOR)
        _, eyescleraglow,                       material_data = self._try_parse_struct_property(material_data, self.EYESCLERAGLOW, self.LINEARCOLOR)
        _, self.eyeroughness,                   material_data = self._try_parse_float_property(material_data, self.EYEROUGHNESS)
        _, self.eyemetal,                       material_data = self._try_parse_float_property(material_data, self.EYEMETAL)
        _, self.wholeeyemetal,                  material_data = self._try_parse_float_property(material_data, self.WHOLEEYEMETAL)
        _, self.wholeeyeglow,                   material_data = self._try_parse_float_property(material_data, self.WHOLEEYEGLOW)
        _, haircolor,                           material_data = self._try_parse_struct_property(material_data, self.HAIRCOLOR, self.LINEARCOLOR)
        _, self.hairmetal,                      material_data = self._try_parse_float_property(material_data, self.HAIRMETAL)
        _, self.hairroughnessmin,               material_data = self._try_parse_float_property(material_data, self.HAIRROUGHNESSMIN)
        _, self.hairroughnessmax,               material_data = self._try_parse_float_property(material_data, self.HAIRROUGHNESSMAX)
        _, hairrootcolor,                       material_data = self._try_parse_struct_property(material_data, self.HAIRROOTCOLOR, self.LINEARCOLOR)
        _, hairtipcolor,                        material_data = self._try_parse_struct_property(material_data, self.HAIRTIPCOLOR, self.LINEARCOLOR)
        _, hairglow,                            material_data = self._try_parse_struct_property(material_data, self.HAIRGLOW, self.LINEARCOLOR)
        _, self.hairroughness,                  material_data = self._try_parse_float_property(material_data, self.HAIRROUGHNESS)
        _, self.hairscatter,                    material_data = self._try_parse_float_property(material_data, self.HAIRSCATTER)
        _, self.hairhuevariation,               material_data = self._try_parse_float_property(material_data, self.HAIRHUEVARIATION)
        _, self.hairvaluevariation,             material_data = self._try_parse_float_property(material_data, self.HAIRVALUEVARIATION)
        _, self.hairedgemaskcontrast,           material_data = self._try_parse_float_property(material_data, self.HAIREDGEMASKCONTRAST)
        _, self.hairedgemaskmin,                material_data = self._try_parse_float_property(material_data, self.HAIREDGEMASKMIN)
        _, self.hairdepthcontrast,              material_data = self._try_parse_float_property(material_data, self.HAIRDEPTHCONTRAST)
        _, self.hairdepthoffset,                material_data = self._try_parse_float_property(material_data, self.HAIRDEPTHOFFSET)
        _, facialhaircolor,                     material_data = self._try_parse_struct_property(material_data, self.FACIALHAIRCOLOR, self.LINEARCOLOR)
        _, eyebrowcolor,                        material_data = self._try_parse_struct_property(material_data, self.EYEBROWCOLOR, self.LINEARCOLOR)
        _, self.eyebrowroughness,               material_data = self._try_parse_float_property(material_data, self.EYEBROWROUGHNESS)
        _, self.eyebrowmetal,                   material_data = self._try_parse_float_property(material_data, self.EYEBROWMETAL)
        _, eyebrowglow,                         material_data = self._try_parse_struct_property(material_data, self.EYEBROWGLOW, self.LINEARCOLOR)
        _, facedecorcolor,                      material_data = self._try_parse_struct_property(material_data, self.FACEDECORCOLOR, self.LINEARCOLOR)
        _, self.facedecorroughness,             material_data = self._try_parse_float_property(material_data, self.FACEDECORROUGHNESS)
        _, self.facedecormetal,                 material_data = self._try_parse_float_property(material_data, self.FACEDECORMETAL)
        _, facedecorglow,                       material_data = self._try_parse_struct_property(material_data, self.FACEDECORGLOW, self.LINEARCOLOR)
        _, bodydecorcolor,                      material_data = self._try_parse_struct_property(material_data, self.BODYDECORCOLOR, self.LINEARCOLOR)
        _, self.bodydecorroughness,             material_data = self._try_parse_float_property(material_data, self.BODYDECORROUGHNESS)
        _, self.bodydecormetal,                 material_data = self._try_parse_float_property(material_data, self.BODYDECORMETAL)
        _, bodydecorglow,                       material_data = self._try_parse_struct_property(material_data, self.BODYDECORGLOW, self.LINEARCOLOR)
        _, bodymarkscolor,                      material_data = self._try_parse_struct_property(material_data, self.BODYMARKSCOLOR, self.LINEARCOLOR)
        _, self.bodymarksroughness,             material_data = self._try_parse_float_property(material_data, self.BODYMARKSROUGHNESS)
        _, self.bodymarksmetal,                 material_data = self._try_parse_float_property(material_data, self.BODYMARKSMETAL)
        _, bodymarksglow,                       material_data = self._try_parse_struct_property(material_data, self.BODYMARKSGLOW, self.LINEARCOLOR)
        _, nailscolor,                          material_data = self._try_parse_struct_property(material_data, self.NAILSCOLOR, self.LINEARCOLOR)
        _, nailsglow,                           material_data = self._try_parse_struct_property(material_data, self.NAILSGLOW, self.LINEARCOLOR)
        _, mawcolor,                            material_data = self._try_parse_struct_property(material_data, self.MAWCOLOR, self.LINEARCOLOR)
        _, mawglow,                             material_data = self._try_parse_struct_property(material_data, self.MAWGLOW, self.LINEARCOLOR)
        _, teethcolor,                          material_data = self._try_parse_struct_property(material_data, self.TEETHCOLOR, self.LINEARCOLOR)
        _, furcolora,                           material_data = self._try_parse_struct_property(material_data, self.FURCOLORA, self.LINEARCOLOR)
        _, furcolorb,                           material_data = self._try_parse_struct_property(material_data, self.FURCOLORB, self.LINEARCOLOR)
        _, furcolorc,                           material_data = self._try_parse_struct_property(material_data, self.FURCOLORC, self.LINEARCOLOR)
        _, furcolord,                           material_data = self._try_parse_struct_property(material_data, self.FURCOLORD, self.LINEARCOLOR)
        _, furtipcolor,                         material_data = self._try_parse_struct_property(material_data, self.FURTIPCOLOR, self.LINEARCOLOR)
        _, pubicfurcolor,                       material_data = self._try_parse_struct_property(material_data, self.PUBICFURCOLOR, self.LINEARCOLOR)
        _, pubicfurtipcolor,                    material_data = self._try_parse_struct_property(material_data, self.PUBICFURTIPCOLOR, self.LINEARCOLOR)
        _, bodyattachmentscolor,                material_data = self._try_parse_struct_property(material_data, self.BODYATTACHMENTSCOLOR, self.CHARACTERATTACHMENTCOLOR)
        _, additionalmaterialtile,              material_data = self._try_parse_struct_property(material_data, self.ADDITIONALMATERIALTILE, self.LINEARCOLOR)
        _, additionalmaterialcolor,             material_data = self._try_parse_struct_property(material_data, self.ADDITIONALMATERIALCOLOR, self.LINEARCOLOR)
        _, additionalmaterialglow,              material_data = self._try_parse_struct_property(material_data, self.ADDITIONALMATERIALGLOW, self.LINEARCOLOR)
        _, self.additionalmaterialuseoffset,    material_data = self._try_parse_float_property(material_data, self.ADDITIONALMATERIALUSEOFFSET)
        _, self.additionalmaterialoffset,       material_data = self._try_parse_float_property(material_data, self.ADDITIONALMATERIALOFFSET)
        _, self.glint,                          material_data = self._try_parse_float_property(material_data, self.GLINT)
        self.remain = material_data
        
        self.lightcolor = LinearColor(lightcolor)
        self.effectcolor = LinearColor(effectcolor)
        self.skincolor = LinearColor(skincolor)
        self.skinfadecolor = LinearColor(skinfadecolor)
        self.skinglow = LinearColor(skinglow)
        self.skinssscolor = LinearColor(skinssscolor)
        self.nipplecolor = LinearColor(nipplecolor)
        self.nippleglow = LinearColor(nippleglow)
        self.nippleaccentcolor = LinearColor(nippleaccentcolor)
        self.nippleaccentglow = LinearColor(nippleaccentglow)
        self.vaginacolor = LinearColor(vaginacolor)
        self.vaginaglow = LinearColor(vaginaglow)
        self.dickbasecolor = LinearColor(dickbasecolor)
        self.dickcolor = LinearColor(dickcolor)
        self.dickglow = LinearColor(dickglow)
        self.dicktipcolor = LinearColor(dicktipcolor)
        self.dicktipglow = LinearColor(dicktipglow)
        self.scrotumcolor = LinearColor(scrotumcolor)
        self.scrotumglow = LinearColor(scrotumglow)
        self.blursheathtint = LinearColor(blursheathtint)
        self.anuscolor = LinearColor(anuscolor)
        self.anusglow = LinearColor(anusglow)
        self.lipscolor = LinearColor(lipscolor)
        self.lipsglow = LinearColor(lipsglow)
        self.eyesocketcolor = LinearColor(eyesocketcolor)
        self.eyerimcolor = LinearColor(eyerimcolor)
        self.eyerimglow = LinearColor(eyerimglow)
        self.eyercolor = LinearColor(eyercolor)
        self.eyerglow = LinearColor(eyerglow)
        self.eyelcolor = LinearColor(eyelcolor)
        self.eyelglow = LinearColor(eyelglow)
        self.eyescleracolor = LinearColor(eyescleracolor)
        self.eyescleraglow = LinearColor(eyescleraglow)
        self.haircolor = LinearColor(haircolor)
        self.hairrootcolor = LinearColor(hairrootcolor)
        self.hairtipcolor = LinearColor(hairtipcolor)
        self.hairglow = LinearColor(hairglow)
        self.facialhaircolor = LinearColor(facialhaircolor)
        self.eyebrowcolor = LinearColor(eyebrowcolor)
        self.eyebrowglow = LinearColor(eyebrowglow)
        self.facedecorcolor = LinearColor(facedecorcolor)
        self.facedecorglow = LinearColor(facedecorglow)
        self.bodydecorcolor = LinearColor(bodydecorcolor)
        self.bodydecorglow = LinearColor(bodydecorglow)
        self.bodymarkscolor = LinearColor(bodymarkscolor)
        self.bodymarksglow = LinearColor(bodymarksglow)
        self.nailscolor = LinearColor(nailscolor)
        self.nailsglow = LinearColor(nailsglow)
        self.mawcolor = LinearColor(mawcolor)
        self.mawglow = LinearColor(mawglow)
        self.teethcolor = LinearColor(teethcolor)
        self.furcolora = LinearColor(furcolora)
        self.furcolorb = LinearColor(furcolorb)
        self.furcolorc = LinearColor(furcolorc)
        self.furcolord = LinearColor(furcolord)
        self.furtipcolor = LinearColor(furtipcolor)
        self.pubicfurcolor = LinearColor(pubicfurcolor)
        self.pubicfurtipcolor = LinearColor(pubicfurtipcolor)
        self.bodyattachmentscolor = CharacterAttachmentColor(bodyattachmentscolor)
        self.additionalmaterialtile = LinearColor(additionalmaterialtile)
        self.additionalmaterialcolor = LinearColor(additionalmaterialcolor)
        self.additionalmaterialglow = LinearColor(additionalmaterialglow)
    
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_struct_property_bytes(self.lightcolor.get_data(),self.LIGHTCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.lightintensity, self.LIGHTINTENSITY))
        data_out.append(self._try_get_struct_property_bytes(self.effectcolor.get_data(), self.EFFECTCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.effectglow, self.EFFECTGLOW))
        data_out.append(self._try_get_struct_property_bytes(self.skincolor.get_data(), self.SKINCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.muscledetails, self.MUSCLEDETAILS))
        data_out.append(self._try_get_float_property_bytes(self.softdetails, self.SOFTDETAILS))
        data_out.append(self._try_get_float_property_bytes(self.bodydetails, self.BODYDETAILS))
        data_out.append(self._try_get_struct_property_bytes(self.skinfadecolor.get_data(), self.SKINFADECOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.skinroughness, self.SKINROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.skinmetal, self.SKINMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.skinglow.get_data(), self.SKINGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.skinssscolor.get_data(), self.SKINSSSCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.specular, self.SPECULAR))
        data_out.append(self._try_get_float_property_bytes(self.skinfade, self.SKINFADE))
        data_out.append(self._try_get_float_property_bytes(self.animatedglow, self.ANIMATEDGLOW))
        data_out.append(self._try_get_struct_property_bytes(self.nipplecolor.get_data(), self.NIPPLECOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.nippleroughness, self.NIPPLEROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.nipplemetal, self.NIPPLEMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.nippleglow.get_data(), self.NIPPLEGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.nippleaccentcolor.get_data(), self.NIPPLEACCENTCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.nippleaccentroughness, self.NIPPLEACCENTROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.nippleaccentmetal, self.NIPPLEACCENTMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.nippleaccentglow.get_data(), self.NIPPLEACCENTGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.vaginacolor.get_data(), self.VAGINACOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.vaginaroughness, self.VAGINAROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.vaginametal, self.VAGINAMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.vaginaglow.get_data(), self.VAGINAGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.dickbasecolor.get_data(), self.DICKBASECOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.dickcolor.get_data(), self.DICKCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.dickroughness, self.DICKROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.dickmetal, self.DICKMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.dickglow.get_data(), self.DICKGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.dicktipcolor.get_data(), self.DICKTIPCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.dicktiproughness, self.DICKTIPROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.dicktipmetal, self.DICKTIPMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.dicktipglow.get_data(), self.DICKTIPGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.scrotumcolor.get_data(), self.SCROTUMCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.scrotumroughness, self.SCROTUMROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.scrotummetal, self.SCROTUMMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.scrotumglow.get_data(), self.SCROTUMGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.blursheathtint.get_data(), self.BLURSHEATHTINT, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.anuscolor.get_data(), self.ANUSCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.anusroughness, self.ANUSROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.anusmetal, self.ANUSMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.anusglow.get_data(), self.ANUSGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.lipscolor.get_data(), self.LIPSCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.lipsroughness, self.LIPSROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.lipsmetal, self.LIPSMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.lipsglow.get_data(), self.LIPSGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyesocketcolor.get_data(), self.EYESOCKETCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.eyesocketshadow, self.EYESOCKETSHADOW))
        data_out.append(self._try_get_struct_property_bytes(self.eyerimcolor.get_data(), self.EYERIMCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyerimglow.get_data(), self.EYERIMGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.eyerimmetal, self.EYERIMMETAL))
        data_out.append(self._try_get_float_property_bytes(self.eyerimroughness, self.EYERIMROUGHNESS))
        data_out.append(self._try_get_struct_property_bytes(self.eyercolor.get_data(), self.EYERCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyerglow.get_data(), self.EYERGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyelcolor.get_data(), self.EYELCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyelglow.get_data(), self.EYELGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyescleracolor.get_data(), self.EYESCLERACOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyescleraglow.get_data(), self.EYESCLERAGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.eyeroughness, self.EYEROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.eyemetal, self.EYEMETAL))
        data_out.append(self._try_get_float_property_bytes(self.wholeeyemetal, self.WHOLEEYEMETAL))
        data_out.append(self._try_get_float_property_bytes(self.wholeeyeglow, self.WHOLEEYEGLOW))
        data_out.append(self._try_get_struct_property_bytes(self.haircolor.get_data(), self.HAIRCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.hairmetal, self.HAIRMETAL))
        data_out.append(self._try_get_float_property_bytes(self.hairroughnessmin, self.HAIRROUGHNESSMIN))
        data_out.append(self._try_get_float_property_bytes(self.hairroughnessmax, self.HAIRROUGHNESSMAX))
        data_out.append(self._try_get_struct_property_bytes(self.hairrootcolor.get_data(), self.HAIRROOTCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.hairtipcolor.get_data(), self.HAIRTIPCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.hairglow.get_data(), self.HAIRGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.hairroughness, self.HAIRROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.hairscatter, self.HAIRSCATTER))
        data_out.append(self._try_get_float_property_bytes(self.hairhuevariation, self.HAIRHUEVARIATION))
        data_out.append(self._try_get_float_property_bytes(self.hairvaluevariation, self.HAIRVALUEVARIATION))
        data_out.append(self._try_get_float_property_bytes(self.hairedgemaskcontrast, self.HAIREDGEMASKCONTRAST))
        data_out.append(self._try_get_float_property_bytes(self.hairedgemaskmin, self.HAIREDGEMASKMIN))
        data_out.append(self._try_get_float_property_bytes(self.hairdepthcontrast, self.HAIRDEPTHCONTRAST))
        data_out.append(self._try_get_float_property_bytes(self.hairdepthoffset, self.HAIRDEPTHOFFSET))
        data_out.append(self._try_get_struct_property_bytes(self.facialhaircolor.get_data(), self.FACIALHAIRCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.eyebrowcolor.get_data(), self.EYEBROWCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.eyebrowroughness, self.EYEBROWROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.eyebrowmetal, self.EYEBROWMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.eyebrowglow.get_data(), self.EYEBROWGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.facedecorcolor.get_data(), self.FACEDECORCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.facedecorroughness, self.FACEDECORROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.facedecormetal, self.FACEDECORMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.facedecorglow.get_data(), self.FACEDECORGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.bodydecorcolor.get_data(), self.BODYDECORCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.bodydecorroughness, self.BODYDECORROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.bodydecormetal, self.BODYDECORMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.bodydecorglow.get_data(), self.BODYDECORGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.bodymarkscolor.get_data(), self.BODYMARKSCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.bodymarksroughness, self.BODYMARKSROUGHNESS))
        data_out.append(self._try_get_float_property_bytes(self.bodymarksmetal, self.BODYMARKSMETAL))
        data_out.append(self._try_get_struct_property_bytes(self.bodymarksglow.get_data(), self.BODYMARKSGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.nailscolor.get_data(), self.NAILSCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.nailsglow.get_data(), self.NAILSGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.mawcolor.get_data(), self.MAWCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.mawglow.get_data(), self.MAWGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.teethcolor.get_data(), self.TEETHCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.furcolora.get_data(), self.FURCOLORA, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.furcolorb.get_data(), self.FURCOLORB, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.furcolorc.get_data(), self.FURCOLORC, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.furcolord.get_data(), self.FURCOLORD, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.furtipcolor.get_data(), self.FURTIPCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.pubicfurcolor.get_data(), self.PUBICFURCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.pubicfurtipcolor.get_data(), self.PUBICFURTIPCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.bodyattachmentscolor.get_data(), self.BODYATTACHMENTSCOLOR, self.CHARACTERATTACHMENTCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.additionalmaterialtile.get_data(), self.ADDITIONALMATERIALTILE, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.additionalmaterialcolor.get_data(), self.ADDITIONALMATERIALCOLOR, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.additionalmaterialglow.get_data(), self.ADDITIONALMATERIALGLOW, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.additionalmaterialuseoffset, self.ADDITIONALMATERIALUSEOFFSET))
        data_out.append(self._try_get_float_property_bytes(self.additionalmaterialoffset, self.ADDITIONALMATERIALOFFSET))
        data_out.append(self._try_get_float_property_bytes(self.glint, self.GLINT))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class CharacterAttachmentColor(Material):
    COLORA = b'\x07\x00\x00\x00\x43\x6F\x6C\x6F\x72\x41\x00'
    COLORB = b'\x07\x00\x00\x00\x43\x6F\x6C\x6F\x72\x42\x00'
    COLORC = b'\x07\x00\x00\x00\x43\x6F\x6C\x6F\x72\x43\x00'
    COLORD = b'\x07\x00\x00\x00\x43\x6F\x6C\x6F\x72\x44\x00'
    GLOWA = b'\x06\x00\x00\x00\x47\x6C\x6F\x77\x41\x00'
    GLOWB = b'\x06\x00\x00\x00\x47\x6C\x6F\x77\x42\x00'
    GLOWC = b'\x06\x00\x00\x00\x47\x6C\x6F\x77\x43\x00'
    GLOWD = b'\x06\x00\x00\x00\x47\x6C\x6F\x77\x44\x00'
    METALA = b'\x07\x00\x00\x00\x4D\x65\x74\x61\x6C\x41\x00'
    METALB = b'\x07\x00\x00\x00\x4D\x65\x74\x61\x6C\x42\x00'
    METALC = b'\x07\x00\x00\x00\x4D\x65\x74\x61\x6C\x43\x00'
    METALD = b'\x07\x00\x00\x00\x4D\x65\x74\x61\x6C\x44\x00'
    ROUGHNESSMIN = b'\x0D\x00\x00\x00\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x4D\x69\x6E\x00'
    ROUGHNESSMAX = b'\x0D\x00\x00\x00\x52\x6F\x75\x67\x68\x6E\x65\x73\x73\x4D\x61\x78\x00'
    UNDERFURADJUST = b'\x0F\x00\x00\x00\x55\x6E\x64\x65\x72\x46\x75\x72\x41\x64\x6A\x75\x73\x74\x00'

    def __init__(self, color_data):
        self._parse_color_data(color_data)
        
    def _parse_color_data(self, color_data):
        _, colora,              color_data = self._try_parse_struct_property(color_data, self.COLORA, self.LINEARCOLOR)
        _, colorb,              color_data = self._try_parse_struct_property(color_data, self.COLORB, self.LINEARCOLOR)
        _, colorc,              color_data = self._try_parse_struct_property(color_data, self.COLORC, self.LINEARCOLOR)
        _, colord,              color_data = self._try_parse_struct_property(color_data, self.COLORD, self.LINEARCOLOR)
        _, glowa,               color_data = self._try_parse_struct_property(color_data, self.GLOWA, self.LINEARCOLOR)
        _, glowb,               color_data = self._try_parse_struct_property(color_data, self.GLOWB, self.LINEARCOLOR)
        _, glowc,               color_data = self._try_parse_struct_property(color_data, self.GLOWC, self.LINEARCOLOR)
        _, glowd,               color_data = self._try_parse_struct_property(color_data, self.GLOWD, self.LINEARCOLOR)
        _, self.metala,         color_data = self._try_parse_float_property(color_data, self.METALA)
        _, self.metalb,         color_data = self._try_parse_float_property(color_data, self.METALB)
        _, self.metalc,         color_data = self._try_parse_float_property(color_data, self.METALC)
        _, self.metald,         color_data = self._try_parse_float_property(color_data, self.METALD)
        _, self.roughnessmin,   color_data = self._try_parse_float_property(color_data, self.ROUGHNESSMIN)
        _, self.roughnessmax,   color_data = self._try_parse_float_property(color_data, self.ROUGHNESSMAX)
        _, self.underfuradjust, color_data = self._try_parse_float_property(color_data, self.UNDERFURADJUST)
        self.remain = color_data
        
        self.colora = LinearColor(colora)
        self.colorb = LinearColor(colorb)
        self.colorc = LinearColor(colorc)
        self.colord = LinearColor(colord)
        self.glowa = LinearColor(glowa)
        self.glowb = LinearColor(glowb)
        self.glowc = LinearColor(glowc)
        self.glowd = LinearColor(glowd)
    
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_struct_property_bytes(self.colora.get_data(), self.COLORA, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.colorb.get_data(), self.COLORB, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.colorc.get_data(), self.COLORC, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.colord.get_data(), self.COLORD, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.glowa.get_data(), self.GLOWA, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.glowb.get_data(), self.GLOWB, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.glowc.get_data(), self.GLOWC, self.LINEARCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.glowd.get_data(), self.GLOWD, self.LINEARCOLOR))
        data_out.append(self._try_get_float_property_bytes(self.metala, self.METALA))
        data_out.append(self._try_get_float_property_bytes(self.metalb, self.METALB))
        data_out.append(self._try_get_float_property_bytes(self.metalc, self.METALC))
        data_out.append(self._try_get_float_property_bytes(self.metald, self.METALD))
        data_out.append(self._try_get_float_property_bytes(self.roughnessmin, self.ROUGHNESSMIN))
        data_out.append(self._try_get_float_property_bytes(self.roughnessmax, self.ROUGHNESSMAX))
        data_out.append(self._try_get_float_property_bytes(self.underfuradjust, self.UNDERFURADJUST))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class LinearColor(Material):
    def __init__(self, linearcolor_data):
        self._parse_linearcolor_data(linearcolor_data)
        
    def _parse_linearcolor_data(self, linearcolor_data):
        self.red    = linearcolor_data[:4]
        self.green  = linearcolor_data[4:8]
        self.blue   = linearcolor_data[8:12]
        self.alpha  = linearcolor_data[12:16]
        self.remain = linearcolor_data[16:]
        if self.remain:
            raise
    
    def get_data(self):
        data_out = []
        data_out.append(self.red)
        data_out.append(self.green)
        data_out.append(self.blue)
        data_out.append(self.alpha)
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class AttachmentMaterial(Material):
    ACCESSORYCOLOR = b'\x0F\x00\x00\x00\x41\x63\x63\x65\x73\x73\x6F\x72\x79\x43\x6F\x6C\x6F\x72\x00'
    UPPERCLOTHINGCOLOR = b'\x13\x00\x00\x00\x55\x70\x70\x65\x72\x43\x6C\x6F\x74\x68\x69\x6E\x67\x43\x6F\x6C\x6F\x72\x00'
    LOWERCLOTHINGCOLOR = b'\x13\x00\x00\x00\x4C\x6F\x77\x65\x72\x43\x6C\x6F\x74\x68\x69\x6E\x67\x43\x6F\x6C\x6F\x72\x00'
    UNDERWEARCOLOR = b'\x0F\x00\x00\x00\x55\x6E\x64\x65\x72\x77\x65\x61\x72\x43\x6F\x6C\x6F\x72\x00'
    BOOTSCOLOR = b'\x0B\x00\x00\x00\x42\x6F\x6F\x74\x73\x43\x6F\x6C\x6F\x72\x00'

    def __init__(self, material_data):
        self._parse_material_data(material_data)
    
    def _parse_material_data(self, material_data):
        _, bodyattachmentscolor,      material_data = self._try_parse_struct_property(material_data, self.ACCESSORYCOLOR, self.CHARACTERATTACHMENTCOLOR)
        _, upperclothingcolor,        material_data = self._try_parse_struct_property(material_data, self.UPPERCLOTHINGCOLOR, self.CHARACTERATTACHMENTCOLOR)
        _, lowerclothingcolor,        material_data = self._try_parse_struct_property(material_data, self.LOWERCLOTHINGCOLOR, self.CHARACTERATTACHMENTCOLOR)
        _, underwearcolor,            material_data = self._try_parse_struct_property(material_data, self.UNDERWEARCOLOR, self.CHARACTERATTACHMENTCOLOR)
        _, bootscolor,                material_data = self._try_parse_struct_property(material_data, self.BOOTSCOLOR, self.CHARACTERATTACHMENTCOLOR)
        self.remain = material_data
        
        self.bodyattachmentscolor = CharacterAttachmentColor(bodyattachmentscolor)
        self.upperclothingcolor = CharacterAttachmentColor(upperclothingcolor)
        self.lowerclothingcolor = CharacterAttachmentColor(lowerclothingcolor)
        self.underwearcolor = CharacterAttachmentColor(underwearcolor)
        self.bootscolor = CharacterAttachmentColor(bootscolor)
        
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_struct_property_bytes(self.bodyattachmentscolor.get_data(), self.ACCESSORYCOLOR, self.CHARACTERATTACHMENTCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.upperclothingcolor.get_data(), self.UPPERCLOTHINGCOLOR, self.CHARACTERATTACHMENTCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.lowerclothingcolor.get_data(), self.LOWERCLOTHINGCOLOR, self.CHARACTERATTACHMENTCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.underwearcolor.get_data(), self.UNDERWEARCOLOR, self.CHARACTERATTACHMENTCOLOR))
        data_out.append(self._try_get_struct_property_bytes(self.bootscolor.get_data(), self.BOOTSCOLOR, self.CHARACTERATTACHMENTCOLOR))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class GameplayTag(GenericParsers):
    def __init__(self, gameplaytag_data):
        self._parse_tags(gameplaytag_data)
    
    def _parse_tags(self, gameplaytag_data):
        self.tags = []
        gameplaytag_length = int.from_bytes(gameplaytag_data[:4], 'little')
        gameplaytag_data = gameplaytag_data[4:]
        if gameplaytag_length > 0:
            for _ in range(gameplaytag_length):
                tag_name_length = int.from_bytes(gameplaytag_data[:4], 'little')
                tag_length = tag_name_length + 4
                self.tags.append(gameplaytag_data[:tag_length])
                gameplaytag_data = gameplaytag_data[tag_length:]
        self.remain = gameplaytag_data
    
    def get_data(self):
        bytes_out = []
        bytes_out.append(len(self.tags).to_bytes(4, 'little'))
        for tag in self.tags:
            bytes_out.append(tag)
        bytes_out.append(self.remain)
        return self.list_to_bytes(bytes_out)


'''World Level Classes'''
class MonsterLevels(Appearance):
    LEVEL = b'\x06\x00\x00\x00\x4C\x65\x76\x65\x6C\x00'
    PROGRESS = b'\x09\x00\x00\x00\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    def __init__(self, monsterlevels_data):
        self._parse_monsterlevels_data(monsterlevels_data)
    
    def _parse_monsterlevels_data(self, monsterlevels_data):
        self.monsterlevel = []
        monsterlevels_data = monsterlevels_data[4:]
        count = int.from_bytes(monsterlevels_data[:4], 'little')
        monsterlevels_data = monsterlevels_data[4:]
        for _ in range(count):
            _, tagname,  monsterlevels_data = self._try_parse_name_property(monsterlevels_data, self.TAGNAME)
            _, level,    monsterlevels_data = self._try_parse_int_property(monsterlevels_data, self.LEVEL)
            _, progress, monsterlevels_data = self._try_parse_int_property(monsterlevels_data, self.PROGRESS)
            monsterlevels_data = monsterlevels_data[len(self.NONE):]
            self.monsterlevel.append(MonsterLevel(tagname, level, progress, self.NONE))
        self.remain = monsterlevels_data
        
    def get_data(self):
        data_out = []
        data_out.append(self.MAP_PADDING)
        data_out.append(len(self.monsterlevel).to_bytes(4, 'little'))
        for monsterlevel in self.monsterlevel:
            data_out.append(monsterlevel.get_data())
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class MonsterLevel(MonsterLevels):
    def __init__(self, tagname, level, progress, remain):
        self.tagname = tagname
        self.level = level
        self.progress = progress
        self.remain = remain
        
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_name_property_bytes(self.tagname, self.TAGNAME))
        data_out.append(self.NONE)
        data_out.append(self._try_get_int_property_bytes(self.level, self.LEVEL))
        data_out.append(self._try_get_int_property_bytes(self.progress, self.PROGRESS))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


'''Sex Posistion Classes'''
class PlayerSexPositions(MonsterLevels):
    def __init__(self, playersexpositions_data):
        self._parse_sexpositions(playersexpositions_data)
    
    def _parse_sexpositions(self, playersexpositions_data):
        self.playersexposition_list = []
        while len(playersexpositions_data) > 0:
            _, sexposition, playersexpositions_data, = self._try_parse_name_property(playersexpositions_data, self.TAGNAME)
            playersexpositions_data = playersexpositions_data[len(self.NONE):]
            self.playersexposition_list.append(SexPosition(sexposition, self.NONE))
    
    def get_data(self):
        return self.playersexposition_list

class SexPosition(PlayerSexPositions):
    def __init__(self, sexpositions_data, remain):
        self.sexposition = sexpositions_data
        self.remain = remain
    
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_name_property_bytes(self.sexposition, self.TAGNAME))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


'''Breeder Stat Progress Class'''
class BreederStatProgress(Appearance):
    STRENGTHPROGRESS =  b'\x11\x00\x00\x00\x53\x74\x72\x65\x6E\x67\x74\x68\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    DEXTERITYPROGRESS = b'\x12\x00\x00\x00\x44\x65\x78\x74\x65\x72\x69\x74\x79\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    WILLPOWERPROGRESS = b'\x12\x00\x00\x00\x57\x69\x6C\x6C\x70\x6F\x77\x65\x72\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    ALLUREPROGRESS =    b'\x0F\x00\x00\x00\x41\x6C\x6C\x75\x72\x65\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    FERTILITYPROGRESS = b'\x12\x00\x00\x00\x46\x65\x72\x74\x69\x6C\x69\x74\x79\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    
    def __init__(self, breederstatprogress_data):
        self._parse_breederstatprogress_data(breederstatprogress_data)
    
    def _parse_breederstatprogress_data(self, breederstatprogress_data):
        _, self.strengthprogress,  breederstatprogress_data = self._try_parse_int_property(breederstatprogress_data, self.STRENGTHPROGRESS)
        _, self.dexterityprogress, breederstatprogress_data = self._try_parse_int_property(breederstatprogress_data, self.DEXTERITYPROGRESS)
        _, self.willpowerprogress, breederstatprogress_data = self._try_parse_int_property(breederstatprogress_data, self.WILLPOWERPROGRESS)
        _, self.allureprogress,    breederstatprogress_data = self._try_parse_int_property(breederstatprogress_data, self.ALLUREPROGRESS)
        _, self.fertilityprogress, breederstatprogress_data = self._try_parse_int_property(breederstatprogress_data, self.FERTILITYPROGRESS)
        self.remain = breederstatprogress_data
        
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_int_property_bytes(self.strengthprogress,  self.STRENGTHPROGRESS))
        data_out.append(self._try_get_int_property_bytes(self.dexterityprogress, self.DEXTERITYPROGRESS))
        data_out.append(self._try_get_int_property_bytes(self.willpowerprogress, self.WILLPOWERPROGRESS))
        data_out.append(self._try_get_int_property_bytes(self.allureprogress,    self.ALLUREPROGRESS))
        data_out.append(self._try_get_int_property_bytes(self.fertilityprogress, self.FERTILITYPROGRESS))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


'''World State Classes'''
class WorldState(Appearance):
    SECONDS = b'\x08\x00\x00\x00\x53\x65\x63\x6F\x6E\x64\x73\x00'
    MINUTE = b'\x07\x00\x00\x00\x4D\x69\x6E\x75\x74\x65\x00'
    HOUR = b'\x05\x00\x00\x00\x48\x6F\x75\x72\x00'
    DAY = b'\x04\x00\x00\x00\x44\x61\x79\x00'
    MONTH = b'\x06\x00\x00\x00\x4D\x6F\x6E\x74\x68\x00'
    ACTIVETRAVELSHRINES = b'\x14\x00\x00\x00\x41\x63\x74\x69\x76\x65\x54\x72\x61\x76\x65\x6C\x53\x68\x72\x69\x6E\x65\x73\x00'
    ACQUIREDRANCHUPGRADES = b'\x16\x00\x00\x00\x41\x63\x71\x75\x69\x72\x65\x64\x52\x61\x6E\x63\x68\x55\x70\x67\x72\x61\x64\x65\x73\x00'
    DIALOGUESTATES = b'\x0F\x00\x00\x00\x44\x69\x61\x6C\x6F\x67\x75\x65\x53\x74\x61\x74\x65\x73\x00'
    DIALOGUESTATE = b'\x0E\x00\x00\x00\x44\x69\x61\x6C\x6F\x67\x75\x65\x53\x74\x61\x74\x65\x00' + ByteMacros.STRUCT_PADDING
    MONSTERLEVELS = b'\x0E\x00\x00\x00\x4D\x6F\x6E\x73\x74\x65\x72\x4C\x65\x76\x65\x6C\x73\x00'
    FERNFED = b'\x08\x00\x00\x00\x46\x65\x72\x6E\x46\x65\x64\x00'
    BREEDINGTASKS = b'\x0E\x00\x00\x00\x42\x72\x65\x65\x64\x69\x6E\x67\x54\x61\x73\x6B\x73\x00'
    BREEDINGTASK = b'\x0D\x00\x00\x00\x42\x72\x65\x65\x64\x69\x6E\x67\x54\x61\x73\x6B\x00' + ByteMacros.STRUCT_PADDING
    SPECIALBREEDINGTASKS = b'\x15\x00\x00\x00\x53\x70\x65\x63\x69\x61\x6C\x42\x72\x65\x65\x64\x69\x6E\x67\x54\x61\x73\x6B\x73\x00'
    DAYSSINCEBREEDINGTASKREFRESH = b'\x1D\x00\x00\x00\x44\x61\x79\x73\x53\x69\x6E\x63\x65\x42\x72\x65\x65\x64\x69\x6E\x67\x54\x61\x73\x6B\x52\x65\x66\x72\x65\x73\x68\x00'
    
    def __init__(self, worldstate_data):
        self._parse_worldstate_data(worldstate_data)
    
    def _parse_worldstate_data(self, worldstate_data):
        _, self.seconds,                      worldstate_data = self._try_parse_int_property(worldstate_data,    self.SECONDS)
        _, self.minute,                       worldstate_data = self._try_parse_int_property(worldstate_data,    self.MINUTE)
        _, self.hour,                         worldstate_data = self._try_parse_int_property(worldstate_data,    self.HOUR)
        _, self.day,                          worldstate_data = self._try_parse_int_property(worldstate_data,    self.DAY)
        _, self.month,                        worldstate_data = self._try_parse_int_property(worldstate_data,    self.MONTH)
        _, activetravelshrines,               worldstate_data = self._try_parse_struct_property(worldstate_data, self.ACTIVETRAVELSHRINES, self.GAMEPLAY_TAG_CONTAINER)
        _, acquiredranchupgrades,             worldstate_data = self._try_parse_struct_property(worldstate_data, self.ACQUIREDRANCHUPGRADES, self.GAMEPLAY_TAG_CONTAINER)
        _, dialoguestates,                    worldstate_data = self._try_parse_array_struct_property(worldstate_data,  self.DIALOGUESTATES,  self.DIALOGUESTATES,  self.DIALOGUESTATE)
        _, monsterlevels,                     worldstate_data = self._try_parse_map_property(worldstate_data, self.MONSTERLEVELS, self.STRUCT_PROPERTY)
        _, self.fernfed,                      worldstate_data = self._try_parse_int_property(worldstate_data,    self.FERNFED)
        _, breedingtasks,                     worldstate_data = self._try_parse_array_struct_property(worldstate_data, self.BREEDINGTASKS, self.BREEDINGTASKS, self.BREEDINGTASK)
        _, specialbreedingtasks,              worldstate_data = self._try_parse_array_struct_property(worldstate_data, self.SPECIALBREEDINGTASKS, self.SPECIALBREEDINGTASKS, self.BREEDINGTASK)
        _, self.dayssincebreedingtaskrefresh, worldstate_data = self._try_parse_int_property(worldstate_data,    self.DAYSSINCEBREEDINGTASKREFRESH)
        
        self.remain =                worldstate_data
        self.activetravelshrines =   GameplayTag(activetravelshrines)
        self.acquiredranchupgrades = GameplayTag(acquiredranchupgrades)
        self.dialoguestates =        DialogueStates(dialoguestates)
        self.monsterlevels =         MonsterLevels(monsterlevels)
        self.breedingtasks =         BreedingTasks(breedingtasks)
        self.specialbreedingtasks =  BreedingTasks(specialbreedingtasks)
        
    def get_data(self):
        data_out = []
        data_out.append(self._try_get_int_property_bytes(self.seconds, self.SECONDS))
        data_out.append(self._try_get_int_property_bytes(self.minute, self.MINUTE))
        data_out.append(self._try_get_int_property_bytes(self.hour, self.HOUR))
        data_out.append(self._try_get_int_property_bytes(self.day, self.DAY))
        data_out.append(self._try_get_int_property_bytes(self.month, self.MONTH))
        data_out.append(self._try_get_struct_property_bytes(self.activetravelshrines.get_data(), self.ACTIVETRAVELSHRINES, self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._try_get_struct_property_bytes(self.acquiredranchupgrades.get_data(), self.ACQUIREDRANCHUPGRADES, self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._try_get_array_struct_property_bytes(self.dialoguestates.get_data(), self.DIALOGUESTATES, self.DIALOGUESTATES, self.DIALOGUESTATE))
        data_out.append(self._try_get_map_property_bytes(self.monsterlevels.get_data(), self.MONSTERLEVELS, self.STRUCT_PROPERTY))
        data_out.append(self._try_get_int_property_bytes(self.fernfed, self.FERNFED))
        data_out.append(self._try_get_array_struct_property_bytes(self.breedingtasks.get_data(), self.BREEDINGTASKS, self.BREEDINGTASKS, self.BREEDINGTASK))
        data_out.append(self._try_get_array_struct_property_bytes(self.specialbreedingtasks.get_data(), self.SPECIALBREEDINGTASKS, self.SPECIALBREEDINGTASKS, self.BREEDINGTASK))
        data_out.append(self._try_get_int_property_bytes(self.dayssincebreedingtaskrefresh, self.DAYSSINCEBREEDINGTASKREFRESH))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)

class DialogueStates(Appearance):
    NPC = b'\x04\x00\x00\x00\x4E\x50\x43\x00'
    def __init__(self, dialoguestates_data):
        self._parse_dialoguestates_data(dialoguestates_data)
    
    def _parse_dialoguestates_data(self, dialoguestates_data):
        self.dialoguestates_list = []
        while len(dialoguestates_data) > 0:
            _, npc, dialoguestates_data = self._try_parse_struct_property(dialoguestates_data, self.NPC, self.GAMEPLAY_TAG_CONTAINER)
            _, tags, dialoguestates_data = self._try_parse_struct_property(dialoguestates_data, self.TAGS, self.GAMEPLAY_TAG_CONTAINER)
            dialoguestates_data = dialoguestates_data[len(self.NONE):]
            self.dialoguestates_list.append(DialogueState(npc, tags, self.NONE))
        
    def get_data(self):
        return self.dialoguestates_list

class DialogueState(DialogueStates):
    def __init__(self, npc, tags, remain):
        self.npc = self._parse_npc(npc)
        self.tags = self._parse_tags(tags)
        self.remain = remain
    
    def _parse_npc(self, npc_data):
        variant_values, npc_data = self.split_byte_list(npc_data)
        if len(variant_values) != 2:
            raise
        
        return Variants(variant_values)
    
    def _parse_tags(self, tag_data):
        tag_list, tag_data = self.split_byte_list(tag_data)
        if tag_data:
            raise
        
        return tag_list
    
    def get_data(self):
        bytes_out = []
        tags = len(self.tags).to_bytes(4, 'little') + self.list_to_bytes(self.tags)
        bytes_out.append(self._try_get_struct_property_bytes(self.npc.get_data(), self.NPC, self.GAMEPLAY_TAG_CONTAINER))
        bytes_out.append(self._try_get_struct_property_bytes(tags, self.TAGS, self.GAMEPLAY_TAG_CONTAINER))
        bytes_out.append(self.remain)
        return self.list_to_bytes(bytes_out)

class BreedingTasks(Appearance):
    DISPLAYNAME = b'\x0C\x00\x00\x00\x44\x69\x73\x70\x6C\x61\x79\x4E\x61\x6D\x65\x00'
    DISCRIPTION = b'\x0C\x00\x00\x00\x44\x65\x73\x63\x72\x69\x70\x74\x69\x6F\x6E\x00'
    REQUIREDVARIANT = b'\x10\x00\x00\x00\x52\x65\x71\x75\x69\x72\x65\x64\x56\x61\x72\x69\x61\x6E\x74\x00'
    REQUIREDSTAT = b'\x0D\x00\x00\x00\x52\x65\x71\x75\x69\x72\x65\x64\x53\x74\x61\x74\x00'
    REQUIREDFLUID = b'\x0E\x00\x00\x00\x52\x65\x71\x75\x69\x72\x65\x64\x46\x6C\x75\x69\x64\x00'
    REQUIREDSTATVALUE = b'\x12\x00\x00\x00\x52\x65\x71\x75\x69\x72\x65\x64\x53\x74\x61\x74\x56\x61\x6C\x75\x65\x00'
    REQUIREDFLUIDML = b'\x11\x00\x00\x00\x52\x65\x71\x75\x69\x72\x65\x64\x46\x6C\x75\x69\x64\x5F\x6D\x6C\x00'
    LEVELREQUIREMENT = b'\x11\x00\x00\x00\x4C\x65\x76\x65\x6C\x52\x65\x71\x75\x69\x72\x65\x6D\x65\x6E\x74\x00'
    REQUIREDTRAITS = b'\x0F\x00\x00\x00\x52\x65\x71\x75\x69\x72\x65\x64\x54\x72\x61\x69\x74\x73\x00'
    REQUIREMENTS = b'\x0D\x00\x00\x00\x52\x65\x71\x75\x69\x72\x65\x6D\x65\x6E\x74\x73\x00'
    DIFFICULTY = b'\x0B\x00\x00\x00\x44\x69\x66\x66\x69\x63\x75\x6C\x74\x79\x00'
    REWARD = b'\x07\x00\x00\x00\x52\x65\x77\x61\x72\x64\x00'
    DAYS = b'\x05\x00\x00\x00\x44\x61\x79\x73\x00'
    COMPLETIONTAGS = b'\x0F\x00\x00\x00\x43\x6F\x6D\x70\x6C\x65\x74\x69\x6F\x6E\x54\x61\x67\x73\x00'
    REWARDMESSAGE = b'\x0E\x00\x00\x00\x52\x65\x77\x61\x72\x64\x4D\x65\x73\x73\x61\x67\x65\x00'
    def __init__(self, breedingtasks_data):
        self._parse_breedingtasks_data(breedingtasks_data)
    
    def _parse_breedingtasks_data(self, breedingtasks_data):
        self.breedingtask_list = []
        
        while len(breedingtasks_data) > 0:
            _, displayname,         breedingtasks_data = self._try_parse_text_property(breedingtasks_data, self.DISPLAYNAME)
            _, discription,         breedingtasks_data = self._try_parse_text_property(breedingtasks_data, self.DISCRIPTION)
            _, requiredvariant,     breedingtasks_data = self._try_parse_struct_property(breedingtasks_data, self.REQUIREDVARIANT, self.GAMEPLAY_TAG_CONTAINER)
            _, requiredstat,        breedingtasks_data = self._try_parse_struct_property(breedingtasks_data, self.REQUIREDSTAT, self.GAMEPLAY_TAG)
            _, requiredfluid,       breedingtasks_data = self._try_parse_struct_property(breedingtasks_data, self.REQUIREDFLUID, self.GAMEPLAY_TAG_CONTAINER)
            _, requiredstatvalue,   breedingtasks_data = self._try_parse_int_property(breedingtasks_data, self.REQUIREDSTATVALUE)
            _, requiredfluidml,     breedingtasks_data = self._try_parse_int_property(breedingtasks_data, self.REQUIREDFLUIDML)
            _, levelrequirement,    breedingtasks_data = self._try_parse_int_property(breedingtasks_data, self.LEVELREQUIREMENT)
            _, requiredtraits,      breedingtasks_data = self._try_parse_struct_property(breedingtasks_data, self.REQUIREDTRAITS, self.GAMEPLAY_TAG_CONTAINER)
            _, requirements,        breedingtasks_data = self._try_parse_text_property(breedingtasks_data, self.REQUIREMENTS)
            _, difficulty,          breedingtasks_data = self._try_parse_int_property(breedingtasks_data, self.DIFFICULTY)
            _, reward,              breedingtasks_data = self._try_parse_int_property(breedingtasks_data, self.REWARD)
            _, days,                breedingtasks_data = self._try_parse_int_property(breedingtasks_data, self.DAYS)
            _, completiontags,      breedingtasks_data = self._try_parse_struct_property(breedingtasks_data, self.COMPLETIONTAGS, self.GAMEPLAY_TAG_CONTAINER)
            _, rewardmessage,       breedingtasks_data = self._try_parse_text_property(breedingtasks_data, self.REWARDMESSAGE)
            breedingtasks_data = breedingtasks_data[len(self.NONE):]
            breedingtask = BreedingTask(displayname, discription, requiredvariant, requiredstat, requiredfluid, requiredstatvalue, requiredfluidml, levelrequirement, requiredtraits, requirements, difficulty, reward, days, completiontags, rewardmessage, self.NONE)
            self.breedingtask_list.append(breedingtask)
        
    def get_data(self):
        return self.breedingtask_list

class BreedingTask(BreedingTasks):
    def __init__(self, displayname, discription, requiredvariant, requiredstat, requiredfluid, requiredstatvalue, requiredfluidml, levelrequirement, requiredtraits, requirements, difficulty, reward, days, completiontags, rewardmessage, remain):
        self.displayname = displayname
        self.discription = discription
        _, self.requiredstat, _ = self._try_parse_name_property(requiredstat, self.TAGNAME)
        self.requiredstatvalue = requiredstatvalue
        self.requiredfluidml = requiredfluidml
        self.levelrequirement = levelrequirement
        self.requirements = requirements
        self.difficulty = difficulty
        self.reward = reward
        self.days = days
        self.rewardmessage = rewardmessage
        self.remain = remain
        
        self.requiredvariant = TagContainer(requiredvariant)
        self.requiredfluid = TagContainer(requiredfluid)
        self.requiredtraits = TagContainer(requiredtraits)
        self.completiontags = TagContainer(completiontags)
    
    def get_data(self):
        bytes_out = []
        bytes_out.append(self._try_get_text_property_bytes(self.displayname,    self.DISPLAYNAME))
        bytes_out.append(self._try_get_text_property_bytes(self.discription,    self.DISCRIPTION))
        bytes_out.append(self._try_get_struct_property_bytes(self.requiredvariant.get_data(),   self.REQUIREDVARIANT,   self.GAMEPLAY_TAG_CONTAINER))
        bytes_out.append(self._try_get_struct_property_bytes(self._try_get_name_property_bytes(self.requiredstat, self.TAGNAME) + self.NONE, self.REQUIREDSTAT, self.GAMEPLAY_TAG))
        bytes_out.append(self._try_get_struct_property_bytes(self.requiredfluid.get_data(),     self.REQUIREDFLUID,     self.GAMEPLAY_TAG_CONTAINER))
        bytes_out.append(self._try_get_int_property_bytes(self.requiredstatvalue,   self.REQUIREDSTATVALUE))
        bytes_out.append(self._try_get_int_property_bytes(self.requiredfluidml,     self.REQUIREDFLUIDML))
        bytes_out.append(self._try_get_int_property_bytes(self.levelrequirement,    self.LEVELREQUIREMENT))
        bytes_out.append(self._try_get_struct_property_bytes(self.requiredtraits.get_data(),    self.REQUIREDTRAITS,    self.GAMEPLAY_TAG_CONTAINER))
        bytes_out.append(self._try_get_text_property_bytes(self.requirements,   self.REQUIREMENTS))
        bytes_out.append(self._try_get_int_property_bytes(self.difficulty,          self.DIFFICULTY))
        bytes_out.append(self._try_get_int_property_bytes(self.reward,              self.REWARD))
        bytes_out.append(self._try_get_int_property_bytes(self.days,                self.DAYS))
        bytes_out.append(self._try_get_struct_property_bytes(self.completiontags.get_data(),    self.COMPLETIONTAGS,    self.GAMEPLAY_TAG_CONTAINER))
        bytes_out.append(self._try_get_text_property_bytes(self.rewardmessage,  self.REWARDMESSAGE))
        bytes_out.append(self.remain)
        return self.list_to_bytes(bytes_out)

class PlayerObtainedVariants(GenericParsers):
    def __init__(self, playerobtainedvariants_data):
        self._parse_playerobtainedvariants_data(playerobtainedvariants_data)
    
    def _parse_playerobtainedvariants_data(self, playerobtainedvariants_data):
        self.playerobtainedvariant_list = []
        while len(playerobtainedvariants_data) > 0:
            variant_values, playerobtainedvariants_data = self.split_byte_list(playerobtainedvariants_data)
            if len(variant_values) != 2:
                raise
            self.playerobtainedvariant_list.append(Variants(variant_values))
    
    def get_data(self):
        return self.playerobtainedvariant_list

class TagContainer(GenericParsers):
    def __init__(self, tag_bytes):
        self.tag_list, remain = self.split_byte_list(tag_bytes)
        if remain:
            raise
        
    def get_data(self):
        bytes_out = []
        bytes_out.append(len(self.tag_list).to_bytes(4, 'little'))
        bytes_out.append(self.list_to_bytes(self.tag_list))
        return self.list_to_bytes(bytes_out)

class Variants(GenericParsers):
    def __init__(self, variant_values):
        self.variant_values = variant_values
        
    def get_data(self):
        bytes_out = []
        bytes_out.append(len(self.variant_values).to_bytes(4, 'little'))
        bytes_out.append(self.list_to_bytes(self.variant_values))
        return self.list_to_bytes(bytes_out)


'''Base Save Editor Class'''
class NephelymSaveEditor(Appearance):
    '''Class for editing saves'''
    def __init__(self, save_file=None):
        if save_file:
            self.load(save_file)

    def _parse_save_data(self, save_data):
        data_header, data_monster_and_player, save_data = self._try_parse_array_struct_property(save_data, self.PLAYERMONSTER,          self.PLAYERMONSTER,          self.CHARACTER_DATA)
        _, offspringbuffer,                   save_data = self._try_parse_array_struct_property(save_data, self.OFFSPRINGBUFFER,        self.PLAYERMONSTER,          self.CHARACTER_DATA)
        _, playersexpositions,                save_data = self._try_parse_array_struct_property(save_data, self.PLAYERSEXPOSITIONS,     self.PLAYERSEXPOSITIONS,     self.GAMEPLAY_TAG)
        _, self.playerspirit,                 save_data = self._try_parse_int_property(save_data, self.PLAYERSPIRIT)
        _, playerspiritform_data,             save_data = self._try_parse_struct_property(save_data, self.PLAYERSPIRITFORM,    self.CHATACTER_DATA)
        _, playerobtainedvariants,            save_data = self._try_parse_array_struct_property(save_data, self.PLAYEROBTAINEDVARIANTS, self.PLAYEROBTAINEDVARIANTS, self.GAMEPLAY_TAG_CONTAINER)
        _, playerseenvariants,                save_data = self._try_parse_array_struct_property(save_data, self.PLAYERSEENVARIANTS,     self.PLAYERSEENVARIANTS,     self.GAMEPLAY_TAG_CONTAINER)
        _, gameflags,                         save_data = self._try_parse_struct_property(save_data, self.GAMEFLAGS,           self.GAMEPLAY_TAG_CONTAINER)
        _, worldstate,                        save_data = self._try_parse_struct_property(save_data, self.WORLDSTATE,          self.SEXYWOLDSTATE)
        _, breederstatprogress,               save_data = self._try_parse_struct_property(save_data, self.BREEDERSTATPROGRESS, self.BREEDERSTATRANKPROGRESS)
        self.remain = save_data
        
        self.header                 = Header(data_header)
        self.nephelyms              = self._parse_nephelyms(data_monster_and_player)
        self.playersexpositions     = PlayerSexPositions(playersexpositions)
        self.offspringbuffer        = self._parse_nephelyms(offspringbuffer)
        self.playerspiritform       = PlayerSpiritForm(playerspiritform_data)
        self.playerobtainedvariants = PlayerObtainedVariants(playerobtainedvariants)
        self.playerseenvariants     = PlayerObtainedVariants(playerseenvariants)
        self.gameflags              = GameplayTag(gameflags)
        self.worldstate             = WorldState(worldstate)
        self.breederstatprogress    = BreederStatProgress(breederstatprogress)

    def _parse_nephelyms(self, monster_and_player_data):
        '''
        Parse out Breeder and Nephelyms from PlayerMonster Block
        returns list of Nephelym
        '''
        cursor = 0
        nephelyms = []
        nephelym_name_positions = []
        while cursor != -1:
            pos_name = monster_and_player_data.find(self.PLAYER_MONSTER_NAME, cursor)
            if pos_name == -1:
                break
            nephelym_name_positions.append(pos_name)
            cursor = pos_name + 1
        
        nephelym_name_count = len(nephelym_name_positions)
        if nephelym_name_count == 4:
            nephelyms.append(Nephelym(monster_and_player_data[nephelym_name_positions[0]:]))
        elif nephelym_name_count > 4:
            data_start = 0
            for position_index in range(4, nephelym_name_count, 4):
                nephelym = Nephelym(monster_and_player_data[nephelym_name_positions[data_start]:nephelym_name_positions[position_index]])
                nephelyms.append(nephelym)
                data_start = position_index
            nephelyms.append(Nephelym(monster_and_player_data[nephelym_name_positions[-4]:]))
        return nephelyms

    def _possible_nephelyms(self):
        for race in self.RACES_FEMALE:
            yield self.RACES_FEMALE[race], self.SEXES['female']
        for race in self.RACES_FUTA:
            yield self.RACES_FUTA[race], self.SEXES['futa']
        for race in self.RACES_MALE:
            yield self.RACES_MALE[race], self.SEXES['male']

    def save(self, file_out):
        '''Fix up data and export save'''
        guids = [x.guid for x in self.nephelyms]
        if self.get_player_nephelym() not in guids:
            self.set_player_nephelym()
        
        self.write_save(file_out, self.get_data())

    def load(self, file_in):
        '''Load and parse data from save'''
        save_data = self.load_save(file_in)
        self._parse_save_data(save_data)

    def set_player_nephelym(self, guid=None):
        '''use guid to set which nephelym is the player'''
        if guid is None:
            guid = self.nephelyms[0].guid
        self.header.playerguid = guid

    def get_player_nephelym(self):
        '''get guid of player nephelym'''
        return self.header.playerguid

    def duplicate_nephelym(self, nephelym, count):
        for x in range(count):
            self.nephelyms.append(nephelym.clone())

    def duplicate_all_nephelyms(self, count, ignore_breeder=True):
        for nephelym in range(len(self.nephelyms)):
            if ignore_breeder:
                ignore_breeder = False
                continue
            self.duplicate_nephelym(self.nephelyms[nephelym], count)

    def add_nephelym(self, nephelym):
        '''Add Nephelym to Nephelym list'''
        self.nephelyms.append(nephelym)

    def remove_nephelym(self, nephelym):
        if nephelym in self.nephelyms:
            self.nephelyms.remove(nephelym)

    def remove_all_nephelym(self):
        self.nephelyms = []

    def all_size_nephelyms(self, ignore_breeder=True):
        '''Make copies of all nephelyms and make them all of the sizes'''
        new_nephelyms = []
        for nephelym in self.nephelyms:
            if ignore_breeder:
                ignore_breeder = False
                new_nephelyms.append(nephelym)
                continue
            for trait in nephelym.traits:
                if trait in self.TRAIT_SIZE.values():
                    nephelym.remove_trait(trait)
            for size in self.TRAIT_SIZE.values():
                new_nephelym = nephelym.clone()
                new_nephelym.add_trait(size)
                new_nephelyms.append(new_nephelym)
        self.nephelyms = new_nephelyms

    def export_nephelym(self, nephelym):
        '''Export datablock to file for nephelym, useful for debugging'''
        name = nephelym.name.strip(b'\x00').decode('utf-8')
        race = nephelym.race.strip(b'\x00').decode('utf-8')
        sex  = nephelym.sex.strip(b'\x00').decode('utf-8')
        file_name = f"{name}_{race}_{sex}.bin"
        with open(file_name, 'wb') as f:
            f.write(nephelym.get_data())

    def export_all_nephelym(self):
        for nephelym in self.nephelyms:
            self.export_nephelym(nephelym)

    def generate_all_from_nephelym(self, nephelym):
        '''Generate All possible Nephelym using one nephelym as the base'''
        for race, sex in self._possible_nephelyms():
            new_nephelym = nephelym.clone()
            new_nephelym.change_race(race)
            new_nephelym.change_sex(sex)
            new_nephelym.change_name(race[:-1] + b' ' + sex)
            self.nephelyms.append(new_nephelym)

    def generate_all_from_presets(self, preset_path, template_nephelym=None):
        if template_nephelym is None:
            template_nephelym = self.nephelyms[0]
        for root, dirs, files in os.walk(preset_path):
            for file in files:
                if file.endswith('.sav'):
                    self.nephelyms.append(self.generate_from_preset(os.path.join(root, file), template_nephelym))

    def generate_from_preset(self, preset_path, template_nephelym=None):
        # @TODO generate without having to use a template_nephelym
        if template_nephelym is None:
            template_nephelym = self.nephelyms[0]
        preset = NephelymPreset(preset_path)
        new_nephelym = template_nephelym.clone()
        new_nephelym.change_appearance(preset)
        new_nephelym.change_name(preset.name)
        new_nephelym.change_sex(preset.sex)
        new_nephelym.change_race(preset.race)
        return new_nephelym

    def get_data(self):
        '''Return data in save file format'''
        data_out = []
        data_out.append(self.header.get_data())
        data_out.append(self._try_get_array_struct_property_bytes(self.nephelyms,                         self.PLAYERMONSTER,          self.PLAYERMONSTER,          self.CHARACTER_DATA))
        data_out.append(self._try_get_array_struct_property_bytes(self.offspringbuffer,                   self.OFFSPRINGBUFFER,        self.OFFSPRINGBUFFER,        self.CHARACTER_DATA))
        data_out.append(self._try_get_array_struct_property_bytes(self.playersexpositions.get_data(),     self.PLAYERSEXPOSITIONS,     self.PLAYERSEXPOSITIONS,     self.GAMEPLAY_TAG))
        data_out.append(self._try_get_int_property_bytes(self.playerspirit, self.PLAYERSPIRIT))
        data_out.append(self._try_get_struct_property_bytes(self.playerspiritform.get_data(),    self.PLAYERSPIRITFORM,    self.CHATACTER_DATA))
        data_out.append(self._try_get_array_struct_property_bytes(self.playerobtainedvariants.get_data(), self.PLAYEROBTAINEDVARIANTS, self.PLAYEROBTAINEDVARIANTS, self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._try_get_array_struct_property_bytes(self.playerseenvariants.get_data(),     self.PLAYERSEENVARIANTS,     self.PLAYERSEENVARIANTS,     self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._try_get_struct_property_bytes(self.gameflags.get_data(),           self.GAMEFLAGS,           self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._try_get_struct_property_bytes(self.worldstate.get_data(),          self.WORLDSTATE,          self.SEXYWOLDSTATE))
        data_out.append(self._try_get_struct_property_bytes(self.breederstatprogress.get_data(), self.BREEDERSTATPROGRESS, self.BREEDERSTATRANKPROGRESS))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


if __name__ == "__main__":
    save_in       = r'0.sav'
    save_out      = r'0_.sav'
    preset_folder = r'..\CharacterPresets'
    
    # DEBUGGING: test if parsing and save of save works.
    # Files should be identical, with execption of maybe spiritform variant and some additional gameplaytags container
    Testing = True
    if Testing:
        NephelymSaveEditor(save_in).save(save_out)
        exit()
    
    #Example of transfering colors from one part to another
    if False:
        x = NephelymSaveEditor(save_in)
        breeder = x.nephelyms[0]
        lowerclothingcolorb = breeder.appearance.attachmentmaterial.lowerclothingcolor.colorb
        lowerclothingglowb = breeder.appearance.attachmentmaterial.lowerclothingcolor.glowb
        
        material = breeder.appearance.material
        material.dickcolor = lowerclothingcolorb
        material.dickglow = lowerclothingglowb
        material.dicktipcolor = lowerclothingcolorb
        material.dicktipglow = lowerclothingglowb
        x.save(save_out)
    
    #Example Converting Old saves to Newer version of game. Nephelyms should be safe, but progress may be broken
    if False:
        old_save = NephelymSaveEditor(r'0.sav')
        new_save = NephelymSaveEditor(r'1.sav')
        old_save.header.gvas = new_save.header.gvas
        old_save.save(r'0_.sav')
    
    
    # Instance of Editor
    nephelym_save_editor = NephelymSaveEditor(save_in)
    
    # Breeder/Player is always the first Nephelym unless changed in the save header
    breeder = nephelym_save_editor.nephelyms[0]
    
    # Change the Spirit form to be breeder. Any NephelymBase derived object will work
    nephelym_save_editor.playerspiritform.change_form(breeder)
    
    # DEBUGGING: Export nephelym_data block to file.
    nephelym_save_editor.export_nephelym(breeder)
    
    
    # Looping over nephelyms require copy if altering number of nephelyms.
    for nephelym in nephelym_save_editor.nephelyms.copy():
        nephelym.change_stat_level('rarity', 'E')
    
    # Remove all nephelym from save editor. Includes breeder
    nephelym_save_editor.remove_all_nephelym()
    
    # Add Nephelym to editor
    nephelym_save_editor.add_nephelym(breeder)
    
    # Clone all nephelyms currently in editor producing in all sizes
    nephelym_save_editor.all_size_nephelyms()
    
    # New Nephelym object instance. Needed or changes with affect all instance of exact object. New guid for clones to fix issue of not showing in game
    breeder_clone = breeder.clone()
    
    # Remove ALL traits of Nephelym
    breeder_clone.remove_all_traits()
    
    # Change all stat ranks of Nephelym
    breeder_clone.replace_all_stat_levels('S')
    
    # Change Rarity of Nephelym. A Legendary, E Common
    breeder_clone.change_stat_level('rarity', 'A')
    
    # Give Nephelym all positive traits 
    breeder_clone.all_positive_traits()
    
    # Change Nephelym size
    breeder_clone.change_size('massive')
    
    # Generate Nephelyms from all presets. Template Nephelym for size and traits
    nephelym_save_editor.generate_all_from_presets(preset_folder, breeder_clone)
    
    # Change appearance from another Nephelym. Current example uses last preset
    breeder_clone.change_appearance(nephelym_save_editor.nephelyms[-1])
    
    # Add Nephelym to Nephelyms
    nephelym_save_editor.add_nephelym(breeder_clone)
    
    # Generate all valid possible nephelym. Template Nephelym for appearance, size and traits
    nephelym_save_editor.generate_all_from_nephelym(breeder_clone)
    
    # Change Race. Auto correct sex if invalid pairing
    breeder.change_race('kestrel')
    
    # Change Sex. Auto correct sex if invalid pairing
    breeder.change_sex('female')
    
    # Export Editor data to specified file
    nephelym_save_editor.save(save_out)
