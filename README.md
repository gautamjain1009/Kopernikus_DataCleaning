
### Dataset Overview: ###
* Dataset consists of monocular images probably recorded in a parking lot. Different cameras are used from different angles to capture the scenes in the parking lot. 
* Dataset contains images from 3 different cameras with different spatial resolutions and there are also some images as noise which might be irrelevant to the scenario which we are tackling. 
  

### Program Workflow: ###
The program aims to identify and remove similar-looking images in a folder by comparing consecutive frames. It utilizes the `compare_frames_change_detection` function, which calculates a score indicating the difference between two frames. Based on the score, images can be identified as duplicates or with minor differences and considered non-essential. The program processes the images, compares them, and removes the similar ones. 
  
### Determining input parameter values: ###
* The input parameters in the program, such as the threshold and minimum contour area, need to be determined based on the characteristics of your dataset. These values impact the sensitivity of the comparison and the criteria for considering images as similar or different. 
* To determine the values, you can use techniques such as statistical analysis, manual inspection of sample frames, or experimentation with different values.
*  Determine_parameters functions provided demonstrate approaches for automatically determining these values.

### Improving data collection of unique cases ###
* To improve data collection of unique cases in the future, you can consider the following:
  * **Diverse data**: Collect a wide range of images that cover various scenarios, angles, lighting conditions, and object configurations. This helps capture a comprehensive representation of the data and reduces the chances of mistakenly identifying unique cases as similar.
  *  **Multiple camera angles** : If possible, capture the same scene or object from different camera angles. This provides different perspectives and helps distinguish between genuinely unique images and those that appear similar due to the camera viewpoint.
  *  **Image metadata**: Consider collecting and utilizing additional metadata, such as timestamps, camera IDs, or other relevant information associated with the images. This information can be used to filter and group images from the same camera or capture event, reducing the likelihood of comparing images from different cameras or unrelated scenarios.

