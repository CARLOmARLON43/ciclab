import sys
sys.path.append('..')   
import logging
import time
from rtde import *
import keyboard
from math import sqrt

def compute_error(target, joints):
    """Computes a 6D vector containing the error in every joint in the control loop

    Args:
        target (list): List of floats containing the target joint angles in radians
        joints (list): List of floats containing the measured joint angles in radians

    Returns:
        list: List of floats containing the angles error in radians
    """
    return [j - joints[i] for i,j in enumerate(target)]

def compute_control_effort(error, gain):
    """Computes a 6D vector containing the control effort in every joint in the control loop

    Args:
        error (list): List of floats containing the angles error in radians
        gain (float): Gain in the control loop (each joint angle error will be multiplied times this value to compute control effort)

    Returns:
        liat: List of floats containing the control efforts in each joint
    """
    return [i*gain for i in error]

def list_to_degrees(angles):
    """Converts input list values from radians to degrees

    Args:
        angles (list): List containing angles in radians

    Returns:
        list: List containing angles in degrees
    """
    return [i*360/(2*3.14592) for i in angles]

def list_to_radians(angles):
    """Converts input list values from degrees to radians

    Args:
        angles (list): List containing angles in degrees

    Returns:
        list: List containing angles in radians
    """
    return [i*(2*3.14592)/(360) for i in angles]


ROBOT_HOST = '10.0.0.150' # ip in settings in the tablet
ROBOT_PORT = 30004
config_filename = 'control_loop_configuration.xml'

logging.getLogger().setLevel(logging.INFO)

#configuration files
conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')
setp_names, setp_types = conf.get_recipe('setp')
watchdog_names, watchdog_types = conf.get_recipe('watchdog')

#connection to the robot
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
con.connect()
connection_state = con.connect()

#check connection
while connection_state != 0:
    print(connection_state)
    time.sleep(5)
    connection_state = con.connect()

# get controller version
con.get_controller_version()

# setup recipes
con.send_output_setup(state_names, state_types)
setp = con.send_input_setup(setp_names, setp_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)

# Set initial target joint angles
# target_joints = [1.6, -1.6, 0, -1.6, 0, 1]
target_joints = [89.85335402347565, -23.220503827531275, -133.09759012547653, -112.66738309350366, -88.49428036141305, -20]
target_joints = list_to_radians(target_joints)
print(target_joints)

# Initialize 6 registers which will hold the target angle values
setp.input_double_register_0 = 0.0
setp.input_double_register_1 = 0.0
setp.input_double_register_2 = 0.0
setp.input_double_register_3 = 0.0
setp.input_double_register_4 = 0.0
setp.input_double_register_5 = 0.0
  
# The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
watchdog.input_int_register_0 = 0

# Reformat setpoint into list
def setp_to_list(setp):
    list = []
    for i in range(0,6):
        list.append(setp.__dict__["input_double_register_%i" % i])
    return list

# Reformat list into setpoint
def list_to_setp(setp, list):
    for i in range (0,6):
        setp.__dict__["input_double_register_%i" % i] = list[i]
    return setp

# Start data synchronization
if not con.send_start():
    sys.exit()


# Save initial time
init_time = time.time()
# Set gain for the control
gain = 1
# Control loop, keeps running until user quits using q
while not(keyboard.is_pressed("q")):

    # Receive UR Robot state
    state = con.receive()

    # If state is None break loop and end connection
    if state is None:
        break
    
    # Read joint angles from registers
    joint_angles = state.actual_q
    position = state.actual_TCP_pose
    # Check if the program is running in the Polyscope
    if state.output_int_register_0 != 0:
        
        # Print joint angles in degrees every second
        if(time.time() - init_time) >= 1:
            init_time = time.time()
            # print(list_to_degrees(joint_angles))
            print(position)
            """if (target_joints[0] == 0):
                target_joints[0] = 1.6
            else:
                target_joints[0] = 0"""    
        # Compute new target joint angles
        # ---
        # Compute control error    
        error = compute_error(target_joints, state.actual_q)
        # Compute control effort
        control_effort = compute_control_effort(error, gain)
        # Reformat control effort list into setpoint
        list_to_setp(setp, control_effort)
        # Send new control effort        
        con.send(setp)
        
    # kick watchdog
    con.send(watchdog)

# set joints speed to 0
list_to_setp(setp, [0,0,0,0,0,0])
con.send(setp)

con.send_pause()

con.disconnect()