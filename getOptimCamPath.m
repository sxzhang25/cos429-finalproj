%%%
% Code reference:
% https://github.com/ishit/L1Stabilizer
%%%

function err = getOptimCamPath(videoname, numFrames, vidsize, ul, lr)
% getOptimCamPath: gets optimal camera path from estimated camera path
%   First, read in the esimated camera path from file. Then use cvx to find
%   the optimal camera path.

fprintf("Optimizing " + videoname)

% Read in estimated camera path from file
n = numFrames;
filename = videoname + "_estTransforms.txt";
fileID = fopen(filename, 'r');
formatSpec = '%f %f %f %f %f %f';
sizeEstCamPath = [6 n];
ecp = fscanf(fileID, formatSpec, sizeEstCamPath);
ecp = ecp';

cvx_begin
% Set weights
w1 = 10;
w2 = 1;
w3 = 100;

% Ratio of affine : translational parts
c1 = [1 1 100 100 100 100];
c2 = [1 1 100 100 100 100];
c3 = [1 1 100 100 100 100];

% Variables
% w.r.t
variable p(n, 6)

% where
variable e1(n, 6)
variable e2(n, 6)
variable e3(n, 6)

% Minimize
minimize(sum(w1*e1*c1' + w2*e2*c2' + w3*e3*c3'))

subject to

    % SMOOTHNESS CONSTRAINTS
    % Frames 1 through n-3
    for i = 1:n - 3
        Ft1 = [ecp(i+1,3) ecp(i+1,4) ecp(i+1,1);
            ecp(i+1,5) ecp(i+1,6) ecp(i+1,2);
            0 0 1];
        Ft2 = [ecp(i+2,3) ecp(i+2,4) ecp(i+2,1);
            ecp(i+2,5) ecp(i+2,6) ecp(i+2,2);
            0 0 1];
        Ft3 = [ecp(i+3,3) ecp(i+3,4) ecp(i+3,1);
            ecp(i+3,5) ecp(i+3,6) ecp(i+3,2);
            0 0 1];

        Bt = [p(i,3) p(i,4) p(i,1); p(i,5) p(i,6) p(i,2); 0 0 1];
        Bt1 = [p(i+1,3) p(i+1,4) p(i+1,1); p(i+1,5) p(i+1,6) p(i+1,2); 0 0 1];
        Bt2 = [p(i+2,3) p(i+2,4) p(i+2,1); p(i+2,5) p(i+2,6) p(i+2,2); 0 0 1];
        Bt3 = [p(i+3,3) p(i+3,4) p(i+3,1); p(i+3,5) p(i+3,6) p(i+3,2); 0 0 1];

        % Residuals
        Rt = Ft1*Bt1 - Bt;
        Rt1 = Ft2*Bt2 - Bt1;
        Rt2 = Ft3*Bt3 - Bt2;

        Rt = [Rt(1,3) Rt(2,3) Rt(1,1) Rt(1,2) Rt(2,1) Rt(2,2)];
        Rt1 = [Rt1(1,3) Rt1(2,3) Rt1(1,1) Rt1(1,2) Rt1(2,1) Rt1(2,2)];
        Rt2 = [Rt2(1,3) Rt2(2,3) Rt2(1,1) Rt2(1,2) Rt2(2,1) Rt2(2,2)];

        % Constraints
        -e1(i,:) <= Rt <= e1(i,:);
        -e2(i,:) <= Rt1 - Rt <= e2(i,:);
        -e3(i,:) <= Rt2 - 2*Rt1 + Rt <= e3(i,:);
    end

    % Frames n-2 and n-1
    Ft1 = [ecp(n-1,3) ecp(n-1,4) ecp(n-1,1);
            ecp(n-1,5) ecp(n-1,6) ecp(n-1,2);
            0 0 1];
    Ft2 = [ecp(n,3) ecp(n,4) ecp(n,1);
            ecp(n,5) ecp(n,6) ecp(n,2);
            0 0 1];

    Bt = [p(n-2,3) p(n-2,4) p(n-2,1); p(n-2,5) p(n-2,6) p(n-2,2); 0 0 1];
    Bt1 = [p(n-1,3) p(n-1,4) p(n-1,1); p(n-1,5) p(n-1,6) p(n-1,2); 0 0 1];
    Bt2 = [p(n,3) p(n,4) p(n,1); p(n,5) p(n,6) p(n,2); 0 0 1];

    % Residuals
    Rt = Ft1*Bt1 - Bt;
    Rt1 = Ft2*Bt2 - Bt1;

    Rt = [Rt(1,3) Rt(2,3) Rt(1,1) Rt(1,2) Rt(2,1) Rt(2,2)];
    Rt1 = [Rt1(1,3) Rt1(2,3) Rt1(1,1) Rt1(1,2) Rt1(2,1) Rt1(2,2)];

    % Constraints
    -e1(n-2,:) <= Rt <= e1(n-2,:); % n-2
    -e2(n-2,:) <= Rt1 - Rt <= e2(n-2,:); % n-2
    -e1(n-1,:) <= Rt1 <= e2(n-1,:); % n-1

    for i = 1:n
        e1(i,:) >= 0;
        e2(i,:) >= 0;
        e3(i,:) >= 0;
        p(i,3) == p(i,6);
        p(i,4) == -p(i,5);
    end

    % PROXIMITY CONSTRAINTS
    U = [0 0 0 0 0 0;
        0 0 0 0 0 0;
        1 0 0 0 0 1;
        0 1 0 0 1 0;
        0 0 1 0 1 0;
        0 0 0 1 0 -1];
    lb = [0.9 -0.1 -0.1 0.9 -0.05 -0.1];
    ub = [1.1 0.1 0.1 1.1 0.05 0.1];

    % Constraints
    for i = 1:n
        lb <= p(i,:)*U <= ub;
    end

    % INCLUSION CONSTRAINTS
    % Check crop window corners
    if (ul(1) < 0 || ul(2) < 0)
        error('Error. One or more crop corners out of bounds.')
    end
    if (lr(1) > vidsize(1) || lr(2) > vidsize(2))
        error('Error. One or more crop corners out of bounds.')
    end

    CR1 = [1 0 ul(1) ul(2) 0 0;
            0 1 0 0 ul(1) ul(2)]';
    CR2 = [1 0 ul(1) lr(2) 0 0;
            0 1 0 0 ul(1) lr(2)]';
    CR3 = [1 0 lr(1) ul(2) 0 0;
            0 1 0 0 lr(1) ul(2)]';
    CR4 = [1 0 lr(1) lr(2) 0 0;
            0 1 0 0 lr(1) lr(2)]';

    % Constraints
    for i = 1:n
        [0 0] <= p(i,:)*CR1 <= vidsize;
        [0 0] <= p(i,:)*CR2 <= vidsize;
        [0 0] <= p(i,:)*CR3 <= vidsize;
        [0 0] <= p(i,:)*CR4 <= vidsize;
    end

cvx_end

err = sum(w1*e1*c1' + w2*e2*c2' + w3*e3*c3');

% Write out to file
% Standard
filename = videoname + "_optTransforms.txt";

% Testing size
% filename = videoname + "_optTransforms" + round(ul(1)) + ".txt";

% Testing aspect ratio
% width = round(lr(1)-ul(1));
% height = round(lr(2)-ul(2));
% filename = videoname + "_optTransforms" + width + ":" + height + ".txt";

% Testing location
% center = [round((ul(1)+lr(1))/2) round((ul(2)+lr(2))/2)];
% filename = videoname + "_optTransforms" + center(1) + "," + center(2) + ".txt";

fileID = fopen(filename, 'w');
for i = 1:n
    fprintf(fileID, '%6.8f %6.8f %6.8f %6.8f %6.8f %6.8f\n', p(i,:));
end
fclose(fileID);

end
