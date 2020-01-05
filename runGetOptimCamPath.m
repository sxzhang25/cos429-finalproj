%%
% COS 429 Final Project
% Sharon Zhang
%
% Runs the CVX solver to find optimized transforms for video
%%

% Change to desired video name (no extension)
videoname = "swim1";

% Extract video information
filename = videoname + "_info.txt";
fileID = fopen(filename, 'r');
formatSpec = '%d';
numFrames = fscanf(fileID, formatSpec, [1]);
formatSpec = '%d %d';
vidsize = fscanf(fileID, formatSpec, [1,2]);
formatSpec = '%d %d';
ul = fscanf(fileID, formatSpec, [1,2]);
lr = fscanf(fileID, formatSpec, [1,2]);

% ratio = 0.4;
% ul = [ratio*vidsize(1) ratio*vidsize(2)];
% lr = [(1-ratio)*vidsize(1) (1-ratio)*vidsize(2)];

% Optimize camera path
err = getOptimCamPath(videoname, numFrames, vidsize, ul, lr)