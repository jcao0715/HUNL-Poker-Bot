'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, BidAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random
import pickle
from selectbuckets import select_bucket

with open("strategy_dict.pkl",'rb') as strategy:
    strategy_dict = pickle.load(strategy)
# with open("preflop_buckets.pkl",'rb') as preflop_buck:
#     preflop_buck = pickle.load(strategy)

class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.

        self.history, represents the current history of the game, ex: ??pc$$Az&&xx@@Oc##Ba
        
        self.hand, represents the players hand in buckets, ex: (0,1,0,2,0) ~ (preflop bucket 0, flop bucket 1, auction bucket 0, turn bucket 2, river bucket 0)

        self.strategy, holds a dictionary with the cfr strategy, ex: {(0,0,1,2): {??ppc$$: [0.46,0.64]...}}

        '''
        
        self.strategy = strategy_dict
        

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #print(bool(active))
        self.history = ""
        self.hand = []
        self.won_auction = False
        self.always_check = False
        
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        pass
        
        

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        #previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not reveal

        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        
        
        p,b,B,P,O = [3,1/3,2/3,1,1.5]
        street_dict = {0:"??",4:"@@",5:"##", 3:'??'}
        action_dict = {'a':RaiseAction,'b':RaiseAction,'B':RaiseAction,'x':CheckAction,'c':CallAction,'z':BidAction,'A':BidAction,'p':RaiseAction,'O':RaiseAction,'f':FoldAction}

        random_num = random.randrange(1,100)
        # May be useful, but you may choose to not use.
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        my_bid = round_state.bids[active]  # How much you bid previously (available only after auction)
        opp_bid = round_state.bids[1-active]  # How much opponent bid previously (available only after auction)
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot

        pot = my_contribution + opp_contribution 
        old_pot = my_contribution + opp_contribution - continue_cost

        bet_dict = {'p':int(3*pot),'b':int(b*pot),'B':int(B*pot),'O':int(O*pot),'P':int(P*pot),'z':int(1.78*pot),'A':int(3/4*pot),'q':int(1/3*pot)}
        
        if self.always_check and BidAction in legal_actions:
            return BidAction(0)
        
        if self.always_check:
            return CheckAction()

        if len(legal_actions) == 1 and CheckAction in legal_actions:
            self.always_check = True
            return CheckAction()
        
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        
        if street_dict[street] not in self.history:
            if street != 0 and self.history[-1] == 'x' and self.history[-2:] != 'xx':
                self.history += 'x'
            if street != 0 and self.history[-1] in {'O','b','B'}:
                self.history += 'c'
            self.history += street_dict[street]

        if BidAction in legal_actions:
            if self.always_check and BidAction in legal_actions:
                return BidAction(0)
            if self.always_check:
                return CheckAction()
            if street != 0 and self.history[-1] in {'p'}:
                self.history += 'c' 
            if len(self.history)%2 == 0:
                self.history += "$$$"
            else:
                self.history += "$$"

        #OOP BB Pre
        if bool(active) and "$" not in self.history:
            self.hand = select_bucket([], my_cards, round_state, active)
            if continue_cost == 0:
                #opponent just calls
                self.history += 'p'
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]
                if action_type in {FoldAction,CallAction}:
                    self.history += 'c'
                    return CheckAction()
                elif action_type is RaiseAction:
                    if action == 'a':
                        self.always_check = True
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
                    
            elif continue_cost > 0:
                #opponent places a bet
                opp_action = estimate_opp_action(self.history,continue_cost,old_pot)
                self.history += opp_action
                print(opp_action,'flop shove')
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is CallAction:
                    self.history += 'c'
                    if opp_action == 'a':
                        if continue_cost < my_stack:
                            self.always_check = True
                            return RaiseAction(max_raise)
                        
                        else:
                            self.always_check = True
                            return CallAction()
                    return CallAction()
                if action_type is FoldAction:
                    return FoldAction()
                if action_type is RaiseAction:
                    if action == "a":
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
        
        
        #IP SB Pre
        if not bool(active) and "$" not in self.history:
            self.hand = select_bucket([], my_cards, round_state, active)
            if continue_cost == 1:
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is RaiseAction:
                    if action == 'a':
                        self.always_check = True
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
                    
                elif action_type is FoldAction:
                    return FoldAction()
                
            elif continue_cost > 1:

                opp_action = estimate_opp_action(self.history,continue_cost,old_pot)

                self.history += opp_action

                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is FoldAction:
                    return FoldAction()
                
                if action_type is CallAction:
                    self.history += 'c'
                    if opp_action == 'a':
                        self.always_check = True
                        if continue_cost < my_stack:
                            
                            return RaiseAction(max_raise)
                    return CallAction()
                
                if action_type is RaiseAction:

                    if action == 'a':
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
                    
        if self.always_check and BidAction in legal_actions:
            return BidAction(0)
            
        if self.always_check:
            return CheckAction()
        
        if len(legal_actions) == 1 and CheckAction in legal_actions:
            self.always_check = True
            return CheckAction()
        
       
        # OPP Auction
        if bool(active) and BidAction in legal_actions:
            self.hand = select_bucket(list(self.hand), board_cards, round_state, active)
            action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
            return BidAction(bet_dict[action])

        # IP Auction
        if not bool(active) and BidAction in legal_actions:
            self.hand = select_bucket(list(self.hand), board_cards, round_state, active)
            self.history += 'o'
            action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
            return BidAction(bet_dict[action])
        


        #IP flop action
        if not bool(active) and my_bid and '@' not in self.history:
        
            if 'z' not in self.history and 'A' not in self.history:
                # self.hand = select_bucket(list(self.hand), board_cards, round_state, active)
                self.history = self.history[:-1]
        
                if my_bid > opp_bid:
                    self.hand = select_bucket(list(self.hand), [my_cards[-1]], round_state, active)
                    self.history += 'Az'
                    
                elif opp_bid > my_bid:

                    self.hand = select_bucket(list(self.hand), board_cards, round_state, active)
                    self.history += 'zA'

                else:
                    self.won_auction = True
                    self.history = self.history + "AA"
                    self.hand = select_bucket(list(self.hand), [my_cards[-1]], round_state, active)
            
                self.history += '&&'
            
            if continue_cost == 0:
                #checks to me
                self.history += 'x'
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]
                if action_type is CheckAction:
                    self.history += 'x'
                    return CheckAction()
                if action_type is RaiseAction:
                    if action == 'a':
                        self.always_check = True
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
            else:
                opp_action  = estimate_opp_action(self.history,continue_cost,old_pot)
                self.history += opp_action

                if opp_action == 'x':
                    return CallAction()
                if opp_action == 'c':
                    return CallAction()
                
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is FoldAction:
                    return FoldAction()
                
                elif action_type is RaiseAction:
                    if action =="a":
                        self.history += 'a'
                        self.always_check = True
                        return RaiseAction(max_raise)
                    else:
                        self.history+=action
                        return RaiseAction(bet_dict[action])
                    
                elif action_type is CallAction:
                    self.history += 'c'
                    if opp_action == 'a':
                        if continue_cost < my_stack:
                            if opp_stack >= 0:
                                self.always_check = True
                                return CallAction()
                            self.always_check = True
                            return RaiseAction(max_raise)
                    return CallAction()
                    

        #OPP flop action
        if bool(active) and my_bid and '@' not in self.history:
            
            if 'z' not in self.history and 'A' not in self.history:
                print("OPP",self.history)
                if my_bid > opp_bid:
                    self.hand = select_bucket(list(self.hand), board_cards, round_state, active)
                    self.history += 'zA'
                        
                elif opp_bid > my_bid:
                    self.hand = select_bucket(list(self.hand), board_cards, round_state, active)
                    self.history += 'Az'
                else:
                    self.hand = select_bucket(list(self.hand), [my_cards[-1]], round_state, active)
                    self.history = self.history + "AA" 
                    
                
                self.history += '&&'

            if continue_cost == 0:
                #first to act
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]
                if action_type is CheckAction:
                    self.history += 'x'
                    return CheckAction()
                if action_type is RaiseAction:
                    if action == 'a':
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
                    
            elif continue_cost > 0:
                opp_action  = estimate_opp_action(self.history,continue_cost,old_pot)
                self.history += opp_action

                if opp_action == 'x':
                    return CallAction()
                if opp_action == 'c':
                    return CallAction()
                
                
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                
                action_type = action_dict[action]

                if action_type is FoldAction:
                    return FoldAction()
                
                elif action_type is RaiseAction:
                    if action == "a":
                        self.history += 'a'
                        return RaiseAction(max_raise)
                    else:
                        self.history+=action
                        return RaiseAction(bet_dict[action])
                    
                elif action_type is CallAction:
                    self.history += 'c'
                    if opp_action == 'a':
                        if continue_cost < my_stack:
                            return RaiseAction(max_raise)
                    return CallAction()
        # IP turn action
        if not bool(active) and '#' not in self.history:
            #add bucketing here
            if len(self.hand) <4:
                self.hand = select_bucket(list(self.hand), [board_cards[-1]], round_state, active)
            if continue_cost == 0:
                #was check to
                self.history += 'x'
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is CheckAction:
                    self.history += 'x'
                    return CheckAction()
                
                if action_type is RaiseAction:
                    if action == 'a':
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
            if continue_cost > 0:
                opp_action  = estimate_opp_action(self.history,continue_cost,old_pot)
                self.history += opp_action

                if opp_action == 'x':
                    return CallAction()
                if opp_action == 'c':
                    return CallAction()
                

                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is FoldAction:
                    return FoldAction()
                
                elif action_type is RaiseAction:
                    if action =="a":
                        if opp_stack >=0:
                            return CallAction()
                        self.history += 'a'
                        return RaiseAction(max_raise)
                    else:
                        self.history+=action
                        return RaiseAction(bet_dict[action])
                    
                elif action_type is CallAction:
                    self.history += 'c'
                    if opp_action == 'a':
                        if continue_cost < my_stack:
                            return RaiseAction(max_raise)
                    return CallAction()
            

        #OPP turn action
        if bool(active)  and '#' not in self.history:
            #bucketing goes here
            if len(self.hand) < 4:
                self.hand = select_bucket(list(self.hand), [board_cards[-1]], round_state, active)
            if continue_cost == 0:
                #first to act
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]
                if action_type is CheckAction:
                    self.history += 'x'
                    return CheckAction()
                if action_type is RaiseAction:
                    if action == 'a':
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
            else:
                opp_action  = estimate_opp_action(self.history,continue_cost,old_pot)
                self.history += opp_action

                if opp_action == 'x':
                    return CallAction()
                if opp_action == 'c':
                    return CallAction()
                

                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is FoldAction:
                    return FoldAction()
                
                elif action_type is RaiseAction:
                    if action =="a":
                        self.history += 'a'
                        return RaiseAction(max_raise)
                    else:
                        self.history+=action
                        return RaiseAction(bet_dict[action])
                    
                elif action_type is CallAction:

                    self.history += 'c'
                    if opp_action == 'a':
                        if continue_cost < my_stack:
                            print('river countinue cost')
                            return RaiseAction(max_raise)
                        
                    return CallAction()
        #IP river
        if not bool(active):
            if len(self.hand) <5:
                self.hand = select_bucket(list(self.hand), [board_cards[-1]], round_state, active)
            if continue_cost == 0:
                #was check to
                self.history += 'x'
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]
                if action_type is CheckAction:
                    self.history += 'x'
                    return CheckAction()
                if action_type is RaiseAction:
                    if action == 'a':
                        print(opp_stack,my_stack,'stacks')
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
            if continue_cost > 0:
                opp_action  = estimate_opp_action(self.history,continue_cost,old_pot)
                self.history += opp_action

                if opp_action == 'x':
                    return CallAction()
                if opp_action == 'c':
                    return CallAction()
                

                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is FoldAction:
                    return FoldAction()
                
                elif action_type is RaiseAction:
                    if action =="a":
                        if opp_stack >= 0:
                            self.always_check = True
                            return CallAction()
                        self.always_check = True
                        return RaiseAction(max_raise)
                    else:
                        self.history+=action
                        return RaiseAction(bet_dict[action])
                    
                elif action_type is CallAction:
                    self.history += 'c'
                    if opp_action == 'a':
                        if continue_cost < my_stack:
                            return RaiseAction(max_raise)
                    return CallAction()
            
        if bool(active):
            #bucketing goes here
            if len(self.hand) < 5:
                self.hand = select_bucket(list(self.hand), [board_cards[-1]], round_state, active)
            if continue_cost == 0:
                #first to act
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]
                if action_type is CheckAction:
                    self.history += 'x'
                    return CheckAction()
                if action_type is RaiseAction:
                    if action == 'a':
                        return RaiseAction(max_raise)
                    else:
                        self.history += action
                        return RaiseAction(bet_dict[action])
            else:
                opp_action  = estimate_opp_action(self.history,continue_cost,old_pot)
                self.history += opp_action

                if opp_action == 'x':
                    return CallAction()
                if opp_action == 'c':
                    return CallAction()
                
                action = find_action(self.strategy,self.history,self.hand,my_stack,opp_stack)
                action_type = action_dict[action]

                if action_type is FoldAction:
                    return FoldAction()
                
                elif action_type is RaiseAction:
                    if action =="a":
                        return RaiseAction(max_raise)
                    else:
                        self.history+=action
                        return RaiseAction(bet_dict[action])
                    
                elif action_type is CallAction:

                    self.history += 'c'
                    if opp_action == 'a':
                        if continue_cost < my_stack:
                            return RaiseAction(max_raise)

                    return CallAction()
        if CheckAction in legal_actions:
            return random.choice([CheckAction(),RaiseAction(min_raise*1.2)])
        else:
            return random.choice([FoldAction(),RaiseAction(min_raise*1.2)])
        
        
        # print(self.history,my_stack,opp_stack)
def estimate_opp_action(history,continue_cost,pot):
    """
    given an action by opponet estimate what it is for our strategy
    ex: ['b','B','p','O','a','c','f']
    ??pc$$$AA&&Oa not accounted for 1

    ratio = continue_cost/pot

    preflop solver interpretations:
        0 < ratio < 10 ~ p
        ratio > 10 ~ a

        if p is already in the history twice a raise (4-bet) is considered an all in 
    
    """
    ratio = continue_cost/pot
    if "$" not in history:
        #only preflop
        if history.count('p') > 1:
            return 'a'
        elif 0 < ratio < 7:
            return 'p'
        else: return 'a'

    if history[-1] in {'@','&','#'}:
        if 0<ratio< 4:
            return 'O'
        else: return 'a'

    if history[-1] == 'x':
        if 0 < ratio <= 0.3:
            return 'x'
        if 0.3 < ratio <= 1.0:
            return 'B'
        if ratio > 1.0: return 'a'
        
    if history[-1] == 'b':
        #for when little bet gets raised
        if ratio < 0.2:
            return 'c'
        if 0.2 <= ratio <= 1.0:
            return 'B'
        else: return 'a'
    if history[-1] == 'O':
        return 'a'
    if history[-1] == 'B':
        return 'a'
    print(history,'case not implemented ;)' )
        
def find_action(strategy,history,buckets,player_1_stack,player_2_stack):
    """
    strategy: dictionary mapping buckets to historys to frequencies of actions

    history: game history
    buckets: hero bucketed hands

    player_1_stack: stack of SB/Button
    player_2_stack: stack of BB

    returns action
    """
    print(buckets,history,'buckets and history')

    if history not in strategy[buckets]:
        return random.choice(['B','f'])
    
    action_array = [int(x*100) for x in strategy[buckets][history]]
    #print(action_array)
    weighted_action = [[action]for action,weight in zip(currently_playable(history,player_1_stack,player_2_stack),action_array) for _ in range(weight) ]
    #print(weighted_action)
    action = random.choice(weighted_action)[0]
    print(action,'chosen action')
    return action


def currently_playable(history,player_1_stack,player_2_stack):
    """
    given the history return an array of playable moves

    What are the playable moves for given histories:

        Case 0: Chance Event
            When history[-1] in {?,&}, this means a chance event has occured. If we are preflop (?), we can raise or fold. If we are post-flop (&), we can check or bet.

        Case 1: When History Ends in Bet
            When history[-1] in {b,B}, the actions possible are call,raise,or fold.
        
        Case 2: When History Ends in all-in
            When history[-1] == 'a', the actions possible are call or fold.
        
        Case 3: When History Ends in check
            When history[-1] == 'x', the actions possible are check or bet.

    Note: We should never encounter call when currently_playable is ran since a call would require a chance node or terminal to be evaluated.

    return [n_1,n_2,...,n_i]
    """
    #temporary all-in adjuster
    all_in = True
    pot = 2*400 - player_1_stack - player_2_stack
    p_size,b_size,B_size,P_size,O_size = [3,1/3,2/3,1,1.5]
    p_size = pot*p_size
    b_bet = pot*b_size
    B_bet = pot*B_size
    P_bet = pot*P_size
    O_bet = pot*O_size
    bet_dict = {'q':pot*random.uniform(0.23, 0.43), 'A': random.uniform(0.43, 0.90),'z':random.uniform(1.334,2.14)}
    if all_in: 
        if history[-1] == 'a':
            return ['c','f']
        if history[-1] == '?':
            return ['p','a','f']
        if history[-1] == 'p':
            if history.count('p') > 1:
                return ['c','a','f']
            else:
                return ['p','c','a','f']
        if history[-1] in {'&','@','#'}:
            if player_1_stack >= O_bet and player_2_stack >= O_bet:
                return ['x','O','a']
            else: return ['x','a']
            #return ['x','b','B','P','O','a']
        if history[-1] == 'b':
            if player_1_stack >= B_bet and player_2_stack >= B_bet:
                return ['c','B','a','f']
            else: return ['c','a']

        if history[-1] == 'B':
            return ['c','a','f']
        if history[-1] == 'P':
            return ['c','a','f']
        if history[-1] == 'O':
            return ['c','a','f']
       
        if history[-1] == 'x':
            if player_1_stack >= B_bet and player_2_stack >= B_bet:
                return ['x','B','a']
            elif  player_1_stack >= b_bet and player_2_stack >= b_bet:
                return ['x','b','a']
            else: return ['x','a']
        if history[-1] == "$":
            if player_1_stack >= bet_dict['A']*pot and player_2_stack >= bet_dict['A']*pot:
                return ['A','z']
            elif  player_1_stack >= bet_dict['q']*pot and player_2_stack >= bet_dict['q']*pot:
                return ['q','z']
            else:return ['z']
        if history[-1] in {'A','z','o'}:
            if player_1_stack >= bet_dict['A']*pot and player_2_stack >= bet_dict['A']*pot:
                return ['A','z']
            elif  player_1_stack >= bet_dict['q']*pot and player_2_stack >= bet_dict['q']*pot:
                return ['q','z']
            else:return ['z']

if __name__ == '__main__':
    run_bot(Player(), parse_args())
