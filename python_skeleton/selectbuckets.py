import pickle
import eval7
from skeleton.states import RoundState
import ctypes
from findflop import most_similar_flop

with open("strategy_dict.pkl",'rb') as strategy:
    strategy_dict = pickle.load(strategy)

with open("buckets/bucketed_auction_flop.pkl", 'rb') as f:
    auction_flop_buckets = pickle.load(f)

with open("buckets/bucketed_auction_turns.pkl", 'rb') as f:
    auction_turn_buckets = pickle.load(f)

with open("buckets/bucketed_auction_river.pkl", 'rb') as f:
    auction_river_buckets = pickle.load(f)

with open("buckets/bucketed_flops.pkl", 'rb') as f:
    flop_buckets = pickle.load(f)

with open("buckets/bucketed_turns.pkl", 'rb') as f:
    turn_buckets = pickle.load(f)

with open("buckets/bucketed_rivers.pkl", 'rb') as f:
    river_buckets = pickle.load(f)

preflop_ranges_dict = {0: eval7.HandRange('23s,24s,25s,26s,27s,34s,35s,36s,37s,45s,46s,32o,43o,42o,54o,53o,52o,65o,64o,63o,62o,74o,73o,72o,83o,82o,28s,29s,2Ts,38s,39s,47s,48s,49s,75o,85o,84o,95o,94o,93o,92o,T5o,T4o,T3o,T2o,J3o,J2o'),
                    1: eval7.HandRange('3Ts,4Ts,56s,57s,58s,59s,5Ts,67s,68s,69s,6Ts,78s,79s,89s,67o,68o,69o,6To,78o,79o,7To,89o,8To'), 
                    2: eval7.HandRange('6Qs,7Ts,7Js,7Qs,8Ts,8Js,8Qs,8Ts,9Ts,9Js,9Qs,TJs,T9o,J8o,J9o,JTo,Q8o,Q9o,QTo,QJo'),
                    3: eval7.HandRange( '33,44,55,K3s,K4s,K5s,K6s,K7s,K8s,A2s,A3s,A4s,A5s,A6s,K5o,K6o,K7o,K8o,K9o,A2o,A3o,A4o,A5o,A6o,A7o,A8o,22,J2s,J3s,J4s,J5s,J6s,Q2s,Q3s,Q4s,Q5s,K2s,J4o,J5o,J6o,J7o,Q2o,Q3o,Q4o,Q5o,Q6o,Q7o,K2o,K3o,K4o'),
                    4: eval7.HandRange('66,77,QTs,QJs,K9s,KTs,KJs,KQs,A7s,A8s,A9s,ATs,AJs,AQs,AKs,KTo,KJo,KQo,A9o,ATo,AJo,AQo,AKo'),
                    5: eval7.HandRange('88,99,TT,JJ,QQ,KK,AA')}

preflops_iso = {}
for bucket in preflop_ranges_dict:
    preflops_iso[bucket] = [(str(card1), str(card2)) for ((card1, card2), _) in preflop_ranges_dict[bucket]]

def custom_sort_key(s):
    return s[0], -ord(s[1])

new_preflops_iso = {i: [] for i in range(6)}    
for bucket in preflops_iso:
    for tup in preflops_iso[bucket]:
        sortedtup = (sorted(tup, key=custom_sort_key))
        new_preflops_iso[bucket].append(sortedtup)

def most_similar_card(cards, target):
    ranks = '23456789TJQKA'
    suits = 'cdhs'

    target_rank = target[0]
    target_suit = target[1]

    same_suit_cards = [card for card in cards if card[1] == target_suit]
    if same_suit_cards:
        closest_card = min(same_suit_cards, key=lambda card: abs(ranks.index(card[0]) - ranks.index(target_rank)))
    else:
        closest_card = min(card_list, key=lambda card: abs(ranks.index(card[0]) - ranks.index(target_rank)))

    return closest_card


