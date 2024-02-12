from flask import Flask, render_template, request
import sqlite3
import random
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def process_orders():
    '''
    Main method; 
    - connects to database
    - waits for REST API calls
    - parses Bootstrap form for name and price inputs
    - updates database with prices and names
    - displays who will pay on web page
    '''
    coffee_trip = []

    # connect to database
    conn = get_db_connection()

    # parse form entries for names and prices of coffees
    for person in range(1, 8):
        name, price = get_name_and_price(person)
        if not price or not is_number(price): continue
        if not update_spending(conn, name, price): continue
        coffee_trip.append(name)
    
    payer = choose_who_pays(conn, coffee_trip)

    # export_to_excel(conn, 'spendings', 'output.xlsx') # uncomment to view database
    conn.close()
    
    return render_template('index.html', payer=payer)


def get_name_and_price(person):
    '''
    Get the name and price of a person

    Parameters:
    - person: index (1-7) on Bootstrap form

    Returns:
    - name: the name inputted into the form textbox
    - price: the price of the corresponding person's coffee
    '''
    name_key = f'person{person}Name'
    price_key = f'person{person}Price'
    name = request.form.get(name_key)
    price = request.form.get(price_key)
    return name, price


def get_spending(conn, name):
    '''
    Get a person's total accumulated spending on coffee

    Parameters:
    - conn: database connection
    - name: name of the person/coworker

    Returns:
    - total spending of the given coworker
    '''
    name = clean_name(name)
    cursor = conn.cursor()
    cursor.execute("SELECT spending FROM spendings WHERE worker_name=?", (name,))
    result = cursor.fetchone()
    cursor.close()
    if result is not None:
        return float(result[0])
    else:
        return None


def update_spending(conn, name, coffee_price):
    '''
    Update or insert a person's total accumulated spending on coffee

    Parameters:
    - conn: database connection
    - name: name of the person/coworker

    Returns:
    - True if successful, False otherwise
    '''
    name = clean_name(name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spendings WHERE worker_name=?", (name,))
    entry = cursor.fetchone()
    if entry:
        cursor.execute("UPDATE spendings SET spending=? WHERE worker_name=?", (float(coffee_price)+get_spending(conn, name), name))
    else:
        cursor.execute("INSERT INTO spendings (worker_name, spending) VALUES (?, ?)", (name, coffee_price))
    conn.commit()
    cursor.close()
    return True


def choose_who_pays(conn, coffee_trip):
    '''
    Choose someone from a coffee trip to pay for all of the coffees, weighted by their individual spending.

    Parameters:
    - conn: database connection
    - coffee_trip: list of names with all people included in coffee trip

    Returns:
    - the chosen person who will pay for the coffee trip expenses,
      if the coffee_trip list is empty, returns "No one" indicating no participant.
    '''
    if not coffee_trip or len(coffee_trip) == 0: return "No one"
    coffee_costs = [get_spending(conn, name) for name in coffee_trip]
    trip_total_cost = sum(coffee_costs)
    weights = [spending / trip_total_cost for spending in coffee_costs]
    chosen_name = random.choices(coffee_trip, weights=weights)[0]
    return chosen_name

def is_number(num):
    '''
    Checks if inputted number is a float or not

    Parameters;
    - num: inputted number

    Returns:
    - True if the input is a number, False otherwise
    '''
    try:
        float_value = float(num)
        return True
    except ValueError:
        return False

def clean_name(name):
    '''
    Cleans inputted name to make SQL entries uniform
    ex. Miles Yang --> milesyang, miles yang --> milesyang

    Parameters:
    - name: name of a worker

    Returns:
    - cleaned version of name
    '''
    return name.replace(" ", "").lower()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def export_to_excel(conn, table, filename):
    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)
    df.to_excel(filename, index=False)
