meSpeak.loadConfig("{{ url_for('static', filename='mespeak_config.json') }}");
meSpeak.loadVoice("{{ url_for('static', filename='en.json') }}");

var speech = false;
var id;
var state = "start";
var params = "";

var recognition = new webkitSpeechRecognition();
recognition.onresult = function(event) { 
	document.getElementById("listening").style.visibility = "hidden";
	text = event.results[0][0].transcript;
	document.getElementById("chatTable").innerHTML += "<tr><td>" + text + "</td></tr>";
  	getResponse(text);
}

function recognize(success){
	if(success && speech){
		recognition.start();
		document.getElementById("listening").style.visibility = "visible";
	}	
// if(!success){
	// 	document.getElementById("listening").innerHTML = "Connection lost. Refresh page.";
	// 	document.getElementById("listening").style.visibility = "visible";
		
	// }
}

function getResponse(text){
	var xmlHttp = null;
	xmlHttp = new XMLHttpRequest();
	var url = "srcdhall?state=" + state
	if(text.length > 0){
		url += "&text=" + text
	}
	xmlHttp.open( "GET", url, false );
	if(params.length > 0){
		xmlHttp.setRequestHeader("params", params)
	}
	xmlHttp.send();
	responseJSON = xmlHttp.responseText;
	responseObject = JSON.parse(responseJSON);
	state = responseObject.state;
	params = responseObject.params;
	document.getElementById("chatTable").innerHTML += "<tr><td>" + responseObject.response + "</td></tr>";
	if(state == "end"){
		id = meSpeak.speak(responseObject.response);
		speech = false;
	} else {
		id = meSpeak.speak(responseObject.response, {}, recognize);
	}
}

function onButtonClick(){
	if(speech == false){
		speech = true;
		state = "start";
		text = "";
		params = "";
		document.getElementById("chatTable").innerHTML = "";
		document.getElementById("button").value = "Stop Dialogue";
		getResponse("")	
	} else {
		speech = false;
		document.getElementById("button").value = "Start Dialogue";
		meSpeak.stop(id);
		recognition.stop();
	}
}