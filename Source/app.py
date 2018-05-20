#!/usr/bin/env python

import os
import re
import json
import firebase_admin

from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)
db_url = {'databaseURL': 'https://rudy-b5e54.firebaseio.com'}


def authenticate():
    key = {
        "type": os.environ['type'],
        "project_id": os.environ['project_id'],
        "private_key_id": os.environ['private_key_id'],
        "private_key": os.environ['private_key'].replace('\\n', '\n'),
        "client_email": os.environ['client_email'],
        "client_id": os.environ['client_id'],
        "auth_uri": os.environ['auth_uri'],
        "token_uri": os.environ['token_uri'],
        "auth_provider_x509_cert_url": os.environ['auth_provider_x509_cert_url'],
        "client_x509_cert_url": os.environ['client_x509_cert_url']}

    return key


key = authenticate()
cred = credentials.Certificate(key)
firebase_admin.initialize_app(cred, db_url)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print('Request from client:')
    print(json.dumps(req, indent=4))

    res = str(process_request(req))
    print('Response from Rudy:')
    print(res)

    return make_response(jsonify({'fulfillmentText': res}))


def process_request(req):
    print('Started processing the received request.')
    res: object
    if req['queryResult'].get('action') == 'getPaperRequisites':
        db_requisites = db.reference('requisites')
        res = get_paper_requisites(req, db_requisites)
    print(res)
    return res


def get_paper_requisites(req, db_requisites):
    res: object
    paper = req['queryResult']['parameters'].get('paper')
    requisite = req['queryResult']['parameters'].get('requisite')
    requisite1 = ''
    if req['queryResult']['parameters'].get('requisite1'):
        requisite1 = req['queryResult']['parameters'].get('requisite1')
    print('Requisites query created.')
    requisites_query = make_requisites_query(db_requisites, paper, requisite, requisite1)
    if requisites_query is None:
        print('Requisites query is empty.')
    res = requisites_query
    print(res)
    return res


def make_requisites_query(db_requisites, paper, requisite, requisite1):
    speech: str
    requisite_result = db_requisites.child(paper).child(requisite).get()

    if requisite_result is None:
        print(requisite_result)
        # requisite_result='No '+requisite+' are exist.'
    else:
        # requisite_result="The list of "+requisite+" are"+str(requisite_result)
        print(requisite_result)

    # requisite1_result: str
    # if requisite1 is not '':
    #     requisite1_result = db_requisites.child(paper).child(requisite1).get()
    #     if requisite1_result is None:
    #         print(requisite1_result)
    #     else:
    #         print(requisite1_result)

    return requisite_result

    # print(db.reference('degrees').child('Bachelor of Applied Science').get())


if __name__ == '__main__':
    # Set default PORT value as 5000, a pre-defined value can be used also.
    port = int(os.getenv('PORT', 5000))
    print('Starting Rudy on port %d' % port)
    app.run(debug=True, port=port, host='0.0.0.0')
