<h2>Markov Melodies</h2>

<h6>Overview: </h6>
Markov Melodies is an exploration into algorithmic musical composition. Given a small amount of user input, the application generates melodies via second-order Markov chains. Generated melody outcomes are then compared to user preferences for major and minor keys using classification machine learning techniques to find a suitable match. Users can share their melodies on their profile, follow other users, and like other users' melodies.

<h6>APIs:</h6>
<ul><li><strong><a href="https://developers.facebook.com/docs/facebook-login/web">Facebook OAuth:</a></strong> Enabling users to sign in via Facebook authentication.</li></ul>

<h6>Libraries:</h6>
<ul>
<li><strong><a href="http://scikit-learn.org/stable/">Scikit-Learn:</a></strong> Python machine learning module for crafting pipelines of various classification algorithm + feature vector combinations. Outcome melodies are then compared to these pipelines for probability predictions to determine if the melody is a match to user preferences.</li>
<li><strong><a href="http://www.chartjs.org/">ChartJS:</a></strong> Data visualization library for diplaying differences between machine learning techniques on the Results page.</li>
<li><strong><a href="http://web.mit.edu/music21/">Music21:</a></strong> MIDI-based music library which both provided seed files to craft Markov chains and handled the conversion between MIDI files to usable data.</li> 
<li><strong><a href="https://mdoege.github.io/PySynth/">PySynth:</a></strong> Library that synthesized wav files from melodies in abc notation. This module is rather limited in scope and not consistent, looking for an alternative.</li>
<li><strong><a href="http://www.vexflow.com/">VexFlow:</a></strong> Library used to build sheet music format to display notes on results page. Not super robust, as it doesn't handle obscure note durations.</li>
<li><strong><a href="https://github.com/sigmonky/webaudio/tree/master/html5piano/html5-piano_1315774273_demo_package">HTML5 Piano:</a></strong> Module used for front-end piano interface.</li>
</ul>

<h6>Deployment: </h6>
<p>This app is still in local development, not currently deployed.</p>

<h6>Future Improvements: </h6>
<ul>
<li>Further testing via Selenium (currently only unittest implemented)</li>
<li>More exploration into various classification algorithms, especially neural networks!</li>
<li>Soundcloud API integration for sharing melodies</li>
<li>Better edge case handling when Markov key not found</li>
<li>Find better synthesizer library and sheet music notation library</li>
<li>Modify app to craft melody based on duration as user input rather that number of notes</li>
</ul>


<h6>About: </h6>
<p>This application was built by Jacqueline Watts as part of a software engineering fellowship at Hackbright Academy. Please find additional portfolio pieces or contact information through <a href="https://github.com/jacquelineawatts">Github</a> or <a href="https://www.linkedin.com/in/jacquelinewatts">LinkedIn</a>.</p>