"use strict";

$(function() {
    $("#melodyForm").validate({
        rules: {
            note1: 'required',
            note2: 'required',
            length: 'required',
            genres: 'required',
            mode: 'required',
        },
        messages: {
            note1: "Please select a first note.",
            note2: "Please select a second note.",
            length: "Please enter a length.",
            genres: "Please select a genre.",
            mode: "Please select major or minor.",
        },
        submitHandler: function(form) {
            form.submit();
        }
    });
});

$(function() {
    $("#signupForm").validate({
        rules: {
            first_name: 'required',
            last_name: 'required',
            email:  {
                required: true,
                email: true
            },
            password: {
                required: true,
                minlength: 8,
            }
        },
        messages: {
            first_name: "Please enter your first name.",
            last_name: "Please enter your last name.",
            email: "Please enter a valid email address.",
            password: "Your password must be at least 8 characters long.",
        },
        submitHandler: function(form) {
            form.submit();
        }
    });
});

$(function() {
    $("#loginForm").validate({
        rules: {
            email:  {
                required: true,
                email: true
            },
        },
        messages: {
            email: "Please enter a valid email address.",
        },
        submitHandler: function(form) {
            form.submit();
        }
    });
});



