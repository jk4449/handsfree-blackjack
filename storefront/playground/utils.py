import cv2 as cv
import numpy as np

def card_to_image(card):
    img_name = card[0] + "_" + card[1] + ".png"
    img_path = "playground/PlayingCards/" + img_name
    img = cv.imread(img_path, cv.IMREAD_COLOR)
    return img

def card_to_string(card):
    return str(card[1]) + " of " + str(card[0])

def calculate_score(cards):
    score = 0
    num_of_A = 0
    for card in cards:
        if card == ["blank", "card"]:
            score += 0
        elif card[1] == "ace":
            score += 1
            num_of_A += 1
        elif card[1] == "king" or card[1] == "queen" or card[1] == "jack":
            score += 10
        else:
            score += int(card[1])
    if num_of_A > 0 and score <= 11:
        score += 10
    return score
def largest_contour(c_lst):
    # returns the contour with the largest area from a list of contours.
    l_area = 0
    l_cnt = None
    for c in c_lst:  # go through all contours in the list
        area = cv.contourArea(c)
        if area > l_area:  # if the area of the current contour is the largest encountered
            l_area = area  # set this area as the largest
            l_cnt = c  # set this contour as the largest contour
    return l_cnt  # return the largest contour

def find_hand_direction(center_x, center_y, handloc_hist, thresh_v, thresh_h):
    if handloc_hist[0][0] > center_x + thresh_h:
        direction_v = "left"
    elif handloc_hist[0][0] + thresh_h < center_x:
        direction_v = "right"
    else:
        direction_v = "none"

    if handloc_hist[0][1] > center_y + thresh_v:
        direction_h = "up"
    elif handloc_hist[0][1] + thresh_v < center_y:
        direction_h = "down"
    else:
        direction_h = "none"
    return (direction_v, direction_h)

