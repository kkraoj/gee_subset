#!/usr/bin/env python

# Google Earth Engine (GEE) Subset package
# 
# Easy subsetting of remote sensing
# time series for processing external
# to GEE.
# 
# This in parts replaces the ORNL DAAC
# MODIS subsets, but extends it to higher
# resolution date such as Landsat and
# Sentinel. It should also work on all
# other gridded products using the same
# product / band syntax.

# load required libraries
import os, argparse
from datetime import datetime
import pandas as pd
import ee
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 200)

# parse arguments in a beautiful way
# includes automatic help generation
def getArgs():

   # setup parser
   parser = argparse.ArgumentParser(
    description = '''Google Earth Engine subsets script: 
                    Allows for the extraction of remote sensing product
                    time series for most of the data available on
                    Google Earth Engine. Locations need to be specied as
                    either a comma delimited file or an explicit latitude
                    and longitude using command line arguments.''',
    epilog = '''post bug reports to the github repository''')
   parser.add_argument('-p',
                       '--product',
                       help = 'remote sensing product available in GEE',
                       required = True)
                       
   parser.add_argument('-b',
                       '--bands',
                       help = 'band name(s) for the requested product',
                       nargs = "+",
                       required = True)
                       
   parser.add_argument('-s',
                       '--start',
                       help = 'start date of the time series (yyyy-mm-dd)',
                       default = "2013-01-01")
                       
   parser.add_argument('-e',
                       '--end',
                       help = 'end date of the time series (yyyy-mm-dd)',
                       default = "2014-12-31")
                       
   parser.add_argument('-pd',
                       '--pad',
                       help = '''grow sampling location 
                       in km east west north south''',
                       default = 0,
                       type = float)

   parser.add_argument('-sc',
                       '--scale',
                       help = '''scale in meter, match the native resolution of
                       the data of interest otherwise mismatches in scale will result in
                       high pixel counts and a system error''',
                       default = "30")

   parser.add_argument('-l',
                       '--location',
                       nargs = 2,
                       help = '''geographic location as latitude longitude
                       provided as -loc latitude longitude''',
                       default = 0,
                       type = float)

   parser.add_argument('-f',
                       '--file',
                       help = '''path to file with geographic locations
                        as provided in a csv file''',
                       default = 0)
                       
   parser.add_argument('-d',
                       '--directory',
                       help = '''directory / path where to write output when not
                       provided this defaults to output to the console''',
                       default = 0)  
                                        
   parser.add_argument('-v',
                       '--verbose',
                       help = '''verbose debugging''',
                       default = False)  
   # put arguments in dictionary with
   # keys being the argument names given above
   return parser.parse_args()

# GEE subset subroutine 
def gee_subset(product = None,
              bands = None,
              start_date = None,
              end_date = None,
              latitude = None,
              longitude = None,
              scale = None,
              pad = 0):

   # fix the geometry when there is a radius
   # 0.01 degree = 1.1132 km on equator
   # or 0.008983 degrees per km (approximate)
   if pad > 0 :
    pad = pad * 0.008983 

   # setup the geometry, based upon point locations as specified
   # in the locations file or provided by a latitude or longitude
   # on the command line / when grow is provided pad the location
   # so it becomes a rectangle (report all values raw in a tidy
   # matrix)
   if pad:
     geometry = ee.Geometry.Rectangle(
       [longitude - pad, latitude - pad,
       longitude + pad, latitude + pad])
   else:
     geometry = ee.Geometry.Point([longitude, latitude])

   # define the collection from which to sample
   col = ee.ImageCollection(product).\
    filterDate(start_date, end_date).\
    filter(ee.Filter.eq('transmitterReceiverPolarisation', bands))
#    filter(ee.Filter.listContains('transmitterReceiverPolarisation', bands[0]))  
   # region values as generated by getRegion
   region = col.getRegion(geometry, int(scale)).getInfo()
    
   # stuff the values in a dataframe for convenience      
   df = pd.DataFrame.from_records(region[1:len(region)])
    
   # use the first list item as column names
   df.columns = region[0]
   
   # drop id column (little value / overhead)
   df.drop('id', axis=1, inplace=True)
   
   # divide the time field by 1000 as in milliseconds
   # while datetime takes seconds to convert unix time
   # to dates
   df.time = df.time / 1000
   df['time'] = pd.to_datetime(df['time'], unit = 's')
   df.rename(columns = {'time': 'date'}, inplace = True)
   df.sort_values(by = 'date')
   
   # add the product name and latitude, longitude as a column
   # just to make sense of the returned data after the fact
   df['product'] = pd.Series(product, index = df.index)
      
   # return output
   return df

if __name__ == "__main__":

   # parse arguments
   args = getArgs()
   
   # read in locations if they exist,
   # overrides the location argument
   if args.file:
      if os.path.isfile(args.file):
        if args.location:
            print("not a valid location file, check path") 
        else:
          locations = pd.read_csv(args.file)
          print("[INFO] Read input locations")
   else:
      locations = pd.DataFrame(['site'] + args.location).transpose()  	 
   
   # initialize GEE session
   # requires a valid authentication token
   # to be present on the system
   ee.Initialize()
   
   # now loop over all locations and grab the
   # data for all locations as specified in the
   # csv file or the single location as specified
   # by a lat/lon tuple
   for loc in locations.itertuples():
      
      # some feedback
      print("processing: %s at %s / %s" % (loc[1],loc[3],loc[2]))
      
      # download data using the gee_subset routine
      # print to console if verbose
      try:
        df = gee_subset(product = args.product,
                       bands = args.bands,
                       start_date = args.start,
                       end_date = args.end,
                       latitude = loc[2],
                       longitude = loc[3],
                       scale = args.scale,
                       pad = args.pad)
      except NameError:
        print("Error: check input parameters")
        if args.verbose:
          raise
      else:
      
        # depending on output options write to file
        # or just print to console   
        if args.directory:
          df.to_csv(args.directory + "/" + str(loc[1]) + "_" + os.path.basename(args.product) + "_gee_subset.csv", index = False)
        else:
          print(df)