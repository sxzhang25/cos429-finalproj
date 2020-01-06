# Project Description
Implementation of Youtube video stabilization algorithm.
Based on work by Matthias Grundmann, Vivek Kwatra, and Irfan Essa:

https://ai.googleblog.com/2011/06/auto-directed-video-stabilization-with.html

# Dependencies
This project uses the following software packages:
```python 
cvx
opencv
numpy
```

# To Use
0. Make sure the video is in the same directory as all the code files. Include the video extension in all instances of `<videoname>`.

1. `python python estimateCameraPath.py <videoname>`

2. Change the variable `videoname` in `runGetOptimCamPath.m` and run the script.

3. `python python createVideo.py <videoname>`

# Examples
The folder *examples* contains examples of the algorithm applied on various videos. A few are shown below.

![pan1.mp4](https://github.com/sxzhang25/COS-429-Final-Project/blob/master/pan.gif?raw=true)

![train1.mp4](https://github.com/sxzhang25/COS-429-Final-Project/blob/master/train.gif?raw=true)

![walking3.mp4](https://github.com/sxzhang25/COS-429-Final-Project/blob/master/walking.gif?raw=true)

![williams2.mp4](https://github.com/sxzhang25/COS-429-Final-Project/blob/master/williams.gif?raw=true)

![yuna1.mp4](https://github.com/sxzhang25/COS-429-Final-Project/blob/master/yuna.gif?raw=true)
