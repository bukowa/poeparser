from elasticsearch_dsl import InnerDoc, Keyword, Text, Nested, Boolean, Integer, DocType


class PoeCategory(InnerDoc):
    """
    category
    """
    accessories = Keyword(multi=True)
    armour = Keyword(multi=True)
    jewels = Keyword(multi=True)
    weapons = Keyword(multi=True)


class PoeSockets(InnerDoc):
    """
    sockets
    """
    group = Integer()
    attr = Keyword()
    sColour = Keyword()


class PoePropsReqs(InnerDoc):
    """
    properties/requirements
    """
    name = Text()
    # values = AttrList()
    displayMode = Integer()
    type = Integer()
    progress = Integer()


class PoeItem(InnerDoc):
    """
    items
    """

    abyssJewel = Boolean()
    additionalProperties = Boolean(multi=True)
    artFilename = Text()
    category = Nested(PoeCategory)
    corrupted = Boolean()
    cosmeticMods = Text(multi=True)
    craftedMods = Text(multi=True)
    descrText = Text()
    duplicated = Boolean()
    elder = Boolean()
    enchantMods = Text(multi=True)
    explicitMods = Text(multi=True)
    flavourText = Text(multi=True)
    frameType = Integer()
    h = Integer()
    icon = Keyword()
    id = Keyword()
    identified = Boolean()
    ilvl = Integer()
    implicitMods = Text(multi=True)
    inventoryId = Text()
    isRelic = Boolean()
    league = Keyword()
    lockedToCharacter = Boolean()
    maxStackSize = Integer()
    name = Text()
    nextLevelRequirements = Nested(PoePropsReqs, multi=True)
    note = Keyword()
    properties = Nested(PoePropsReqs, multi=True)
    prophecyDiffText = Text()
    prophecyText = Text()
    requirements = Nested(PoePropsReqs, multi=True)
    secDescrText = Text()
    shaper = Boolean()
    socketedItems = Nested()
    sockets = Nested(PoeSockets)
    stackSize = Integer()
    support = Boolean()
    talismanTier = Integer()
    typeLine = Text()
    utilityMods = Text(multi=True)
    verified = Boolean()
    w = Integer()
    x = Integer()
    y = Integer()


class PoeStash(InnerDoc):
    accountName = Keyword()
    lastCharacterName = Keyword()
    id = Keyword()
    stash = Text()
    stashType = Keyword()
    items = Nested(PoeItem)
    public = Boolean()


class PoeJson(DocType):

    class Index:
        name = 'poejson2'

    next_change_id = Keyword()
    stashes = Nested(PoeStash, multi=True)
