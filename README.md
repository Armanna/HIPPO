# Business Model and the Problem
https://gist.github.com/matheus-hellohippo/a0e28bcbeade9e5044a08808a847a11c

# Some refinements
- In Claims event schema the quantity column data type is float instead of int
- In the Goal 4 take most 5 common quantities


# Run the project to get the output data

## Create a virtual environment
python -m venv .venv

## Activate the virtual environment
### Windows
.\.venv\Scripts\activate
### Mac or Linus
source .\.venv\bin\activate

## Install the dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

## Run the application
python main.py

## Check the app.log