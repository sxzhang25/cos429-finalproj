##
# COS 429 Final Project
# Sharon Zhang
#
# This module uses the optimal transforms to create the stabilized video.
#

import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import sys

def writeStableVideo(videoname, optTransforms, vidsize, ul, lr):
    """
    Given a video and a sequence of optimal transforms, produce a new 
    stabilized video.
    
    videoname: the name of the video
    optTransforms: a sequence of homographies
    vidsize: the dimensions [w,h] of the video
    ul: the upper-left corner of the crop window (x,y)
    lr: the lower-right corner of the crop window (x,y)
    """

	# create stabilized video
    final_frames = []
    box_frames = []
    orig_frames = []
    vidcap = cv2.VideoCapture(videoname)

    # create final video dimensions
    width, height = int(lr[0]-ul[0]), int(lr[1]-ul[1])
    ratio = vidsize[0]/width if width > height else vidsize[1]/height
    width = int(ratio*width)
    height = int(ratio*height)
    vid = np.float32([ [0,0], [width,0], [width,height], [0,height] ])
    box = np.float32([ [ul[0],ul[1],1], [lr[0],ul[1],1], [lr[0],lr[1],1], [ul[0],lr[1],1] ])

    # handle first frame separately
    success, img = vidcap.read()
    if success:
        transform = optTransforms[0]
        warpedBox = np.float32((box @ transform.T)[:,:2])
        correction = cv2.estimateRigidTransform(warpedBox, vid, fullAffine=True)

        # create final video frame
        newFrame = cv2.warpAffine(img, correction, (width,height))

        # create video with crop box frame
        newFrameBox = img.copy()
        for j in range(4):
        	cv2.line(newFrameBox, (warpedBox[j,0], warpedBox[j,1]),
                                (warpedBox[(j+1) % 4,0], warpedBox[(j+1) % 4,1]),
                                (0,255,0), 2)

    num = 0
    while success:
        # add imgs to video frame arrays
        final_frames.append(newFrame)
        box_frames.append(newFrameBox)
        orig_frames.append(img)

        # read next frame
        success, img = vidcap.read()
        if not success:
            break

        transform = optTransforms[num]
        warpedBox = np.float32((box @ transform.T)[:,:2])
        correction = cv2.estimateRigidTransform(warpedBox, vid, fullAffine=True)

        # create final video frame
        newFrame = cv2.warpAffine(img, correction, (width,height))

        # create video with crop box frame
        newFrameBox = img.copy()
        for j in range(4):
        	cv2.line(newFrameBox, (warpedBox[j,0], warpedBox[j,1]),
                                (warpedBox[(j+1) % 4,0], warpedBox[(j+1) % 4,1]),
                                (0,255,0), 2)

        num += 1

	# create stabilized video + original video comparison
    frame_array = []
    for f,o in zip(final_frames,orig_frames):
        height, width, layers = f.shape
        if width > height:
            f = np.concatenate((o,f), axis=0)
        else:
            f = np.concatenate((o,f), axis=1)
        size = (f.shape[1], f.shape[0])
        frame_array.append(f)

    out = cv2.VideoWriter('{}_new.mp4'.format(videoname.split('.')[0]), cv2.VideoWriter_fourcc(*'mp4v'), 30, size)
    for frame in frame_array:
        out.write(frame)
    out.release()

    # create video with moving crop box
    box_array = []
    for b in box_frames:
        height, width, layers = b.shape
        size = (width, height)
        frame_array.append(b)

    out1 = cv2.VideoWriter('{}_box.mp4'.format(videoname.split('.')[0]), cv2.VideoWriter_fourcc(*'mp4v'), 30, size)
    for frame in frame_array:
        out1.write(frame)
    out1.release()

    # create stabilized video + moving crop box comparison
    # frame_array = []
    # box_array = []
    # for f,b in zip(final_frames,box_frames):
    #     height, width, layers = b.shape
    #     print(f.shape, b.shape)
    #     if f.shape[0] is b.shape[0]:
    #         b = np.concatenate((b,f), axis=1)
    #     else:
    #         b = np.concatenate((b,f), axis=0)
    #     size = (b.shape[1], b.shape[0])
    #     frame_array.append(b)
    #
    # out = cv2.VideoWriter('{}_rect_mid.mp4'.format(videoname.split('.')[0]), cv2.VideoWriter_fourcc(*'mp4v'), 30, size)
    # for frame in frame_array:
    #     out.write(frame)
    # out.release()

    # create saliency map video
    # saliency = cv2.saliency.StaticSaliencyFineGrained_create()
    #
    # frame_array = []
    # for f in final_frames:
    #     success, saliencyMap = saliency.computeSaliency(f)
    #     threshMap = cv2.threshold(saliencyMap.astype('uint8'), 0, 255,
    #                                 cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    #     f = cv2.bitwise_and(f, f, mask=threshMap)
    #     height, width, layers = f.shape
    #     size = (width, height)
    #     frame_array.append(f)
    #
    # out = cv2.VideoWriter('{}_map.mp4'.format(videoname.split('.')[0]), cv2.VideoWriter_fourcc(*'mp4v'), 30, size)
    # for frame in frame_array:
    #     out.write(frame)
    # out.release()

