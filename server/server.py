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
from dotenv import load_dotenv

from datastore.postgre import PostgreStorage
from datastore.db_config import db_config

from flask_httpauth import HTTPTokenAuth

load_dotenv()

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

logger_config = LoggerConfig('Server')

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

postgres = PostgreStorage(db_config)

# Hardcoded token
API_TOKEN = os.getenv('API_TOKEN')

# @app.route('/get_token')
# def get_token():
#     return jsonify({'token': API_TOKEN})

@auth.verify_token
def verify_auth_token(token):
    return token == API_TOKEN

@app.route('/protected')
@auth.login_required
def protected_route():
    return jsonify({'message': 'This is protected data, accessible only with the correct token.'})


def validate_ticker_data(currency1, currency2, ticker, postgres, existing_ticker=None):
    """Validate ticker data for adding or updating."""
    if not ticker:
        raise ValueError('Missing required field: Ticker')
    elif currency1 == currency2:
        raise ValueError('Currency1 cannot be the same as Currency2')
    elif postgres.ticker_exists(currency1, currency2, ticker) and ticker != existing_ticker:
        raise ValueError('Ticker already exists')

@app.route('/price_data')
@auth.login_required
def gets_data():
    """Retrieve price data."""
    try:
        data = postgres.select_price()
        # logging.info(str(data))
        return jsonify({'data': data})
    except Exception as e:
        logging.error('Error gets data : %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/currency_data')
@auth.login_required
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
@auth.login_required
def ticker_post():
    """Insert ticker data."""
    try:
        currency1 = request.json.get('currency1')
        currency2 = request.json.get('currency2')
        ticker = request.json.get('ticker')

        # Validate data
        validate_ticker_data(currency1, currency2, ticker, postgres)

        data = [currency1,currency2,ticker]
        postgres.insert_ticker(data)

        logging.info('Data inserted successfully')
        return jsonify({'message': 'Data inserted successfully'}), 200
    except ValueError as ve:
        logging.warning('Validation error: %s', str(ve))
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.error('Error inserting ticker data : %s', str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/ticker_data')
@auth.login_required
def ticker_data():
    """Retrieve ticker data."""
    try:
        data = postgres.select_ticker()
        logging.info('{str(data)}')
        return jsonify({'data': data})
    except Exception as e:
        logging.error('Error selecting ticker data : %s', str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/ticker_delete', methods=['DELETE'])
@auth.login_required
def ticker_delete():
    """Delete ticker data."""
    try:
        ticker_name = request.json.get('data')  
        postgres.delete_ticker(ticker_name)
        logging.info("Row with ID %s deleted successfully", ticker_name)
        return jsonify({'message': f"Row with ID {ticker_name} deleted successfully"}), 200
    except Exception as e:
        logging.error('Error deleting ticker data : %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/ticker_update', methods=['PATCH'])
@auth.login_required
def ticker_update():
    """Update ticker data."""
    try:
        currency1 = request.json.get('currency1')
        currency2 = request.json.get('currency2')
        ticker = request.json.get('ticker')
        existing_ticker = request.json.get('existing_ticker')
        data = [currency1,currency2,ticker,existing_ticker]

        # Validate data
        validate_ticker_data(currency1, currency2, ticker, postgres)

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
        return render_template('price_list.html', api_token=API_TOKEN)
    except Exception as e:
        logging.error('Error displaying price list page: %s', str(e))
        return str(e), 500

@app.route('/ticker_list')
def ticker_list():
    """Display ticker list page."""
    try:
        logging.info('ticker_list.html')
        return render_template('ticker_list.html', api_token=API_TOKEN)
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
    
@app.route('/footer.html')
def footer():
    """Display footer."""
    try:
        logging.info('footer.html')
        return render_template('footer.html')
    except Exception as e:
        logging.error('Error displaying footer : %s', str(e))
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
