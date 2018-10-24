import snakeoil3_gym 
import numpy as np 
import random as rd 
from gym_torcs import TorcsEnv



PI= 3.14159265359

def get_n_clients(N, start_port):
	clients = []
	for i in range(N):
		c = snakeoil3_gym.Client(p=start_port+i)
		clients.append(c)
	return clients



def drive_example(c, target_speed, init_pos):
	u'''This is only an example. It will get around the track but the
	correct thing to do is write your own `drive()` function.'''
	S,R= c.S.d,c.R.d
	# target_speed=1000
	min_dist = 10
	# Steer To Corner
	R[u'steer']= S[u'angle']*10 / PI
	# Steer To the old pose
	R[u'steer'] += (init_pos - S[u'trackPos'])*.3

	R[u'steer'] = np.clip(R[u'steer'], -.1, .1)

	# print(R[u'steer'])

	R[u'accel'] = 0.5

	if target_speed-10 < S[u'speedX']:
	    R[u'accel'] = 0.01

	if target_speed <= S[u'speedX']:
	    R[u'accel'] = 0.


	opponents = S['opponents']
	front = np.array([opponents[15], opponents[16], opponents[17], opponents[18], opponents[19], opponents[20]])
	back  = np.array([opponents[-3], opponents[-2], opponents[-1], opponents[0], opponents[1], opponents[2]])
	left  = np.array([opponents[6], opponents[7], opponents[8], opponents[9], opponents[10], opponents[11]])
	right = np.array([opponents[23], opponents[24], opponents[25], opponents[26], opponents[27], opponents[28], opponents[29]])


	# R[u'accel'] += np.random.normal(0, 0.1)

	# Throttle Control
	# if S[u'speedX'] < target_speed - (R[u'steer']*50):
	#     R[u'accel']+= .01
	# else:
	#     R[u'accel']-= .01
	# if S[u'speedX']<10:
	#    R[u'accel']+= 1/(S[u'speedX']+.1)


	if min(front) < 10:
		R[u'accel'] = 0.0

	if min(back) < 10:
		R[u'accel'] += 1.0
		R[u'brake'] = 0.

	# if min(front) > 100:
	# 	R[u'accel'] += 1.0

	# Traction Control System
	# if ((S[u'wheelSpinVel'][2]+S[u'wheelSpinVel'][3]) -
	#    (S[u'wheelSpinVel'][0]+S[u'wheelSpinVel'][1]) > 5):
	#    R[u'accel']-= .2

	# Automatic Transmission
	# R[u'gear']=1
	# if S[u'speedX']>50:
	#     R[u'gear']=2
	# if S[u'speedX']>80:
	#     R[u'gear']=3
	# if S[u'speedX']>110:
	#     R[u'gear']=4
	# if S[u'speedX']>140:
	#     R[u'gear']=5
	# if S[u'speedX']>170:
	#     R[u'gear']=6
	return


def block_driving(maxSteps):
	# env = TorcsEnv(vision=False, throttle=True, gear_change=False, main=1)

	velocities_range = [[100, 120], [70, 90], [40, 70]]

	clients = get_n_clients(10, 3101)	

	for c in clients:
		c.get_servers_input(0)

	target_v1 = np.random.choice(range(velocities_range[0][0], velocities_range[0][1]))
	target_v2 = np.random.choice(range(velocities_range[1][0], velocities_range[1][1]))
	target_v3 = np.random.choice(range(velocities_range[2][0], velocities_range[2][1]))

	target_speed = [target_v1]*4 + [target_v2]*4 + [target_v3]*2

	init_track_pos = [c.S.d['trackPos'] for c in clients]
	print(init_track_pos)
	print(target_speed)
	# init_track_pos = [0.75, -0.75, 0.75, -0.75]*2 + [0.75, -0.75]

	for step in range(maxSteps,0,-1):
		for i, c in enumerate(clients):
			c.get_servers_input(step) 
			drive_example(c, target_speed[i], init_track_pos[i])
			c.respond_to_server()

	for c in clients:
		c.shutdown()



def lane_driving(maxSteps):
	clients = get_n_clients(10, 3101)

	init_track_pos = 0.75

	for step in range(maxSteps,0,-1):
		for i, c in enumerate(clients):
			c.get_servers_input(step)
			drive_example(c, 100+i, init_track_pos)
			c.respond_to_server()

		if (maxSteps - step)%100 == 0:
			init_track_pos *= -1
	for c in clients:
		c.shutdown()



if __name__ == "__main__":
	block_driving(10000)