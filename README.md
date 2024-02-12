# Instructions
1. Download the folder onto your local machine
2. Navigate to the folder in your terminal/command line
3. Use a Python virtual environment (optional)
4. Run command: pip install -r requirements.txt
5. Run command: python init_db.py
6. Run command: export FLASK_APP=app
7. Run command: flask run
8. Open in browser the URL routing to the IP and port the app is running on

# App Instructions
1. Input up to 7 different coffee orders: each order has the coworker's name and the price of the coffee they have ordered
2. After inputting all coffee orders for the current trip, click the "Submit Orders" button at the bottom of the page, and the program will decide who should pay for the entire coffee trip

# Assumptions
* The coworker who will pay is chosen using a weighted probability: if a coworker has spent more money on coffee, they are more likely to be chosen to pay for the entire coffee trip.
* A coworker's total spending on coffee is stored in a database "database.db," and the weighted probability uses the data stored in this database.
* On a given coffee trip (each time the "Submit Orders" button is pressed), it is guaranteed that a coworker must be on this trip to be chosen to pay for all of the coffees.
