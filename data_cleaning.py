import os
import cv2
import imutils
from imaging_interview import preprocess_image_change_detection, compare_frames_change_detection
from datetime import datetime
import numpy as np 
import argparse

def get_timestamp(filename):

    # Define the two possible timestamp formats
    formats = ['%Y-%m-%d_%H-%M-%S', '%Y%m%d%H%M%S']

    for fmt in formats:
        try:
            timestamp = datetime.strptime(filename, fmt)
            return timestamp
        except ValueError:
            pass

    # If no valid timestamp format is found, return the filename itself
    return filename

def get_camera_id(filename):

    # Extract the camera ID from the file name
    # Modify this function based on your specific file naming convention
    camera_id = filename.split('-')[0]  # Example: cameraID_timestamp.jpg

    return camera_id

def reshape_image(image, target_width, target_height):

    # Get the current dimensions of the image
    current_height, current_width = image.shape[:2]

    # Resize the image to the target dimensions
    reshaped_image = cv2.resize(image, (target_width, target_height))

    return reshaped_image

def determine_parameters(sample_folder, resize_width, resize_height):

    sample_files = [f for f in os.listdir(sample_folder) if os.path.isfile(os.path.join(sample_folder, f))]

    # Sort image files by timestamp
    sample_files = sorted(sample_files, key=get_timestamp)

    # Calculate the average score of the sample frames
    scores = []
    contour_areas = []

    prev_processed = None
    for sample_file in sample_files:
        sample_path = os.path.join(sample_folder, sample_file)

        if sample_path.endswith(".png") or sample_path.endswith(".jpg"):

            sample_img = cv2.imread(sample_path)
            
            if sample_img is None:
                continue
            
            sample_img_resized = reshape_image(sample_img, resize_width, resize_height) #TODO: add to cli args and make it as a global constant
            sample_img_processed = preprocess_image_change_detection(sample_img_resized)

            if prev_processed is not None:
                score, contours, _ = compare_frames_change_detection(prev_processed, sample_img_processed, 500)
                scores.append(score)

                # Calculate the contour area for each contour in the current frame
                areas = [cv2.contourArea(c) for c in contours]
                contour_areas.extend(areas)

            prev_processed = sample_img_processed

    # Set the threshold value based on the average score
    average_score = np.mean(scores)
    threshold = average_score * 0.5  # Adjust the multiplier as needed

    # Set the minimum contour area based on a percentage of the average contour area
    average_area = np.mean(contour_areas)
    min_contour_area = average_area * 0.2  # Adjust the multiplier as needed


    return threshold, min_contour_area


def find_similar_images(folder_path, resize_width, resize_height, threshold, min_contour_area, num_consecutive_frames):
    """
    TODO: remove two for loops and add mapping based apporach to stop repititve image processing
    """
    
    # Get a list of image file paths in the folder
    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Sort image files by timestamp
    image_files = sorted(image_files, key=get_timestamp)

    # List to store the indices of deleted frames
    deleted_indices = []

    # Iterate through the images
    for i in range(len(image_files)):
        
        if image_files[i].endswith(".png") or image_files[i].endswith(".jpg"):
            
            # Skip deleted frames
            if i in deleted_indices:
                continue

            img1_path = os.path.join(folder_path, image_files[i])

            # Load  and resize the image
            img1 = cv2.imread(img1_path)

            # Skip processing if the image is None
            if img1 is None:
                continue

            img1_resized = reshape_image(img1, resize_width, resize_height)
            
            # Preprocess the resized image
            img1_processed = preprocess_image_change_detection(img1_resized)

            # Extract the camera ID from the file name
            camera_id_prev = get_camera_id(image_files[i])

            # Skip images without a valid camera ID
            if camera_id_prev is None:
                continue

            # Compare the first image with the consecutive frames
            for j in range(i + 1, min(i + num_consecutive_frames + 1, len(image_files))):
                
                if image_files[i].endswith(".png") or image_files[i].endswith(".jpg"):
                    
                    img2_path = os.path.join(folder_path, image_files[j])

                    camera_id_next = get_camera_id(image_files[i])

                    # Skip images without a valid camera ID
                    if camera_id_next is None or camera_id_next != camera_id_prev:
                        print(f"Camera ID previous:: {camera_id_prev} not equal to Camera ID next:: {camera_id_next} skipping this frame")
                        continue
                    
                    # Load and resize the consecutive frames
                    img2 = cv2.imread(img2_path)

                    # Skip processing if the image is None
                    if img2 is None:
                        continue

                    img2 = reshape_image(img2, resize_width, resize_height)

                    img2_processed = preprocess_image_change_detection(img2)

                    # Compare the processed images
                    score, _, _ = compare_frames_change_detection(img1_processed, img2_processed, min_contour_area)

                    # If the score is below the threshold, remove the similar image
                    if score < threshold:
                        os.remove(img2_path)
                        print(f"Removed similar image: {img2_path}")
                        deleted_indices.append(j)    


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='2D Lane detection')
    parser.add_argument("--resize_h", type=int, default=480, help="resize height")
    parser.add_argument("--resize_w", type=int, default=640, help="resize_width")
    parser.add_argument("--dataset_path", type=str, default="/home/gauti/Documents/kopernikus_automotive_test/dataset-candidates-ml/dataset/", help="dataset path")

    #parsing args
    args = parser.parse_args()

    folder_path = args.dataset_path
    threshold_avg, contour_area_avg=  determine_parameters(folder_path, resize_width= args.resize_w , resize_height= args.resize_h)

    print(f"The min threshold: {threshold_avg} and the min contour area: {contour_area_avg}")
    find_similar_images(folder_path, resize_width = args.resize_w, resize_height = args.resize_h, threshold = threshold_avg, min_contour_area = contour_area_avg, num_consecutive_frames = 3)

    print("====== FInished processing all the images =======")