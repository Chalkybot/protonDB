import requests
import subprocess
import sys
import os
import time
import re as regex
import json

URL='https://www.protondb.com/api/v1/reports/summaries/'
DB_URL='http://api.steampowered.com/ISteamApps/GetAppList/v2/?&max_results=50000'
DIRS = os.listdir(f"{os.path.expanduser('~')}/.local/share/Steam/steamapps/common/")
LOCAL_ID_DATABASE=f"{os.path.expanduser('~')}/.local/share/Steam/id_database.json"
#blacklist=["SteamVR", "Proton EasyAntiCheat Runtime", "Steam.dll", "Steamworks Shared", "Proton 7.0", "SteamLinuxRuntime_soldier"]
VERSION=1

def help():
    print("""
    protondb - A Proton database commandline interface
    
    Default usage:

    protondb [game]     : Search the proton database for the game and list the quality of play.

    Additional available arguments:
    
    --help              : Display this message.
    --version           : Check the version of this script.
    --refresh           : Force a database reset.
    --installed         : Check installed games and lists their rating.
    --search            : Search for games, usage: '--search [game]'.
    --database          : Displays current entries in database.""")
    sys.exit(0)

def argHandler():
    if len(sys.argv)<2:
        print("No input given, try --help")
        sys.exit(0)
    
    argumentList=''
    if(sys.argv[1][:2])=='--':
        arg=sys.argv[1][2:]
        match arg:
            case "help":
                help()
            case "version":
                print(f"Proton database CLI version {VERSION}")
                sys.exit(0)
            case "installed":
                print("\033[4mInstalled games:\033[0m")
                multi(installedGames())
            case "refresh":
                print("Forcing a database sync...")
                dataBaseHandler(2)
            case "search":
                length = os.get_terminal_size().columns
               #f"{colourText((values[1][:len(name)]), 4)}{values[1][len(name):]}"
                for argument in sys.argv[2:]:
                    argumentList+=f"{argument} "
                if len(argumentList)<0:
                    print("Given search term too short.")
                    sys.exit(0)
                argumentList=argumentList[:-1]
                gameList=search(argumentList, DATABASE)
                if gameList==0:
                    print("No games found.")
                    sys.exit(0)
                idList=gameList[1::2]
                gameList=gameList[::2]
                if len(gameList)==1:
                    return [gameList[0],idList[0]]
                dupes = findDuplicates(gameList)
                for index, game in enumerate(gameList):
                    gameInfo=''
                    toPrint=f"({str(index).rjust(len(str(len(gameList))),' ')}) {colourText((game[:len(argumentList)]), 4)}{game[len(argumentList):]} "
                    if dupes is not False and game in dupes:
                        gameInfo=f":: {info(idList[index])}"
                        if len(gameInfo)>length:
                            toCut=len(f"{toPrint}{gameInfo}")-length-3
                            gameInfo=f"{gameInfo[:-toCut]}..."
                    print(f"{toPrint}{gameInfo}")
                
                toCheck=input(f"Game to check (0-{index}): ")
                if not toCheck.isnumeric():
                    print("Invalid response, exiting...")
                    sys.exit(1)
                while int(toCheck) > index:
                    print("Invalid response, please try again.")
                    toCheck=input(f"Game to check (0-{index}): ")
                return [gameList[int(toCheck)], idList[int(toCheck)]]
            case "database":
                databaseEntries = len(DATABASE['applist']['apps'])
                print(f"Entries in database: {databaseEntries}")
                sys.exit(0)              
            case _:
                print("Command not found, please try --help.")
                sys.exit(0)  

    for argument in sys.argv[1:]:
        argumentList+=f"{argument} "
    return argumentList[:-1]

def info(id):
    
    response=requests.get(f"https://store.steampowered.com/api/appdetails?appids={id}").text
    responseJson=json.loads(response)
    try:
        smallDescription=responseJson[str(id)]['data']['short_description']
        return smallDescription
    except:
        return "no description found"
    
        
def colourText(input, colour):
    match colour:
        case -1:
            output=f"\033[3m{input}\033[0m"
        case 0:
            output=f"\033[31m{input}\033[0m"
        case 1:
            output=f"\033[35{input}\033[0m"
        case 2:
            output=f"\033[36m{input}\033[0m"
        case 3:
            output=f"\033[33m{input}\033[0m"
        case 4:
            output=f"\033[32m{input}\033[0m"
    return output

