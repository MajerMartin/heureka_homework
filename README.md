# Heureka Homework

This repository contains my implementation of assignment given by [Heureka.cz](https://www.heureka.cz) to assess my skills for Python Backend Developer position. The main goal of the task was to create simple Heureka-like website using provided API. The task is described in detail in provided [documents](/doc) (czech only).

The backend of the solution was implemented in Python 3.6 with Flask microframework and the frontend using Bootstrap 4.

## Running the Server
1. Clone the repository.
```
git clone https://github.com/MajerMartin/heureka_homework.git
cd heureka_homework
```
2. Initialize virtual environment for Python 3.6. If using conda distribution, run the following commands.
```
conda create -n myenv python=3.6
source activate myenv
```
3. Install dependencies.
```
pip install -r requirements.txt
```
4. Run the server.
```
cd heureka
export FLASK_APP=app.py
flask run
```
5. Navigate to "http://localhost:5000/" in your browser.

## Running the Tests
1. Navigate to the tests folder.
```
cd heureka_homework/tests
```
2. Run all tests.
```
python -m unittest
```

## Notes
* API calls are cached using custom TLRU [cache](/heureka/Cache.py).
* Page settings are defined in global [configuration file](/heureka/config.py).

## TODO
* Add logging.
* Asynchronously preload first page of products for every category.
* Asynchronously preload next page of products for currently selected category.
