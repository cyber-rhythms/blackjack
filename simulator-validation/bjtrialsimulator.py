#!/usr/bin/env python
# coding: utf-8

# This combines the following simulators:
# 
# 1) Basic Strategy, constant betting - the required modules for this simulator are listed first.
# 
# 2) HI-LO Card counting, variable betting, no HI-LO Strategy variation - the required modules for this simulator are listed after all modules for Basic Strategy have been listed.
# 
# After all the required modules are listed, the *same* random seed is chosen, and the simulator for both 1) and 2) is run.
# For both 1) and 2):
# 
# * A logfile is generated for both so that the internal workings of each simulator can be checked.
# * A csv file containing each time series trajectory of player capital stock by row is output to a csv file.

# In[2]:


import pandas as pd
import random
from matplotlib import pyplot 
import numpy as np

import sys
sys.stdout = open('simulatorlogfile.txt', 'w')


# In[3]:


columns = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
index = [i for i in range(5, 22)]
index2 = ['A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10']
index3 = ['2, 2','3, 3', '4, 4', '5, 5', '6, 6', '7, 7', '8, 8', '9, 9', '10, 10', 'J, J', 'Q, Q', 'K, K', 'A, A']
indices = index + index2 + index3
basic_strategy_table = pd.read_csv('basic-strategy.csv', header=None)
basic_strategy_table.index = indices
basic_strategy_table.columns = columns

basic_strategy_table_no_doubling = pd.read_csv('basic-strategy-no-doubling.csv', header=None)
basic_strategy_table_no_doubling.index = indices
basic_strategy_table_no_doubling.columns = columns


# In[ ]:


# The following modules are used for the implementation of the Basic Strategy, constant betting simulator.


# In[4]:


def getcards(decks=1):
    """Brings out a number of sealed decks of cards in their original order to the virutal gaming table.

    Creates a dictionary tracking the name of each card, its quantity, and its value
    
    Keyword argument:
        decks {int} -- the number of 52-card decks that the casino is using (default 1)
    
    Returns:
        dictionary{keys: values} -- dictionary object where keys are the card name (e.g. 'K' for King )
                                    and where the values are a list object containing the card's quantity and its value.
                                    
    The value for the ace contains three elements, as aces can further take on the value of 1 or 11, depending on 
    the context of the hand. No distinction is made between card suits, i.e. spades, hearts, clubs, diamonds.
    """
    
    deck = {}
    total_cards = decks * 52
    card_quantity = int(total_cards / 13)
    
    deck['A'] = [card_quantity, 1, 11]

    for card in range(2, 11):
        deck[str(card)] = [card_quantity, card]
    
    for card in "JQK":
        deck[str(card)] = [card_quantity, 10]
        
    return deck, total_cards


# In[5]:


def shuffler(deck, total_cards):
    
    """Shuffles the decks of cards, and places them inside the virtual gaming table card-shoe."""
    
    shuffled_shoe = []
    
    while len(shuffled_shoe) < total_cards:
        draw = random.choice(list(deck))
        if deck[draw][0] == 0:
            pass
        else:
            deck[draw][0] -= 1
            shuffled_shoe.append(draw)
            
    return shuffled_shoe


# In[7]:


def openinghand():
    
    """Deals two cards to the player, and one to the dealer from the shuffled shoe. Outputs a message if there is Blackjack
    
    Cards are taken sequentially from the shuffled card shoe, beginning with the last element of the shuffled shoe list object
    and working in reverse order."""
    
    player = []
    dealer = []

    player.append(shuffled_shoe.pop())
    player.append(shuffled_shoe.pop())
    
    dealer.append(shuffled_shoe.pop())
    
    if ('A' in player) and (('10' in player) or ('J' in player) or ('Q' in player) or ('K' in player)):
        player_blackjack = 1
        print("Blackjack, house pays out at 3:2")
    else:
        player_blackjack = 0
        print("No Blackjack this time")
        
    return player, dealer, player_blackjack


# In[8]:


def decode(action):
    if action == 'Sp':
        message = 'split'
    elif action == 'H':
        message = 'hit'
    elif action == 'D':
        message = 'double down'
    else:
        message = 'stick'
    return message


# In[9]:


