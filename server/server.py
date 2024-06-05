"""
Module: server

This module contains the Flask server code for handling various endpoints.
"""

import sys
import os
import logging
from flask import Flask, render_template, jsonify, request
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from loggers.loggers_config import LoggerConfig

from datastore.postgre import PostgreStorage
from datastore.db_config import db_config

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

logger_config = LoggerConfig('Server')

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'super-secret'

# jwt = JWTManager(app)

postgres = PostgreStorage(db_config)

@app.route('/price_data')
def gets_data():
    """Retrieve price data."""
    try:
        data = postgres.select_price()
        logging.info('{str(data)}')
        return jsonify({'data': data})
    except Exception as e:
        logging.error('Error gets data : %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/currency_data')
def currency_data():
    """Retrieve currency data."""
    try:
        data = postgres.select_currency()
        logging.info('{str(data)}')
        return jsonify({'data': data})
    except Exception as e:
        logging.error('Error select currency data : %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/ticker_post', methods=['POST'])
def ticker_post():
    """Insert ticker data."""
    try:
        currency1 = request.json.get('currency1')
        currency2 = request.json.get('currency2')
        ticker = request.json.get('ticker')

        data = [currency1,currency2,ticker]
        postgres.insert_ticker(data)

        logging.info('Data inserted successfully')
        return jsonify({'message': 'Data inserted successfully'}), 200
    except Exception as e:
        logging.error('Error inserting ticker data : %s', str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/ticker_data')
def ticker_data():
    """Retrieve ticker data."""
    try:
        data = postgres.select_ticker()
        logging.info('{str(data)}')
        return jsonify({'data': data})
    except Exception as e:
        logging.error('Error selecting ticker data : %s', str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/ticker_delete', methods=['POST'])
def ticker_delete():
    """Delete ticker data."""
    try:
        ticker_name = request.json.get('data')  
        print(ticker_name)
        postgres.delete_ticker(ticker_name)
        logging.info("Row with ID %s deleted successfully", ticker_name)
        return jsonify({'message': f"Row with ID {ticker_name} deleted successfully"}), 200
    except Exception as e:
        logging.error('Error deleting ticker data : %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/ticker_update', methods=['POST'])
def ticker_update():
    """Update ticker data."""
    try:
        cur1 = request.json.get('currency1')
        cur2 = request.json.get('currency2')
        ticker = request.json.get('ticker')
        existing_ticker = request.json.get('existing_ticker')
        data = [cur1,cur2,ticker,existing_ticker]
        postgres.update_ticker(data)
        logging.info("Row with ID %s updated successfully", existing_ticker)
        return jsonify({'message': f"Row with ID {existing_ticker} updated successfully"}), 200
    except Exception as e:
        logging.error('Error updating ticker data : %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/price_list')
def display_data():
    """Display price list page."""
    try:
        logging.info('price_list.html')
        return render_template('price_list.html')
    except Exception as e:
        logging.error('Error displaying price list page: %s', str(e))
        return str(e), 500

@app.route('/ticker_list')
def ticker_list():
    """Display ticker list page."""
    try:
        logging.info('ticker_list.html')
        return render_template('ticker_list.html')
    except Exception as e:
        logging.error('Error displaying ticker list page: %s', str(e))
        return str(e), 500

@app.route('/navbar.html')
def navbar():
    """Display navbar."""
    try:
        logging.info('navbar.html')
        return render_template('navbar.html')
    except Exception as e:
        logging.error('Error displaying navbar: %s', str(e))
        return str(e), 500

@app.route('/styles.css')
def css():
    """Serve CSS styles."""
    try:
        logging.info('styles.css')
        return render_template('styles.css')
    except Exception as e:
        logging.error('Error serving CSS styles: %s', str(e))
        return str(e), 500

@app.route('/home')
def home():
    """Display home page."""
    try:
        logging.info('index.html')
        return render_template('index.html')
    except Exception as e:
        logging.error('Error displaying home page: %s', str(e))
        return str(e), 500
