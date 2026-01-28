CATEGORY_MAP = {

    # ======================
    # TOPS
    # ======================
    "shirt": [
        "shirts", "formal shirts", "casual shirts",
        "shirts, tops & tunic", "shirts,tops&tshirts"
    ],

    "tshirt": [
        "tshirts", "tops & tshirts", "shirts,tops&tshirts"
    ],

    "top": [
        "tops", "tops & tunics", "kurtis & tunics"
    ],

    "blouse": ["blouses"],

    "bodysuit": ["bodysuits"],


    # ======================
    # ETHNIC WEAR
    # ======================
    "saree": ["sarees"],

    "kurta": [
        "kurtas", "kurta pyjama sets", "kurta sets",
        "kurta suit sets", "kurta-bottom set"
    ],

    "kurti": [
        "kurtas & kurtis", "kurtis & tunics"
    ],

    "ethnic_set": [
        "ethnic suit sets", "ethnic wear sets",
        "2-piece ethnic suit", "3p-suit sets",
        "fusion wear sets", "skd set", "sets"
    ],

    "lehenga": ["lehenga choli sets"],

    "salwar": [
        "salwars & churidars", "pyjamas & churidars",
        "churidars & leggings"
    ],

    "dupattas": ["dupattas"],

    "sherwani": ["sherwani sets"],

    "ethnic_jacket": ["ethnic jackets"],


    # ======================
    # DRESSES & JUMPSUITS
    # ======================
    "dress": [
        "dresses", "dresses & frocks", "dresses & gowns",
        "dresses & jumpsuits"
    ],

    "jumpsuit": [
        "jumpsuit & playsuits",
        "jumpsuits & playsuits",
        "jumpsuits &playsuits",
        "dungarees &playsuits"
    ],

    "dungarees": ["dungarees"],


    # ======================
    # BOTTOMS
    # ======================
    "jeans": [
        "jeans", "jeans & jeggings", "jeans & pants"
    ],

    "trousers": [
        "trousers & pants", "pants", "track pants"
    ],

    "shorts": [
        "shorts", "shorts & 3/4ths", "pyjamas & shorts"
    ],

    "skirt": [
        "skirt", "skirts", "skirts & ghagras"
    ],

    "leggings": ["leggings"],


    # ======================
    # OUTERWEAR
    # ======================
    "jacket": [
        "jackets", "jackets & coats", "jackets & shrugs",
        "jackets & boleros", "shrugs & jackets"
    ],

    "blazer": ["blazers & waistcoats"],

    "sweatshirt": [
        "sweatshirt & hoodies",
        "sweatshirts & hoodie",
        "sweatshirts & hoodies",
        "sweatshirts &jackets"
    ],

    "sweater": ["sweaters & cardigans"],

    "rainwear": [
        "rainwear and windcheaters",
        "rainwear&windcheater"
    ],


    # ======================
    # FOOTWEAR (ORDER MATTERS!)
    # ======================
    "sports_shoes": [
        "sports shoes", "sports&outdoor shoes",
        "men_sports", "women_sports"
    ],

    "sneakers": ["sneakers"],

    "formal_shoes": ["formal shoes"],

    "boots": [
        "boots", "men_boots", "women_boots"
    ],

    "sandals": [
        "sandals", "flat sandals", "heeled sandals",
        "casual sandals", "men_sandals", "women_sandals"
    ],

    "slippers": [
        "flip flop & slippers",
        "flip flops & slipper",
        "men_slippers", "women_slippers"
    ],

    "shoes": [
        "shoes", "casual shoes", "flat shoes", "heeled shoes",
        "footwear"
    ],


    # ======================
    # INNERWEAR & SLEEPWEAR
    # ======================
    "innerwear": [
        "innerwear", "bras", "bras & bralettes",
        "briefs", "boxers", "trunks",
        "panties", "panties & bloomers",
        "camisoles & slips", "shapewear"
    ],

    "nightwear": [
        "night & lounge wear sets",
        "night&loungewearsets",
        "nightshirts & nighti",
        "nightshirts&nighties",
        "nightsuit sets",
        "sleepsuits & nightsuit"
    ],

    "thermal": ["thermal wear"],


    # ======================
    # ACCESSORIES & JEWELLERY
    # ======================
    "jewellery": [
        "fashion jewellery", "fashionjewellerysets",
        "traditional jewellery", "traditionaljewellery",
        "jewellery sets"
    ],

    "earrings": ["earrings"],
    "necklaces": ["necklaces & pendants", "pendants"],
    "rings": ["rings"],
    "bracelets": ["bracelets & bangles"],

    "watches": ["watches"],
    "sunglasses": ["sunglasses"],

    "hair_accessories": ["hair accessories"],

    "shawls": ["shawls & wraps"],
    "stoles": ["stoles & scarves", "stoles & scarves"],


    # ======================
    # BAGS & TRAVEL
    # ======================
    "handbags": ["handbags", "bags & purses"],
    "clutches": ["clutches & wristlets"],
    "backpacks": ["backpacks", "laptop bags"],
    "luggage": ["luggage & trolley bags"],
    "wallets": ["wallets"],
    "belts": ["belts"],
    "travel_accessories": ["travel accessories"],


    # ======================
    # KIDS / HOME / MISC
    # ======================
    "baby": ["baby bedding & furniture"],
    "home": ["towels & bath robes"],
    "swimwear": ["swimwear"],

}


def normalize_category(raw_category: str | None) -> str | None:
    if not raw_category:
        return None

    raw = raw_category.strip().lower()

    for canonical, variants in CATEGORY_MAP.items():
        if raw == canonical:
            return canonical
        for v in variants:
            if raw == v.lower():
                return canonical

    # fallback: keep cleaned raw
    return raw