def basic_player_multiple_hits(player, dealer, player_blackjack):
    
    if len(player) == 2:
        
        if player_blackjack == 1:
            cardvalues = [21]
            decision = 'S'
            print("It's my lucky day")
        else:
            if player[0] == player[1]:
                lookup_pairs = player[0] + ", " + player[1]
                decision = basic_strategy_table.loc[lookup_pairs, dealer[0]]
                print("As I have a pair of {}s".format(player[0]))
            elif ('A' in player):
                if player[0] == 'A':
                    lookup_soft_total = player[0] + player[1]
                else:
                    lookup_soft_total = player[1] + player[0]
                
                decision = basic_strategy_table.loc[lookup_soft_total, dealer[0]]
                print("As I have a soft total")
            else:
                cardvalues = []
                for card in player:
                    cardvalues.append(deck[card][1])
                
                lookup_hard_total = sum(cardvalues)
                decision = basic_strategy_table.loc[lookup_hard_total, dealer[0]]
                print("I have a total of {}.".format(lookup_hard_total))
        
    if len(player) > 2: 
        
        if 'A' in player:  # check if the >3 hand has an ace, i.e. is potentially soft.
            if player[0] != 'A':  # re-order dual ace to the left
                ace_index = player.index('A')  
                player[0], player[ace_index] = player[ace_index], player[0]
            
            cardvalues_no_ace = [deck[card][1] for card in player[1::]]
            
            if sum(cardvalues_no_ace) <= 10: # check soft totals
                lookup_soft_total = player[0] + str(sum(cardvalues_no_ace))

                decision = basic_strategy_table_no_doubling.loc[lookup_soft_total, dealer[0]]
                print("As I have a soft {}, that is {} or {}.".format(11 + sum(cardvalues_no_ace), 1 + sum(cardvalues_no_ace), 11 + sum(cardvalues_no_ace)))
            else:
                lookup_hard_total = deck['A'][1] + sum(cardvalues_no_ace) # variable naming, hard total as ace can only take value 1 now
                
                decision = basic_strategy_table_no_doubling.loc[lookup_hard_total, dealer[0]]
                print("I have {}.".format(1 + sum(cardvalues_no_ace)))
        else:
            cardvalues = [deck[card][1] for card in player]
            lookup_hard_total = sum(cardvalues)
            
            decision = basic_strategy_table_no_doubling.loc[lookup_hard_total, dealer[0]]
            print("I have {}.".format(sum(cardvalues)))
            
    return decision


# In[10]:


def player_action(player, decision):
    
    if decision == 'S':
        print(player)
        return player# -> go to dealerturn()

    if decision == 'D':
        drawcard = shuffled_shoe.pop()
        player.append(drawcard)
        print(player) #-> go to dealerturn(), and also have to modify payout
        return player
        
    
    if decision == 'H':
        drawcard = shuffled_shoe.pop()
        player.append(drawcard)
        print(player) #-> now there are three cards in player hand and one in dealer
        return player
        

    if decision == 'Sp': 
        multiple_hand_player = [player[i:i+1] for i in range(len(player))] #splits the player hand into two cards and places them in two sub-hands
    
        drawcard1 = shuffled_shoe.pop()
        drawcard2 = shuffled_shoe.pop()
    
        print("After, splitting, I receive {} and {} in each of my hands".format(drawcard1, drawcard2))
    
        multiple_hand_player[0].append(drawcard1)
        multiple_hand_player[1].append(drawcard2)
        
        print("My new hands are: " + str(multiple_hand_player))
        
    return multiple_hand_player


# In[11]:


# Busting module
# O/S - simplify the logic, if possible. Make it a function of a generic argument like hand?

def check_if_bust(player):
    if 'A' in player:
        if player[0] != 'A':
            ace_index = player.index('A')
            player[0], player[ace_index] = player[ace_index], player[0]
            
        card_values_no_ace = [deck[card][1] for card in player[1::]]
        
        if sum(card_values_no_ace) <= 10:
            bust_indicator = 0
        elif sum(card_values_no_ace) > 20:
            bust_indicator = 1
        else:
            bust_indicator = 0
    else:
        card_values = [deck[card][1] for card in player]
        
        if sum(card_values) > 21:
            bust_indicator = 1
        else:
            bust_indicator = 0
            
    return bust_indicator


# In[12]:


def player_turn(player, decision):

    while decision == 'H':
        playerbust_indicator = check_if_bust(player)
        
        if playerbust_indicator == 0:
            print("Continue decision-action sequence")
            decision = basic_player_multiple_hits(player, dealer, player_blackjack)
            print(decision)
            player = player_action(player, decision)
            print(player)
        else:
            print("Now dealer's turn as I have gone bust, CF takes over")
            break
    else:
        if decision == 'S':
            print("Decision-action sequence terminated by decision = 'S'")
            print("Go to dealer, CF takes over")
            playerbust_indicator = 0
        elif decision == 'D':
            print("Decision-action sequence terminated by decision = 'D'")
            print("Go to dealer, CF takes over")
            playerbust_indicator = check_if_bust(player)
            
            if playerbust_indicator:
                print("Player doubled and busted.")
            else:
                print("Player doubled and did not bust.")
                
        elif decision == 'Sp':  # This part was added hastily - you need to think out the logic of this through.
            playerbust_indicator = check_if_bust(player)
        
    return player, decision, playerbust_indicator


