from flask import Flask, render_template, jsonify, request
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

@app.route('/ticker_post', methods=['POST'])
def ticker_post():
    try:
        currency1 = request.json.get('currency1')
        currency2 = request.json.get('currency2')
        ticker = request.json.get('ticker')

        data = [currency1,currency2,ticker]
        postgres.insert_ticker(data)  
        
        return jsonify({'message': 'Data inserted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/ticker_data')
def ticker_data():
    try:
        data = postgres.select_ticker()
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Delete masih ggal
@app.route('/ticker_delete', methods=['POST'])
def ticker_delete():
    try:
        # Get the ID of the row to delete from the request data
        ticker_name = request.json.get('data')  # Assuming the ID is passed in the JSON payload
        print(ticker_name)
        postgres.delete_ticker(ticker_name)
        return jsonify({'message': f"Row with ID {ticker_name} deleted successfully"}), 200
    except Exception as e:
        # Handle exceptions or errors here
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
