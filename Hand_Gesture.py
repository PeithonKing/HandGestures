import cv2 # for capturing the video from desired source
import mediapipe as mp # for tracking the hand positions
from pyfirmata import Arduino, util # communicating with arduino

# Initializing Arduino board
board = Arduino("COM5")
it = util.Iterator(board)
it.start()

# Capturing the video
cap = cv2.VideoCapture(0) # 0 denotes the first camera attached to my system

# Initializing mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# keeping track of the button position
state = 0

def dist(hand, n, m, colour = (0,0,255), size = 15):
    '''finding distance between two points on hand'''
    global img
    x1, y1 = hand[n][0], hand[n][1]
    x2, y2 = hand[m][0], hand[m][1]
    cv2.circle(img, (x1, y1), size, colour, cv2.FILLED)
    cv2.circle(img, (x2, y2), size, colour, cv2.FILLED)
    dely = y2 - y1
    delx = x2 - x1
    sq = delx**2 + dely**2
    return sq**0.5

while True:
    success, img = cap.read() # Dealing with images from the footage
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # because cv2 gives BGR and mp takes RGB
    results = hands.process(imgRGB) # detecting hand in image

    if results.multi_hand_landmarks: # if hand is detected
        handLms = results.multi_hand_landmarks[0] # always go for a single hand more
        # precisely the first one, and leave all other hands (if multiple hands are detected)
        hand = {}
        for id, lm in enumerate(handLms.landmark):
            h, w, c = img.shape # have to do this because lm.x and lm.y are just ratios
            hand[id] = (int(lm.x*w), int(lm.y*h)) # and then do this to get actual pixels
            
        # print(hand)
        mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
        # try commenting out the above line and note the difference

        # I guess u can undestand the rest urself... can't you?
        # Just determining gestures by relative distance between parts of hand
        d = dist(hand, 0, 8, (225,0,0), 20)
        dc = dist(hand, 0, 5)
        # print(d/dc)
        if (d/dc) > 1.3:
            if state == 0:
                print("Switching on!\n")
                board.digital[13].write(1)
                state = 1
        else:
            if state == 1:
                print("Switching off!\n")
                board.digital[13].write(0)
                state = 0
    
    # showing the captured video
    # cv2.imshow("capture", img)
    # cv2.waitKey(1)