# In[13]:


def player_action_parent(player, decision):
    
    if decision == 'S':
        print(player)
        return player# -> go to dealerturn()

    if decision == 'D':
        drawcard = shuffled_shoe.pop()
        player.append(drawcard)
        print(player) #-> go to dealerturn(), and also have to modify payout
        return player
        
    
    if decision == 'H':
        drawcard = shuffled_shoe.pop()
        player.append(drawcard)
        print(player) #-> now there are three cards in player hand and one in dealer
        return player
        

    if decision == 'Sp': 
        player_split_hands = [player[i:i+1] for i in range(len(player))] #splits the player hand into two cards and places them in two sub-hands
    
        drawcard1 = shuffled_shoe.pop()
        drawcard2 = shuffled_shoe.pop()
                    
        print("After, splitting, I receive {} and {} in each of my hands".format(drawcard1, drawcard2))
    
        player_split_hands[0].append(drawcard1)
        player_split_hands[1].append(drawcard2)
        
        if [hand[0] == hand[1] for hand in player_split_hands] == [True, False]:  # if additional pairs are drawn then these are placed at the end of the list of lists.
            player_split_hands[0], player_split_hands[1] = player_split_hands[1], player_split_hands[0]
        
        print("My new hands are: " + str(player_split_hands))
        
        return player_split_hands


# In[14]:


def player_action_child(player, decision):
    
    if decision == 'S':
        print(player)
        return player# -> go to dealerturn()

    if decision == 'D':
        drawcard = shuffled_shoe.pop()
        player.append(drawcard)
        print(player) #-> go to dealerturn(), and also have to modify payout
        return player
        
    
    if decision == 'H':
        drawcard = shuffled_shoe.pop()
        player.append(drawcard)
        print(player) #-> now there are three cards in player hand and one in dealer
        return player  

    if decision == 'Sp':
        
        index = player_split_hands.index(player) 
        
        player_split_hands.insert(index + 1, list(player.pop()))  # Turn one hand with a pair into two separate hands inside player_split_hands
    
        drawcard1 = shuffled_shoe.pop()
        drawcard2 = shuffled_shoe.pop()
    
        print("After, splitting, I receive {} and {} in each of my hands".format(drawcard1, drawcard2))
    
        player_split_hands[index].append(drawcard1)
        player_split_hands[index + 1].append(drawcard2)
        
        if [hand[0] == hand[1] for hand in player_split_hands[index:index + 2]] == [True, False]: # Ensures that if further pairs are drawn these are not resolved first.
            player_split_hands[index], player_split_hands[index + 1] = player_split_hands[index + 1], player_split_hands[index]
        
        print("My new hands are: {} and {}.".format(player_split_hands[index], player_split_hands[index + 1]))
        
        player = player_split_hands[index] 
        
    return player


# In[15]:


def player_multiple_turns(player_split_hands):
    
    decision_list = []
    playerbust_indicator_list = []
    
    for hand in player_split_hands:
        
        print("Loop is working on hand {}".format(hand))
    
        if ('A' in hand) and (('10' in hand) or ('J' in hand) or ('Q' in hand) or ('K' in hand)):
            decision = 'S'
        else:
            decision = basic_player_multiple_hits(hand, dealer, player_blackjack)
            
        if (hand[0] == 'A') and (hand[1] != 'A'):
            decision = 'S'
        player = player_action_child(hand, decision)
    
        if decision == 'Sp':
            while player[0] == player[1]:
                decision = basic_player_multiple_hits(player, dealer, player_blackjack)
                player = player_action_child(player, decision)
            else:  
                if ('A' in player) and (('10' in player) or ('J' in player) or ('Q' in player) or ('K' in player)): 
                    decision = 'S'
                else:
                    decision = basic_player_multiple_hits(player, dealer, player_blackjack)
            
                if (player[0] == 'A') and (player[1] != 'A'): 
                    decision = 'S'
                player = player_action_child(player, decision)
            
        player, decision, playerbust_indicator = player_turn(player, decision)
        decision_list.append(decision)
        playerbust_indicator_list.append(playerbust_indicator)
    
    return player_split_hands, decision_list, playerbust_indicator_list


# In[16]:


def evaluate_hand(player):
    if 'A' in player:
        soft_total_indicator = 1
        print("Player has a soft total")
    else:
        soft_total_indicator = 0
        print("Player has a hard total")
    return soft_total_indicator


# In[17]:


