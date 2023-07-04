import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import glob

def read_emlid_pos(fldrlistPPK, plot=False):
    """read and parse multiple pos files in multiple folders provided
    
    :param fldrlistPPK: list of folders to provide
    :param plot: if a path name will save a QA/QC plots (default=False)
    :return:
    """
    T_ppk = pd.DataFrame()
    for fldr in sorted(fldrlistPPK):
        # this is before ppk processing so should agree with nmea strings
        fn = glob.glob(os.path.join(fldr, "*.pos"))[0]
        try:
            colNames = ['datetime', 'lat', 'lon', 'height', 'Q', 'ns', 'sdn(m)',  'sde(m)', 'sdu(m)', \
                        'sdne(m)', 'sdeu(m)',  'sdun(m)', 'age(s)',  'ratio']
            Tpos = pd.read_csv(fn, delimiter=r'\s+ ', header=10, names=colNames, engine='python')
            print(f'loaded {fn}')
            if all(Tpos.iloc[-1]):  #if theres nan's in the last row
                Tpos = Tpos.iloc[:-1] # remove last row
            T_ppk = pd.concat([T_ppk, Tpos]) # merge multiple files to single dataframe
        
        except:
            continue
    T_ppk['datetime'] = pd.to_datetime(T_ppk['datetime'], format='%Y/%m/%d %H:%M:%S.%f')
    
    
    # now make plot of both files
    # first llh file
    # plt.plot(T_LLH['lon'], T_LLH['lat'], '.-m', label = 'LLH file')
    # plt.xlabel('longitude')
    # plt.ylabel('latitude')
    if plot is not False:
        plt.plot(T_ppk['lon'], T_ppk['lat'], '.-g', label = 'PPK file')
        plt.xlabel('longitude')
        plt.ylabel('latitude')
        plt.legend()
        plt.tight_layout()
        plt.savefig(plot+'Lat_Lon')
        plt.close()
        
        fig = plt.figure()
        plt.plot(T_ppk['datetime'], T_ppk['height'], label='elevation')
        plt.plot(T_ppk['datetime'], 10 * T_ppk['Q'], '.', label='quality factor')
        plt.plot(T_ppk['datetime'], 10000 * (T_ppk['lat'] - T_ppk['lat'].iloc[0]), label='lat from original lat')
        plt.xlabel('time')
        plt.legend()
        plt.tight_layout()
        plt.savefig(plot+'elev_Q')
        plt.close()
