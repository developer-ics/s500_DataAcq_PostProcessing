The data you have requested is divided into the following files: 
   - igr22916.sp3
   - mafa3430.23o
   - mafa.log.txt
   - mafa3430.23g
   - mafa3430.23n


UFCORS FILE TYPES AND NAMING CONVENTIONS
=========================================

You will have received one or more of the following files in response to your request:

  Type of File      Contents                              Name
_____________________________________________________________________________
  Observation       GNSS code and phase data              SSSSDDD0.YYo
  Navigation        Broadcast GPS orbit information       SSSSDDD0.YYn
  Navigation        Broadcast GLONASS orbit information   SSSSDDD0.YYg  
  IGS Ephemeris     Precise GPS orbit information         igZWWWWX.sp3
                    Precise GLONASS orbit information     igZWWWWX.sp3
                    Rapid GPS orbit information           igZWWWWX.sp3
                    Ultra-Rapid GPS orbit information     igZWWWWX_HH.sp3                     
  Coordinates       Position and velocity of CORS site    SSSS_08.coord.txt
  Log               Current and historical info. for site SSSS.log.txt
  Datasheet         Descriptive information for site      SSSS.ds
______________________________________________________________________________

  SSSS = Four character site ID
  DDD  = 3-digit Day-of-year when data was observed 
  YY   = Year when data was observed
  Z    = s - precise GPS orbit (available approximately within 14 days)
	 l - precise GLONASS orbit (available approximately within 14 days)
	 r - rapid GPS orbit (available within 48 hours)
         u - ultra-rapid GPS orbit (available within 12 hours)
  WWWW = GPS week number
  X    = 0 - for Sunday
	 1 - for Monday
	 2 - for Tuesday
	 3 - for Wednesday
	 4 - for Thursday
	 5 - for Friday
	 6 - for Saturday
  HH   = two-digit hour

DATA FORMAT
===========

The observation and navigation files are in RINEX format version 2.11
For format details see https://files.igs.org/pub/data/format/rinex211.txt

IGS Ephemeris data files are supplied in the SP3 format version c.
For format details see https://files.igs.org/pub/data/format/sp3.txt


SOFTWARE TO TRANSFORM EPHEMERIS FILES from SP3c to SP3a AVAILABLE
-------------------------------------------------------------------
Since January 29th, 2006 the International GNSS Service (IGS) began
making its precise ephemeris files available only in the SP3-c format.  

To convert a file from SP3-c format to the older SP3-a format, there is a 
compiled executable file for Windows NT/2000/XP, and source code is also 
available at:

    https://geodesy.noaa.gov/orbits/

Last Updated: 2021-07-14
