'use strict';

exports.requirementAdvice = (request, response) => {
	
  // Get the paper code from the request
  let paper = request.body.queryResult.parameters['paper']; // paper is a required param
  
  // Get the requirement from the request
  let requirement = '';
  if (request.body.queryResult.parameters['requirement']) {
    requirement = request.body.queryResult.parameters['requirement'];
  }
  
  let requirement1 = '';
  if (request.body.queryResult.parameters['requirement1']){
	  requirement1 = request.body.queryResult.parameters['requirement1'];
  }
  
  // Call get requirement
  getRequirement(paper, requirement, requirement1).then((output) => {
	  response.json({ 'fulfillmentText': output }); // Return the results of the getRequirement function to Dialogflow
  }).catch(() => {
	  response.json({ 'fulfillmentText': 'Unable to process your request. Please try with different sentence structures.' });
  });
};

function getRequirement (paper, requirement, requirement1) {
	return new Promise((resolve, reject) => {
		
	});
}
/* function callWeatherApi (city, date) {
  return new Promise((resolve, reject) => {


    // Make the HTTP request to get the weather
    http.get({host: host, path: path}, (res) => {
      let body = ''; // var to store the response chunks
      res.on('data', (d) => { body += d; }); // store each response chunk
      res.on('end', () => {
        // After all the data has been received parse the JSON for desired data
        let response = JSON.parse(body);
        let forecast = response['data']['weather'][0];
        let location = response['data']['request'][0];
        let conditions = response['data']['current_condition'][0];
        let currentConditions = conditions['weatherDesc'][0]['value'];

        // Create response
        let output = `Current conditions in the ${location['type']} 
        ${location['query']} are ${currentConditions} with a projected high of
        ${forecast['maxtempC']}°C or ${forecast['maxtempF']}°F and a low of 
        ${forecast['mintempC']}°C or ${forecast['mintempF']}°F on 
        ${forecast['date']}.`;

        // Resolve the promise with the output text
        console.log(output);
        resolve(output);
      });
      res.on('error', (error) => {
        console.log(`Error calling the weather API: ${error}`)
        reject();
      });
    });
  });
} */
    