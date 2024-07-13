Overview
This document provides instructions for executing a Python script through the main entry point. 
It's essential to ensure that the required CSV files (users.csv, records1.csv, records2.csv, 
records3.csv, and players.csv) are located in the same directory as the main Python script. 
This setup is necessary for the correct functioning of the script.

Prerequisites
Python: The script requires Python to be installed on your system. If you don't have Python installed, download and install it from python.org.

pygame: pip install pygame
openCV: pip install opencv-python

CSV Files: Ensure that the CSV files (users.csv, records1.csv, records2.csv, records3.csv, and players.csv) are placed in the same directory as the main Python script.

Execution Instructions
Windows
Open Command Prompt: Press Win + R, type cmd, and press Enter.

Navigate to the Script Directory: Use the cd command to change to the directory containing your script.

Example:

cd path\to\your\script
Replace path\to\your\script with the actual path to your Python script.

Run the Script: Execute the script by typing:


python main.py
Ensure that main.py is the name of your main Python script.

Linux
Open Terminal: You can usually open it by pressing Ctrl + Alt + T.

Navigate to the Script Directory: Use the cd command to change to your script's directory.

Example:


cd /path/to/your/script
Replace /path/to/your/script with the actual path.

Run the Script: Execute the script by typing:

python3 main.py
or

./main.py
(Make sure your script has execution permissions. You can set it with chmod +x main.py.)

macOS
Open Terminal: You can find it in Applications -> Utilities, or use Spotlight to search for it.

Navigate to the Script Directory: Use the cd command to navigate to your script's directory.

Example:


cd /path/to/your/script
Replace /path/to/your/script with the actual path.

Run the Script: Execute the script by typing:


python3 main.py
or

./main.py
(Ensure your script is executable with chmod +x main.py.)

Additional Notes
Python Version: The instructions assume Python 3 is installed. If you have multiple Python versions, you may need to replace python or python3 with the specific version you intend to use (e.g., python3.8).

File Paths: If you encounter issues related to file paths, ensure that the CSV files are indeed in the same directory as your Python script or adjust the file paths in your Python code accordingly.

Dependencies: If your script requires external libraries, make sure to install them using pip. For example:


pip install library-name
If you encounter any issues or need further assistance, please refer to the Python documentation or seek help from online programming communities.