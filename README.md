[![DOI](https://zenodo.org/badge/97874563.svg)](https://zenodo.org/badge/latestdoi/97874563)

# Google Earth Engine subset script & library

This is a small python script to subset GEE gridded data products into time series for a given location or list of locations. This script should make it easier to subset remote sensing time series for processing external to GEE. 

This in part replaces for example the ORNL DAAC MODIS subsets or Daymet web services, but extends these to higher resolution date such as Landsat and Sentinel. More so, it should also work on all other gridded products using the same product / band syntax (e.g. the MODIS phenology product MCD12Q2 or the MODIS snow product MOD10A1). If this code made your life easier please refer to it using the Zenodo citation and DOI (see below / medallion) in any research papers.

## Installation

clone the repository

```bash
git clone https://github.com/kkraoj/gee_subset.git
```

Make sure you have a working Google Earth Engine python API setup. The installation instructions can be found on the [GEE developer site](https://developers.google.com/earth-engine/python_install).

## Use

### To query
Below you find an example call to the scrip which downloads Sentinel-1 SAR (-p, --product) backscatter data for bands VV and VH (-b, --band) for a number of sites as listed in selected_sites.csv and saves the results on the users desktop (-d, --directory).

```bash
./gee_subset.py -p "COPERNICUS/S1_GRD" \
                -b "VH" \
                -f "~/Desktop/selected_sites.csv" \
                -d "/Users/foo/Desktop/"
```

``` bash
# prints output to console
./gee_subset.py -p "COPERNICUS/S1_GRD" \
                -b "B1" "B2" \
                -s "2015-01-01" \
                -e "2015-12-31" \
                -l 44.064665 -71.287575
```

Sites can be listed as a latitude longitude tuple using the -loc parameter, or by providing the before mentioned csv file (-f, --file parameter). Either one should be provided.

The csv file is a comma delimited file of the format:

	site, latitude, longitude.

A padding value can be provided (-pd, --pad) so one can download a rectangular window of data padded x km in either direction around a particular location. This option is limited by the maximum pixels which GEE can export. For normal use (i.e. 1 to 2 km padding) this should not present a problem for most products. Be weary of using large padding as Google Earth Engine limits maximum computation of 300s.

General help can be queried by calling:
```bash
./gee_subset.py -h
```

In addition the script can be loaded as a library in a python script by calling:

```python
import gee_subset
```
The function is called gee_subset(). Consult the script for correct parameter naming conventions. Currently minimum error trapping is provided.

###  To timeshift 
The output gee_subset.py is a .csv file for each location. Each .csv file contains a columns called 'date' which contains the date and time of satellite observation in UTM format. To change this UTM time to that of local timezone refer to script shift_time.py. The script accepts gee_subset.py's output in pandas dataframe and adds a column called 'obs_date_local' for each row.

## Data format

The output of the script is [tidy data](https://cran.r-project.org/web/packages/tidyr/vignettes/tidy-data.html) in which each row is an observation. Multiple observations can be returned in case a padding value is specified. Multiple bands can be called at once by providing multiple valid bands as an argument. Multiple bands will be returned as columns in the tidy data format.

## References

Hufkens K. (2017) A Google Earth Engine time series subset script & library. DOI: 10.5281/zenodo.833789.
