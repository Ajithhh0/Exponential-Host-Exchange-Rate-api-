import os
import yfinance as yf
from flask import Flask, request, make_response, jsonify
from dotenv import load_dotenv
from datetime import date
from flask_expects_json import expects_json
from jsonschema import ValidationError

app = Flask(__name__) 
load_dotenv()

# Define the JSON schema for the request body
schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "number"},
        "from_currency": {"type": "string", "pattern": "^[a-zA-Z]{3}$"},
        "to_currency": {"type": "string", "pattern": "^[a-zA-Z]{3}$"},
        "Date": {"type": "string", "format": "date"}
    },
    "required": ["amount", "from_currency", "to_currency"]
}


@app.route('/endpoint', methods=['POST'])
@expects_json(schema)
def convert_currency():
    try:
        # Validate the request body against the schema
        #jsonschema.validate(request.get_json(), schema)

        data = request.get_json()
        print(data)
        amount = float(data['amount'])
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        Date = data.get('date')

        # Optional date parameter
        if Date:
            # Get the exchange rates for the specified currencies and date
            historical_data = yf.download(from_currency+to_currency+'=X', start="2004-01-01", end=date)
            if not historical_data.empty:
                rate = historical_data['Close'][0]
            else:
                return "Error getting historical exchange rates"
        else:
            # Get the latest exchange rate for the specified currencies
            latest_data = yf.download(from_currency+to_currency+'=X', period='1d')
            if not latest_data.empty:
              rate = latest_data['Close'][0]
            else:
                return "Error getting latest exchange rates"

        converted_amount = amount * rate
        return jsonify({"result": converted_amount})
    except jsonschema.exceptions.ValidationError as e:
        # Return a 400 Bad Request if the request body doesn't match the schema
        return f"Invalid request: {e.message}", 400
    except Exception as e:
        print(e)       
        return "something went wrong",500
@app.errorhandler(400)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        orginal_error = error.description
        return make_response(jsonify({"error":orginal_error.message}),400)

if __name__ == '__main__':
    app.run(port=os.getenv('PORT'))
    