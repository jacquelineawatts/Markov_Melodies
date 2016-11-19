var PIANO_KEYS = 88;

$(document).ready(function() {

	$(".white").mousedown(function () {
	  	toneId = $(this).attr('id');
			play_multi_sound('tone-'+toneId);
	 });

	$(".white").mouseup(function () {
	  	toneId = $(this).attr('id');
			//stop_multi_sound('tone-'+toneId, 'mouse');
	 });
 	
	$(".black").mousedown(function () {
	  	toneId = $(this).attr('id');
			play_multi_sound('tone-'+toneId);
	 });

	$(".black").mouseup(function () {
	  	toneId = $(this).attr('id');
			stop_multi_sound('tone-'+toneId, 'mouse');
	 });
 	
 	//Toggles and other stuffs
	$("#piano div.keyname").hide();
	$("#piano div.kbkeyname").hide();
	
	$("#toggleKeyNames").click(function () {
		$("#piano div.kbkeyname").hide();
		$("#toggleKeyboardKeysNames").removeClass('on');
		$("#piano div.keyname").toggle();
		$(this).toggleClass('on');
	 });
	 
	$("#toggleKeyboardKeysNames").click(function () {
		$("#piano div.keyname").hide();
		$("#toggleKeyNames").removeClass('on');
		$("#piano div.kbkeyname").toggle();
		$(this).toggleClass('on');
	 });
	 
	$("#Octaves").click(function () {
		$("#piano div.oN").toggle();
		$(this).toggleClass('on');
	 });
	 
	$("#Strings").click(function () {
		$("#pianoStrings").toggle();
		$(this).toggleClass('on');
	 });

	$("#switchLight").click(function () {
		$('body').toggleClass('FogOfWar');
		$('html').toggleClass('FogOfWar');
		$(this).toggleClass('off');
	 });

	$("div.pickColor").click(function () {
	  var color = $(this).css("background-color");
		$('body').toggleClass('FogOfWar');
	});


})


//ARRAY WITH ALL THE KEYS
//the array content starts from element 1 so eleemnt 0 i zero, empty, nada, 0 gree
var keyboardKeys = new Array (PIANO_KEYS); 
var k;

for (k=0;k < PIANO_KEYS; k++) {
	keyboardKeys[k] = eval("pKey"+k);
	//console.log(keyboardKeys[k]);
}

//LOOP trought all the  keyboard-piano keys
for (i=0; i <keyboardKeys.length; i++) {
		
		
		//BIND ON KEY DOWN
		$(document).bind('keydown', keyboardKeys[i], function (evt){
			
			//console.log("obajdam se ot funkciqta vutre " + evt.data.value +  evt.data.flag + evt.data.sound);
			
			//check the flag false - key is down, true - key is up
			if(evt.data.flag) {
			 evt.data.flag = false;
			 $(evt.data.value).addClass('pressed');
			 play_multi_sound(evt.data.sound);
			}
			
			return false;
		});


//$(document).bind('keydown', 'r',function (evt){ alert('adasd'); });

		//BIND ON KEY UP
		$(document).bind('keyup', keyboardKeys[i], function (evt){
			
			//console.log("obajdame se ot funkciqta vutre " + evt.data.value +  evt.data.flag + evt.data.sound);
			
			//check the flag false - key is down, true - key is up
			evt.data.flag = true; 
			$(evt.data.value).removeClass('pressed');
			//stop_multi_sound(evt.data.sound); //don't so cool as shoud
			
			return false; 
			
		});

}

var channel_max = 32;										// number of channels
audiochannels = new Array();

for (a=0;a<channel_max;a++) {									// prepare the channels
	audiochannels[a] = new Array();
	audiochannels[a]['channel'] = new Audio();						// create a new audio object
	audiochannels[a]['finished'] = -1;							// expected end time for this channel
	audiochannels[a]['keyvalue'] = '';
}


//PLAY SOUND
function play_multi_sound(s) {


	for (a=0;a <audiochannels.length; a++) {
		thistime = new Date();
		if (audiochannels[a]['finished'] < thistime.getTime()) {			// is this channel finished?
			
			//console.log(audiochannels[a]['keyvalue']);
			
			try
		  {		
					audiochannels[a]['finished'] = thistime.getTime() + document.getElementById(s).duration*1000;
					audiochannels[a]['channel'] = document.getElementById(s);
					audiochannels[a]['channel'].currentTime = 0;
					audiochannels[a]['channel'].volume=1;
					audiochannels[a]['channel'].play();
					audiochannels[a]['keyvalue'] = s;
					
					//console.log("the key is pressed - play");
					
					//console.log(audiochannels[a]['keyvalue']);

		  }
		  catch(v)
		  {	
		  	//show the error message (alert or log) or hide it when public
		    //alert(v.message);
		   //	console.log(v.message); 
		  }

			break;
		}
	}
}


function stop_multi_sound(s, sender) {

	for (a=0;a <audiochannels.length; a++) {
		
		//console.log('chanel keyvalue = '+audiochannels[a]['keyvalue']);

		if (audiochannels[a]['keyvalue'] == s) {			// is this channel finished?
			
			try
		  {
					audiochannels[a]['channel'] = document.getElementById(s);
					
					//audiochannels[a]['channel'].currentTime =  audiochannels[a]['channel'].duration;
					//audiochannels[a]['keyvalue'] = 'nema';
					
					if(sender != undefined && sender == 'mouse') {
						setTimeout ("audiochannels[a]['channel'].pause()", 2500 );
						setTimeout ("audiochannels[a]['channel'].currentTime = 0", 2500 );
					}else {
						//audiochannels[a]['channel'].volume=0;
						setTimeout ("audiochannels[a]['channel'].pause()", 2500 );
						setTimeout ("audiochannels[a]['channel'].currentTime = 0", 2500 );
					}
					
					//console.log("the key is UP - stop sound " + s + ' = ' + audiochannels[a]['channel'].duration + '== ' + audiochannels[a]['channel'].currentTime);
					//console.log(audiochannels[a]['keyvalue']);
		  }
		  catch(v)
		  {	
		  	//show the error message (alert or log) or hide it when public
		    //alert(v.message);
		   	console.log(v.message); 
		  }

			break;
		}
	}
}


	 