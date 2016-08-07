# Poof!
Poof will change the location of your iOS device on Find my Friends to anywhere in the world!

To use Poof: python poof.py appleID password UDID latitude longitude

Apple does not appear to store UDID information as of iOS 9, so currently, you have to manually enter the UDID of the device that you want to spoof location data for. If you do not have or do not want to use your appleID / password, you can also use a MobileMeAuthToken.

Example: python poof.py johndoe@apple.com secretpassword LongAndRandomUDID 40.7484 -73.9857
This example will spoof the location of device with the UDID "LongAndRandomUDID" on the iCloud account "johndoe@apple.com" to 40.7484° N, 73.9857° W, which are the coordinates of the Empire State Building.

NOTE: Latitude coordinates that are north are positive (south are negative), and longitude coordinate that are west are negative (east are positive).

Future features: 
1.) Find the UDID of all devices linked to the iCloud account 
2.) Spoof location of FindMyiPhone (already coded, just need to implement into poof)
3.) Find Friends of Friends - Basically the same as FMF, but this will find the friends of any iCloud account, with just a MMeAuthToken! :D
