"""
Created on 2/19/2016
This script is desinged to create netCDF files using the netCDF4 module from python as
part of the Coastal Model Test Bed (CMTB)

@author: Spicer Bak
@contact: Spicer.Bak@usace.army.mil
"""
import numpy as np
import netCDF4 as nc
import csv, yaml
import datetime as DT
import time as ttime
import datetime as DT


def makenc_generic(inputfname, globalYaml, varYaml, data):
    """
    
    Args:
        inputfname:
        globalYaml:
        varYaml:
        data:
        
    Returns:

    """
    varMetData = import_template_file(varYaml)
    globalMetaData = import_template_file(globalYaml)
    fid = init_nc_file(inputfname, globalMetaData)
    # create dimensions
    _createDimensions(fid, varMetData, data)
    # write variables and data
    write_data_to_nc(fid, varMetData, data)
    fid.close()


def ncFile2ncFile(inputFile, globalYaml, varYaml, **kwargs):
    """Updates inputFile with new variables in varYaml and global Meta data in global Yaml
    
    Args:
        globalYaml:
        inputFile (object):
        varYaml:

    Keyword Args:
        'mesh data' a dictionary containing mesh topology
        
    Returns:

    """
    meshData = kwargs.get('meshData', None)
    dateCreated = DT.date.today()
    dateIssued = dateCreated
    geospatial_lon_min = None  # other spatial data
    time_coverage_start = '2015-09-18T22:00:00Z'
    time_coverage_end = '2015-09-18T22:00:00Z'
    print('!!!! TODO: how to handle geospatial netCDF conventions')
    print('!!!! TODO: how to handle time_coverage_start/end')
    globalMetaData = import_template_file(globalYaml)
    # update global metaData with file write date
    if 'dateCreated' not in globalMetaData:
        globalMetaData.update({'dateCreated': dateCreated.strftime('%Y-%m-%d')})
    else:
        globalMetaData['dateCreated'] = dateCreated.strftime('%Y-%m-%d')
    if 'dateIssued' not in globalMetaData:
        globalMetaData.update({'dateIssued': dateIssued.strftime('%Y-%m-%d')})
    else:
        globalMetaData['dateIssued'] = dateIssued.strftime('%Y-%m-%d')
    # read in variable metadata
    varMetData = import_template_file(varYaml)
    data_lib, dimensionLib, varMetaNetCDF, globalMetaNetCDF = readNetCDFfile(inputFile)
    # now combine netCDF variable and global metaData
    globalMetaData = _combineGlobalMetaData(globalMetaData, globalMetaNetCDF)
    varMetData = _combineVaribleMetaData(varMetData, varMetaNetCDF)
    
    # begin File writing proceedure
    ####### should this be its own function and the above be input specific (matlab, python, or netCDF file) ###########
    # create file
    fid = init_nc_file(inputFile, globalMetaData)
    # create dimensions
    inputFileDimensions = readDimensions(inputFile)
    _createDimensions(varMetData, inputFileDimensions)
    # write variables and data
    write_data_to_nc(fid, varMetData, data_lib)
    print('Write capability for compression to combine with significant digit attribute')
    fid.close()


def _combineGlobalMetaData(newGlobalMetaData, originalGlobalMetaData):
    """Combines global metadata from original file to new data.
    
    Function will combine two metadata dictionaries.  If there is a conflict with attribute name, function will take
    preference to the newGlobalMetaData values.
    
    Args:
        newGlobalMetaData: data takes preference over original metadata below
        originalGlobalMetaData: files original metaData

    Returns:
        globalMetaData dictionary that can be used in this package for writing netCDF files

    """
    return originalGlobalMetaData.update(newGlobalMetaData)


def _combineVaribleMetaData(newVarMetaData, oldVarMetaData):
    """Combines metatdata dictionaries for variables.
    
    Function will combine two metadata dictionaries.  If there is a conflict with attribute name, function will take
    preference to the newVarMetaData values.
    
    Args:
        newVarMetaData: input metadata dictionary from readNetCDFfile function
        oldVarMetaData: input metadata dictionary from import_template_file function

    Returns:
        variableMetaData dictionary
    """
    print('do stuff')
    
    return variableMetaData


