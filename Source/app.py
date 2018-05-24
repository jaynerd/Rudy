#!/usr/bin/env python

# ----------------------------------REGION IMPORT---------------------------------- #

# Importing os to access core libraries of Heroku including secured config vars.
import os

# Importing json to manage communication contents in the acceptable json format.
import json

# Importing firebase_admin to authenticate server's Firebase database access.
import firebase_admin

# credentials will be used to confirm identification of the service key provided in
# Heroku's config vars.
from firebase_admin import credentials

# db will be the main database that Rudy will be accessing.
from firebase_admin import db

# Flask package will manage flow of communications between the server and client.
# 1. jsonify will be used for translating Rudy's response into an acceptable json
# format.
# 2. make_response will pass the text response from Heroku app (Rudy) to client's
# Dialogflow view.
# 3. request components contains json format messages from the client side (input).
from flask import Flask, jsonify, make_response, request

# --------------------------------END_REGION IMPORT-------------------------------- #


# ----------------------------------REGION GLOBAL---------------------------------- #

# Starting flask app in global layout.
app = Flask(__name__)

# Database url (Firebase).
db_url = {'databaseURL': 'https://rudy-b5e54.firebaseio.com'}

# Secured service account key json from Heroku's config vars.
key = {"type": os.environ['type'],
       "project_id": os.environ['project_id'],
       "private_key_id": os.environ['private_key_id'],
       "private_key": os.environ['private_key'].replace('\\n', '\n'),
       "client_email": os.environ['client_email'],
       "client_id": os.environ['client_id'],
       "auth_uri": os.environ['auth_uri'],
       "token_uri": os.environ['token_uri'],
       "auth_provider_x509_cert_url": os.environ['auth_provider_x509_cert_url'],
       "client_x509_cert_url": os.environ['client_x509_cert_url']}

# Authentication process into Firebase.
print('Rudy (Firebase): Connecting to Firebase.')
cred = credentials.Certificate(key)
firebase = firebase_admin.initialize_app(cred, db_url)
print(firebase)
print('Rudy (Firebase): Firebase access granted.')

# Generating database references.
db_requisites = db.reference('requisites')
db_majors = db.reference('majors')
db_major_list = db.reference('major-list')


# --------------------------------END_REGION GLOBAL-------------------------------- #


# ---------------------------------REGION WEBHOOK---------------------------------- #

# The fulfillment webhook settings in Dialogflow should have a url that ends with
# '/webhook'. For example, if an Heroku app has a url of rudybot.app, the finalized
# Dialogflow's webhook integration address should be 'rudybot.app/webhook'. Upon
# generating a successful server-client connection, the client request will be rout
# -ed to the webhook function below.
@app.route('/webhook', methods=['POST'])
def webhook():
    # Get a request from client then print.
    req = request.get_json(silent=True, force=True)
    print('Rudy (Flask): Request received ->')
    print(json.dumps(req, indent=4))

    # Process the request to get a response.
    res = process_request(req)

    # Returning acquired response in json format to the client's Dialogflow view.
    return make_response(res)


# Sorting out client's request then forward to a matching function based on the
# action parameter of the request's intent.
def process_request(req):
    print('Rudy (Heroku): Request processing started.')

    # Request sorting process.
    result: str
    if req['queryResult'].get('action') == 'getPaperRequisites':
        result = get_paper_requisites(req)
    elif req['queryResult'].get('action') == 'getMajorDetails':
        result = get_major_details(req)
    elif req['queryResult'].get('action') == 'getMajorList':
        result = get_major_list(req)

    # Show the response log before jsonify.
    print('Rudy (Heroku): Generated response ->')
    print(result)

    # Returning the result in the acceptable json format.
    return jsonify({'fulfillmentText': result})


# -------------------------------END_REGION WEBHOOK-------------------------------- #


# --------------------------------REGION PARAMETERS-------------------------------- #