def compute_playerscore(player):
    soft_total_indicator = evaluate_hand(player)
    
    if soft_total_indicator:
        if player[0] != 'A':
            ace_index = player.index('A')
            player[0], player[ace_index] = player[ace_index], player[0]
            
        cardvalues_no_ace = [deck[card][1] for card in player[1::]]
        
        if sum(cardvalues_no_ace) >= 11:
            playerscore = deck['A'][1] + sum(cardvalues_no_ace)
        elif sum(cardvalues_no_ace) <= 10:
            playerscore = deck['A'][2] + sum(cardvalues_no_ace)   
    else:
        playerscore = sum([deck[card][1] for card in player])
        
    return playerscore


# In[18]:


def compute_multiple_playerscores(player_split_hands):
    playerscore_list = []
    for hand in player_split_hands:
        playerscore = compute_playerscore(hand)
        playerscore_list.append(playerscore)
    
    return playerscore_list


# In[19]:


def evaluate_hand(dealer):
    if 'A' in dealer:
        soft_total_indicator = 1
        print("Dealer has a soft total")
    else:
        soft_total_indicator = 0
        print("Dealer has a hard total")
    return soft_total_indicator


# In[20]:


def hard_total_score(dealer):
    cardvalues = [deck[card][1] for card in dealer]
    return sum(cardvalues)


# In[21]:


def soft_total_score(dealer):
    if dealer[0] != 'A':
        ace_index = dealer.index('A')
        dealer[0], dealer[ace_index] = dealer[ace_index], dealer[0]
        
    cardvalues_no_ace = [deck[card][1] for card in dealer[1::]]
    
    if sum(cardvalues_no_ace) <= 5:
        status = 'H'
        dealerscore = 0
        print("Dealer has soft {}, that is {} or {}. Dealer must draw a card.".format(11 + sum(cardvalues_no_ace), 1 + sum(cardvalues_no_ace), 11 + sum(cardvalues_no_ace)))
    if (sum(cardvalues_no_ace) >= 6) and (sum(cardvalues_no_ace) <= 10):
        print("Dealer has {}. Dealer must stick.".format(11 + sum(cardvalues_no_ace)))
        status = 'S'
        dealerscore = 11 + sum(cardvalues_no_ace)
    if (sum(cardvalues_no_ace) >= 11) and (sum(cardvalues_no_ace) <= 15):
        print("Dealer has {}. Dealer must draw cards".format(1 + sum(cardvalues_no_ace)))
        status = 'H'
        dealerscore = 1 + sum(cardvalues_no_ace)
    if (sum(cardvalues_no_ace) >= 16) and sum(cardvalues_no_ace) <= 20:
        print("Dealer has {}. Dealer must stick.".format(1 + sum(cardvalues_no_ace)))
        status = 'S'
        dealerscore = 1 + sum(cardvalues_no_ace)
    elif sum(cardvalues_no_ace) > 20:
        status = 'B'
        dealerscore = 1 + sum(cardvalues_no_ace)
        
    return [status, dealerscore]


# In[22]:


def dealerturn(dealer):
    
    drawcard = shuffled_shoe.pop()
    dealer.append(drawcard)
    
    print("Dealer draws {}.".format(drawcard))
    
    soft_total_indicator = evaluate_hand(dealer)  # Evaluates whether there is an ace in the dealer's hand
    
    hard_total = hard_total_score(dealer)  # Computes hand's score whether this is a hard or soft hand 
    
    dealerbust_indicator = check_if_bust(dealer)
      
    while (soft_total_indicator == 0) and (hard_total < 17):
        
        drawcard = shuffled_shoe.pop()
        dealer.append(drawcard)
        print("As dealer's score is less than 17, dealer draws {}.".format(drawcard))
        print(dealer)
        soft_total_indicator = evaluate_hand(dealer)
        hard_total = hard_total_score(dealer)
        dealerbust_indicator = check_if_bust(dealer)
        if dealerbust_indicator == 1:
            print("Dealer has bust with total of {}".format(hard_total))
            dealerscore = hard_total
            dealerbust_indicator = 1
            break
    else:
        print("Either dealer has an ace in hand, has drawn an ace, or chosen to stick on greater than 17 or has bust.") #This happens when the statement x becomes false 
    
        if soft_total_indicator == 1:
            soft_total = soft_total_score(dealer)
            while (soft_total[0] == 'H'):
                drawcard = shuffled_shoe.pop()
                dealer.append(drawcard)
                print("Dealer draws {}.".format(drawcard))
                soft_total = soft_total_score(dealer)
                if soft_total[0] == 'B':
                    print("Dealer has bust")
                    dealerscore = soft_total[1]
                    dealerbust_indicator = 1
                    break
            else:
                dealerscore = soft_total[1]
                dealerbust_indicator = 0
                
        # Cases of hard hand, have to deal with >17 and bust, and >17 stick
        else: 
            if hard_total > 21:
                dealerscore = hard_total
                dealerbust_indicator = 1
            elif hard_total <= 21:
                dealerscore = hard_total
                dealerbust_indicator = 0
                
    print(dealer)
    
    return dealer, dealerscore, dealerbust_indicator


