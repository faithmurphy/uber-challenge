"""
Creates an HTTP endpoint that accepts POST requests with JSON email data
which is then sent via HTTP request through Mailgun or Mandrill

author: Faith Murphy
"""

from flask import Flask, request, make_response
import json
import urllib2
import urllib
import re
import base64

app = Flask(__name__)

MAILGUN_API_KEY = "key"
MAILGUN_REQUEST_URL = "https://api.mailgun.net/v2/sandbox10101617827d47de87f5bf9debfa67c9.mailgun.org/messages"

MANDRILL_API_KEY = "key"
MANDRILL_URL = "https://mandrillapp.com/api/1.0"

VALID_POST_PARAMETERS = ['to', 'to_name', 'from', 'from_name', 'subject', 'body']
SERVER_ERROR_CODES = [500, 502, 503, 504]

@app.route('/email', methods=['POST'])
def email():

    if request.method == 'POST':
        if validateJSON(request.form):
            text = convertHTMLtoPlainText(request.form['body'])
            result =  send_email("Mailgun", request.form['to'], request.form['to_name'],
                                 request.form['from'], request.form['from_name'],
                                 request.form['subject'], text)
            if result == 200:
                return make_response("", 200)

            # If response > 500, then error is on Mailgun side. Try to use Mandrill
            elif result in SERVER_ERROR_CODES:
                response = send_email("Mandrill", request.form['to'], request.form['to_name'],
                                      request.form['from'], request.form['from_name'],
                                      request.form['subject'], text)

                return make_response("", response)
        return make_response("", 400)
    return make_response("", 405)

def send_email (service, to, to_name, from_address, from_name, subject, body):
    if service == "Mailgun":
        data={"from": from_name + ' <' + from_address +'>',
              "to": to_name + ' <' + to +'>',
              "subject": subject,
              "text": body}

        data = urllib.urlencode(data)
        req = urllib2.Request(MAILGUN_REQUEST_URL, data)

        req.add_header("Authorization", "Basic %s" % base64.encodestring("api:%s" % MAILGUN_API_KEY).strip())
        response = urllib2.urlopen(req)
        return response.getcode()

    else:
        message = {"key": MANDRILL_API_KEY, "message" : {"text" : body, "subject" : subject, "from_email" :
            from_address, "from_name" : from_name,  "to" : [{"email" : to, "name"
        : to_name, "type" : "to"}], "headers": {"Reply-To": from_address}}}

        req = urllib2.Request(MANDRILL_URL+'/messages/send.json', json.dumps(message), {'Content-Type' : 'application/json'})
        response = urllib2.urlopen(req)
        return response.getcode()


def convertHTMLtoPlainText(html):
    """ Converts the HTML to plain text by strips the HTML tags """
    return re.sub('<[^<]+?>', '', html)

def validateJSON(json):
    """ Validates that the fields are all present, not empty, and do not only contain whitespace"""
    if len(VALID_POST_PARAMETERS) == len(json.keys()):
        for key in VALID_POST_PARAMETERS:
            if (key not in json) or (len(json[key]) < 1) or (json[key].isspace() == True): #validate not empty
                return False
        return validateEmailAddresses(json)
    else:
        return False

def validateEmailAddresses(json):
    to = json['to']
    from_email = json['from']
    return (validateEmailAddressFormat(to) and validateEmailAddressFormat(from_email))

def validateEmailAddressFormat(email):
    """ Verify the address is well formatted (ex. only one @ ..)
     and that the email address is not just whitespace chars """
    if not (re.match(r"[^@]+@[^@]+\.[^@]+", email)) or (email.isspace()):
        return False
    return True

@app.errorhandler(404)
def page_not_found(error):
    return make_response("", 404)

if __name__ == '__main__':
    app.run()
