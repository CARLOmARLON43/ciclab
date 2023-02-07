

class ur3_control:
	def __init__ (self):
		self.ROBOT_HOST = '10.0.0.150' # ip in settings in the tablet
		self.ROBOT_PORT = 30004
		self.config_filename = 'control_loop_configuration.xml'
		
		self.con = None
		self.target_joints = None
		self.gain = None
		self.setp = None
		self.watchdog = None

	def conect(self):
		logging.getLogger().setLevel(logging.INFO)
		#configuration files
		conf = rtde_config.ConfigFile(self.config_filename)
		state_names, state_types = conf.get_recipe('state')
		setp_names, setp_types = conf.get_recipe('setp')
		watchdog_names, watchdog_types = conf.get_recipe('watchdog')

		#connection to the robot
		self.con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
		self.con.connect()
		connection_state = self.con.connect()

		#check connection
		while connection_state != 0:
		    time.sleep(5)
		    connection_state = self.con.connect()

		self.con.send_output_setup(state_names, state_types)
		self.setp = self.con.send_input_setup(setp_names, setp_types)
		self.watchdog = self.con.send_input_setup(watchdog_names, watchdog_types)

		# Initialize 6 registers which will hold the target angle values
		self.setp.input_double_register_0 = 0.0
		self.setp.input_double_register_1 = 0.0
		self.setp.input_double_register_2 = 0.0
		self.setp.input_double_register_3 = 0.0
		self.setp.input_double_register_4 = 0.0
		self.setp.input_double_register_5 = 0.0
		  
		# The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
		self.watchdog.input_int_register_0 = 0
		return 1

	def data_sinc(self):
		# Start data synchronization
		if not self.con.send_start():
		    sys.exit()


		# Save initial time
		init_time = time.time()
		# Set gain for the control
		gain = 1
		# Control loop, keeps running until user quits using q
		while not(keyboard.is_pressed("q")):

		    # Receive UR Robot state
		    state = self.con.receive()

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
		        list_to_setp(self.setp, control_effort)
		        # Send new control effort        
		        self.con.send(self.setp)
		        
		    # kick watchdog
		    self.con.send(watchdog)

	

ur3_control1 = ur3_control()