def readNetCDFfile(inputFile):
    """Opens inputNetCDF file and creates dictionaries for data, dimensions, variable meta data and global metadata.
    
    Args:
        inputFile: input netCDF file

    Returns:
        data_lib, dimensionLib,  varMetaData, globalMetaData
        
    """
    ncfile = nc.Dataset(inputFile)
    dimensionLib = ncfile.dimensions
    data_Lib = ncfile.variables
    # now collect variables and metadata
    varMetaData = {'_variables': [], '_attributes': [], '_dimensions': []}
    globalMetaData = {}
    
    # First: get all global Metadata
    for att in ncfile.ncattrs():
        globalMetaData[att] = ncfile.getncattr(att)
    # Second: write dimensions
    for dd, dim in enumerate(dimensionLib):
        varMetaData['_dimensions'].append(dim)
    
    # Third: get variable names and attributes
    for ncVar in data_Lib:
        varMetaData['_variables'].append(ncVar)  # add variable to list of variables to write
        
        varMetaData[ncVar] = {
                'name':     data_Lib[ncVar].name,
                'dim':      list(data_Lib[ncVar].dimensions),
                'chunking': data_Lib[ncVar].chunking(),
                }
        for var in data_Lib[ncVar].ncattrs():  # add attributes to variable metadatalist
            varMetaData[ncVar][var] = data_Lib[ncVar].getncattr(var)
    
    ncfile.close()  # close file
    
    return data_Lib, dimensionLib, varMetaData, globalMetaData


def readDimensions(inputFile):
    """This function is not implemented yet, but desgned to read the dimensions from a netCDF file.
    
    Args:
        inputFile:

    Returns:

    """


def _createDimensions(fid, varMetaData, data):
    """
    
    Args:
        fid: file id of open netCDF file (should have global meta data by this point)
        varMetaData: varMetaData dictionary
        data: dictionary with dimension name and size

    Returns:
        None
    
    """
    for dim in varMetaData['_dimensions']:  # loop through each dimension
        # first check that dimensions have corresponding variables (CF assumption)
        assert (dim in varMetaData['_variables']), "dimension {} doesn't have a corresponding variable".format(dim)
        try:
            fid.createDimension(dim, len(data[dim]))
        except TypeError:  # in the event you have a np.array(1) -- singlton dimensionally zero so no len
            fid.createDimension(dim, np.size(data[dim]))


def import_template_file(yaml_location):
    """This function loads a yaml file and returns the attributes in dictionary.
    
    This function is Step 1 in netCDF file creation, open global and variable yamls. This was originally written by
    RPS ASA, further edited by Spicer Bak

    Args:
      yaml_location: yaml file location (local or absolute path)

    Returns:
        dictionary with variables from the yaml file

    """
    # load the template
    with open(yaml_location, 'r') as f:
        # use safe_load instead load
        vars_dict = yaml.safe_load(f)
    
    return vars_dict


def init_nc_file(nc_filename, attributes):
    """Create the netCDF file and write the Global Attributes.
    
    written by ASA

    will initalize netCDF file and set global attributes, write date created and issued to global meta data

    Args:
      nc_filename: output netCDF file name
      attributes: attributes from global yaml load

    Returns:
        open netCDF file ready for writing data

    """
    ncfile = nc.Dataset(nc_filename, 'w', clobber=True)
    
    # Write some Global Attributes
    for key, value in attributes.items():
        if value is not None:
            setattr(ncfile, key, value)
    
    dt_today = ttime.strftime("%Y-%m-%d")
    ncfile.date_created = dt_today
    ncfile.date_issued = dt_today
    
    return ncfile


