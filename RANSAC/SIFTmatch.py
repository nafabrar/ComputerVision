from PIL import Image, ImageDraw
import numpy as np
import csv
import math

def ReadKeys(image):
    """Input an image and its associated SIFT keypoints.

    The argument image is the image file name (without an extension).
    The image is read from the PGM format file image.pgm and the
    keypoints are read from the file image.key.

    ReadKeys returns the following 3 arguments:

    image: the image (in PIL 'RGB' format)

    keypoints: K-by-4 array, in which each row has the 4 values specifying
    a keypoint (row, column, scale, orientation).  The orientation
    is in the range [-PI, PI] radians.

    descriptors: a K-by-128 array, where each row gives a descriptor
    for one of the K keypoints.  The descriptor is a 1D array of 128
    values with unit length.
    """
    im = Image.open(image+'.pgm').convert('RGB')
    keypoints = []
    descriptors = []
    first = True
    with open(image+'.key','rb') as f:
        reader = csv.reader(f, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC,skipinitialspace = True)
        descriptor = []
        for row in reader:
            if len(row) == 2:
                assert first, "Invalid keypoint file header."
                assert row[1] == 128, "Invalid keypoint descriptor length in header (should be 128)."
                count = row[0]
                first = False
            if len(row) == 4:
                keypoints.append(np.array(row))
            if len(row) == 20:
                descriptor += row
            if len(row) == 8:
                descriptor += row
                assert len(descriptor) == 128, "Keypoint descriptor length invalid (should be 128)."
                #normalize the key to unit length
                descriptor = np.array(descriptor)
                descriptor = descriptor / math.sqrt(np.sum(np.power(descriptor,2)))
                descriptors.append(descriptor)
                descriptor = []
    assert len(keypoints) == count, "Incorrect total number of keypoints read."
    print "Number of keypoints read:", int(count)
    return [im,keypoints,descriptors]

def AppendImages(im1, im2):
    """Create a new image that appends two images side-by-side.

    The arguments, im1 and im2, are PIL images of type RGB
    """
    im1cols, im1rows = im1.size
    im2cols, im2rows = im2.size
    im3 = Image.new('RGB', (im1cols+im2cols, max(im1rows,im2rows)))
    im3.paste(im1,(0,0))
    im3.paste(im2,(im1cols,0))
    return im3

def DisplayMatches(im1, im2, matched_pairs):
    """Display matches on a new image with the two input images placed side by side.

    Arguments:
     im1           1st image (in PIL 'RGB' format)
     im2           2nd image (in PIL 'RGB' format)
     matched_pairs list of matching keypoints, im1 to im2

    Displays and returns a newly created image (in PIL 'RGB' format)
    """
    im3 = AppendImages(im1,im2)
    offset = im1.size[0]
    draw = ImageDraw.Draw(im3)
    for match in matched_pairs:
        draw.line((match[0][1], match[0][0], offset+match[1][1], match[1][0]),fill="red",width=2)
    im3.show()
    return im3

def match(image1,image2):
    """Input two images and their associated SIFT keypoints.
    Display lines connecting the first 5 keypoints from each image.
    Note: These 5 are not correct matches, just randomly chosen points.

    The arguments image1 and image2 are file names without file extensions.

    Returns the number of matches displayed.

    Example: match('scene','book')

    Each row corresponds to a descriptor vector. To select the best match
    for a vector from the first image, you should measure its angle to
    each vector from the second matrix.

    As the descriptor vectors are already normalized to have unit length,
    the angle between them is the inverse cosine (math.acos(x) function in Python) of the dot product
    of the vectors. The vector with the smallest angle is the nearest neighbor (i.e., the best match).
    """
    im1, keypoints1, descriptors1 = ReadKeys(image1)
    im2, keypoints2, descriptors2 = ReadKeys(image2)
    #
    # REPLACE THIS CODE WITH YOUR SOLUTION (ASSIGNMENT 5, QUESTION 3)
    #
    #Generate five random matches (for testing purposes)
    matched_pairs = []
    angles = []
    angle_threshold = 0.70
    descriptors1_length = range(len(descriptors1))
    descriptors2_length = range(len(descriptors2))
    for i in (descriptors1_length):
        for j in (descriptors2_length):
            # Each row corresponds to a descriptor vector.
            # To select the best match for a vector from the first image, you
            # should measure its angle to each vector from the second matrix.
            angles.append(math.acos(np.dot(descriptors1[i],descriptors2[j])))
        # Compare smallest and second smallest angle. Using sorted to find the angle
        # from the angles
        # Compare the ratio of angles with our ratio
        sortedangles = sorted(angles)
        ratio = sortedangles[0]/sortedangles[1]
        if (ratio<angle_threshold):
            # if below threshold add it to matchedpairs
            matched_pairs.append([keypoints1[i],keypoints2[angles.index(sortedangles[0])]])
        # empty the angles list for next iteration
        angles=[]
    # RANSAC
    # number of iteration
    iteration = 10
    #  15 degrees
    orientation_thresh = 15 * math.pi/180
    # scale threshold
    scale_thresh = 0.9
    best_subset = []
    for i in range(iteration):
        # local bestmatch
        bestmatch = []
        #  for each ransac select just one match at random
        #  then check all the other matches for consistency with it
        random_index = np.random.randint(len(matched_pairs))
        onematchrandom = matched_pairs[random_index]
        #  calculate orientation and scale difference of one random match
        df_scale = abs(onematchrandom[0][2] - onematchrandom[1][2])
        df_orientation = abs(onematchrandom[0][3] - onematchrandom[1][3]) % (2*math.pi)
        for m in matched_pairs:
            #  check that the change of orientation between the two keypoints
            #  of each match agrees within, say, 30 degrees.deltaOrientation2 = match[0][3] - match[1][3]
            df_scale_1 = abs(m[0][2] - m[1][2])
            df_orientation1 = abs(m[0][3] - m[1][3]) % (2*math.pi)
            # calculate angle difference
            df_angle = (df_orientation-df_orientation1)
            # size difference
            df_size = abs(df_scale-df_scale_1)
            # subtract if angle is greater than pi
            if df_angle > math.pi :
                df_angle = df_angle - math.pi
            # If the size and angle are below threshold add it to bestmatch list
            if (df_size <= scale_thresh and df_angle <= orientation_thresh):
                bestmatch.append(m)

        if len(bestmatch) > len(best_subset):
            best_subset = bestmatch
        #
        # END OF SECTION OF CODE TO REPLACE
        #
    im3 = DisplayMatches(im1, im2, best_subset)
    return im3

#Test run...
# match('scene','book')
match('library2','library')

