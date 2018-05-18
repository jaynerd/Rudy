#!/usr/bin/env python

import os
import json

from flask import Flask
from flask import request
from flask import make_response

# flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    speech: str
    if request.get("result").get("action") == 'getRequisiteForPaper':
        speech = make_response({'fullfillmentText': 'HIHIHIHIHHI'})

    return speech


if __name__ == '__main__':
    # bind to PORT if defined, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    print('Starting Rudy on port %d' % port)
    app.run(debug=False, port=port, host='0,0,0,0')