def write_data_to_nc(ncfile, template_vars, data_dict):
    """This function writes the variables, data, and the variable attributes to the netCDF file.

    In the yaml, the "[variable]:" needs to be in the data dictionary, the output netcdf variable will take the name
    "name:"
    
    Args:
      ncfile: this is an already opened netCDF file with already defined dimensions
      template_vars (dict): variable and meta data associated with data_dict
      data_dict (dict): this is a dictionary with keys associated to those hopefully in template_vars, this holds the data

    Returns:
      netCDF file (still open)
      also returns error strings and count that were created during the data writing process

    """
    # Keep track of any errors found
    num_errors = 0
    error_str = ''
    
    # write some more global attributes if present
    if '_attributes' in template_vars:
        for var in template_vars['_attributes']:
            if var in data_dict:
                setattr(ncfile, var, data_dict[var])
    
    accept_vars = template_vars['_variables']
    # List all possible variable attributes in the template
    possible_var_attr = ['standard_name', 'long_name', 'coordinates', 'flag_values', 'flag_meanings', 'description',
                         'notes', 'positive', 'valid_min', 'valid_max', 'calendar', 'description', 'cf_role',
                         'missing_value', 'topology_dimension', 'node_coordinates', "face_node_connectivity",
                         "face_node_connectivity", "face_dimension", "start_index"]
    
    # Write variables to file
    for var in accept_vars:  # only write variables that were loaded from [_variables] attribute in .yaml file
        if var in data_dict:
            try:
                if "fill_value" in template_vars[var] and "least_significant_digit" in template_vars[var]:
                    if 'comp_level' not in template_vars[var]:  # set default
                        template_vars[var]['comp_level'] = 6  # set above default 4 level by package
                    new_var = ncfile.createVariable(template_vars[var]["name"],
                                                    template_vars[var]["data_type"],
                                                    template_vars[var]["dim"],
                                                    fill_value=template_vars[var]["fill_value"],
                                                    least_significant_digit=template_vars[var][
                                                        'least_significant_digit'],
                                                    zlib=True,
                                                    complevel=template_vars[var]['comp_level'])
                elif "fill_value" in template_vars[var]:
                    new_var = ncfile.createVariable(template_vars[var]["name"], template_vars[var]["data_type"],
                                                    template_vars[var]["dim"],
                                                    fill_value=template_vars[var]["fill_value"])
                else:
                    new_var = ncfile.createVariable(template_vars[var]["name"],
                                                    template_vars[var]["data_type"],
                                                    template_vars[var]["dim"])
                
                new_var.units = template_vars[var]["units"]
                
                # Write the attributes
                for attr in template_vars[var]:  # possible_var_attr:  # only write attributes listed in this list above
                    if attr in template_vars[var] and attr != 'name':
                        if template_vars[var][attr] == 'NaN':
                            setattr(new_var, attr, np.nan)
                        else:
                            setattr(new_var, attr, template_vars[var][attr])
                # Write the short_name attribute as the variable name
                if 'short_name' in template_vars[var]:
                    new_var.short_name = template_vars[var]["short_name"]
                else:
                    new_var.short_name = template_vars[var]["name"]
                # _____________________________________________________________________________________
                # Write the data (1D, 2D, or 3D)
                # ______________________________________________________________________________________
                if var == "station_name":
                    station_id = data_dict[var]
                    data = np.empty((1,), 'S' + repr(len(station_id)))
                    data[0] = station_id
                    new_var[:] = nc.stringtochar(data)
                elif len(template_vars[var]["dim"]) == 0:
                    try:
                        new_var[:] = data_dict[var]
                    except Exception as e:
                        new_var = data_dict[var]
                
                elif len(template_vars[var]["dim"]) == 1:
                    # catch some possible errors for frequency and direction arrays
                    if template_vars[var]["data_type"] == 'str':
                        for i, c in enumerate(template_vars[var]["data_type"]):
                            new_var[i] = data_dict[var][i]
                    else:
                        try:
                            new_var[:] = data_dict[var]
                        except IndexError as e:
                            try:
                                new_var[:] = data_dict[var][0][0]
                            except Exception:
                                raise e
                
                elif len(template_vars[var]["dim"]) == 2:
                    # create an empty 2d data set of the correct sizes
                    try:
                        # handles row vs col data, rather than transposing the array just figure out which it is
                        length = data_dict[var][0].shape[1]
                        if data_dict[var][0].shape[0] > length:
                            length = data_dict[var][0].shape[0]
                        
                        x = np.empty([data_dict[var].shape[0], length], dtype=np.float64)
                        for i in range(data_dict[var].shape[0]):
                            # squeeze the 3d array in to 2d as dimension is not needed
                            x[i] = np.squeeze(data_dict[var][i])
                        new_var[:, :] = x
                    except Exception as e:
                        # if the tuple fails must be right...right?
                        new_var[:] = data_dict[var]
                
                elif len(template_vars[var]["dim"]) == 3:
                    # create an empty 3d data set of the correct sizes
                    # this portion was modified by Spicer Bak
                    assert data_dict[
                               var].shape == new_var.shape, 'The data must have the Same Dimensions  (missing time?)'
                    x = np.empty([data_dict[var].shape[0], data_dict[var].shape[1], data_dict[var].shape[2]],
                                 np.float64)
                    for i in range(data_dict[var].shape[0]):
                        x[i] = data_dict[var][i]
                    new_var[:, :, :] = x[:, :, :]
            
            except Exception as e:
                num_errors += 1
                print(('ERROR WRITING VARIABLE: {} - {} \n'.format(var, str(e))))
    
    return num_errors, error_str