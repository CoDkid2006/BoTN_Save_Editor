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
PlayerMonsters - Breeder and Nephelyms
>Each entity starts with their name
Nephelym
    

PlayerSexPositions - Sex Positions unlocked --ArrayProperty
PlayerSpirit - Player Spirit Energy --IntProperty
PlayerSpiritForm - Spirit Properties --StructProperty
    

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
    STRUCT_PADDING = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    ### Save header macros
    GUID_HEADER = b'\x10\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x47\x75\x69\x64\x00' + STRUCT_PADDING
    PLAYER_UNIQUE_ID = b'\x0F\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x55\x6E\x69\x71\x75\x65\x49\x44\x00' + STRUCT_PROPERTY + GUID_HEADER
    PLAYERWEALTH_ARRAY_PROP = b'\x0D\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x57\x65\x61\x6C\x74\x68\x00' + ARRAY_PROPERTY
    PLAYERBODYFLUIDS_ARRAY_PROP = b'\x11\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x42\x6F\x64\x79\x46\x6C\x75\x69\x64\x73\x00' + ARRAY_PROPERTY
    #Nephelym/Breeder Block Headers
    PLAYERMONSTER = b'\x0F\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x4D\x6F\x6E\x73\x74\x65\x72\x73\x00'
    PLAYERMONSTER_ARRAY_PROP = PLAYERMONSTER + ARRAY_PROPERTY
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
    GUID_PROP = b'\x05\x00\x00\x00\x47\x75\x69\x64\x00' + STRUCT_PADDING
    
    ### Spiritform Macros
    UNIQUEID = b'\x09\x00\x00\x00\x55\x6E\x69\x71\x75\x65\x49\x44\x00'
    SPIRITFORM_GUID = UNIQUEID + STRUCT_PROPERTY + GUID_HEADER
    PLAYERSPIRIT_INT_PROP = b'\x0D\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x70\x69\x72\x69\x74\x00' + INT_PROPERTY
    PLAYERSPIRITFORM_STRUCT_PROP = b'\x11\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x70\x69\x72\x69\x74\x46\x6F\x72\x6D\x00' + STRUCT_PROPERTY
    
    
    ### Footer Macros
    PLAYERSEXPOSITIONS = b'\x13\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x65\x78\x50\x6F\x73\x69\x74\x69\x6F\x6E\x73\x00'
    PLAYERSEXPOSITIONS_ARRAY_PROP = PLAYERSEXPOSITIONS + ARRAY_PROPERTY
    CHATACTER_DATA = b'\x0E\x00\x00\x00\x43\x68\x61\x72\x61\x63\x74\x65\x72\x44\x61\x74\x61\x00' + STRUCT_PADDING
    PLAYEROBTAINEDVARIANTS = b'\x17\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x4F\x62\x74\x61\x69\x6E\x65\x64\x56\x61\x72\x69\x61\x6E\x74\x73\x00'
    PLAYEROBTAINEDVARIANTS_ARRAY_PROP = PLAYEROBTAINEDVARIANTS + ARRAY_PROPERTY
    PLAYERSEENVARIANTS = b'\x13\x00\x00\x00\x50\x6C\x61\x79\x65\x72\x53\x65\x65\x6E\x56\x61\x72\x69\x61\x6E\x74\x73\x00'
    PLAYERSEENVARIANTS_ARRAY_PROP = PLAYERSEENVARIANTS + ARRAY_PROPERTY
    GAMEFLAGS = b'\x0A\x00\x00\x00\x47\x61\x6D\x65\x46\x6C\x61\x67\x73\x00'
    GAMEFLAGS_STRUCT_PROP = GAMEFLAGS + STRUCT_PROPERTY
    WORLDSTATE = b'\x0B\x00\x00\x00\x57\x6F\x72\x6C\x64\x53\x74\x61\x74\x65\x00'
    WORLDSTATE_STRUCT_PROP = WORLDSTATE + STRUCT_PROPERTY
    SEXYWOLDSTATE = b'\x0F\x00\x00\x00\x53\x65\x78\x79\x57\x6F\x72\x6C\x64\x53\x74\x61\x74\x65\x00' + STRUCT_PADDING
    BREEDERSTATPROGRESS = b'\x14\x00\x00\x00\x42\x72\x65\x65\x64\x65\x72\x53\x74\x61\x74\x50\x72\x6F\x67\x72\x65\x73\x73\x00'
    BREEDERSTATPROGRESS_STRUCT_PROP = BREEDERSTATPROGRESS + STRUCT_PROPERTY
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
        '''Return Int value in byte format'''
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
    
    def _parse_guid(self, guid_bytes, guid_macro):
        '''Parses guid from datablock'''
        cursor = guid_bytes.find(guid_macro)
        if cursor == -1:
            raise Exception(f'Invalid Save: {guid_macro}')
        guid_start = cursor + len(guid_macro)
        return guid_bytes[:cursor], guid_bytes[guid_start:guid_start + 16], guid_bytes[guid_start + 16:]
    
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
        name_char_length = name_length - 4
        bytes_out = name_macro \
            + name_length.to_bytes(8, 'little') \
            + b'\x00' \
            + name_char_length.to_bytes(4, 'little') \
            + name_bytes
        return bytes_out
    
    def _get_guid_bytes(self, guid_bytes, guid_macro):
        '''Rebuild guid string'''
        return guid_macro + guid_bytes
    
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


