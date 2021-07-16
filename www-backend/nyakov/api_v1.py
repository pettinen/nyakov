import os
import re

import requests
from flask import Blueprint, request


api_v1 = Blueprint("api_v1", __name__)


twitch_emotes = {
    "2020ByeGuys": "304822038",
    "2020Capture": "304572368",
    "2020Celebrate": "304857015",
    "2020Delivery": "304573229",
    "2020Drop": "304821857",
    "2020Forward": "304821979",
    "2020Gift": "304573236",
    "2020Glitchy": "304821871",
    "2020HomeWork": "304573244",
    "2020MaskUp": "304822061",
    "2020Pajamas": "304573252",
    "2020Partnered": "304821885",
    "2020Party": "304573256",
    "2020Rivalry": "304573264",
    "2020Selfie": "304573270",
    "2020Shhh": "304836436",
    "2020Shred": "304822010",
    "2020Snacking": "304821908",
    "2020SpeakUp": "304573272",
    "2020Surprise": "304573275",
    "2020Suspicious": "304573280",
    "2020Takeout": "304822046",
    "2020Unity": "304822026",
    "2020Unroll": "304573286",
    "2020Victory": "304836425",
    "2020Wish": "304822055",
    "4Head": "354",
    ":(": "2",
    ":)": "1",
    ":/": "10",
    ":D": "3",
    ":O": "8",
    ":P": "12",
    ":|": "5",
    ";)": "11",
    ";P": "13",
    "<3": "9",
    ">(": "4",
    "ANELE": "3792",
    "ArgieB8": "51838",
    "ArsonNoSexy": "50",
    "AsexualPride": "307827267",
    "AsianGlow": "74",
    "B)": "7",
    "BCWarrior": "30",
    "BOP": "301428702",
    "BabyRage": "22639",
    "BagOfMemes": "425696",
    "BatChest": "115234",
    "BegWan": "160394",
    "BibleThump": "86",
    "BigBrother": "1904",
    "BigPhish": "160395",
    "BisexualPride": "307827313",
    "BlackLivesMatter": "302537250",
    "BlargNaut": "114738",
    "BloodTrail": "69",
    "BrainSlug": "115233",
    "BrokeBack": "4057",
    "BuddhaBar": "27602",
    "CarlSmile": "166266",
    "ChefFrank": "90129",
    "Clappy": "192361",
    "ClappyDerp": "192362",
    "ClappyHype": "192363",
    "CoolCat": "58127",
    "CoolStoryBob": "123171",
    "CorgiDerp": "49106",
    "CrreamAwk": "191313",
    "CupFooty": "1077992",
    "CurseLit": "116625",
    "DAESuppy": "973",
    "DBstyle": "73",
    "DansGame": "33",
    "DarkMode": "461298",
    "DatSheffy": "111700",
    "DendiFace": "58135",
    "DogFace": "114835",
    "DoritosChip": "102242",
    "DrinkPurple": "110785",
    "DxCat": "110734",
    "EarthDay": "959018",
    "EleGiggle": "4339",
    "EntropyWins": "376765",
    "ExtraLife": "302426269",
    "FBBlock": "1441276",
    "FBCatch": "1441281",
    "FBChallenge": "1441285",
    "FBPass": "1441271",
    "FBPenalty": "1441289",
    "FBRun": "1441261",
    "FBSpiral": "1441273",
    "FBtouchdown": "626795",
    "FUNgineer": "244",
    "FailFish": "360",
    "FightCC": "300710644",
    "FlipThis": "112295",
    "FootBall": "302628600",
    "FootGoal": "302628617",
    "FootYellow": "302628613",
    "FortBush": "822126",
    "FortHype": "822137",
    "FortLlama": "822146",
    "FortOne": "822112",
    "FrankerZ": "65",
    "FreakinStinkin": "117701",
    "FutureMan": "98562",
    "GayPride": "307827321",
    "GenderFluidPride": "307827326",
    "GingerPower": "32",
    "GivePLZ": "112291",
    "GlitchCat": "304486301",
    "GlitchLit": "304489128",
    "GlitchNRG": "304489309",
    "GrammarKing": "3632",
    "GreenTeam": "530890",
    "GunRun": "1584743",
    "HSCheers": "444572",
    "HSWP": "446979",
    "Haha2020": "301112670",
    "HahaBaby": "301108084",
    "HahaBall": "301112669",
    "HahaCat": "301108083",
    "HahaDoge": "301108082",
    "HahaDreidel": "301112663",
    "HahaElf": "301108081",
    "HahaGingercat": "301108078",
    "HahaGoose": "301108075",
    "HahaHide": "301108072",
    "HahaLean": "301108068",
    "HahaNutcracker": "301108063",
    "HahaNyandeer": "301114312",
    "HahaPoint": "301108057",
    "HahaPresent": "301108052",
    "HahaReindeer": "301108048",
    "HahaShrugLeft": "301108047",
    "HahaShrugMiddle": "301108046",
    "HahaShrugRight": "301108045",
    "HahaSleep": "301108041",
    "HahaSnowhal": "301108053",
    "HahaSweat": "301108037",
    "HahaThink": "301108032",
    "HahaThisisfine": "301108013",
    "HahaTurtledove": "301108011",
    "HassaanChop": "20225",
    "HeyGuys": "30259",
    "HolidayCookie": "1713813",
    "HolidayLog": "1713816",
    "HolidayOrnament": "1713818",
    "HolidayPresent": "1713819",
    "HolidaySanta": "1713822",
    "HolidayTree": "1713825",
    "HotPokket": "357",
    "HypeAttack": "emotesv2_f35caa0f5f3243b88cfbd85a3c9e69ff",
    "HypeBanana": "301739487",
    "HypeBard": "304420723",
    "HypeBeard": "emotesv2_f045d9aa07d54961ab2ba77174305278",
    "HypeBigfoot1": "301205397",
    "HypeBigfoot2": "301205398",
    "HypeBigfoot3": "301205399",
    "HypeBigfoot4": "301205400",
    "HypeBigfoot5": "301205401",
    "HypeBigfoot6": "301205402",
    "HypeBlob": "301739493",
    "HypeBlock": "301739489",
    "HypeBook": "304420732",
    "HypeBounce": "301739491",
    "HypeBrain": "301739472",
    "HypeBug": "301739471",
    "HypeCar": "301739483",
    "HypeCash": "304420757",
    "HypeCherry": "301739468",
    "HypeChest": "301739465",
    "HypeChimp": "301739462",
    "HypeCoin": "304420761",
    "HypeCozy": "emotesv2_031719611d64458fb76982679a2d492a",
    "HypeCreep": "emotesv2_19e3d6baefa5477caeaa238bf1b31fb1",
    "HypeDaze": "301739490",
    "HypeDerp": "emotesv2_22683be90477418fbc8e76e0cd91a4bd",
    "HypeDisguise": "emotesv2_dc24652ada1e4c84a5e3ceebae4de709",
    "HypeDoh": "emotesv2_69a7806c6837428f82475e99677d2f78",
    "HypeDragon1": "301205403",
    "HypeDragon2": "301205405",
    "HypeDragon3": "301205406",
    "HypeDragon4": "301205409",
    "HypeDragon5": "301205411",
    "HypeDragon6": "301205413",
    "HypeEars": "emotesv2_5ade9654471d406994040073d80c78ac",
    "HypeEyes": "emotesv2_23f63a570f724822bb976f36572a0785",
    "HypeFighter": "304420773",
    "HypeFire": "301739501",
    "HypeFirst": "301739484",
    "HypeFrog": "301739466",
    "HypeGG": "304420784",
    "HypeGems": "304420779",
    "HypeGhost": "301739463",
    "HypeGriffin1": "301205414",
    "HypeGriffin2": "301205415",
    "HypeGriffin3": "301205416",
    "HypeGriffin4": "301205417",
    "HypeGriffin5": "301205418",
    "HypeGriffin6": "301205419",
    "HypeHay": "emotesv2_50e775355dbe4992a086f24ffaa73676",
    "HypeHeart": "304420791",
    "HypeHeh": "emotesv2_62199faa2ca34ea8a0f3567990a72a14",
    "HypeHeyFriends": "emotesv2_be2e7ac3e077421da3526633fbbb9176",
    "HypeHide": "emotesv2_6a99bc2baae743099b23ed6ab07bc5c4",
    "HypeHit": "304420797",
    "HypeJewel": "301739492",
    "HypeJudge": "emotesv2_164b5a252ea94201b7fcfcb7113fe621",
    "HypeJuggle": "304420806",
    "HypeKO": "301739497",
    "HypeKick": "304420811",
    "HypeLol": "304420818",
    "HypeLove": "301739495",
    "HypeMage": "304420826",
    "HypeMine": "emotesv2_ebc2e7675cdd4f4f9871557cfed4b28e",
    "HypeMiss": "304420830",
    "HypeOni1": "301205421",
    "HypeOni2": "301205422",
    "HypeOni3": "301205423",
    "HypeOni4": "301205424",
    "HypeOni5": "301205426",
    "HypeOni6": "301205427",
    "HypeOoh": "emotesv2_994d515930a14e5396fd36d45e785d48",
    "HypePeace": "301739470",
    "HypePizza": "301739502",
    "HypePotion": "304420861",
    "HypePunch": "301739499",
    "HypePunk": "301739496",
    "HypePurr": "emotesv2_69a7806c6837428f82475e99677d2f78",
    "HypeRIP": "304420886",
    "HypeRacer": "301739482",
    "HypeRanger": "304420869",
    "HypeRock": "304420892",
    "HypeRogue": "304420899",
    "HypeRun": "304420909",
    "HypeScream": "emotesv2_a05d626acce9485d83fdfb02b6553826",
    "HypeShame": "emotesv2_680c3aae688947d8b6067cff1a8bcdbe",
    "HypeShield": "304420921",
    "HypeShip": "301739476",
    "HypeShy": "emotesv2_d4a50cfaa51f46e99e5228ce8ef953c4",
    "HypeSideeye": "301739479",
    "HypeSign": "301739478",
    "HypeSmoke": "304420932",
    "HypeSneak": "304421025",
    "HypeSquawk": "emotesv2_07dfbc3be2af4edea09217f6f9292b40",
    "HypeStahp": "emotesv2_661e2889e5b0420a8bb0766dd6cf8010",
    "HypeSus": "emotesv2_e0d949b6afb94b01b608fb3ad3e08348",
    "HypeSwipe": "304421029",
    "HypeTarget": "304421037",
    "HypeTeamwork": "301739494",
    "HypeTongue": "emotesv2_ea658eb2e9d54833a4518c6dcc196dc6",
    "HypeTrophy": "301739485",
    "HypeTune": "304421042",
    "HypeUnicorn1": "301205429",
    "HypeUnicorn2": "301205430",
    "HypeUnicorn3": "301205431",
    "HypeUnicorn4": "301205432",
    "HypeUnicorn5": "301205745",
    "HypeUnicorn6": "301205749",
    "HypeWant": "emotesv2_2a3cd0373fe349cf853c058f10fae0be",
    "HypeWho": "304421049",
    "HypeWink": "304421058",
    "HypeWow": "emotesv2_d20a5e514e534288a1104b92c4f87834",
    "HypeWut": "304421062",
    "HypeYas": "emotesv2_d8271fc8f0264fdc9b1ac79051f75349",
    "HypeYawn": "emotesv2_0f5d26b991a44ffbb88188495a8dd689",
    "HypeYesPlease": "emotesv2_fa2dad1f526b4c0a843d2cc4d12a7e06",
    "HypeYikes": "301739481",
    "HypeYum": "emotesv2_a964a0cbae9348e6bd981bc714eec71d",
    "HypeZap": "301739475",
    "HypeZzz": "304421067",
    "HyperCheese": "303179111",
    "HyperCooldown": "303179112",
    "HyperCrate": "303179114",
    "HyperCrown": "303179115",
    "HyperGravity": "303179116",
    "HyperHaste": "303179118",
    "HyperHex": "303179119",
    "HyperJump": "303179121",
    "HyperLost": "303179122",
    "HyperMayhem": "303179126",
    "HyperMine": "303179127",
    "HyperParkour": "303179131",
    "HyperReveal": "303179133",
    "HyperSlam": "303179136",
    "HyperTiger": "303179137",
    "IntersexPride": "307827332",
    "InuyoFace": "160396",
    "ItsBoshyTime": "133468",
    "JKanStyle": "15",
    "Jebaited": "114836",
    "JonCarnage": "26",
    "KAPOW": "133537",
    "KPOPTT": "304047269",
    "KPOPcheer": "304047297",
    "KPOPdance": "304047335",
    "KPOPfan": "304047364",
    "KPOPglow": "303975379",
    "KPOPheart": "304047383",
    "KPOPlove": "303975434",
    "KPOPmerch": "304047397",
    "KPOPselfie": "304047404",
    "KPOPvictory": "303975459",
    "Kappa": "25",
    "KappaClaus": "74510",
    "KappaHD": "115850",
    "KappaPride": "55338",
    "KappaRoss": "70433",
    "KappaWealth": "81997",
    "Kappu": "160397",
    "Keepo": "1902",
    "KevinTurtle": "40",
    "Kippa": "1901",
    "KomodoHype": "81273",
    "KonCha": "160400",
    "Kreygasm": "41",
    "LUL": "425618",
    "LesbianPride": "307827340",
    "LuvBlondeL": "301396403",
    "LuvBlondeR": "301396475",
    "LuvBlush": "301396406",
    "LuvBrownL": "301396467",
    "LuvBrownR": "301396400",
    "LuvCool": "301396382",
    "LuvGift": "301396432",
    "LuvHearts": "301396428",
    "LuvOops": "301396357",
    "LuvPeekL": "301396363",
    "LuvPeekR": "301396373",
    "LuvSign": "301396453",
    "LuvSnooze": "301396378",
    "LuvUok": "301396388",
    "MVGame": "142140",
    "Mau5": "30134",
    "MaxLOL": "1290325",
    "MercyWing1": "1003187",
    "MercyWing2": "1003189",
    "MikeHogu": "81636",
    "MindManners": "425692",
    "MingLee": "68856",
    "MiniK": "115849",
    "MorphinTime": "156787",
    "MrDestructoid": "28",
    "NewRecord": "307763444",
    "NinjaGrumpy": "138325",
    "NomNom": "90075",
    "NonbinaryPride": "307827356",
    "NotATK": "34875",
    "NotLikeThis": "58765",
    "OSFrog": "81248",
    "OWL2019Tracer": "1833318",
    "O_o": "6",
    "OhMyDog": "81103",
    "OneHand": "66",
    "OpieOP": "100590",
    "OptimizePrime": "16",
    "PJSalt": "36",
    "PJSugar": "102556",
    "PMSTwin": "92",
    "PRChase": "28328",
    "PanicVis": "3668",
    "PansexualPride": "307827370",
    "PartyHat": "965738",
    "PartyPopper": "425697",
    "PartyTime": "135393",
    "PeoplesChamp": "3412",
    "PermaSmug": "27509",
    "PicoMause": "111300",
    "PinkMercy": "1003190",
    "PipeHype": "4240",
    "PixelBob": "1547903",
    "PogChamp": "305954156",
    "PokAegislash": "743910",
    "PokBlastoise": "864143",
    "PokBlaziken": "743872",
    "PokBraixen": "743912",
    "PokChandelure": "743914",
    "PokCharizard": "743875",
    "PokCroagunk": "743889",
    "PokDarkrai": "864145",
    "PokDecidueye": "864147",
    "PokEmpoleon": "864148",
    "PokGarchomp": "743918",
    "PokGardevoir": "743884",
    "PokGengar": "743886",
    "PokLucario": "743892",
    "PokMachamp": "743895",
    "PokMaskedpika": "743899",
    "PokMewtwo": "743901",
    "PokPikachu": "743904",
    "PokSceptile": "743922",
    "PokScizor": "864149",
    "PokShadowmew": "743929",
    "PokSuicune": "743905",
    "PokWeavile": "743907",
    "Poooound": "117484",
    "PopCorn": "724216",
    "PorscheWIN": "300745158",
    "PowerUpL": "425688",
    "PowerUpR": "425671",
    "PraiseIt": "38586",
    "PrideCrown": "302303565",
    "PrideCute": "302303594",
    "PrideDragon": "302303581",
    "PrideFloat": "302303599",
    "PrideFlower": "302303577",
    "PrideHeartL": "302303573",
    "PrideHeartR": "302303574",
    "PrideHeyyy": "302303567",
    "PrideKoala": "302303566",
    "PrideLGBTea": "302303585",
    "PrideLaugh": "302303593",
    "PrideLion": "302303576",
    "PrideLove": "302303568",
    "PridePaint": "302303563",
    "PridePenguin": "302303578",
    "PridePog": "302303596",
    "PrideRhino": "302303587",
    "PrideRise": "302303570",
    "PrideShrug": "302303601",
    "PrideStrong": "302303569",
    "PrideToucan": "302303582",
    "PrideUnicorn": "302303580",
    "PrideUwu": "302303590",
    "PrideWave": "302303579",
    "PrideWorld": "302303564",
    "PrimeMe": "115075",
    "PrimeRlyTho": "134253",
    "PrimeUWot": "134252",
    "PrimeYouDontSay": "134251",
    "PunOko": "160401",
    "PunchTrees": "47",
    "PurpleStar": "624501",
    "R)": "14",
    "RPGAyaya": "300904280",
    "RPGBukka": "300904281",
    "RPGBukkaNoo": "300904282",
    "RPGEmpty": "300904285",
    "RPGEpicStaff": "300904286",
    "RPGEpicSword": "300904287",
    "RPGFei": "300904288",
    "RPGFireball": "300904289",
    "RPGGhosto": "300904290",
    "RPGHP": "300904291",
    "RPGMana": "300904292",
    "RPGOops": "300904293",
    "RPGPhatLoot": "300904294",
    "RPGSeven": "300904296",
    "RPGShihu": "300904298",
    "RPGStaff": "300904299",
    "RPGTreeNua": "300904300",
    "RPGYonger": "300904302",
    "RaccAttack": "114870",
    "RalpherZ": "1900",
    "RedCoat": "22",
    "RedTeam": "530888",
    "ResidentSleeper": "245",
    "RitzMitz": "4338",
    "RlyTho": "134256",
    "RuleFive": "107030",
    "SMOrc": "52",
    "SSSsss": "46",
    "SabaPing": "160402",
    "ScaredyCat": "112293",
    "SeemsGood": "64138",
    "SeriousSloth": "81249",
    "ShadyLulu": "52492",
    "ShazBotstix": "87",
    "ShowOfHands": "303564554",
    "SingsMic": "300116349",
    "SingsNote": "300116350",
    "SirMad": "301544923",
    "SirPrise": "301544926",
    "SirSad": "301544924",
    "SirShield": "301544919",
    "SirSword": "301544922",
    "SirUwU": "301544927",
    "SmoocherZ": "89945",
    "SoBayed": "1906",
    "SoonerLater": "2113050",
    "Squid1": "191762",
    "Squid2": "191763",
    "Squid3": "191764",
    "Squid4": "191767",
    "StinkyCheese": "90076",
    "StinkyGlitch": "304486324",
    "StoneLightning": "17",
    "StrawBeary": "114876",
    "SuperVinlin": "118772",
    "SwiftRage": "34",
    "TBAngel": "143490",
    "TF2John": "1899",
    "TPFufun": "508650",
    "TPcrunchyroll": "323914",
    "TTours": "38436",
    "TableHere": "112294",
    "TakeNRG": "112292",
    "TearGlove": "160403",
    "TehePelo": "160404",
    "ThankEgg": "160392",
    "TheIlluminati": "145315",
    "TheRinger": "18",
    "TheTarFu": "111351",
    "TheThing": "7427",
    "ThunBeast": "1898",
    "TinyFace": "111119",
    "TombRaid": "864205",
    "TooSpicy": "114846",
    "TransgenderPride": "307827377",
    "TriHard": "120232",
    "TwitchLit": "166263",
    "TwitchRPG": "1220086",
    "TwitchSings": "300116344",
    "TwitchUnity": "196892",
    "TwitchVotes": "479745",
    "UWot": "134255",
    "UnSane": "111792",
    "UncleNox": "114856",
    "VirtualHug": "301696583",
    "VoHiYo": "81274",
    "VoteNay": "106294",
    "VoteYea": "106293",
    "WTRuck": "114847",
    "WholeWheat": "1896",
    "WutFace": "28087",
    "YouDontSay": "134254",
    "YouWHY": "4337",
    "ZombieKappa": "515391",
    "bleedPurple": "62835",
    "cmonBruh": "84608",
    "copyThis": "112288",
    "duDudu": "62834",
    "imGlitch": "112290",
    "mcaT": "35063",
    "neonyaBread": "303040841",
    "neonyaDab": "303040831",
    "neonyaHi": "302225947",
    "neonyaJam": "302172076",
    "neonyaKakkActivated": "emotesv2_cf0a56dc9be8477aae4a8676b491de2d",
    "neonyaKakkakun": "emotesv2_e97e5d0e93e84e4697d15e320ef890c3",
    "neonyaLove": "302172049",
    "neonyaRainbowWink": "emotesv2_f326b4276b6641f580956dfdba3086dc",
    "neonyaRainbowkun": "emotesv2_85d7d9995f98419fac5098e1bec4ac21",
    "neonyaRave": "303040793",
    "neonyaWink": "303041004",
    "panicBasket": "22998",
    "pastaThat": "112289",
    "riPepperonis": "62833",
    "twitchRaid": "62836",
}


