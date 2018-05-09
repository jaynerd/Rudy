'use strict';

process.env.DEBUG = 'actions-on-google:*';

const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);

const paperDatabase = admin.database().ref('/paper');

exports.rudy = functions.https.onRequest((request, response) => {
	
  // Get the paper code from the request
  let paper = request.body.queryResult.parameters['paper']; // paper is a required param
  let major = request.body.queryResult.parameters['major'];
  // Get the requirement from the request
  let requirement = '';
  if (request.body.queryResult.parameters['requirement']) {
    requirement = request.body.queryResult.parameters['requirement'];
  }
  
  let requirement1 = '';
  
  if (request.body.queryResult.parameters['requirement1']){
	  requirement1 = request.body.queryResult.parameters['requirement1'];
  }
  if(major){
  paperDatabase.child(major).once('value', snap => {
	  const courseSet = snap.val().c1;
	      response.json({ 'fulfillmentText': "Here is the list of courses for " + major + ": "+courseSet +"." }); 
  });
	if(paper){
  paperDatabase.child(paper).once('value', snap => {
	  const prereq = snap.val().p;
	      response.json({ 'fulfillmentText': "Pre-requisite of " + paper + " is "+prereq +"." }); 
	});


  // Call get requirement
 // getRequirement(paper, requirement, requirement1).then((output) => {
//	  response.json({ 'fulfillmentText': output }); // Return the results of the getRequirement function to Dialogflow
 // }).catch(() => {
//	  response.json({ 'fulfillmentText': 'Unable to process your request. Please try with different sentence structures.' });
//  });
}}});