# Get required parameters (papers & requirements) from the request for a database
# query.
def get_paper_requisites(req):
    print('Rudy (Flask): Extracting required parameters. (papers)')

    # Getting parameters.
    speech = ''
    paper = req['queryResult']['parameters'].get('paper')
    requisites = [req['queryResult']['parameters'].get('requisite'),
                  req['queryResult']['parameters'].get('requisite1')]

    # Query creation.
    print('Rudy (Heroku): Requisites query created.')
    requisites_query = make_requisites_query(paper, requisites)

    # Parsing query results into a speech format.
    counter = 0
    for result in requisites_query:
        if result is None:
            print('Rudy (Firebase): Requisites query is empty.')
            speech += 'There are no ' + requisites[counter] + ' for paper: ' \
                      + paper + '. '
        else:
            print('Rudy (Firebase): Parsing query results.')
            speech += 'The list of ' + requisites[counter] + ' are: ' \
                      + str(result).strip('[]') + '. '
        counter += 1

    # Returning the speech contexts.
    return speech


# Get required parameters (majors) from the request for a database query.
def get_major_details(req):
    print('Rudy (Flask): Extracting required parameters. (majors)')

    # Getting parameters.
    speech = ''
    major = req['queryResult']['parameters'].get('major')

    # Query creation.
    print('Rudy (Heroku): Major details query created.')
    details_query = make_details_query(major)

    # Parsing query results into a speech format.
    counter = 1
    for result in details_query:
        if result is None:
            print('Rudy (Firebase): Major details query is empty.')
            speech += 'There are no Year ' + str(counter) + ' courses for ' \
                      + major + ' major. '
        else:
            print('Rudy (Firebase): Parsing query results.')
            speech += 'The list of suggested courses for Year ' + str(counter) \
                      + ' are: ' + str(result).strip('[]') + '. '
        counter += 1

    # Returning the speech contexts.
    return speech

def get_major_list(req):
    print('Rudy (Flask): Extracting required parameters. (majors)')

    # Getting parameters.
    speech = ''
    majorlist = req['queryResult']['parameters'].get('major-list')

    # Query creation.
    print('Rudy (Heroku): Major details query created.')
    list_query = make_majorlist_query(majorlist)

    # Parsing query results into a speech format.
    for result in list_query:
        if result is None:
            print('Rudy (Firebase): Major details query is empty.')
            speech += 'There are no majors.'
        else:
            print('Rudy (Firebase): Parsing query results.')
            speech += 'The majors offered in the BCIS department are: ' + str(result).strip('[]') + '.'

    return speech 


# ------------------------------END_REGION PARAMETERS------------------------------ #


# -----------------------------------REGION QUERY---------------------------------- #

# Get requisite data source from Firebase based on the request parameters.
def make_requisites_query(paper, requisites):
    print('Rudy (Firebase): Accessing to the database.')

    # Making a list of query results for multiple requisite parameters.
    query_result = [db_requisites.child(paper).child(requisites[0]).get()]

    # If client asks about two different types of requite parameters.
    if requisites[1] is not '' and requisites[0] is not requisites[1]:
        query_result.append(db_requisites.child(paper).child(requisites[1]).get())

    # Returning collected query results.
    return query_result


# Get major details data source from Firebase based on the request parameters.
def make_details_query(major):
    print('Rudy (Firebase): Accessing to the database.')

    # Making a list of query results for multiple year details for the major.
    query_result = [[db_majors.child(major).child('Year 1').get()],
                    [db_majors.child(major).child('Year 2').get()],
                    [db_majors.child(major).child('Year 3').get()]]

    # Returning collected query results.
    return query_result

def make_majorlist_query(major):
    print('Rudy (Firebase): Accessing to the database.')

    query_result = [[db_major_list.get()]]

    return query_result

# ---------------------------------END_REGION QUERY-------------------------------- #


# Initializing the app to server connection (hosting).
if __name__ == '__main__':
    # Setting the default port to 5000. Other defined values can be used as an
    # alternative.
    port = int(os.getenv('PORT', 5000))
    print('Rudy (Heroku): Starting Rudy on port %d' % port)
    app.run(debug=True, port=port, host='0.0.0.0')