bttv_emotes = {
    "02Hype": "5b5217dd379b93298eb05e13",
    "02HypeFlip": "5f10124f19a5bd0524ecbdf1",
    "02REE": "5b2164d85eaa38694dc916a5",
    ":tf:": "54fa8f1401e468494b85b537",
    "AYAYA": "58493695987aab42df852e0f",
    "AYAYABASS": "5bbecbb0605b7273d160f6f6",
    "AYAYAHey": "5cf11a501b2ddd446eaf3048",
    "AngelThump": "566ca1a365dbbdab32ec055b",
    "Anone": "5b4ed661a13f8e3953e298c7",
    "BBoomer": "5c447084f13c030e98f74f58",
    "BirbRave": "5c32f7f9b2b08c560f6ae60a",
    "BlobDJ": "5bdc64d4fd50d42c9708db35",
    "BoneZone": "5b6c5efadd8fb0185163bd4f",
    "BroBalt": "54fbf00a01abde735115de5c",
    "CandianRage": "54fbf09c01abde735115de61",
    "CatJam": "5ec5574b924aa35e32a56111",
    "CiGrip": "54fa8fce01e468494b85b53c",
    "Clap": "55b6f480e66682f576dd94f5",
    "ConcernDoge": "566c9f6365dbbdab32ec0532",
    "CrabPls": "5cc0f81c9bf845390d1c037e",
    "CruW": "55471c2789d53f2d12781713",
    "D:": "55028cd2135896936880fdd7",
    "Danceboye": "5cc132e09bf845390d1c05cb",
    "DatSauce": "54fa903b01e468494b85b53f",
    "DogChamp": "5ffdf28dc96152314ad63960",
    "DuckerZ": "573d38b50ffbf6cc5cc38dc9",
    "EBINYA": "5f5b8e2768d9d86c020e4f05",
    "FeelsAmazingMan": "5733ff12e72c3c0814233e20",
    "FeelsBadMan": "566c9fc265dbbdab32ec053b",
    "FeelsBirthdayMan": "55b6524154eefd53777b2580",
    "FeelsGoodMan": "566c9fde65dbbdab32ec053e",
    "FeelsSnowyMan": "566decae65dbbdab32ec0699",
    "FireSpeed": "566c9ff365dbbdab32ec0541",
    "FishMoley": "566ca00f65dbbdab32ec0544",
    "ForeverAlone": "54fa909b01e468494b85b542",
    "GabeN": "54fa90ba01e468494b85b543",
    "HYPERCLAP": "5b35ca08392c604c5fd81874",
    "HYPERPOGGERS": "60054cf582cf6865d5525341",
    "HYPERS": "5e2ae3b61df9195f1a4ce64e",
    "HailHelix": "54fa90f201e468494b85b545",
    "Hhhehehe": "566ca02865dbbdab32ec0547",
    "HyperNeko": "5afdfe6702e8e2270c373de3",
    "KEKW": "5e9c6c187e090362f8b0b9e8",
    "KKona": "566ca04265dbbdab32ec054a",
    "KaRappa": "550b344bff8ecee922d2a3c1",
    "KappaCool": "560577560874de34757d2dc0",
    "KoishiBlob": "607c81ce39b5010444d01cc2",
    "LuL": "567b00c61ddbe1786688a633",
    "M&Mjc": "54fab45f633595ca4c713abc",
    "NaM": "566ca06065dbbdab32ec054e",
    "Notes": "5e63c5ba8c0f5c3723a8bc87",
    "Orinpls": "5b8b0ab2ce0f6662da64f3bc",
    "PEPEDS": "5be9f494a550811484ed2dd4",
    "POGGERS": "58ae8407ff7b7276f8e594f2",
    "POGGIES": "5b457bbd0485f43277cecac0",
    "PartyKirby": "5c3a9d8bbaa7ba09c9cfca37",
    "PartyParrot": "5e4991cb751afe7d553ddd9c",
    "PauseChamp": "5cd6b08cf1dac14a18c4b61f",
    "PepeHands": "59f27b3f4ebd8047f54dee29",
    "PepoDance": "5a6edb51f730010d194bdd46",
    "PoggersHype": "5dd5cdf0cae6d75f02670676",
    "PoleDoge": "566ca09365dbbdab32ec0555",
    "REEEEEEEE": "5e3c456ed736527d5cd27ba5",
    "REEEblanket": "5ef8ed4e51e3910deed63cd0",
    "RainbowHyper": "5e69073f6d485d372b28e89f",
    "RainbowPls": "5b35cae2f3a33e2b6f0058ef",
    "RainbowPlsFAST": "5dda62cae579cd5efad7859e",
    "RarePepe": "555015b77676617e17dd2e8e",
    "RoACTIVATED": "5a36efbaabff055e46929d33",
    "RonSmug": "55f324c47f08be9f0a63cce0",
    "SaltyCorn": "56901914991f200c34ffa656",
    "ShoopDaWhoop": "54fa932201e468494b85b555",
    "SourPls": "566ca38765dbbdab32ec0560",
    "SqShy": "59cf182fcbe2693d59d7bf46",
    "TambChan": "5f0b129aa2ac620530369ec4",
    "TambIntensifies": "5f07bdd1a2ac6205303674f5",
    "TaxiBro": "54fbefeb01abde735115de5b",
    "TwaT": "54fa935601e468494b85b557",
    "VapeNation": "56f5be00d48006ba34f530a4",
    "VisLaud": "550352766f86a5b26c281ba2",
    "WanWan": "566462e07fc3c70d30096e2d",
    "WatChuSay": "54fa99b601e468494b85b55d",
    "Wowee": "58d2e73058d8950a875ad027",
    "WubTF": "5dc36a8db537d747e37ac187",
    "ZZoomer": "5d8b41c8d2458468c1f48d6e",
    "aniBlush": "56ad30fb015a54353d24594d",
    "ariW": "56fa09f18eff3b595e93ac26",
    "ayayaJAM": "5c36c6981a0b6956017d6b01",
    "bUrself": "566c9f3b65dbbdab32ec052e",
    "blobDance": "5ada077451d4120ea3918426",
    "blobHYPERS": "5d7d041eb58d1868c285cb65",
    "bongoTap": "5ba6d5ba6ee0c23989d52b10",
    "boomerDISCO": "5f3fc31eafb6965d6e7c4234",
    "bttvNice": "54fab7d2633595ca4c713abf",
    "catDance": "5bc116eddd373363d2c76479",
    "catJAM": "5f1b0186cf6d2144653d2970",
    "catJAMJAM": "60086ef86c75a765d4634513",
    "cvHazmat": "5e76d338d6581c3724c0f0b2",
    "cvL": "5e76d2d2d112fc372574d222",
    "cvMask": "5e76d399d6581c3724c0f0b8",
    "cvR": "5e76d2ab8c0f5c3723a9a87d",
    "gachiBASS": "57719a9a6bdecd592c3ad59b",
    "gachiBOP": "59a2a35339266478fce92509",
    "gachiHYPER": "59143b496996b360ff9b807c",
    "haHAA": "555981336ba1901877765555",
    "kandiCute": "5f39f51c3212445d6fb450c2",
    "kumaPls": "5af454b657376e68acb7512a",
    "miyanoHype": "588763bbafc2ff756c3f4c26",
    "monkaS": "56e9f494fff3cc5c35e5287e",
    "monkaSTEER": "5ed0fd17f54be95e2a835054",
    "monkaTOS": "5a7fd054b694db72eac253f4",
    "nepSmug": "60efcc928ed8b373e4222a63",
    "notsquishY": "5709ab688eff3b595e93c595",
    "peepoClap": "5d38aaa592fc550c2d5996b8",
    "peepoHappy": "5a16ee718c22a247ead62d4a",
    "peepoSax": "5e0e80113267f72103fd2642",
    "peepoShy": "5eaa12a074046462f768344b",
    "peepoVroom": "5f4d6fcf68d9d86c020d888c",
    "pepeBASS": "5c393177fb40bc09d7c6c3aa",
    "pepeD": "5b1740221c5a6065a7bad4b5",
    "pepeJAM": "5b77ac3af7bddc567b1d5fb2",
    "pepeJAMJAM": "5c36fba2c6888455faa2e29f",
    "popCat": "600ec76782cf6865d552f241",
    "pugPls": "5de88ccef6e95977b50e6eb1",
    "rengePls": "5d8ce6d41df66f68c80c45e5",
    "shamiSmash": "5e14ef61b974112104804429",
    "sosGame": "553b48a21f145f087fc15ca6",
    "tehPoleCat": "566ca11a65dbbdab32ec0558",
}


@api_v1.get("/generate")
def generate():
    user = request.args.get("user")
    try:
        if not user or not re.fullmatch(r"\w+", user, re.ASCII):
            user = None
    except UnicodeDecodeError:
        pass

    port = os.environ["NYAKOV_PORT"]
    params = {"user": user} if user else None
    response = requests.get(f"http://localhost:{port}/", params)

    try:
        data = response.json()
    except json.JSONDecodeError:
        return {"error": "unexpected-error"}, 500

    if response.status_code != 200:
        return data, response.status_code

    parsed = []

    for word in data["words"]:
        if word in twitch_emotes:
            parsed.append({
                "type": "emote",
                "source": "twitch",
                "id": twitch_emotes[word],
                "name": word,
            })
        elif word in bttv_emotes:
            parsed.append({
                "type": "emote",
                "source": "bttv",
                "id": bttv_emotes[word],
                "name": word,
            })
        else:
            parsed.append({"type": "word", "text": word})

    return {
        "message": parsed,
        "timestamp": data["timestamp"],
        "username": data["username"],
    }

