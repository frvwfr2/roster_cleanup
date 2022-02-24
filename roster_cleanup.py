import csv
import argparse
import os

# raw_csv_path = "C:\\Users\\Andrew\\TriUlti Rosters\\Coed - West Preliminary Draft List - Sheet1.csv"
# raw_csv_path = "C:\\Users\\Andrew\\TriUlti Rosters\\2022-Sunday-Coed-Spring-League_2022-02-23-20_33.csv"

# division_contains = "West"

parser = argparse.ArgumentParser(description="Breaks down a roster into the requested baggage pairs")
parser.add_argument("--input_csv", help="Path to the CSV location", required=True)
parser.add_argument("--division_contains", help="Filter for only division containing the given string", default="")
args = parser.parse_args()

class Player:
    def __init__(self, info):
        # Full thing stored into self.info, but important attrs are stored separately
        self.id = info["id"]
        self.info = info
        self.info["Notes"] = self.info["Notes"].strip()
        self.raw_string = ""
        self.name = f"{info['first_name']} {info['last_name']}"
        self.baggage_group_id = info['baggage_group_id']
        self.baggage = info['baggage']
        if "status" in info:
            self.status = info['status']
        # Status is formatted weird sometimes?
        elif 'ï»¿"status"' in info:
            self.status = info['ï»¿"status"']
        self.gender = info['gender']
        # self.gender_id = info['gender_id']
        self.player_score = info['player_score']
        if 'division' in info:
            self.division = info['division']
        else:
            self.division = None

    def __repr__(self):
        return  f"{self.status} / {self.gender:6} - {self.name} - {self.baggage_group_id}" # - {self.baggage_group_id} {self.baggage}"

players = list()
unaccepted = list()
# Pairs is a list of tuples, the tuples are made up of the baggage player objects (player1_obj, player2_obj)
# pairs = list()
ff_pairs = list()
mm_pairs = list()
mf_pairs = list()
m_solos = list()
f_solos = list()
found_baggages = list()

log_messages = list()
# We want to log what file this came from
log_messages.append(f"Source file: {args.input_csv}")

fields = None

# Finds the pair (if any) for a specified player. Once we find a pair, we should tag it elsewhere and maybe clear both players from the list of players
def find_pair(players, player):
    # Iterate over every player and find the baggage
    for p in players:
        # print(p, player)
        # We don't want to trigger on our own self
        # But we want to find the other player with the same baggage_group_id
        if p != player and p.baggage_group_id == player.baggage_group_id:
            # print(f"PAIR FOUND {p} {player}")
            # mm
            if p.gender == "male" and player.gender == "male":
                mm_pairs.append( (p, player) )
            # mf
            elif p.gender == "male" and player.gender == "female":
                mf_pairs.append( (p, player) )
            # fm 
            elif p.gender == "female" and player.gender == "male":
                mf_pairs.append( (p, player) )
            # ff
            elif p.gender == "female" and player.gender == "female":
                ff_pairs.append( (p, player) )
            # unable to find pair
            else:
                print("ERROR something has gone wrong")
                log_messages.append(f"Error finding gender grouping for pair: {p} and {player}")
            found_baggages.append(p.baggage_group_id)

# Parse all of the players into objects, and store them in a list of players[]
with open(args.input_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    first_row = True
    for row in reader:
        # If we are on the first row, print all the keys 
        if first_row:
            print(list(row.keys()))
            fields = list(row.keys())
            first_row = False
        p = Player(row)
        # If this player is in this division
        if args.division_contains in p.division:
            # but was NOT accepted, store them separately
            if p.status != "accepted":
                unaccepted.append(p)
                # print(f"Player NOT accepted: {p}")
            # Otherwise, keep 'em
            else:
                players.append(p)
                # print(f"Player accepted: {p}")

            # print(p)

print()


# Identify all baggages. This will also put them into the proper MM, MF, FF list
for player in players:
    # print(player.name)
    # If the player has a baggage group
    if player.baggage_group_id != "" and player.baggage_group_id not in found_baggages:
        print(f"Checking pairs for player: {player}")
        # print(f"Finding baggage for player {player}")
        find_pair(players, player)
        # players.remove(p2)
        # players.remove(p1)
# print(found_baggages)

# For any players remaining, put them into M and F lists
print("LOOKING AT SOLO PLAYERS NOW")
for p in players:
    if p.baggage_group_id == "":
        if p.gender == "male":
            m_solos.append(p)
            players.remove(p)
        elif p.gender == "female":
            f_solos.append(p)
            players.remove(p)

print("DONE PUTTING PLAYERS INTO LISTS")
# for p in players:
#     print(f"Warning: player {p} was not removed from the list!")
#     log_messages.append(f"Warning: player {p} was not removed from the list!")


# print("MF PAIRS")
# for pair in mf_pairs:
#     print(pair)

# print("FF PAIRS")
# for pair in ff_pairs:
#     print(pair)

# print("MM PAIRS")
# for pair in mm_pairs:
#     print(pair)

# print("SOLOS")
# for player in players:
#     print(player)

output_path = os.path.dirname(os.path.abspath(args.input_csv))
with open(f"{output_path}\\{args.division_contains}_OUTPUT.csv", 'w', newline='') as csvfile:
    fieldnames = fields
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    # writer.writerows(mf_pairs)
    writer.writerow({"id": "MF_PAIRS"})
    for pair in mf_pairs:
        writer.writerow(pair[0].info)
        writer.writerow(pair[1].info)
        writer.writerow({})
    writer.writerow({"id": "FF_PAIRS"})
    for pair in ff_pairs:
        writer.writerow(pair[0].info)
        writer.writerow(pair[1].info)
        writer.writerow({})
    writer.writerow({"id": "MM_PAIRS"})
    for pair in mm_pairs:
        writer.writerow(pair[0].info)
        writer.writerow(pair[1].info)
        writer.writerow({})
    writer.writerow({"id": "M SOLOS"})
    for solo in m_solos:
        writer.writerow(solo.info)
    writer.writerow({})
    writer.writerow({"id": "F SOLOS"})
    for solo in f_solos:
        writer.writerow(solo.info)
    
    writer.writerow({})
    writer.writerow({})
    writer.writerow({})
    writer.writerow({})
    writer.writerow({"id": "NOT ACCEPTED PLAYERS"})
    for p in unaccepted:
        writer.writerow(p.info)
    writer.writerow({})
    writer.writerow({})
    writer.writerow({})
    writer.writerow({"id": "LOG MESSAGES"})
    for log in log_messages:
        writer.writerow({"id": log})


# Groups at the end to set

# MM Pairs
# MF Pairs
# FF Pairs
# M Solo
# F Solo