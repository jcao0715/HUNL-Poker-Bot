import pickle
import eval7
from skeleton.states import RoundState
import ctypes

# may have to change path
# shared = ctypes.CDLL('../waugh_iso/src/hand_index.so')

MAX_ROUNDS = 8
NUM_SUITS = 4
RANKS = '23456789TJQKA'
SUITS = 'shdc'

class HandIndexer(ctypes.Structure):
    _fields_ = [
        ("cards_per_round", ctypes.c_uint8 * MAX_ROUNDS),
        ("round_start", ctypes.c_uint8 * MAX_ROUNDS),
        ("rounds", ctypes.c_uint32),
        ("configurations", ctypes.c_uint32 * MAX_ROUNDS),
        ("permutations", ctypes.c_uint32 * MAX_ROUNDS),
        ("round_size", ctypes.c_uint64 * MAX_ROUNDS),

        ("permutation_to_configuration", ctypes.POINTER(ctypes.c_uint32) * MAX_ROUNDS),
        ("permutation_to_pi", ctypes.POINTER(ctypes.c_uint32) * MAX_ROUNDS),
        ("configuration_to_equal", ctypes.POINTER(ctypes.c_uint32) * MAX_ROUNDS),

        ("configuration", ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)) * MAX_ROUNDS),
        ("configuration_to_suit_size", ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)) * MAX_ROUNDS),
        ("configuration_to_offset", ctypes.POINTER(ctypes.c_uint64) * MAX_ROUNDS)
    ]

with open("buckets/bucketed_flops.pkl", 'rb') as f:
    flop_buckets = pickle.load(f)

def str2num(hands):
    cards = []
    for hand in hands:
        rank = RANKS.index(hand[0])
        suit = SUITS.index(hand[1])
        cards.append(4 * rank + suit)
    return cards

def num2str(hands):
    cards = []
    for hand in hands:
        rank = RANKS[hand // 4]
        suit = SUITS[hand % 4]
        cards.append(rank + suit)
    return cards


    

def most_similar_flop(flop_bucket, target):
    all_flops = []
    for bucket in flop_buckets[flop_bucket]:
        all_flops.extend(flop_buckets[flop_bucket][bucket])
    max_common_cards = -1
    closest_flop = None
    for flop in all_flops:
        common_cards = len(set(flop) & set(target))
        if common_cards > max_common_cards:
            max_common_cards = common_cards
            closest_flop = flop
    for bucket, lst in flop_buckets[flop_bucket].items():
        if closest_flop in lst:
            return bucket
    
def most_similar_flop(flop_bucket, target):
    max_rank_matches = -1
    max_suit_matches = -1
    closest_flop = None

    target_ranks = set(card[0] for card in target)
    target_suits = set(card[1] for card in target)

    all_flops = []
    for bucket in flop_buckets[flop_bucket]:
        all_flops.extend(flop_buckets[flop_bucket][bucket])
    for flop in all_flops:
        flop_ranks = set(card[0] for card in flop)
        flop_suits = set(card[1] for card in flop)
        rank_matches = len(target_ranks & flop_ranks)
        suit_matches = len(target_suits & flop_suits)
        if rank_matches > max_rank_matches or (rank_matches == max_rank_matches and suit_matches > max_suit_matches):
            max_rank_matches = rank_matches
            max_suit_matches = suit_matches
            closest_flop = flop
    for bucket, lst in flop_buckets[flop_bucket].items():
        if closest_flop in lst:
            return bucket
        continue


def find_flop(curr_buckets, new_cards, round_state, active):
    res = -1
    my_cards = round_state.hands[active]
    street = round_state.street
    board_cards = round_state.deck[:street]

    full_board = my_cards + board_cards
    full_board = str2num(full_board)
    cards = (ctypes.c_uint8 * 5)(*full_board)
    store_res = (ctypes.c_uint8 * 5)(*([]))
    canonical = []
    indexer = HandIndexer()
    initialize = shared.hand_indexer_init(2, (ctypes.c_uint8 * 2)(*([2, 3])), ctypes.byref(indexer))
    index = shared.hand_index_last(indexer, cards)
    unindex = shared.hand_unindex(indexer, 1, index, store_res)
    for card in store_res:
        canonical.append(card)
    canonical = num2str(canonical)
    flop = tuple(sorted(canonical[2:]))

    pf = curr_buckets[0]
    searchdict = flop_buckets[pf]
    for bucket, lst in searchdict.items():
        if flop in lst:
            res = bucket
            break
    
    res = most_similar_flop(pf, new_cards) if res == -1 else res
    return res