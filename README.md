# Yellowfin s500 Data Acquisition and Processing

1.  S500 sonar data post processing:

    See readme.md here for instructions on MATLAB scripts (including compiled executables) to process s500 and reach GNSS sonar data: <https://github.com/developer-ics/s500_DataAcq_PostProcessing/tree/main/ProcessingScripts_Latest_Stable>

    The compiled executables are located in:

    <https://github.com/developer-ics/s500_DataAcq_PostProcessing/tree/main/ProcessingScripts_Latest_Stable/MatlabRuntimeCompiledExes/YellowFin_Processing>

    The run time environment can be installed using:

    <https://github.com/developer-ics/s500_DataAcq_PostProcessing/blob/main/ProcessingScripts_Latest_Stable/MatlabRuntimeCompiledExes/YellowFin_Processing/for_redistribution/MyAppInstaller_web.exe>

2.  Data Acquisition:

    See this readme.md for more information on Python scripts that reside onboard the yellowfin USV to acquire data from the s500 echosounder:

    https://github.com/developer-ics/s500_DataAcq_PostProcessing/tree/main/DataAcquisition_On_USV

3.  Data Visualization:

    The Yellowfin Raspberry PI datalogger sends realtime depth information to the Pixhawk Cube, which in turn transmits this to the Basestation via MAVLink. The following python script is required on the Basestation PC to view this data. More information is in the readme.md:

    [https://github.com/developer-ics/s500_DataAcq_PostProcessing/tree/main/DataAcquisition_BaseStation](https://github.com/developer-ics/s500_DataAcq_PostProcessing/tree/main/DataAcquisition_BaseStation%20)
