# 1. Get project code
Clone the repository or unzip the project source code.
The project is located at https://github.com/JaMugen/ChristopherGaudious_Project2_SourceCode

Project zip can also be downloaded from the github link using the download zip option in provided under code. 

# Enter the project directory
The directory of the source code is titled ChristopherGaudious_Project2_SourceCode enter this directory to run the project.
# Create and Activate Virtual Environment

## Create Environment
In your respective command line environment use the python command for creating a virtual environment.
The project was created using WSL with Ubuntu Operating System so a valid command is
```bash
python3 -m venv .venv
```

## Enter Environment
```bash
source .venv/bin/activate
```

## Install Dependencies
The project uses Coloroma for colored command line output. The project comes with a requirements file so use the command
```bash
pip install -r requirements.txt
```
to install dependencies

# Run the game
To run the project run the main.py within the virtual environment

```bash
python main.py
```

# Build: Movement

AI player can now move along the board toward a room.