def installedGames():
    games=''
    toDelete=''
    for directory in DIRS:
        if directory[:6].lower()=='proton' or directory[:5].lower()=='steam':
            toDelete+=directory
        games=[e for e in DIRS if e not in toDelete]
    return games

def findDuplicates(listOfElements):
    if len(listOfElements) == len(set(listOfElements)):
        return False
    seen = set()
    dupes = []

    for x in listOfElements:
        if x in seen:
            dupes.append(x)
        else:
            seen.add(x)
    return dupes


def search(name, database):
    possibilities=[]
    for game in database['applist']['apps']:
        values = list(game.values())
        #print(values[1])
        if values[1].lower()[:len(name)]==name.lower():
            possibilities.append(values[1])
            possibilities.append(values[0])
    if len(possibilities)<1:
        return 0
    else: 
        return possibilities



def dataBaseHandler(DataBaseRenewal=0):
    if os.path.exists(LOCAL_ID_DATABASE):
        lastMod=os.path.getmtime(LOCAL_ID_DATABASE) # Check the modification time of the local database file in epoch form.
        time_change=(time.time()-lastMod)/259200 # Divide the time since modification from the current time in epoch form and divide it by the amount of seconds in three days.
        if (time_change)>1:
            print("Database older than 3 days, synching...")
            DataBaseRenewal=1
    else:
        print("Database missing, synching...")
        DataBaseRenewal=1

    if DataBaseRenewal==1 or DataBaseRenewal==2:
            response=requests.get(DB_URL).text
            response=response.lower()
            response=regex.sub("""™|℠|®|©|@|'""",'',response)
            with open(LOCAL_ID_DATABASE,'w') as localDatabase:
                localDatabase.write(response)
                print("Database successfully synched.")
    if DataBaseRenewal==2:  
        sys.exit(0)
    
    with open(LOCAL_ID_DATABASE,'r') as localDatabase:
        return json.loads(localDatabase.read())      
    
def idMatch(name, database):
    ids=[]
    for game in database["applist"]["apps"]: # Goes through every game in the database
        values = list(game.values())         # Creates a list.
        if values[1]==name:
            ids.append(values[0])
     
    for entry in ids:
        if not requests.get(f"{URL}{entry}.json").status_code==404:
            return entry
    return None

def gameQuality(id):
    quality = json.loads(requests.get(f"{URL}{id}.json").text)
    
    tier            =   quality['bestReportedTier']
    trendingTier    =   quality['trendingTier']
    total           =   quality['total']

    ranks = [tier, trendingTier, total]
    for ranking in ranks:
        match ranking:
            case "platinum":
                ranks.append(4)
            case "gold":
                ranks.append(3)
            case "silver":
                ranks.append(2)
            case "bronze":
                ranks.append(1)
            case "borked":
                ranks.append(0)
    
    return ranks

def multi(games):
    for game in games:

        game=regex.sub("[_]"," ", game)
        gameName = f"{game[0].upper()}{game[1:]}"
        game = regex.sub("""™|℠|®|©|@|'""",'',game.lower())
        gameID =idMatch(game, DATABASE) 
        

        if gameID == None:
            print(f"{colourText(gameName, -1)}")
            continue

        gameRankings = gameQuality(gameID)

        print (f"{colourText(gameName, gameRankings[4])}")
    sys.exit(0)
    
def single(game, gameID=None):

    if gameID is None:
        gameID = idMatch(game, DATABASE)
    else:
        if requests.get(f"{URL}{gameID}.json").status_code==404:
            print("Game not listed on protonDB.")
            sys.exit(0)
    if gameID == None:
        print("Game not listed on protonDB.")
        sys.exit(0)
    gameRankings = gameQuality(gameID)
    game = f"{game[0].upper()}{game[1:]}"

    print(f"""
    {game} had {gameRankings[2]} ratings.
    The average rating was {colourText(gameRankings[1],gameRankings[4])}.
    The trending rating was {colourText(gameRankings[0],gameRankings[3])}""")
    toInstall =input(f"\n    Do you wish to install {game}? [Y/n] ")
    if toInstall.lower() == 'y':
        subprocess.run(["steam", f"steam://rungameid/{gameID} > /dev/null"])
    else:
        print("    exiting...")

if __name__=='__main__':
    id = None
    DATABASE = dataBaseHandler()
    arguments=argHandler()
    name = arguments
    if isinstance(arguments,list):
        name = arguments[0]
        id   = arguments[1]
    
    single(name, id)
