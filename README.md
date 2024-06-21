# canvas-quiz-scripts
Automatically change availability and extend quizzes for students based on CFA acoomodations.

## Getting Started

### Requirements:
* Clone the repo into your preferred IDE, for example, Visual Studio Code
* Python 3.10 or later - [found here](http://www.python.org/getit/)

**Troubleshooting for Window Users:**
* Running commands with "pip" or "pip3" heading shows error that the command cannot be found & need to check your path:
    1. In the Window's search bar, find "Edit the system environment variables", a pop up should appear upon clicking it.
    2. Click on "Advanced" from the top bars.
    3. Click "Environment Variables near the bottom right.
    4. Under "System Variables", (NOT "User Variables"), double click on "Path" to open it.
    5. In the new pop up called "Edit environment variable", click "New" on the right.
    6. Enter two new paths depending on where you installed Python, for example: (folder names for Python can change depending on version)
        * C:\Users\[username]\AppData\Local\Programs\Python\Python310\Scripts
        * C:\Users\[username]\AppData\Local\Programs\Python\Python310
    7. Click "Ok" until all pop ups disappear

### Creating a .env file
Create a [Canvas API token](https://learninganalytics.ubc.ca/for-students/canvas-api/) and save it for later.

Create a .env file in the root directory with the following fields:
```
API_KEY={YOUR API KEY}
API_URL={YOUR API DOMAIN}
```
> An example canvas domain is: https://{school}.instructure.com
* **Note**: Do not include the curly brackets when inputting these values. The API_KEY is your generated token. The API_URL for UBC Canvas is: https://canvas.ubc.ca

### Setting up your environment
> You can set up your environment any way you'd like. Below are instructions for creating it with virtualenv

* `pip install virtualenv` (if you don't already have virtualenv installed)
* `virtualenv venv` to create your new environment (called 'venv' here)
* `source venv/bin/activate` (to enter the virtual environment)
* `pip install -r requirements.txt` (to install the requirements in the current environment)

**Troubleshooting for Window Users:**
* `source venv/bin/activate` is a Linux command. The command `venv\Scripts\activate` is for Windows, read below if the command still does not work.
* Problem may follow for Windows showing scripts are disabled. In this case, go to Windows Powershell by searching for it from Start. Enter the command `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`, type in "Y" and press enter. Then, try `venv\Scripts\activate` again.

### Setting up Student Accomodations

#### CSV
Create a .csv file with two columns:
* Student
* Extension

List the *Student Number* in the Student column and the *Time Accomodation* in the Extension column. (e.g. 12312346, 1.5 for a student with a student number of 12312346 and an accomodation for x1.5 exam time.)

An example .csv file should look like the following.

```
Student,Extension
357480,1.5
357399,2.0
357495,1.25
456789,1.5
```
#### PDFs

Create a folder in the root directory of the cloned repository. Copy all PDFs from the Centre for Accessibility into the new folder. The script will automatically extract the *Student Number* and *Time Accomodation* of every student.

### Running the Script

* First, open a terminal, then navigate to canvas_quiz_extender.
* Run the script using `python main.py {file_path}`. Replace `{file_path}` with either: the file name of the .csv, or the name of the new folder with the CFA PDFs.