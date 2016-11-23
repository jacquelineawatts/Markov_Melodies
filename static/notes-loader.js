"use strict";

$('#note1').hide();
$('#note2').hide();
$('#note3').hide();

var notesLoop = function(){
    console.log('Im here');
    $('#note1').fadeIn(500).fadeOut(500);
    setTimeout(function() {
        $('#note2').fadeIn(500).fadeOut(500);
    }, 1000);
    setTimeout(function(){
        $('#note3').fadeIn(500).fadeOut(500);
    }, 2000);
};

$('#melodyForm').on('submit', function(evt) {
    $("#full-page").empty();
    // $("#musical-notes-loader").html('<center>LOOK AT ME!</center>');
    notesLoop();
    var timer = 0;
    for (var i=0; i<5; i++){
        timer = timer + 3000;
        setTimeout(function (){ 
            notesLoop();}, timer);
    }
});
