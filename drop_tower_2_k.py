"""
Harry Duckworth
Dyson School of Design Engineering
Imperial College London

Ready a madymo linear and rotational acceleration file and export it as a k file for LS-DYNA
"""
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def read_dt_xlsx(source):
    """
    Open the xlsx from the drop tower file and import it to dataframe
    """
 
    df_lin = pd.read_excel(source, 
                        index_col=0,
                        header=0, 
                        usecols=['Time(ms)','lac_x(mm/ms^2)', 'lac_y(mm/ms^2)', 'lac_z(mm/ms^2)']
                        )

    df_rot = pd.read_excel(source, 
                        index_col=0,
                        header=0, 
                        usecols=['Time(ms)','aac_x(rad/ms^2)', 'aac_y(rad/ms^2)', 'aac_z(rad/ms^2)']
                        )

    print('\nCheck Data being imported: ')
    print(df_lin.head())
    print(df_rot.head())
    print()

    return df_lin, df_rot

def write_acc_comp(curve, cog_id, pres_motion_dof, pres_motion_type, lcid, output_acc_file):
    '''
    Create a k file for acceleration curve
    '''
 
    # Write prescribed motion keyword (this applies the curve to the centre of gravity)
    output_acc_file.write("*BOUNDARY_PRESCRIBED_MOTION_RIGID\n")
    output_acc_file.write("$#     pid       dof       vad      lcid        sf       vid     death     birth\n")
    output_acc_file.write(str(cog_id).rjust(10) +
                            str(pres_motion_dof).rjust(10) +
                            str(pres_motion_type).rjust(10) +
                            str(lcid).rjust(10) +
                            "       1.0         01.00000E28       0.0\n")
    output_acc_file.write("*DEFINE_CURVE_TITLE\n")
    output_acc_file.write("Acceleration component\n")
    output_acc_file.write("$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint\n")
    output_acc_file.write(str(lcid).rjust(10)+"         0       1.0       1.0       0.0       0.0         0         0\n")
    output_acc_file.write("$#                a1                  o1  \n")

    # Get time and data
    time = curve.index.values.tolist()
    data = curve.iloc[:].tolist()

    # Loop through each timestep and print  
    for i in range(len(time)):
        output_acc_file.write(str(round(time[i],10)).rjust(20) + str(round(data[i],10)).rjust(20) + '\n') 

def plot_acc(df_lin, df_rot):
    """
    Create plots of acc data
    """

    sns.set_theme()
    sns.set_style("ticks")
    sns.set_context("paper")

    n = 1
    fig, ax = plt.subplots(2, sharex=True, figsize = (5, 5))
    labels = ['x', 'y', 'z', 'x', 'y', 'z']
    start_times = [0, 0, 0]
    end_times = [0, 0, 0]
    colors = ['forestgreen', 'steelblue', 'darkorchid', 'firebrick', 'darkorange', 'gold']

    sns.lineplot(
        ax=ax[0], 
        data=df_lin, 
        palette=colors[0:3], 
        linewidth=1,
        dashes=False
        )

    sns.lineplot(
        ax=ax[1], 
        data=df_rot, 
        palette=colors[3:6], 
        linewidth=1,
        dashes=False
        )

    ax[0].set_ylabel('Linear Acceleration $(m/s^2)$')
    ax[1].set_ylabel('Rotational Velocity $(rad/s)$')
    ax[1].set_xlabel('Time $(ms)$')

    plt.savefig('acc.svg', bbox_inches='tight', dpi = 600)
    plt.savefig('acc.png', bbox_inches='tight', dpi = 600)

    plt.show()

def create_acc_file(df_lin, df_rot, cog_id):

    max_time = min(df_lin.index[-1], df_rot.index[-1])

    # Create file
    output_acc_file = open(os.path.join("acceleration" + ".k"), "w+")
    n = 0
        
    output_acc_file.write("*CONTROL_TERMINATION\n")
    output_acc_file.write("$#  endtim    endcyc     dtmin    endeng    endmas     nosol  \n")
    output_acc_file.write(str(round(max_time, 9)).rjust(10) + "         0       0.0       0.01.000000E8         0\n")

    print("Writing acceleration data...")
    
    # Variables
    pres_motion_dof  = 1
    lcid = 1

    # Constants
    pres_motion_type_lin = 1
    pres_motion_type_rot = 0

    for col in df_lin.columns:
        write_acc_comp(df_lin[col], cog_id, pres_motion_dof, pres_motion_type_lin, lcid, output_acc_file)
        
        # Update Variabels
        pres_motion_dof += 1 
        lcid += 1
        
    pres_motion_dof += 1 

    for col in df_rot.columns:
        write_acc_comp(df_rot[col], cog_id, pres_motion_dof, pres_motion_type_lin, lcid, output_acc_file)
        
        # Update Variabels
        pres_motion_dof += 1 
        lcid += 1
        
    output_acc_file.write("*END\n")
    output_acc_file.close()

if __name__ == "__main__":

    # System arguments
    dt_acc_file = sys.argv[1]
    cog_id = sys.argv[2]

    # User Messages
    print("Creating acceleration file using: ")
    print('    ' + dt_acc_file)

    # Import Data to Dataframes
    df_lin, df_rot = read_dt_xlsx(dt_acc_file)

    # Create Plots 
    plot_acc(df_lin, df_rot)

    # Scale data to mm and ms
    df_lin = df_lin.multiply(1)
    df_rot = df_rot.multiply(1)

    # Create k file
    create_acc_file(df_lin, df_rot, cog_id)