videoname = sys.argv[1]

estTransforms = []
optTransforms = []

# read in the estimated camera path
with open("{}_estTransforms.txt".format(videoname.split('.')[0]), "r") as f:
    for line in f:
        s = [float(i) for i in line.split(' ')]
        if len(s) == 1: # skip frame count
            continue
        transform = np.array([[s[2], s[3], s[0]], [s[4], s[5], s[1]], [0, 0, 1]])
        estTransforms.append(transform)

# read in the optimized camera path
with open('{}_optTransforms.txt'.format(videoname.split('.')[0]), "r") as f:
    for line in f:
        s = [float(i) for i in line.split(' ')]
        transform = np.array([[s[2], s[3], s[0]], [s[4], s[5], s[1]], [0, 0, 1]])
        optTransforms.append(transform)

# get the video file
f = open("{}_info.txt".format(videoname.split('.')[0]), "r")
lines = f.readlines()
vidsize = [int(i) for i in lines[1].split(' ')]

# user input crop box
ul = [float(i) for i in lines[2].split(' ')]
lr = [float(i) for i in lines[3].split(' ')]

# automatic testing crop box
# ratio = 0.4
# ul = (ratio*vidsize[0], ratio*vidsize[1])
# lr = ((1-ratio)*vidsize[0], (1-ratio)*vidsize[1])

# testing crop box placement
# ul = [25, 110]
# lr = [610, 230]

# create the stabilized video
writeStableVideo(videoname, optTransforms, vidsize, ul, lr)

# plot the stimated and optimized camera paths
point = np.array([[0], [0], [1]])
point_est_path = np.zeros((0,2))
point_opt_path = np.zeros((0,2))

Ct = np.identity(3)
for i in range(len(estTransforms)):
    Ct = Ct @ estTransforms[i]

    # estimated path
    new_point = Ct @ point
    point_est_path = np.concatenate((point_est_path, new_point[:2].T), axis=0)

    # optimized path
    adj_point = Ct @ optTransforms[i] @ point
    point_opt_path = np.concatenate((point_opt_path, adj_point[:2].T), axis=0)

plt.figure()
plt.plot([i for i in range(len(point_est_path))], point_est_path[:,0], label="est")
plt.plot([i for i in range(len(point_opt_path))], point_opt_path[:,0], label="opt")
plt.title("x motion")
plt.legend()
plt.show()

plt.figure()
plt.plot([i for i in range(len(point_est_path))], point_est_path[:,1], label="est")
plt.plot([i for i in range(len(point_opt_path))], point_opt_path[:,1], label="opt")
plt.title("y motion")
plt.legend()
plt.show()
