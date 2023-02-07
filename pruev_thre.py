import time
import threading

class threadi:
	def __init__(self):
		self.STATE=0
		self.t = threading.Thread(target=self.monitor)
		self.target_ang = []
		self.target_pos = p[]

	def monitor(self):
		print("monitoring...")
		temp = self.STATE


		while self.STATE != -1:

			if self.STATE == 1:
				#Move to joint angles
				print("move to angles")

			if self.STATE == 2:
				#Move to joint angles
				print("move to position")

			if self.STATE == 3:
				#Move to joint angles
				print("Print joint angles")

			if self.STATE == 4:
				#Move to joint angles
				print("print head position")
				



			if temp!= self.STATE:
				print("-->",end="")
				print(self.STATE)

				temp = self.STATE
			time.sleep(0.5)

	def conect(self):
		self.t.start()
		return 0
	def change(self,n):
		self.STATE = n
		return 0

	def stop(self):
		self.STATE = -1
		self.t.join()
		return 0

t1 = threadi()
t1.conect()
time.sleep(3)
t1.change(2)
time.sleep(4)
t1.change(3)
time.sleep(1)
t1.stop()





