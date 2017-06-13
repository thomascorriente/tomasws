#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):

    print(req.get("result").get("action"))
    
    if req.get("result").get("action") == "nombre":
        print("entro a nombre")
        result = req.get("result")
        parameters = result.get("parameters")
        nombre = parameters.get("nombre")
        print(nombre)
        #baseurl = "http://www.aeselsalvadormovil.com/aesmovil/WcfMovil/AESMovil.svc/GetInterrupciones/1244050"
        baseurl = "http://www.aeselsalvadormovil.com/aesmovil/WcfMovil/AESMovil.svc/GetDetalleFactura/2366498"
        yql_query = baseurl       
        yql_url = yql_query #baseurl + urlencode({'q': yql_query}) + "&format=json"
        print(yql_url)
        result = urlopen(yql_url).read()
        print(result)
        data = json.loads(result)
        print(data)
        dataWS=data.get('data')
        saldo_pagar=dataWS.get('saldo_pagar')
        print(saldo_pagar)
        res = makeWebhookResult(data)
        return {
        "speech": "nombre",
        "displayText": "nombre",
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
        }
    elif req.get("result").get("action") == "consultasaldo":
        print("Entro a consulta de saldo")
        result = req.get("result")
        parameters = result.get("parameters")
        NICJeson = parameters.get("NIC")
        print(NICJeson)
        NIC = NICJeson.get("number")
        print(NIC)
        #baseurl = "http://www.aeselsalvadormovil.com/aesmovil/WcfMovil/AESMovil.svc/GetInterrupciones/1244050"
        baseurl = "http://www.aeselsalvadormovil.com/aesmovil/WcfMovil/AESMovil.svc/GetDetalleFactura/" + str(NIC)
        result = urlopen(baseurl).read()
        print(result)
        data = json.loads(result)
        print(data)
        dataWS=data.get('data')
        saldo_pagar=dataWS.get('saldo_pagar')
        print(saldo_pagar)
        speech="Su saldo a pagar es:" + saldo_pagar
        return {
        "speech": speech,
        "displayText": speech,
        "source": "ConsultaSaldoAES"
        } 
    elif req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        print(yql_url)
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
        return res
    else:
        return {}


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "El dia de hoy, en " + location.get('city') + ": " + condition.get('text') + \
             ", la temperatura es " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
