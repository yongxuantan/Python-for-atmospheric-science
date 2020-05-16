### Program: ImageCompression.py
### Language: Python 
- Version: 3.6.5
- Libraries: matplotlib.pyplot, numpy, PIL.Image, random
### Written by: Your truly
#### Input images: Penguins.jpg, Koala.jpg
#### Purpose: Apply K-means clustering for image compression.


### Instructions:
- Place ImageCompression.py, Penguins.jpg, and Koala.jpg in the same directory.
	
- The assignment3.py is the only program that needs to be executed, and should take 
	about 9 hours to complete. If you run it in Spyder, you will output in console that
	shows the progress. 

- The algorithm reached maximum 100 iterations for both images on the K=20 clusters and 
	K=15 clusters for  the koala image. Thus, these runs did not reach minimum but should 
	be sufficient for this assignment.

- The program will output all the penguins_kXX.jpg and koala_kXX.jpg images. Each number
	following the _k represents the number of clusters being used to generate that image.

- Since the initial pixels are selected at random, there is a chance the algorithm converges to a 
	local minima. In that case, your images will look different.
	
- To save console output into a file, append this command to program call " > <filename.ext>"

- Use case:
	- navigate to program directory in terminal then execute the following command: 
		- python ImageCompression.py
	
#### Note: 
_To run program in windows environment, please refer to this tutorial_
(https://www.pythoncentral.io/execute-python-script-file-shell/)