def find_contour(frame):
    skin_lower = np.array([80, 135, 85], dtype="uint8")
    skin_upper = np.array([200, 200, 150], dtype="uint8")
    converted = cv.cvtColor(frame, cv.COLOR_BGR2YCR_CB)
    skinMask = cv.inRange(converted, skin_lower, skin_upper)
    img_contours, _ = cv.findContours(skinMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    return largest_contour(img_contours)

def percentage(dir_lst, dir): #percentage of dir in dir_list
    if len(dir_lst) == 0:
        return 0
    count = 0
    for i in range(len(dir_lst)):
        if dir_lst[i] == dir:
            count += 1
    return count / len(dir_lst)

def percentage_e(dir_lst, dir, e): #percentage of dir in position e of dir_list
    if len(dir_lst) == 0:
        return 0
    count = 0
    for i in range(len(dir_lst)):
        if dir_lst[i][e] == dir:
            count += 1
    return count / len(dir_lst)

def find_closest_key_gesture(img_contour, key_gestures, key_gesture_threshold):
    min_diff = 1
    closest_match = -1  # index of the closest match.
    for i in range(len(key_gestures)):
        for example in key_gestures[i]:
            diff = cv.matchShapes(img_contour, example, cv.CONTOURS_MATCH_I1, 0) - key_gesture_threshold[i]
        if diff < min_diff:
            min_diff = diff
            closest_match = i
    return min_diff, closest_match

def initialize_key_gestures():
    dd_img_name = ["doubledown0.jpg", "doubledown1.jpg", "doubledown2.jpg"]
    sp_img_name = ["split0.jpg", "split1.jpg", "split2.jpg"]
    skin_lower = np.array([80, 135, 85], dtype="uint8")
    skin_upper = np.array([200, 200, 150], dtype="uint8")
    img_path = "playground/Ref_Images/"
    key_gestures = [[],[]]
    for i in range(3):
        img = cv.imread(img_path + dd_img_name[i], cv.IMREAD_GRAYSCALE)
        img_contours, _ = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        key_gestures[0].append(largest_contour(img_contours))
    for i in range(3):
        img = cv.imread(img_path + sp_img_name[i], cv.IMREAD_GRAYSCALE)
        img_contours, _ = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        key_gestures[1].append(largest_contour(img_contours))
    return key_gestures
         
class GestureIdentifierSystem:
    def __init__(self, key_gestures):
        self.key_gestures = key_gestures
        self.key_gesture_name = ["doubledown", "split"]
        self.handloc_memory = 5
        self.directions_memory = 20
        self.key_gesture_threshold = [0.12, 0.15]
        self.stay_still_threshold = 0.8
        self.handloc_hist = [(0, 0) for i in range(self.handloc_memory)]
        self.direction_hist = ["none" for i in range(self.directions_memory)]
        self.gesture_hist = ["none" for i in range(self.directions_memory)]
        self.no_movement_thresh = 10
        self.curr_key_gesture = "none"
        self.hit_stage = 0  # 0, 1, 2, 3, 4
        self.stand_stage = 0  # 0, 1, 2, 3, 4
        self.player_input = None
        self.hand_dir_v_thresh = 20
        self.hand_dir_h_thresh = 40
        self.stand_time_thresh = 4
        self.hit_time_thresh = 3
        
    def process_gesture(self, frame):
        player_input = None
        debug_frame = frame.copy()

        img_contour = find_contour(debug_frame)  # find hand contour
        # Draw a rect.
        x, y, w, h = cv.boundingRect(img_contour)
        center_x, center_y = x + w // 2, y + h // 2
        cv.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
        cv.circle(debug_frame, (center_x, center_y), 2, (0, 0, 255), 2)

        # Find closest key gesture
        min_diff, closest_match = find_closest_key_gesture(img_contour, self.key_gestures, self.key_gesture_threshold)
        # Is the closest key gesture is close enough?
        if min_diff < self.key_gesture_threshold[closest_match]:
            curr_key_gesture = self.key_gesture_name[closest_match]  # update curr gesture
            cv.putText(debug_frame, curr_key_gesture + ": " + str(min_diff), (10, 110),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv.LINE_AA)
        else:
            curr_key_gesture = "none"
            cv.putText(debug_frame, self.key_gesture_name[closest_match] + ": " + str(min_diff), (10, 110),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv.LINE_AA)
        # identify double down
        if curr_key_gesture == "doubledown":
            if percentage(self.gesture_hist, "doubledown") == 1 and percentage(self.direction_hist, ("none", "none")) > self.stay_still_threshold:
                player_input = "doubledown"
        # identify split
        elif curr_key_gesture == "split":
            if percentage(self.gesture_hist, "split") == 1 and percentage(self.direction_hist, ("none", "none")) > self.stay_still_threshold:
                player_input = "split"

        # identify hit
        if percentage_e(self.direction_hist[-self.hit_time_thresh:], "up", 1) > 0.95 and percentage(self.direction_hist[-self.hit_time_thresh:], ("none", "up")) > 0.7:
            if self.hit_stage == 0 or self.hit_stage == 2:
                self.hit_stage += 1
        elif percentage_e(self.direction_hist[-self.hit_time_thresh:], "down", 1) > 0.95 and percentage(self.direction_hist[-self.hit_time_thresh:], ("none", "down")) > 0.7:
            if self.hit_stage == 1:
                self.hit_stage += 1
            elif self.hit_stage >= 3:
                player_input = "hit"

        # identify stand
        if percentage_e(self.direction_hist[-self.stand_time_thresh:], "left", 0) > 0.8:
            if self.stand_stage == 0 or self.stand_stage == 2:
                self.stand_stage += 1
        elif percentage_e(self.direction_hist[-self.stand_time_thresh:], "right", 0) > 0.8:
            if self.stand_stage == 1:
                self.stand_stage += 1
            elif self.stand_stage >= 3:
                player_input = "stand"

        #reset stand and hit stage to 0 if there is no movement
        if percentage(self.direction_hist[-self.no_movement_thresh:], ("none", "none")) > 0.8:
            self.hit_stage = 0
            self.stand_stage = 0
        cv.putText(debug_frame, "hitstage: " + str(self.hit_stage), (10, 330), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv.LINE_AA)
        cv.putText(debug_frame, "standstage: " + str(self.stand_stage), (10, 360), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv.LINE_AA)

        # Find Hand direction
        direction = find_hand_direction(center_x, center_y, self.handloc_hist, self.hand_dir_v_thresh, self.hand_dir_h_thresh)

        # update history
        self.direction_hist.pop(0)
        self.direction_hist.append(direction)

        self.handloc_hist.pop(0)
        self.handloc_hist.append((center_x, center_y))

        self.gesture_hist.pop(0)
        self.gesture_hist.append(curr_key_gesture)
        #display camera if debugging
        return debug_frame, player_input