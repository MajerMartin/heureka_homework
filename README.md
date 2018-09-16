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
* Synchronous API calls are cached using custom TLRU [cache](/heureka/Cache.py). Asynchronous API calls are cached using inherited [asynchronous cache](/heureka/AsyncCache.py) (currently slightly duplicated code).
* Page settings are defined in global [configuration file](/heureka/config.py).
* Offers in products page are collected asynchronously.

## TODO
* Add logging.
* Refactor Cache.py and AsyncCache.py.
* Add tests for AsyncCache.py.

## Screenshots
![Homepage](img/homepage.png?raw=true)
![Products](img/products.png?raw=true)
![Offers](img/offers.png?raw=true)
