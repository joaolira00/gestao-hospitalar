# Hospital Management 
## Content Table

|Sections|
|------|
| [Description](#description)
| [Technologies Used](#technologies-used)
| [Requirements](#requirements)
| [Installation](#installation) 
| [Running The Program](#running-the-program)|


## Description:
A Hospital Management Software developed with Python and FastAPI.

## Technologies Used:
- Python
- FastAPI
- PostgreSQL

## Requirements:
For this project, you will nedd [Python 3.12](https://www.python.org/downloads/release/python-3129/).

## Installation:

1. Clone this repo:
```
$ git clone https://github.com/joaolira00/gestao-hospitalar.git
```

2. Install Python virtual environment in the project folder:
```
$ py -3.12 -m venv venv
```

3. Activate the venv:
```
$ venv/Scripts/activate
```

4. Install the project dependencies:
```
$ pip install -r requirements.txt
```
## Running The Program:
1. Run the uvicorn server with this command
```
$ uvicorn main:app --reload
```

2. You can now access the API documentation on URL below:
```
$ http://127.0.0.1:8000/scalar
```
