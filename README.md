# COS 429 Final Project
Fall 2019
Sharon Zhang

# Project Description
Implementation of Youtube video stabilization algorithm.
Based on work by Matthias Grundmann, Vivek Kwatra, and Irfan Essa:
https://ai.googleblog.com/2011/06/auto-directed-video-stabilization-with.html

# Dependencies
```python 
cvx
opencv
numpy
```

# To Use
1. ```python python estimateCameraPath.py <videoname>```

2. Change the variable 'videoname' in runGetOptimCamPath.m and run the script.

3. ```python python createVideo.py <videoname>```

# Examples
The folder 'examples' contains examples of the algorithm applied on various videos.