# In[25]:


def handoutcome(playerscore, dealerscore, playerbust_indicator, dealerbust_indicator, player_blackjack):
    
    """Encodes the outcome of hand using whether or not the dealer or player has bust, their respective scores, and
    whether the player has blackjacked.
    
    Can be extended if analysis required tracking the evolution of this variable."""
    
    if player_blackjack == 1:
        hand_outcome = 3
        print("Player wins the hand with Blackjack")
    else:
        if playerbust_indicator == 1 and dealerbust_indicator == 1:
            hand_outcome = 0
            print("Player busts. Dealer also busts. But the 'edge' means that player loses the hand.")
        elif playerbust_indicator == 0 and dealerbust_indicator == 1:
            hand_outcome = 1 
            print("Dealer busts. Player wins the hand") 
        elif playerbust_indicator == 1 and dealerbust_indicator == 0:
            hand_outcome = 0
            print("Player busts. Player loses the hand")
        else:
            if playerscore > dealerscore:
                hand_outcome = 1
                print("Player has higher score. Player wins the hand")
            elif playerscore < dealerscore:
                hand_outcome = 0
                print("Dealer has higher score. Dealer wins the hand")
            else:
                hand_outcome = 2
                print("Both dealer and player have the same score, the outcome of the hand is a draw.")
                  
    return hand_outcome


# In[26]:


def multiple_hand_outcomes(playerscore_list, dealerscore, 
                           playerbust_indicator_list, dealerbust_indicator, 
                           player_blackjack):
    
    multiple_hand_outcome_list = []
    
    for playerscore, playerbust_indicator in zip(playerscore_list, playerbust_indicator_list):
        hand_outcome = handoutcome(playerscore, dealerscore, playerbust_indicator, dealerbust_indicator, player_blackjack)
        multiple_hand_outcome_list.append(hand_outcome)
        
    return multiple_hand_outcome_list


# In[ ]:


def payout_loss(hand_outcome, decision):
    
    """Uses the outcome to calculate payoffs/losses, and decision of whether player has doubled down
    to update player's capital stock accordingly. """
    
    global capital_stock
    
    if hand_outcome == 0:
        if decision == 'D':
            new_capital = capital_stock[-1] - (2 * bet_per_round)
            capital_stock.append(new_capital)
            print("Player loses " + str(2 * bet_per_round) + " pounds from earlier doubling down.")
        else:
            new_capital = capital_stock[-1] - bet_per_round
            capital_stock.append(new_capital)
            print("Player loses " + str(bet_per_round) + " pounds.")
    
    elif hand_outcome == 1:
        if decision == 'D':
            new_capital = capital_stock[-1] + (2 * bet_per_round)
            capital_stock.append(new_capital)
            print("Player wins " + str(2 * bet_per_round) + " pounds from earlier doubling down.")
        else:
            new_capital = capital_stock[-1] + bet_per_round
            capital_stock.append(new_capital)
            print("Player wins  " + str(bet_per_round) + " pounds")
        
    elif hand_outcome == 2:
        new_capital = capital_stock[-1]
        capital_stock.append(new_capital)
        print("Draw, no change to player's initial capital.")
        
    else:
        new_capital = capital_stock[-1] + (1.5 * bet_per_round)
        capital_stock.append(new_capital)
        print("Player blackjacks, house pays out " + str(1.5 * bet_per_round) + " pounds.")
        
    print("Player now has" + " " + str(capital_stock[-1]) + " " + "pounds remaining.")
        
    return capital_stock


# In[ ]:


def multiple_payout_loss(multiple_hand_outcome_list, decision_list):
    
    global capital_stock
    
    for hand_outcome, decision in zip(multiple_hand_outcome_list, decision_list):
    
        capital_stock = payout_loss(hand_outcome, decision)
    
    return capital_stock


# In[ ]:


def replenish_shoe(threshold):
    
    """Checks whether or not  we are near the end of a shoe. If so, discards the remaining cards in the current shoe,
    collects them together with remaining cards that were discarded in previous hands, reshuffles all of them togther,
    and finally replenishes the shoe."""
    
    global deck
    global total_cards
    global shuffled_shoe
    global shoe_number
    
    fraction_cards_remaining = len(shuffled_shoe) / total_cards
    
    if fraction_cards_remaining < threshold:
        shuffled_shoe.clear
        deck, total_cards = getcards(decks=6)
        shuffled_shoe = shuffler(deck, total_cards)
        shoe_number += 1
        
        print("As we are reaching near the end of the shoe, we will reshuffle")
        print("=========================== SHOE {} ===========================".format(shoe_number))
    else:
        print("No need for reshuffling yet, as card threshold not reached")

    return shuffled_shoe


# In[ ]:


# The following modules are used, either in addition to, or in place of modules above in the HI-LO Card Counting control flow.


# In[ ]:


def player_bets(truecount, total_cards_dealt):
    
    """A specification of player betting behaviour. Uses the truecount from the previous round to inform betting behaviour.
    If it is the first round of a shoe, then the minimum bet is placed."""
    
    if total_cards_dealt == 0:
        current_hand_bet = bet_per_round
        print("As this is the first round of the shoe, there is no available statistical information to use to place bets.")
        print("I will therefore bet {}".format(current_hand_bet))
    else:
        if (truecount <= 2):
            current_hand_bet = bet_per_round
            print("As the true count is {}, I will bet {}".format(truecount, current_hand_bet))
        if truecount > 2:
            current_hand_bet = 20 * bet_per_round
            print("As the true count is {}, I will bet {}".format(truecount, current_hand_bet))
    return current_hand_bet


# In[ ]:


def update_truecount(player, dealer, runningcount, total_cards_dealt):
    
    """Updates the true count, running count, and the number of cards dealt; at the end of the round. This information is used
    to inform the player's bet in the next round."""
    
    print("At the beginning of the round, the running count was {}, and the total number of cards dealt was {}".format(runningcount, total_cards_dealt))
    
    cards_dealt = player + dealer
    
    current_round_running_count = 0 
    
    for card in cards_dealt:
        if card in ['2','3','4','5','6']:
            current_round_running_count += 1
        if card in ['7','8','9']:
            current_round_running_count += 0
        if card in ['10','J', 'Q', 'K', 'A']:
            current_round_running_count -= 1
            
    runningcount = current_round_running_count + runningcount
            
    current_round_cards_dealt = len(cards_dealt)
    total_cards_dealt += current_round_cards_dealt
    total_unseen_cards = total_cards - total_cards_dealt
    unseen_decks = total_unseen_cards / 52 
    truecount = runningcount / unseen_decks
    
    print("The change in the running count for this round is {}".format(current_round_running_count))
    
    print("At the end of the round, the running count is now {}, and the number of unseen decks is {}, giving a true count of {}".format(runningcount, unseen_decks, truecount))
    
    return truecount, runningcount, total_cards_dealt


# In[ ]:


def multiple_hand_update_truecount(player_split_hands, dealer, runningcount, total_cards_dealt):
    
    """Updates the true count, running count and the number of cards dealt; at the end of round, for every hand."""
    
    print("At the beginning of the round, the running count was {}, and the total number of cards dealt was {}".format(runningcount, total_cards_dealt))
    
    cards_dealt = []
    
    for hand in player_split_hands:
        cards_dealt += hand
        
    cards_dealt += dealer
    
    current_round_running_count = 0
    
    for card in cards_dealt:
        if card in ['2','3','4','5','6']:
            current_round_running_count += 1
        if card in ['7','8','9']:
            current_round_running_count += 0
        if card in ['10','J', 'Q', 'K', 'A']:
            current_round_running_count -= 1
            
    runningcount = current_round_running_count + runningcount
            
    current_round_cards_dealt = len(cards_dealt)
    total_cards_dealt += current_round_cards_dealt
    total_unseen_cards = total_cards - total_cards_dealt
    unseen_decks = total_unseen_cards / 52 
    truecount = runningcount / unseen_decks
    
    print("The change in the running count for this round is {}".format(current_round_running_count))
    
    print("The running count is {}, and the number of unseen decks is {}, giving a true count of {}".format(runningcount, unseen_decks, truecount))
    
    return truecount, runningcount, total_cards_dealt


# In[27]:


def payout_loss_variable_bets(hand_outcome, decision):
    
    """Uses the outcome to calculate payoffs/losses, and decision of whether player has doubled down
    to update player's capital stock accordingly. """
    
    global capital_stock
    
    if hand_outcome == 0:
        if decision == 'D':
            new_capital = capital_stock[-1] - (2 * current_hand_bet)
            capital_stock.append(new_capital)
            print("Player loses " + str(2 * current_hand_bet) + " pounds from earlier doubling down.")
        else:
            new_capital = capital_stock[-1] - current_hand_bet
            capital_stock.append(new_capital)
            print("Player loses " + str(current_hand_bet) + " pounds.")
    
    elif hand_outcome == 1:
        if decision == 'D':
            new_capital = capital_stock[-1] + (2 * current_hand_bet)
            capital_stock.append(new_capital)
            print("Player wins " + str(2 * current_hand_bet) + " pounds from earlier doubling down.")
        else:
            new_capital = capital_stock[-1] + current_hand_bet
            capital_stock.append(new_capital)
            print("Player wins  " + str(current_hand_bet) + " pounds")
        
    elif hand_outcome == 2:
        new_capital = capital_stock[-1]
        capital_stock.append(new_capital)
        print("Draw, no change to player's initial capital.")
        
    else:
        new_capital = capital_stock[-1] + (1.5 * current_hand_bet)
        capital_stock.append(new_capital)
        print("Player blackjacks, house pays out " + str(1.5 * current_hand_bet) + " pounds.")
        
    print("Player now has" + " " + str(capital_stock[-1]) + " " + "pounds remaining.")
        
    return capital_stock


# In[28]:


def multiple_payout_loss_variable_bets(multiple_hand_outcome_list, decision_list):
    
    global capital_stock
    
    for hand_outcome, decision in zip(multiple_hand_outcome_list, decision_list):
    
        capital_stock = payout_loss_variable_bets(hand_outcome, decision)
    
    return capital_stock


# In[29]:


def clear_count_variables(truecount, runningcount, total_cards_dealt):
    
    truecount = 0
    runningcount = 0
    total_cards_dealt = 0
    
    return truecount, runningcount, total_cards_dealt


# In[30]:


def replenish_shoe_reset_counts(threshold):
    
    """Checks whether or not  we are near the end of a shoe. If so, discards the remaining cards in the current shoe,
    collects them together with remaining cards that were discarded in previous hands, reshuffles all of them togther,
    and finally replenishes the shoe.
    
    If the shoe is replenished, this module resets the true count, running count, and total number of cards dealt"""
    
    global deck
    global total_cards
    global shuffled_shoe
    
    global truecount
    global runningcount
    global total_cards_dealt
    
    global shoe_number
    
    fraction_cards_remaining = len(shuffled_shoe) / total_cards
    
    if fraction_cards_remaining < threshold:
        shuffled_shoe.clear
        deck, total_cards = getcards(decks=6)
        shuffled_shoe = shuffler(deck, total_cards)
        shoe_number += 1
        truecount, runningcount, total_cards_dealt = clear_count_variables(truecount, runningcount, total_cards_dealt)
        
        print("As we are reaching near the end of the shoe, we will reshuffle")
        print("As we have reshuffled, all card-counting variables are reset")
        print("=========================== SHOE {} ===========================".format(shoe_number))
        
    else:
        print("No need for reshuffling yet, as card threshold not reached")

    return shuffled_shoe


# In[ ]:


# Not sure how to implement this, and save logfile at the same time using > logfile.txt in command line.

# ensemble_realisations_basic_strategy = int(input("Enter how many times you want to run an independent 1000-hand simulation, using Basic Strategy, and fixed betting behaviour: "))
# ensemble_realisations_card_counting = int(input("Enter how many times you want to run an independent 1000-hand simulation, using HI-LO card counting, and variable betting behavior: "))


# In[5]:


# Instead I;m going to just save test values.

ensemble_realisations_basic_strategy = 2
ensemble_realisations_card_counting = 2


# In[ ]:


# Set random seed for running Basic Strategy simulator.

random.seed(21)


# In[ ]:


# Create a placeholder array that contains a number of 1000 hand trajectories/time-series of player capital stock,
# under Basic Strategy.
# This number of trajectories (rows) is a user-defined parameter, and determines the number of rows of the array.

ensemble_array_basic_strategy = np.zeros((ensemble_realisations_basic_strategy, 1000))


# In[ ]:


# Control flow for the Basic Strategy Simulator. 

