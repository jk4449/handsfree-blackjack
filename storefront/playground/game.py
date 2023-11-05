import cv2 as cv
from random import shuffle
import numpy as np
from . import utils

class Game:
    def __init__(self, key_gestures, p_cards=[[],[]], d_cards=[], deck=[]): #empty list if you wanna start fresh.
        # new deck
        self.dealer_card_show = False
        self.num_of_player = 1
        self.curr_player = 0
        self.blank_card_img = cv.imread("playground/PlayingCards/blank_card.png", cv.IMREAD_COLOR)
        self.text_box_img = cv.imread("playground/PlayingCards/text_box.png", cv.IMREAD_COLOR)
        self.back_img = cv.imread("playground/PlayingCards/back.png", cv.IMREAD_COLOR)
        numbers = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]
        suits = ["hearts", "clubs", "diamonds", "spades"]
        if len(deck) == 0:
            self.deck = []
            for s in suits:
                for n in numbers:
                    self.deck.append([s, n])
            shuffle(self.deck)
        else:
            self.deck = deck
        self.display_text = ""
        self.player_cards = p_cards
        self.dealer_cards = d_cards
        self.deal_first_two_cards()
    def deal_player(self):
        self.player_cards[self.curr_player].append(self.deck.pop())
    def deal_dealer(self):
        self.dealer_cards.append(self.deck.pop())
    def deal_first_two_cards(self):
        bc = False
        if len(self.dealer_cards) == 0:
            bc = True
            self.dealer_cards.append(["blank", "card"])
        while len(self.player_cards[self.curr_player]) < 2:
            self.deal_player()
        if bc == True:
            self.dealer_cards.pop()
            self.deal_dealer()
            self.deal_dealer()
        else:
            while len(self.dealer_cards) < 2:
                self.deal_dealer()
    def player_score(self):
        return utils.calculate_score(self.player_cards[self.curr_player])
    def display(self, text=""):
        max_length = max(len(self.player_cards[0]), len(self.player_cards[1]), len(self.dealer_cards))
        player_cards_img = utils.card_to_image(self.player_cards[0][0])
        for i in range(1, max_length):
            if i < len(self.player_cards[0]):
                player_cards_img = np.concatenate((player_cards_img, utils.card_to_image(self.player_cards[0][i])), axis=1)
            else:
                player_cards_img = np.concatenate((player_cards_img, self.blank_card_img), axis=1)
        if self.num_of_player == 2:
            second_player_cards_img = utils.card_to_image(self.player_cards[1][0])
            for i in range(1, max_length):
                if i < len(self.player_cards[1]):
                    second_player_cards_img = np.concatenate((second_player_cards_img, utils.card_to_image(self.player_cards[1][i])), axis=1)
                else:
                    second_player_cards_img = np.concatenate((second_player_cards_img, self.blank_card_img), axis=1)

            player_cards_img = np.concatenate((player_cards_img, second_player_cards_img), axis=0)

        dealer_cards_img = utils.card_to_image(self.dealer_cards[0])
        for i in range(1, max_length):
            if i < len(self.dealer_cards):
                if self.dealer_card_show:
                    dealer_cards_img = np.concatenate((dealer_cards_img, utils.card_to_image(self.dealer_cards[i])), axis=1)
                else:
                    dealer_cards_img = np.concatenate((dealer_cards_img, self.back_img), axis=1)
            else:
                dealer_cards_img = np.concatenate((dealer_cards_img, self.blank_card_img), axis=1)

        text_box_imgs = self.text_box_img
        for i in range(1, max_length):
            text_box_imgs = np.concatenate((text_box_imgs, self.text_box_img), axis=1)

        img = np.concatenate((player_cards_img, dealer_cards_img, text_box_imgs), axis=0)

        cv.putText(img, "Player" + str(self.curr_player + 1) + "'s Score: " + str(utils.calculate_score(self.player_cards[self.curr_player])), (10, 360+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)

        #outline curr green
        if self.dealer_card_show:
            cv.rectangle(img, (0, 330 * 2), (img.shape[1], 330 + 330 * 2), (0, 255, 0), 2)
        else:
            cv.rectangle(img, (0, 330 * self.curr_player), (img.shape[1], 330 + 330 * self.curr_player), (0, 255, 0), 2)
        #outline cards red if the player lost or is losing
        if utils.calculate_score(self.player_cards[0]) > 21 or (self.dealer_card_show and utils.calculate_score(self.player_cards[0]) < utils.calculate_score(self.dealer_cards)):
            cv.rectangle(img, (0, 0), (img.shape[1], 330), (0, 0, 255), 2)
        if self.num_of_player == 2:
            if utils.calculate_score(self.player_cards[1]) > 21 or (self.dealer_card_show and utils.calculate_score(self.player_cards[0]) < utils.calculate_score(self.dealer_cards)):
                cv.rectangle(img, (0, 330), (img.shape[1], 660), (0, 0, 255), 2)

        if self.dealer_card_show:
            cv.putText(img, "Dealer's Score: " + str(utils.calculate_score(self.dealer_cards)), (10, 380+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
            cv.putText(img, "Dealer's Turn", (10, 400+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
        else:
            cv.putText(img, "Dealer's Score: unknown", (10, 380+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
            cv.putText(img, "Player" + str(self.curr_player + 1) + "'s Turn", (10, 400+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 0), 1, cv.LINE_AA)

        cv.putText(img, text, (10, 420+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
        return img
    