class Header(GenericParsers):
    '''Header Parser'''
    def __init__(self, header_data):
        self._parse_header_data(header_data)
    
    def _parse_header_data(self, header_data):
        self.gvas,                header_data = self._parse_gvas(header_data)
        _, self.playerguid,       header_data = self._parse_guid(header_data, self.PLAYER_UNIQUE_ID)
        _, self.playerwealth,     header_data = self._parse_array_property(header_data, self.PLAYERWEALTH_ARRAY_PROP     ,self.INT_PROPERTY, 4)
        _, self.playerbodyfluids, header_data = self._parse_array_property(header_data, self.PLAYERBODYFLUIDS_ARRAY_PROP ,self.STRUCT_PROPERTY)
        self.remain = header_data
    
    def _parse_gvas(self, header_data):
        cursor = header_data.find(self.PLAYER_UNIQUE_ID)
        if cursor == -1:
            raise Exception('Invalid Header: PLAYER_UNIQUE_ID')
        return header_data[:cursor], header_data[cursor:]
    
    def get_data(self):
        data_out = []
        data_out.append(self.gvas)
        data_out.append(self._get_guid_bytes(self.playerguid, self.PLAYER_UNIQUE_ID))
        data_out.append(self._get_array_property_bytes(self.playerwealth, self.PLAYERWEALTH_ARRAY_PROP, self.INT_PROPERTY, 4))
        data_out.append(self._get_array_property_bytes(self.playerbodyfluids, self.PLAYERBODYFLUIDS_ARRAY_PROP, self.STRUCT_PROPERTY))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


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
        _, self.name,           nephelym_data = self._parse_name(nephelym_data)
        _, self.guid,           nephelym_data = self._parse_guid(nephelym_data, self.NEPHELYM_GUID)
        _, self.race, self.sex, nephelym_data = self._parse_variant(nephelym_data)
        _, self.appearance,     nephelym_data = self._parse_struct_property(nephelym_data, self.APPEARANCE_STRUCT_PROP,    self.CHARACTER_APPEARANCE)
        _, self.splatter,       nephelym_data = self._parse_struct_property(nephelym_data, self.SPLATTER_STRUCT_PROP,      self.FLUID_SPLATTER)
        _, self.citargetvalue,  nephelym_data = self._parse_struct_property(nephelym_data, self.CITARGETVALUE_STRUCT_PROP, self.CHARACTER_MORPH)
        _, self.cibuffer,       nephelym_data = self._parse_struct_property(nephelym_data, self.CIBUFFER_STRUCT_PROP,      self.CHARACTER_MORPH)
        _, self.cirate,         nephelym_data = self._parse_float_property(nephelym_data,  self.CIRATE)
        _, self.cialpha,        nephelym_data = self._parse_float_property(nephelym_data,  self.CIALPHA)
        _, self.appliedscheme,  nephelym_data = self._parse_struct_property(nephelym_data, self.APPLIEDSCHEME_STRUCT_PROP, self.CHARACTER_APPLIED_SCHEME)
        _, self.stats,          nephelym_data = self._parse_struct_property(nephelym_data, self.STAT_STRUCT_PROP,          self.CHARACTER_STATS)
        _, self.mother,         nephelym_data = self._parse_struct_property(nephelym_data, self.MOTHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        _, self.father,         nephelym_data = self._parse_struct_property(nephelym_data, self.FATHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        _, self.traits,         nephelym_data = self._parse_traits(nephelym_data)
        _, self.playertags,     nephelym_data = self._parse_struct_property(nephelym_data, self.PLAYERTAGS_STRUCT_PROP,    self.GAMEPLAY_TAG_CONTAINER)
        _, self.states,         nephelym_data = self._parse_struct_property(nephelym_data, self.STATES_STRUCT_PROP,        self.GAMEPLAY_TAG_CONTAINER)
        _, self.offspringid,    nephelym_data = self._parse_struct_property(nephelym_data, self.OFFSPRINGID_STRUCT_PROP,   self.GUID_PROP)
        _, self.lastmateid,     nephelym_data = self._parse_struct_property(nephelym_data, self.LASTMATEID_STRUCT_PROP,    self.GUID_PROP)
        self.lastmatesexcount = nephelym_data
    
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
        data_out.append(self._get_struct_property_bytes(self.appearance, self.APPEARANCE_STRUCT_PROP, self.CHARACTER_APPEARANCE))
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
        data_out.append(self.lastmatesexcount)
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
        _, self.appearance,     preset_data = self._parse_struct_property(preset_data, self.SCHEME_PROP_STRUCT, self.CHARACTER_APPEARANCE)
        _, self.rarities,       preset_data = self._parse_rarities(preset_data)
        self.remain = preset_data
    
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
        data_out.append(self._get_struct_property_bytes(self.appearance, self.SCHEME_PROP_STRUCT, self.CHARACTER_APPEARANCE))
        return self.list_to_bytes(data_out)

class PlayerSpiritForm(NephelymBase):
    def __init__(self, spiritform_data):
        self._parse_spiritform_data(spiritform_data)
    
    def _parse_spiritform_data(self, spiritform_data):
        _, self.guid,           spiritform_data = self._parse_guid(spiritform_data, self.SPIRITFORM_GUID)
        _, self.race, self.sex, spiritform_data = self._parse_race_sex(spiritform_data)
        _, self.appearance,     spiritform_data = self._parse_struct_property(spiritform_data, self.APPEARANCE_STRUCT_PROP,    self.CHARACTER_APPEARANCE)
        _, self.appliedscheme,  spiritform_data = self._parse_struct_property(spiritform_data, self.APPLIEDSCHEME_STRUCT_PROP, self.CHARACTER_APPLIED_SCHEME)
        _, self.mother,         spiritform_data = self._parse_struct_property(spiritform_data, self.MOTHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        _, self.father,         spiritform_data = self._parse_struct_property(spiritform_data, self.FATHER_STRUCT_PROP,        self.CHARACTER_PARENT_DATA)
        self.remain = spiritform_data
    
    def _parse_race_sex(self, nephelym_data):
        '''Spiritform doesn't always have variant block if using default spirit race and sex'''
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
        data_out.append(self._get_struct_property_bytes(self.appearance, self.APPEARANCE_STRUCT_PROP, self.CHARACTER_APPEARANCE))
        data_out.append(self._get_struct_property_bytes(self.appliedscheme, self.APPLIEDSCHEME_STRUCT_PROP, self.CHARACTER_APPLIED_SCHEME))
        data_out.append(self._get_struct_property_bytes(self.mother, self.MOTHER_STRUCT_PROP, self.CHARACTER_PARENT_DATA))
        data_out.append(self._get_struct_property_bytes(self.father, self.FATHER_STRUCT_PROP, self.CHARACTER_PARENT_DATA))
        data_out.append(self.remain)
        return self.list_to_bytes(data_out)


class NephelymSaveEditor(GenericParsers):
    '''Class for editing saves'''
    def __init__(self, save_file=None):
        if save_file:
            self.load(save_file)

    def _parse_save_data(self, save_data):
        data_header, data_monster_and_player, save_data = self._parse_array_property(save_data,  self.PLAYERMONSTER_ARRAY_PROP,     self.STRUCT_PROPERTY)
        _, self.playersexpositions,           save_data = self._parse_playersexpositions(save_data)
        _, self.playerspirit,                 save_data = self._parse_playerspirit(save_data)
        _, playerspiritform_data,             save_data = self._parse_struct_property(save_data, self.PLAYERSPIRITFORM_STRUCT_PROP, self.CHATACTER_DATA)
        _, self.playerobtainedvariants,       save_data = self._parse_playerobtainedvariants(save_data)
        _, self.playerseenvariants,           save_data = self._parse_playerseenvariants(save_data)
        _, self.gameflags,                    save_data = self._parse_struct_property(save_data, self.GAMEFLAGS_STRUCT_PROP,        self.GAMEPLAY_TAG_CONTAINER)
        _, self.worldstate,                   save_data = self._parse_struct_property(save_data, self.WORLDSTATE_STRUCT_PROP,       self.SEXYWOLDSTATE)
        _, self.breederstatprogress,          save_data = self._parse_breederstatprogress(save_data)
        self.header = Header(data_header)
        self.nephelyms = self._parse_nephelyms(data_monster_and_player)
        self.playerspiritform = PlayerSpiritForm(playerspiritform_data)
        self.data_footer = save_data

    def _parse_nephelyms(self, data_monster_and_player):
        '''
        Parse out Breeder and Nephelyms for PlayerMonster Block
        returns list of Nephelym
        '''
        cursor = 0
        name_count = 0
        neph_start = 0
        nephelyms = []
        while cursor != -1:
            pos_name = data_monster_and_player.find(self.PLAYER_MONSTER_NAME, cursor)
            if pos_name == -1:
                if name_count == 4:
                    nephelyms.append(Nephelym(data_monster_and_player[neph_start:]))
                break
            if name_count == 0:
                neph_start = pos_name
            name_count += 1
            if name_count == 5:
                name_count = 0
                nephelyms.append(Nephelym(data_monster_and_player[neph_start:pos_name]))
                cursor = pos_name
            else:
                cursor = pos_name + 1
        return nephelyms

    def _parse_playersexpositions(self, save_data):
        try:
            pre_data, playersexpositions, save_data = self._parse_array_property(save_data, self.PLAYERSEXPOSITIONS_ARRAY_PROP, self.STRUCT_PROPERTY)
        except:
            pre_data = b''
            playersexpositions = b''
        return pre_data, playersexpositions, save_data

    def _parse_playerspirit(self, save_data):
        try:
            pre_data, playerspirit, save_data = self._parse_int_property(save_data, self.PLAYERSPIRIT_INT_PROP)
        except:
            pre_data = b''
            playerspirit = b''
        return pre_data, playerspirit, save_data

    def _parse_playerobtainedvariants(self, save_data):
        try:
            pre_data, playerobtainedvariants, save_data = self._parse_array_property(save_data, self.PLAYEROBTAINEDVARIANTS_ARRAY_PROP, self.STRUCT_PROPERTY)
        except:
            pre_data = b''
            playerobtainedvariants = b''
        return pre_data, playerobtainedvariants, save_data

    def _parse_playerseenvariants(self, save_data):
        try:
            pre_data, playerseenvariants, save_data = self._parse_array_property(save_data, self.PLAYERSEENVARIANTS_ARRAY_PROP, self.STRUCT_PROPERTY)
        except:
            pre_data = b''
            playerseenvariants = b''
        return pre_data, playerseenvariants, save_data

    def _parse_breederstatprogress(self, save_data):
        try:
            pre_data, breederstatprogress, save_data = self._parse_struct_property(save_data, self.BREEDERSTATPROGRESS_STRUCT_PROP, self.BREEDERSTATRANKPROGRESS)
        except:
            pre_data = b''
            breederstatprogress = b''
        return pre_data, breederstatprogress, save_data

    def _get_player_monster_data(self):
        nephelyms = self.list_to_bytes([neph.get_data() for neph in self.nephelyms])
        count = len(self.nephelyms)
        length_neph = len(nephelyms)
        length_header = length_neph + len(self.CHARACTER_DATA) + 8 + len(self.STRUCT_PROPERTY) + len(self.PLAYERMONSTER) + 4
        header_new = self.PLAYERMONSTER_ARRAY_PROP \
            + length_header.to_bytes(8, 'little') \
            + self.STRUCT_ARRAY_PROPERTY \
            + count.to_bytes(4, 'little') \
            + self.PLAYERMONSTER \
            + self.STRUCT_PROPERTY \
            + length_neph.to_bytes(8, 'little') \
            + self.CHARACTER_DATA \
            + nephelyms
        return header_new

    def _get_playersexpositions(self):
        if self.playersexpositions == b'':
            data = b''
        else:
            data = self._get_array_property_bytes(self.playersexpositions, self.PLAYERSEXPOSITIONS_ARRAY_PROP, self.STRUCT_PROPERTY)
        return data

    def _get_playerspirit(self):
        if self.playerspirit == b'':
            data = b''
        else:
            data = self._get_int_property_bytes(self.playerspirit, self.PLAYERSPIRIT_INT_PROP)
        return data

    def _get_playerobtainedvariants(self):
        if self.playerobtainedvariants == b'':
            data = b''
        else:
            data = self._get_array_property_bytes(self.playerobtainedvariants, self.PLAYEROBTAINEDVARIANTS_ARRAY_PROP, self.STRUCT_PROPERTY)
        return data

    def _get_playerseenvariants(self):
        if self.playerseenvariants == b'':
            data = b''
        else:
            data = self._get_array_property_bytes(self.playerseenvariants, self.PLAYERSEENVARIANTS_ARRAY_PROP, self.STRUCT_PROPERTY)
        return data

    def _get_breederstatprogress(self):
        if self.breederstatprogress == b'':
            data = b''
        else:
            data = self._get_struct_property_bytes(self.breederstatprogress,   self.BREEDERSTATPROGRESS_STRUCT_PROP,     self.BREEDERSTATRANKPROGRESS)
        return data

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
            template_nephelym = self.Nephelyms[0]
        for root, dirs, files in os.walk(preset_path):
            for file in files:
                if file.endswith('.sav'):
                    self.nephelyms.append(self.generate_from_preset(os.path.join(root, file), template_nephelym))

    def generate_from_preset(self, preset_path, template_nephelym=None):
        # @TODO generate without having to use a template_nephelym
        if template_nephelym is None:
            template_nephelym = self.Nephelyms[0]
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
        data_out.append(self._get_player_monster_data())
        data_out.append(self._get_playersexpositions())
        data_out.append(self._get_playerspirit())
        data_out.append(self._get_struct_property_bytes(self.playerspiritform.get_data(), self.PLAYERSPIRITFORM_STRUCT_PROP, self.CHATACTER_DATA))
        data_out.append(self._get_playerobtainedvariants())
        data_out.append(self._get_playerseenvariants())
        data_out.append(self._get_struct_property_bytes(self.gameflags,                   self.GAMEFLAGS_STRUCT_PROP,        self.GAMEPLAY_TAG_CONTAINER))
        data_out.append(self._get_struct_property_bytes(self.worldstate,                  self.WORLDSTATE_STRUCT_PROP,       self.SEXYWOLDSTATE))
        data_out.append(self._get_breederstatprogress())
        data_out.append(self.data_footer)
        return self.list_to_bytes(data_out)


if __name__ == "__main__":
    save_in       = r'0.sav'
    save_out      = r'15.sav'
    preset_folder = r'..\CharacterPresets'
    
    # DEBUGGING: test if parsing and save of save works. 
    # Files should be identical, with except of spirit form if not changed yet
    Testing = False
    if Testing:
        NephelymSaveEditor(save_in).save(save_out)
        exit()
    
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