def select_bucket(curr_buckets, new_cards, round_state, active):
    """
        list ~ curr_buckets: a list of the current buckets we hold
        list ~ new_cards: a list of the new card(s) (strings) we have and need to bucket

        returns a new list of all buckets, ex: [0,1,2] + [2]
        given new card, search for that card in the buckets and return the bucket it is in
    """
    #im pretending this is finished for now (4:50am)
    new_bucket = []
    curr_round = len(curr_buckets)
    my_cards = round_state.hands[active]
    street = round_state.street
    board_cards = round_state.deck[:street]

    # find preflop bucket
    if len(curr_buckets) == 0: 
        new_cards = sorted(new_cards, key=custom_sort_key)
        for bucket, lst in new_preflops_iso.items():
            if new_cards in lst:
                new_bucket.append(bucket)
                break
    
    # find flop bucket
    if len(curr_buckets) == 1:
        new_cards = tuple(sorted(new_cards))
        # new_bucket.append(find_flop(curr_buckets, new_cards, round_state, active))
        new_bucket.append(most_similar_flop(curr_buckets[0], new_cards))

    if len(curr_buckets) == 2:
        # check my_cards. if length 2, no auction card is turn card. otherwise is auction card.
        if len(my_cards) == 3: # auction card
            for bucket, lst in auction_flop_buckets[tuple(curr_buckets)].items():
                if new_cards[0] in lst:
                    new_bucket.append(bucket)
                    break
            if not new_bucket:
                all_cards = []
                for bucket in auction_flop_buckets[tuple(curr_buckets)]:
                    all_cards.extend(auction_flop_buckets[tuple(curr_buckets)][bucket])
                most_similar = most_similar_card(all_cards, new_cards[0])
                for bucket, lst in auction_flop_buckets[tuple(curr_buckets)].items():
                    if most_similar in lst:
                        new_bucket.append(bucket)
                        break
        # else: # turn card
        #     for bucket, lst in turn_buckets[tuple(curr_buckets)].items():
        #         if new_cards[0] in lst:
        #             new_bucket.append(bucket)
        #             break
        #     if not new_bucket:
        #         all_cards = []
        #         for bucket in turn_buckets[tuple(curr_buckets)]:
        #             all_cards.extend(turn_buckets[tuple(curr_buckets)][bucket])
        #         most_similar = most_similar_card(all_cards, new_cards[0])
        #         for bucket, lst in turn_buckets[tuple(curr_buckets)].items():
        #             if most_similar in lst:
        #                 new_bucket.append(bucket)
        #                 break
        else:
            new_bucket.append(-1)
    # auction card
    # auction_card = True
    # if len(curr_buckets) >= 3 and curr_buckets[2] == -1:
    #     auction_card = False
    
    auction_card = False
    if len(curr_buckets) >= 3 and curr_buckets[2] != -1:
        auction_card = True

    if len(curr_buckets) == 3:
        if auction_card:
            for bucket, lst in auction_turn_buckets[tuple(curr_buckets)].items():
                if new_cards[0] in lst:
                    new_bucket.append(bucket)
                    print("new bucket", bucket)
                    break
            if not new_bucket:
                all_cards = []
                for bucket in auction_turn_buckets[tuple(curr_buckets)]:
                    all_cards.extend(auction_turn_buckets[tuple(curr_buckets)][bucket])
                most_similar = most_similar_card(all_cards, new_cards[0])
                for bucket, lst in auction_turn_buckets[tuple(curr_buckets)].items():
                    if most_similar in lst:
                        new_bucket.append(bucket)
                        break
        if tuple(curr_buckets)[2] != -1: # not auction card
            curr_buckets = curr_buckets[:2]
            for bucket, lst in turn_buckets[tuple(curr_buckets)].items():
                if new_cards[0] in lst:
                    new_bucket.append(bucket)
                    break
            if not new_bucket:
                all_cards = []
                for bucket in turn_buckets[tuple(curr_buckets)]:
                    all_cards.extend(turn_buckets[tuple(curr_buckets)][bucket])
                most_similar = most_similar_card(all_cards, new_cards[0])
                for bucket, lst in turn_buckets[tuple(curr_buckets)].items():
                    if most_similar in lst:
                        new_bucket.append(bucket)
                        break
    
    if len(curr_buckets) == 4:
        if auction_card:
            for bucket, lst in auction_river_buckets[tuple(curr_buckets)].items():
                if new_cards[0] in lst:
                    new_bucket.append(bucket)
                    break
            if not new_bucket:
                all_cards = []
                for bucket in auction_river_buckets[tuple(curr_buckets)]:
                    all_cards.extend(auction_river_buckets[tuple(curr_buckets)][bucket])
                most_similar = most_similar_card(all_cards, new_cards[0])
                for bucket, lst in auction_river_buckets[tuple(curr_buckets)].items():
                    if most_similar in lst:
                        new_bucket.append(bucket)
                        break
        if tuple(curr_buckets)[2] != -1: # not auction card
            curr_buckets = curr_buckets[:2] + [curr_buckets[-1]]
            for bucket, lst in river_buckets[tuple(curr_buckets)].items():
                if new_cards[0] in lst:
                    new_bucket.append(bucket)
                    break
            if not new_bucket:
                all_cards = []
                for bucket in river_buckets[tuple(curr_buckets)]:
                    all_cards.extend(river_buckets[tuple(curr_buckets)][bucket])
                most_similar = most_similar_card(all_cards, new_cards[0])
                for bucket, lst in river_buckets[tuple(curr_buckets)].items():
                    if most_similar in lst:
                        new_bucket.append(bucket)
                        break

    return tuple(curr_buckets + new_bucket)