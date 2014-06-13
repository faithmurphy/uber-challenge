uber-challenge
==============

INSTALLATION:

Assure that Python and Flask are installed on the machine and modify the API keys for both Mandrill and Mailgun in challenge.py

DESIGN:

Python - I chose to use Python because I am familiar with it and after skimming the documentation for Flask I thought it would be easy to integrate the two pieces

Flask - I have never had to use a micro framework before and Flask looked simple and straightforward to use.

ASSUMPTIONS:

* That no outside Python libraries could be used for this challenge
* That the HTML that is sent in the POST request is valid. I could not find an easy to verify the HTML without downloading and importing an outside library
* That none of the inputted data could contain only whitespace characters
