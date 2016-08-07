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
    return mmeFMFAppToken

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
    
def setLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude): #we need UDID. apple does not appear to store this information, so for now, we have to do it automatically.
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
        return "Error changing location, status code <%s>!" % response.status_code
    else:
        return "Successfully changed location to <%s;%s>!" % (latitude, longitude)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='FMFLocationChanger')
    parser.add_argument("appleID", type=str, default=None, help="Apple ID")
    parser.add_argument("password", type=str, default=None, help="password")
    parser.add_argument("UDID", type=str, default=None, help="Unique Device Identifier")
    parser.add_argument("latitude", type=float, default=None, help="latitude")
    parser.add_argument("longitude", type=float, default=None, help="longitude")    
    args = parser.parse_args()

    user = args.appleID
    try: #in the event we are supplied with an DSID, convert it to an int
        int(user)
        user = int(user)
    except ValueError:
        pass
    passw = args.password
    latitude = args.latitude
    longitude = args.longitude
    UDID = args.UDID

    try:
        (DSID, authToken) = dsidFactory(user, passw)
    except:
        print "Error getting DSID and MMeAuthToken!\n%s" % dsidFactory(user, passw)
        sys.exit()
    try:
        mmeFMFAppToken = tokenFactory(DSID, authToken) #get tokens by using token.
    except:
        print "Error getting mmeFMFAppToken!\n%s" % tokenFactory(DSID, authToken)
        sys.exit()
    try:
        while True:
            print setLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude)
            os.system("sleep 30") #wait 30 seconds before going again.
    except Exception, e:
        print e
        sys.exit()
