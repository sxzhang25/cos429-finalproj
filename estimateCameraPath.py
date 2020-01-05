##
# COS 429 Final Project
# Sharon Zhang
#
# This module estimates the actual camera path.
#

import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys

class Window():
    """
    A pop-up window with the video frame for user to select crop window
    """
    
    def __init__(self, img):
        self.count = 0
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.points = []

    def getCoords(self):
        if self.count >= 2:
            plt.close()
            return
        fig = plt.figure()
        plt.title('Select crop box')
        plt.imshow(self.img)
        cid = fig.canvas.mpl_connect('button_press_event', self.__onclick__)
        plt.show()
        return self.points

    def __onclick__(self,click):
        self.points.append((click.xdata, click.ydata))
        self.count += 1

def estimateTransforms(orig_frames):
    """
    Given a sequence of video frames, estimate the camera path transforms between
    each consecutive pair of frames

    orig_frames: an array of images
    """

    # extract SIFT features and compute optical flow
    sift_fg = cv2.xfeatures2d.SIFT_create(50)
    sift_bg = cv2.xfeatures2d.SIFT_create(150)
    bf = cv2.BFMatcher()
    transforms = []

    for num in range(1, len(orig_frames)):
        if (num % 10 is 1):
            print("frame", num-1, "-> frame", num, "(of {})".format(count-1))

        # get current and previous frame
        f_curr = cv2.cvtColor(orig_frames[num], cv2.COLOR_BGR2GRAY)
        f_prev = cv2.cvtColor(orig_frames[num-1], cv2.COLOR_BGR2GRAY)

        # get foreground/background masks
        _, fg_mask1 = cv2.threshold(f_prev, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        _, bg_mask1 = cv2.threshold(f_prev, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        _, fg_mask2 = cv2.threshold(f_curr, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        _, bg_mask2 = cv2.threshold(f_curr, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # compute SIFT features in foreground and background
        kp2, des2 = sift_fg.detectAndCompute(f_curr, fg_mask2)
        kp1, des1 = sift_fg.detectAndCompute(f_prev, fg_mask1)

        kp2_bg, des2_bg = sift_bg.detectAndCompute(f_curr, bg_mask2)
        kp1_bg, des1_bg = sift_bg.detectAndCompute(f_prev, bg_mask1)

        if len(kp2) > 0 and len(kp2_bg) > 0:
            kp2 = np.concatenate((kp2,kp2_bg), axis=0)
        elif not kp2:
            kp2 = kp2_bg

        if len(kp1) > 0 and len(kp1_bg) > 0:
            kp1 = np.concatenate((kp1,kp1_bg), axis=0)
        elif not kp1:
            kp1 = kp1_bg

        if des2 is not None and des2_bg is not None:
            des2 = np.concatenate((des2,des2_bg), axis=0)
        elif not des2:
            des2 = des2_bg

        if des1 is not None and des1_bg is not None:
            des1 = np.concatenate((des1,des1_bg), axis=0)
        elif not des1:
            des1 = des1_bg

        # extract good feature matches
        matches = bf.knnMatch(des1, des2, k=2)

        # print('Before filtering:', len(matches))
        good = []
        for m,n in matches:
            if m.distance < 0.25*n.distance:
                good.append(m)
        # print('After filtering:', len(good))

        pts_dst = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
        pts_src = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)

        # calculate optical flow
        if len(pts_dst) > 0 and len(pts_src) > 0:
            M = cv2.estimateRigidTransform(pts_src, pts_dst, fullAffine=False)

        if M is not None:
            transforms.append(M)
        else:
            if num > 1:
                transforms.append(transforms[-1])
            else:
                CONST_TRANSFORM = np.zeros((2,3))
                CONST_TRANSFORM[0,0] = 1
                CONST_TRANSFORM[1,1] = 1
                transforms.append(CONST_TRANSFORM)

    print("Finished analyzing {} frames".format(num))
    return transforms

# store original frames
videoname = sys.argv[1]

vidcap = cv2.VideoCapture(videoname)
success, img = vidcap.read()
height, width, ch = img.shape

# input bounding box
win = Window(img)
ul, lr = win.getCoords()

count = 0
success = True
orig_frames = []
while success:
    orig_frames.append(img)
    count += 1
    success, img = vidcap.read()
    if not success:
        print ('Failed on frame', count)

print('Finished reading {} frames'.format(count-1))

# estimate camera path transforms
transforms = estimateTransforms(orig_frames)

# record video information
f = open('{}_info.txt'.format(videoname.split('.')[0]), 'w')
f.write('{}\n'.format(count-1)) # total frames
f.write('{} {}\n'.format(width, height)) # video dimensions
f.write('{} {}\n'.format( int(ul[0]), int(ul[1]) )) # ul
f.write('{} {}\n'.format( int(lr[0]), int(lr[1]) )) # lr

# write estimated transforms to file
f = open('{}_estTransforms.txt'.format(videoname.split('.')[0]), 'w')
for i in range(len(transforms)):
    cp = transforms[i]
    f.write('{} {} {} {} {} {}\n'.format(cp[0,2], cp[1,2], cp[0,0], cp[0,1], cp[1,0], cp[1,1]))

# plot estimated camera path
Ct = np.identity(3)
motion = np.zeros((len(transforms),2))
for i in range(len(transforms)):
    Ct = Ct @ np.concatenate((transforms[i], [[0,0,1]]), axis=0)
    motion[i,:] = Ct[:2,2]

plt.figure()
plt.plot([i for i in range(len(transforms))], motion[:,0])
plt.title("x motion")
plt.show()

plt.figure()
plt.plot([i for i in range(len(transforms))], motion[:,1])
plt.title("y motion")
plt.show()
