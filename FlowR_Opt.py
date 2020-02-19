
##############################################################################################################################################################################################################################################
##############################################################################################################################################################################################################################################

# FLOW-R OPTIMIZATION PROGRAM

##############################################################################################################################################################################################################################################
##############################################################################################################################################################################################################################################

# Import Packages
import subprocess
import arcpy
from scipy.optimize import brute

# Activate the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# Definition of the function, that (for given input-parameters) runs Flow-R and calculates a hit-false-ratio
def FlowR_HFR(x):
    """Runs FlowR and calculates a hit-false-ratio (hfr)"""
    # run flow-r and calculate hit false ratio
    holmgren_x = x[0]   # Parameters from function attribute
    reach_angle = x[1]
    run = str(x[0])+"_"+str(x[1])   # create name for folders based on changing input parameters
    run_name = run_date+str(run)
    # create string as input for Flow-R with all needed parameters
    tot_string = [Flowr_path, "--dem=" + str(dempath), "--sources=" + str(startingpointspath), "--sources-val=ge1", "--spreading-algo=holmgren", "--holmgren-x=" + str(holmgren_x), "--holmgren-dh=" + str(holmgren_dh), "--friction-algo=reach-angle", "--reach-angle=" + str(reach_angle), "--max-velocity=" + str(max_velo), "--persistence-algo=weights", "--weights=default", "--output=1,3", "--output-path=" + str(outpath), "--threads-nb=8", "--log-level=2", "--run-name=" + str(run_name)]
    # run Flow-R
    subprocess.call(tot_string, shell=True)

    # preparation for hit-false-ratio (hfr)
    extent_flowr_pfad = outpath + "\\" + run_name + "\\" + run_name + "-extent-tot.tif" # path to the file created by Flow-R

    extent_ngkat = arcpy.Raster(extent_ngkat_pfad)  # import of ngkat-raster
    extent_flowr = arcpy.Raster(extent_flowr_pfad)  # import of Flow-R-raster
    # no data to value 0
    reclass_extent_ngkat = arcpy.sa.Con(arcpy.sa.IsNull(extent_ngkat), 0, extent_ngkat, "Value =1")
    reclass_extent_ngkat.save(output + "\\" + run_name + "-reclass_extent_ngkat.tif")

    # multiplie with multiplier to prepare calculation
    ngkat_multiplier = 3
    extent_ngkat_3 = reclass_extent_ngkat * ngkat_multiplier
    extent_ngkat_3.save(output + "\\" + run_name + "-ngkat_multiplied.tif")

    # subtract ngkat-raster from Flow-R-raster
    dif_flowr_ngkat = extent_flowr - extent_ngkat_3
    dif_flowr_ngkat.save(output + "\\" + run_name + "-dif_flowr_ngkat.tif")
    dif_import_pfad = output + "\\" + run_name + "-dif_flowr_ngkat.tif"

    # search for hits and falses in dif_flowr_ngkat and count them
    my_dict = {row[0]: row[1] for row in arcpy.da.SearchCursor(dif_import_pfad, ['Value', 'Count'])}
    keys = my_dict.keys()
    if 0 in keys:
        count_0 = my_dict[0]
    else:
        count_0 = 0
    if 1 in keys:
        count_1 = my_dict[1]
    else:
        count_1 = 0
    if -2 in keys:
        count_2 = my_dict[-2]
    else:
        count_2 = 0
    if -3 in keys:
        count_3 = my_dict[-3]
    else:
        count_3 = 0
    # Hit false ratio:
    hfr = 1 - (count_2 / (count_1 + count_2 + count_3))
    return hfr                                              # returns hfr as result of the "FlowR_HFR(x)" function


##############################################################################################################################################################################################################################################
##############################################################################################################################################################################################################################################
# set Working Directory

work_dir = r"C:\Users\Peter_Muster\Documents\Fancy_Projects"


# Import Data and set Directories
Flowr_path = work_dir + r"\FlowR_Optimization\FlowR_engine\FlowR_engine.exe"
dempath = work_dir + r"\FlowR_Optimization\Data\DEM\DEM.tif"
startingpointspath = work_dir + r"\FlowR_Optimization\Data\Startingpoint\Startingpoint.tif"
extent_ngkat_pfad = work_dir + r"\FlowR_Optimization\Data\ngkat_extent\ngkat_extent.tif"
outpath = work_dir + r"\FlowR_Optimization\Output\FlowR"
output = work_dir + r"\FlowR_Optimization\Output\hfr_steps"


##############################################################################################################################################################################################################################################
##############################################################################################################################################################################################################################################

# optimization

# Fixed parameters, don't change
holmgren_dh = 2
max_velo = 15
run = 0

# run_date format: "dd.mm.yyyy_", change to date of run
run_date = "31.01.2020_"

# ranges for the optimization function
rranges = (slice(1, 10, 1),slice(1, 20, 1))

# run the optimization function, which accesses the FlowR_HFR function again and again with changing parameters
solution = brute(FlowR_HFR, rranges, full_output=True)

# When the best hfr possible is found, give out the results to optimal holmgren x, reach angle, and the acquired hfr
print("The optimal input for holmgren x is:")
print(solution[0][0])
print("The optimal input for the reach angle is:")
print(solution[0][1])
print("The reached hfr:")
print(solution[1])
