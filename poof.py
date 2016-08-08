import getpass
import argparse
import requests
import sys
import base64
import os
import plistlib

def tokenFactory(dsid, mmeAuthToken):
    mmeAuthTokenEncoded = base64.b64encode("%s:%s" % (dsid, mmeAuthToken))
    #now that we have proper auth code, we will attempt to get all account tokens.
    url = "https://setup.icloud.com/setup/get_account_settings"
    headers = {
        'Authorization': 'Basic %s' % mmeAuthTokenEncoded,
        'Content-Type': 'application/xml',
        'X-MMe-Client-Info': '<iPhone6,1> <iPhone OS;9.3.2;13F69> <com.apple.AppleAccount/1.0 (com.apple.Preferences/1.0)>'
    }
    response = requests.request(
        method='POST',
        url=url,
        headers = headers,
    )
    if response.status_code != 200:
        return "HTTP Error: %s" % response.status_code
    #staple it together & call it bad weather
    content = response.text
    mmeFMFAppToken = plistlib.readPlistFromString(content)["tokens"]["mmeFMFAppToken"]
    mmeFMIToken = plistlib.readPlistFromString(content)["tokens"]["mmeFMIPToken"]
    return (mmeFMFAppToken, mmeFMIToken)

def dsidFactory(uname, passwd): #can also be a regular DSID with AuthToken
    creds = base64.b64encode("%s:%s" % (uname, passwd))
    url = "https://setup.icloud.com/setup/authenticate/%s" % uname
    headers = {
        'Authorization': 'Basic %s' % creds,
        'Content-Type': 'application/xml',
    }
    response = requests.request(
        method='POST',
        url=url,
        headers=headers,
    )
    if response.status_code != 200:
        if response.status_code == 401:
            return "HTTP Error 401: Unauthorized. Are you sure the credentials are correct?"
        elif response.status_code == 409:
            return "HTTP Error 409: Conflict. 2 Factor Authentication appears to be enabled. You cannot use this script unless you get the your MMeAuthToken (generated either on your computer or your phone)."
        else:
            return "HTTP Error %s.\n" % response.status_code
    content = response.text
    DSID = int(plistlib.readPlistFromString(content)["appleAccountInfo"]["dsPrsID"]) #stitch our own auth DSID
    mmeAuthToken = plistlib.readPlistFromString(content)["tokens"]["mmeAuthToken"] #stitch with token
    return (DSID, mmeAuthToken)

def fmiSetLoc(DSID, mmeFMIToken, UDID, latitude, longitude):
    mmeFMITokenEncoded = base64.b64encode("%s:%s" % (DSID, mmeFMIToken))
    url = 'https://p04-fmip.icloud.com/fmipservice/findme/%s/%s/currentLocation' % (DSID, UDID)
    headers = {
        'Authorization': 'Basic %s' % mmeFMITokenEncoded,
        'X-Apple-PrsId': '%s' % DSID,
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
        'User-Agent': 'FMDClient/6.0 iPhone6,1/13F69',
        'X-Apple-Find-API-Ver': '6.0',
    }
    json = {
        "locationFinished": False,
        "deviceInfo": {
            "batteryStatus": "NotCharging",
            "udid": UDID,
            "batteryLevel": 0.50, #we set to 50% (arbitrary number)
            "isChargerConnected": False
        },
        "longitude": longitude,
        "reason": 1,
        "horizontalAccuracy": 65,
        "latitude": latitude,
        "deviceContext": {
        },
    }
    response = requests.request(
        method='POST',
        url=url,
        headers=headers,
        json=json,
    )
    if response.status_code != 200:
        return "Error changing FindMyiPhone location, status code <%s>!" % response.status_code
    else:
        return "Successfully changed FindMyiPhone location to <%s;%s>!" % (latitude, longitude)
    
def fmfSetLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude): #we need UDID. apple does not appear to store this information, so for now, we have to do it automatically.
    mmeFMFAppTokenEncoded = base64.b64encode("%s:%s" % (DSID, mmeFMFAppToken))
    url = 'https://p04-fmfmobile.icloud.com/fmipservice/friends/%s/%s/myLocationChanged' % (DSID, UDID)
    headers = {
        'host': 'p04-fmfmobile.icloud.com',
        'Authorization': 'Basic %s' % mmeFMFAppTokenEncoded,
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'FindMyFriends/5.0 iPhone6,1/9.3.2(13F69)',
        'Accept-Encoding': 'gzip, deflate',
        'X-Apple-Find-API-Ver': '2.0',
        'X-Apple-AuthScheme': 'Forever',
    }
    json = {
        "serverContext": {
            "authToken": "%s" % mmeFMFAppToken,
            "prsId": DSID,
        },
        "clientContext": {
            "appName": "FindMyFriends", #need for proper server response
            "appVersion": "5.0", #also need for proper server response
            "userInactivityTimeInMS": 5,
            #"deviceClass": "iPhone",
            #"productType": "iPhone6,1",
            "deviceUDID": "%s" % UDID, #This is quite important.
            "location": {
                "altitude": 57, #random number. can change.
                "longitude": "%s" % longitude,
                "source": "app",
                "horizontalAccuracy": 1.0, #perfect horizontal accuracy.
                "latitude": "%s" % latitude,
                "speed": -1,
                "verticalAccuracy": 1.0 #perfect vertical accuracy.
            }
        }
    }
    response = requests.request(
        method='POST',
        url=url,
        headers=headers,
        json=json,
    )
    if response.status_code != 200:
        return "Error changing FindMyFriends location, status code <%s>!" % response.status_code
    else:
        return "Successfully changed FindMyFriends location to <%s;%s>!" % (latitude, longitude)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='FMFLocationChanger')
    parser.add_argument("UDID", type=str, default=None, help="Unique Device Identifier")
    parser.add_argument("latitude", type=float, default=None, help="latitude")
    parser.add_argument("longitude", type=float, default=None, help="longitude")
    parser.add_argument("serviceSelect", type=int, default=None, help="0 for both, 1 for just FMF, 2 for just FMI")
    args = parser.parse_args()

    user = raw_input("Apple ID: ")
    try: #in the event we are supplied with an DSID, convert it to an int
        int(user)
        user = int(user)
    except ValueError: #otherwise we have an apple id and can not convert
        pass
    passw = getpass.getpass()
    latitude = args.latitude
    longitude = args.longitude
    UDID = args.UDID
    serviceSelect = args.serviceSelect #default to spoofing both

    try:
        (DSID, authToken) = dsidFactory(user, passw)
    except:
        print "Error getting DSID and MMeAuthToken!\n%s" % dsidFactory(user, passw)
        sys.exit()

    try:
        mmeFMFAppToken = tokenFactory(DSID, authToken)[0] #get tokens by using token.
    except:
        print "Error getting mmeFMFAppToken!\n%s" % tokenFactory(DSID, authToken)[0] #0 is the FMFAppToken
        sys.exit()

    try:
        mmeFMIToken = tokenFactory(DSID, authToken)[1]
    except:
        print "Error getting mmeFMIToken!\n%s" % tokenFactory(DSID, authToken)[1]
        sys.exit()

    try:
        while True:
            if serviceSelect == 0 or serviceSelect == 1 or serviceSelect == 2:
                if serviceSelect == 0: #do both
                    print fmiSetLoc(DSID, mmeFMIToken, UDID, latitude, longitude)
                    print fmfSetLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude)
                    print "Waiting 5 seconds to send FMI/FMF spoof again."
                    os.system("sleep 5") #wait 30 seconds before going again.
                elif serviceSelect == 1:
                    print fmfSetLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude)
                    print "Waiting 5 seconds to send FMF spoof again."
                    os.system("sleep 5")
                else: #serviceSelect is 2, wants FMI only.
                    print fmiSetLoc(DSID, mmeFMIToken, UDID, latitude, longitude)
                    print "Waiting 5 seconds to send FMI spoof again."
                    os.system("sleep 5")
            else:
                print "Service select must have a value of 0, 1, or 2."
                sys.exit()
    except KeyboardInterrupt:
        print "Ctrl-C. Stopping."
        sys.exit()
    except Exception, e:
        print e
        sys.exit()
