# Poof!
Poof will spoof the location of your iOS device on Find my Friends and Find my iPhone to anywhere in the world!

**To use Poof:** *python poof.py*

Poof allows you to spoof just FMF, just FMIP, or both.

Apple does not appear to store UDID information as of iOS 9, so currently, you have to manually enter the UDID of the device that you want to spoof location data for. If you do not have or do not want to use your appleID / password, you can also use a MobileMeAuthToken.

**Poof** will spoof your location every 5 seconds until you terminate the program. You can run it in the background and forget about it, or run it 24/7 on a device that can always be powered on, like the Raspberry Pi. You can run poof for years without it locking you out of your account, due to the way that poof retrieves authentication tokens.

**Example**: *python poof.py* 

Username: johndoe@apple.com
Password: secretPassword
Latitude: 40.7484
Longitude: -73.9857
UDID: LongAndRandomUDID 
Service Select: 2

This example will spoof the location of device with the UDID "LongAndRandomUDID" on the iCloud account "johndoe@apple.com" to 40.7484° N, 73.9857° W, which are the coordinates of the Empire State Building, on both FMF and FMIP. 

If you enter an invalid UDID, poof will not be able to verify if the location has been spoofed. So make sure that the UDID is valid.

**NOTE**: Latitude coordinates that are north are positive (south are negative), and longitude coordinate that are west are negative (east are positive).

Future features: 
- [ ] Find the UDID of all devices linked to the iCloud account 
- [ ] Find Friends of Friends - Basically the same as FMF, but this will find the friends of any iCloud account, with just a MMeAuthToken!
- [ ] Confirm that the location has changed by making a request to iCloud to get the location of the device in question. This causes problems, however, if you pass in only your MMeAuthToken.
- [ ] Pull old location from iCloud instead of IP address. See above note for possible issues with this.