for realisation in range(ensemble_realisations_basic_strategy):
    
    print("*************************REALISATION {}**********************************".format(realisation))
    
    initial_capital = 5000
    capital_stock = [initial_capital]
    bet_per_round = 5
    
    deck, total_cards = getcards(decks=6)
    shuffled_shoe = shuffler(deck, total_cards)
    
    print("Consistency check: {}".format(shuffled_shoe))
    
    shoe_number = 0
    
    print("=========================== SHOE {} ===========================".format(shoe_number))
    
    for iteration in range(1000):
        print("----------------------------- ROUND {} ---------------------------".format(iteration))
        player, dealer, player_blackjack = openinghand()
        print("Player's hand is {} and dealer's upcard is {}".format(player, dealer))
        decision = basic_player_multiple_hits(player, dealer, player_blackjack)

        if decision == 'Sp':
            player_split_hands = player_action_parent(player, decision)
            player_split_hands, decision_list, playerbust_indicator_list = player_multiple_turns(player_split_hands)
            playerscore_list = compute_multiple_playerscores(player_split_hands)
            dealer, dealerscore, dealerbust_indicator = dealerturn(dealer)
            multiple_hand_outcome_list = multiple_hand_outcomes(playerscore_list, dealerscore, playerbust_indicator_list, dealerbust_indicator, player_blackjack)
            capital_stock = multiple_payout_loss(multiple_hand_outcome_list, decision_list)
            shuffled_shoe = replenish_shoe(0.25)
        else:
            player = player_action(player, decision)
            player, decision, playerbust_indicator = player_turn(player, decision)
            playerscore = compute_playerscore(player)
            dealer, dealerscore, dealerbust_indicator = dealerturn(dealer)
            hand_outcome = handoutcome(playerscore, dealerscore, playerbust_indicator, dealerbust_indicator, player_blackjack)
            capital_stock = payout_loss(hand_outcome, decision)
            shuffled_shoe = replenish_shoe(0.25)
    
    capital_stock_array = np.array(capital_stock[:1000])
    ensemble_array_basic_strategy[realisation, :] = capital_stock_array


# In[ ]:


np.savetxt("BS_simulation", ensemble_array_basic_strategy, delimiter=',')


# In[ ]:


# Set random seed for running the card counting simulator.

random.seed(21)


# In[ ]:


# Create a placeholder array that contains a number of 1000 hand trajectories/time-series of player capital stock,
# under HI-LO Card Counting.
# This number of trajectories (rows) is a user-defined parameter, and determines the number of rows of the array.

ensemble_array_card_counting = np.zeros((ensemble_realisations_card_counting, 1000))


# In[34]:


# Control flow for the Hi-LO Card Counting Simulator. 

for realisation in range(ensemble_realisations_card_counting):
    
    print("*************************REALISATION {}**********************************".format(realisation))
    
    initial_capital = 5000
    capital_stock = [initial_capital]
    bet_per_round = 5

    truecount = 0
    total_cards_dealt = 0
    runningcount = 0
    
    deck, total_cards = getcards(decks=6)
    shuffled_shoe = shuffler(deck, total_cards)
    
    print("Consistency check: {}".format(shuffled_shoe))
    
    shoe_number = 0
    
    print("=========================== SHOE {} ===========================".format(shoe_number))

    for iteration in range(1000):
        print("----------------------------- ROUND {} ---------------------------".format(iteration))
        current_hand_bet = player_bets(truecount, total_cards_dealt)
        player, dealer, player_blackjack = openinghand()
        print("Player's hand is {} and dealer's upcard is {}".format(player, dealer))
        decision = basic_player_multiple_hits(player, dealer, player_blackjack)

        if decision == 'Sp':
            player_split_hands = player_action_parent(player, decision)
            player_split_hands, decision_list, playerbust_indicator_list = player_multiple_turns(player_split_hands)
            playerscore_list = compute_multiple_playerscores(player_split_hands)
            dealer, dealerscore, dealerbust_indicator = dealerturn(dealer)
            truecount, runningcount, total_cards_dealt = multiple_hand_update_truecount(player_split_hands, dealer, runningcount, total_cards_dealt)
            multiple_hand_outcome_list = multiple_hand_outcomes(playerscore_list, dealerscore, playerbust_indicator_list, dealerbust_indicator, player_blackjack)
            capital_stock = multiple_payout_loss_variable_bets(multiple_hand_outcome_list, decision_list)
            shuffled_shoe = replenish_shoe_reset_counts(0.25)
        else:
            player = player_action(player, decision)
            player, decision, playerbust_indicator = player_turn(player, decision)
            playerscore = compute_playerscore(player)
            dealer, dealerscore, dealerbust_indicator = dealerturn(dealer)
            truecount, runningcount, total_cards_dealt = update_truecount(player, dealer, runningcount, total_cards_dealt)
            hand_outcome = handoutcome(playerscore, dealerscore, playerbust_indicator, dealerbust_indicator, player_blackjack)
            capital_stock = payout_loss_variable_bets(hand_outcome, decision)
            shuffled_shoe = replenish_shoe_reset_counts(0.25)
            
    capital_stock_array = np.array(capital_stock[:1000])
    ensemble_array_card_counting[realisation, :] = capital_stock_array 


# In[ ]:


np.savetxt("CC_simulation", ensemble_array_card_counting, delimiter=',')

