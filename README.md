# handsfree-blackjack
WebApp where people can play blackjack with hand gestures. No click/keyboard input necessary!

Recognizable Gestures

• Hit: Double tap (vertical Up-Down-Up-Down motion)

• Stand: Horizontal hand wave (horizontal Left-Right-Left-Right motion)

• Double Down: make number 1 with the index finger, and point the finger down towards the table and hold the pose.

• Split: Same as double-down but use index and middle finger to make an inverted V shape.

The system works in most settings where there is sufficient light, background is
stationary, and the color of the table and the background is not too similar to the
user’s skin color. One way to ensure that the system works well is to turn off the
lights in the room, block natural lights, and only have one light source (ex. lamp) that
shines the light at the user’s hand. User can also check if the system is working well.
The user can adjust the background and lights to make sure that the
green rectangle shows up around their hand.

**Double Down Recognition Function**

This is the function used to recognize “Double Down”

Accept if all 4 criteria are met:

1. Currently identified hand contour is closest to an example of “double down” contour.
2. The difference between the current hand contour and that example is below a threshold
(key_gesture_threshold).
3. The previous two criteria has been met for a threshold (stay_still_threshold) amount of time.
4. User’s hand has not been moving for a threshold (stay_still_threshold) amount of time.

**Split Recognition Function**

This is the function used to recognize “Split”. It is very similar to “Double Down”. The two gesture uses a different
key_gesture_threshold.

Accept if all 4 criteria are met:
1. Currently identified hand contour is closest to an example of “split” contour.
2. The difference between the current hand contour and that example is below a threshold
(key_gesture_threshold).
3. The previous two criteria has been met for a threshold (stay_still_threshold) amount of time.
4. User’s hand has not been moving for a threshold (stay_still_threshold) amount of time.

**Finding the Closest Hand Contour**

I noticed that the system does not recognize the gesture well if the wrist is slightly turned to a different angle, etc.
Therefore, I made it so that the system records 3 contours for each gesture: one with low angle, one with medium
angle, and one with high angle. All three should be facing the camera directly, and any attempted gestures must
face the camera directly as well for better recognition. When finding the closest hand contour, the system would
simply search through all recorded capture and if one of the three “split” happens to be the closest, it will return
“split” and vice versa.

**Key Gesture Thresholds**
Key gesture threshold is used in the identification of “split” and “double down”. A function (cv2.matchShape) is
called to compare the difference between the real-time hand pose and key gestures that we are looking for (“split”
and “double down”). If the difference is smaller than a threshold, the real-time hand pose can be identified as that
key gesture. If multiple key gestures are under the threshold, the real-time hand pose is identified as the one with
the smallest difference. If none of the key gestures are under the threshold, the real-time hand pose is identified as
“none”.
The system was first built using the same threshold for all key gestures. However, I noticed that some gestures are
harder to be recognized than others. Therefore, I conducted a small survey. 

I gestured “double down” in various ways rotating my wrist, and recorded its difference to the “double down”
contour. All datapoint fell below difference of 0.12. Therefore, I decided to make the key_gesture_threshold for “double down” 0.12.

Split was more difficult to recognize. I was able to vary not only the wrist, but the distance between the two
fingers. The little twists and small adjustments made the split difference higher on average. Since most points fell 
under difference of 0.15, I decided to make the threshold 0.15.

**Stay Still Threshold**
For a stationary gesture to be recognized, the hand pose should stay still for Stay Still Threshold amount of time.
The threshold should not be too short that it recognizes a gesture that it not intended to be recognized, nor too
long that it makes the user wait too much. I determined this threshold by first setting it to about 2 seconds, and
gradually lowering it while using the system. I stopped lowering the threshold when the system recognized a
stationary gesture when I was not completely still posing and waiting for it. 

**Hand Dir Threshold**
Hand direction is recognized when the user moved their hand “significantly” from their last position. I computed the
movement from position A to position B by the movement in the center point of the bounding rectangle of their
hand contour. That “significantly” is determined by this threshold. When I was testing the system by myself, I would
move my hands precisely, so the system worked well with low hand dir threshold of 20. However, when I was
testing the system, I noticed that many people struggled because while they move their hand vertically, gesturing
“hit”, it was often recognized as “stand” since the vertical movement of the hand usually accompanied horizontal
movement. Therefore, I decided to make two different threshold for detecting vertical movement and horizontal
movement, and set the horizontal hand direction threshold to 40. When I made this change, a participant who
could only get the system to correctly recognize “hit” 1 out of 10 times was now able to get the system to correctly
recognize “hit” 10 out of 10 times, and “stand” 10 out of 10 times. 

**Hand Going Up/Down/Left/Right?**

The “hand going up/down/left/right?” decision function in the flow charts above utilizes the information of past
record of hand directions. If the vertical direction was “up” 95% of the times in the past hit_time threshold
records, and if the horizontal direction was not “left” nor “right” 70% of the times in the past hit_time threshold
records, the system will say that the hand was going up. Vice versa for “down”. However, for “hand going left/
right”, the system will not check if there was a vertical component to the movement. This is because by observing
the participants, I noticed that it is very hard to not move vertically while moving horizontally, especially since the
hand is off the table. Also, the shape of your hand changes during the gesture “stand” which means that there is
movement of the center of the hand contour independent of the hands’s movement. The hand direction is largely
dependent in the center point of the hand contour, so it is very rare for even the intended “stand” to have no
vertical movement component. Below is a capture of intended “stand”. We can see that the center of the
bounding rect moves up as the hand moves the the right.

**Skin Recognition Threshold**
Last but not least, one the most important part of the algorithm is accurate hand detection. Research by Shaik,
Khamar Basha, et al.[1] show that it is more efficient to work in the YCbCr color space than the RGB color space.
YCbCr color space does not mix the color with intensity, and hence can have better skin detection under uneven
lighting conditions. Therefore, I worked in the YCbCr color space to detect skin in this project. Research by Kolkur,
S., et al.[2] has come up with a well performing threshold for human skin detection. I have used their YCbCr color
space lower bound, and came up with my own YCbCr color space upper bound after trial and error. The
thresholds are as follows: skin_lower = \[80, 135, 85\], skin_upper = \[200, 200, 150\].

[1] Shaik, Khamar Basha, et al. “Comparative Study of Skin Color Detection and Segmentation in HSV and Ycbcr
Color Space.” Procedia Computer Science, vol. 57, 2015, pp. 41–48., https://doi.org/10.1016/
j.procs.2015.07.362.
[2] Kolkur, S., et al. “Human Skin Detection Using RGB, HSV and YCbCr Color Models.” Proceedings of the
International Conference on Communication and Signal Processing 2016 (ICCASP 2016), 2017, pp. 324–332.,
https://doi.org/10.2991/iccasp-16.2017.51.

