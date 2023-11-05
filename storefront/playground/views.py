from django.shortcuts import render
from .models import *
from django.http import StreamingHttpResponse
import cv2 as cv
from . import utils
from . import game
import threading
import numpy as np
import time

# Create your views here.
# request handler
def description(request):
    return StreamingHttpResponse(gen_text(b), content_type="text/plain")

def video_feed(request):
    return StreamingHttpResponse(gen(b), content_type="multipart/x-mixed-replace;boundary=frame")
def index(request):
    return render(request, 'blackjack.html')

def game_feed(request):
    return StreamingHttpResponse(gen_game(b), content_type="multipart/x-mixed-replace;boundary=frame")

class BlackJack(object):
    def __init__(self):
        self.cap = cv.VideoCapture(0)
        self.key_gestures = utils.initialize_key_gestures()
        self.taking_input = False
        self.skin_lower = np.array([80, 135, 85], dtype="uint8")
        self.skin_upper = np.array([200, 200, 150], dtype="uint8")
        self.thisgame = game.Game(self.key_gestures, [[],[]], [], [])
        self.game_frame = self.thisgame.display()
        self.vid_frame_width = 500
        _, img = self.cap.read()
        self.vid_frame_height = int( self.vid_frame_width/img.shape[1] * img.shape[0] )
        print(self.vid_frame_height)
        threading.Thread(target=self.round, args=()).start()
    def __del__(self):
        self.cap.release()
    def get_vid_frame(self):
        if not self.taking_input:
            _, self.frame = self.cap.read()
        img = self.frame
        resize = cv.resize(img, (self.vid_frame_width, self.vid_frame_height), interpolation=cv.INTER_LINEAR)
        _, jpeg = cv.imencode('.jpg', resize)
        return jpeg.tobytes()
    def get_game_frame(self):
        img = self.game_frame
        resize = cv.resize(img, (480, 640), interpolation=cv.INTER_LINEAR)
        _, jpeg = cv.imencode('.jpg', resize)
        return jpeg.tobytes()
    def get_description(self):
        return str(self.taking_input)
    def update_game_display(self, text="", pause=1):
        self.game_frame = self.thisgame.display(text)
        time.sleep(pause)
    def round(self):
        while True:
            #player's turn
            scores, _ = self.player_round()
            if sum(scores) > 0: # if there is any unbusted playable set left
                #dealer's turn
                dealer_score = self.dealer_round()
                for s in range(len(scores)):
                    if scores[s] > dealer_score:
                        self.update_game_display("Player" + str(s+1) + " WIN!", 2)
                    else:
                        self.update_game_display("Player" + str(s+1) + " LOOSE", 2)
                self.update_game_display("end of round", 1)
            self.update_game_display("Good game. I hope to play with you again.")
            # start a new round
            self.thisgame = game.Game(self.key_gestures, [[],[]], [], [])
    def get_player_input(self):
        gis = utils.GestureIdentifierSystem(self.key_gestures)
        player_move = None
        self.taking_input = True
        while player_move == None:
            _, img = self.cap.read()
            self.frame, player_move = gis.process_gesture(img)
        self.taking_input = False
        return player_move
    def dealer_round(self):
        self.thisgame.dealer_card_show = True
        while utils.calculate_score(self.thisgame.dealer_cards) < 16:
            self.thisgame.dealer_cards.append(self.thisgame.deck.pop())
            self.update_game_display()
        dealer_score = utils.calculate_score(self.thisgame.dealer_cards)
        if dealer_score > 21:
            self.update_game_display("Dealer Busted")
            dealer_score = 0
        return dealer_score
    def player_round(self):
        scores = []
        self.update_game_display("Player move: ", 0)
        player_move = self.get_player_input()
        self.update_game_display("Player move: " + player_move)
        while True:
            while player_move == "hit":
                self.thisgame.deal_player()
                self.update_game_display()
                curr_score = utils.calculate_score(self.thisgame.player_cards[self.thisgame.curr_player])
                if curr_score > 21:
                    self.update_game_display("Player Busted. You Loose", 2)
                    return [0], self.thisgame.deck
                self.update_game_display("Player move: ", 0)

                player_move = self.get_player_input()

                self.update_game_display("Player move: " + player_move)
            if player_move == "stand":
                return [utils.calculate_score(self.thisgame.player_cards[self.thisgame.curr_player])], self.thisgame.deck
            elif player_move == "doubledown" and len(self.thisgame.player_cards[self.thisgame.curr_player]) == 2:
                self.update_game_display("Betsize is doubled. This is your last card. Good luck.")
                self.thisgame.deal_player()
                self.update_game_display()
                curr_score = utils.calculate_score(self.thisgame.player_cards[self.thisgame.curr_player])
                if curr_score > 21:
                    self.update_game_display("Player Busted. You Loose", 2)
                    return [0], self.thisgame.deck
                else:
                    scores.append(utils.calculate_score(self.thisgame.player_cards[self.thisgame.curr_player]))
                    return scores, self.thisgame.deck
            elif player_move == "split" and self.thisgame.num_of_player == 1 and len(self.thisgame.player_cards[0]) == 2 and \
                    self.thisgame.player_cards[0][0][1] == self.thisgame.player_cards[0][1][1]:
                self.thisgame.num_of_player = 2
                self.thisgame.player_cards[1] = [self.thisgame.player_cards[0][1]]
                self.thisgame.player_cards[0] = [self.thisgame.player_cards[0][0]]
                self.thisgame.deal_first_two_cards()
                score1, self.thisgame.deck = self.player_round()
                self.thisgame.curr_player = 1
                self.thisgame.deal_first_two_cards()

                score2, self.thisgame.deck = self.player_round()
                scores = [score1[0], score2[0]]
                return scores, self.thisgame.deck
            else:
                self.update_game_display("Illegal move. Please Choose another move.")
                self.update_game_display("Player move: ", 0)
                player_move = self.get_player_input()
                self.update_game_display("Player move: " + player_move)
def gen(cam):
    while True:
        frame = cam.get_vid_frame()
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
def gen_game(cam):
    while True:
        frame = cam.get_game_frame()
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
def gen_text(cam):
    while True:
        txt = cam.get_description()
        yield (f'{txt}')
# Initialize BlackJack Game!
b = BlackJack()