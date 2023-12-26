from flask import Flask, render_template, jsonify
from datastore.postgre import PostgreStorage

app = Flask(__name__)

postgres = PostgreStorage()

@app.route('/price_data')
def gets_data():
    try:

        data = postgres.select_price()  
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/currency_data')
def currency_data():
    try:
        data = postgres.select_currency() 
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/ticker_data')
def ticker_data():
    try:
        data = postgres.select_ticker()
        print(data)
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/price_list')
def display_data():
    try:
        return render_template('price_list.html')
    except Exception as e:
        return str(e), 500
    
@app.route('/ticker_list')
def ticker_list():
    try:
        return render_template('ticker_list.html')
    except Exception as e:
        return str(e), 500
    
@app.route('/home')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
