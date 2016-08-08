# Poof!
Poof will change the location of your iOS device on Find my Friends and Find my iPhone to anywhere in the world!

To use Poof: *python poof.py UDID latitude longitude serviceSelect*

You enter your iCloud credentials in a secure prompt, as opposed to passing them in as arguments.

The serviceSelect argument allows you to spoof just FMF (pass in 1), just FMIP (pass in 2), or both (pass in 0).

Apple does not appear to store UDID information as of iOS 9, so currently, you have to manually enter the UDID of the device that you want to spoof location data for. If you do not have or do not want to use your appleID / password, you can also use a MobileMeAuthToken.

**Poof** will spoof your location every 5 seconds until you terminate the program. You can run it in the background and forget about it, or run it 24/7 on a device that can always be powered on, like the Raspberry Pi. You can run poof for years without it locking you out of your account, due to the way that poof retrieves authentication tokens.

**Example**: *python poof.py LongAndRandomUDID 40.7484 -73.9857*

This example will spoof the location of device with the UDID "LongAndRandomUDID" on the iCloud account "johndoe@apple.com" to 40.7484° N, 73.9857° W, which are the coordinates of the Empire State Building.

**NOTE**: Latitude coordinates that are north are positive (south are negative), and longitude coordinate that are west are negative (east are positive).

Future features: 
- [ ] Find the UDID of all devices linked to the iCloud account 
- [x] Spoof location of FindMyiPhone (already coded, just need to implement into poof)
- [ ] Find Friends of Friends - Basically the same as FMF, but this will find the friends of any iCloud account, with just a MMeAuthToken!
