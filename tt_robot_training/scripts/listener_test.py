#!/usr/bin/env python

import sys

import tf as transform
import rospy
from geometry_msgs.msg import TwistStamped
from gazebo_msgs.srv import GetModelState

import random
import numpy as np
import pandas as pd
import logging
import tensorflow as tf
from collections import deque
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input
from keras.layers.merge import Add, Multiply
from keras.optimizers import Adam
import keras.backend as K


logging.getLogger('tensorflow').setLevel(logging.ERROR)


class ActorCritic:
    def __init__(self, sess):
        self.sess = sess
        self.states = 12
        self.actions = 6  
        self.learn_rate = 0.001
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = .99995
        self.gamma = .9999995
        self.tau   = .125
        self.memory = deque(maxlen=2000)
        self.scores = []

        self.output_range = 2


        # ===================================================================== #
        #                               Actor Model                             #
        # Chain rule: find the gradient of chaging the actor network params in  #
        # getting closest to the final value network predictions, i.e. de/dA    #
        # Calculate de/dA as = de/dC * dC/dA, where e is error, C critic, A act #
        # ===================================================================== #


        self.actor_state_input, self.actor_model = self.create_actor_model('actor')
        _, self.target_actor_model = self.create_actor_model('actor_target')  

        self.actor_critic_grad = tf.placeholder(tf.float32, [None, self.actions]) # where we will feed de/dC (from critic)
        
        actor_model_weights = self.actor_model.trainable_weights
        self.actor_grads = tf.gradients(self.actor_model.output, actor_model_weights, -self.actor_critic_grad) # dC/dA (from actor)
        grads = zip(self.actor_grads, actor_model_weights)
        self.optimize = tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)

        # ===================================================================== #
        #                              Critic Model                             #
        # ===================================================================== #       

        self.critic_state_input, self.critic_action_input, self.critic_model = self.create_critic_model('critc')
        _, _, self.target_critic_model = self.create_critic_model('critc_target') 

        self.critic_grads = tf.gradients(self.critic_model.output, self.critic_action_input) # where we calcaulte de/dC for feeding above
        
        # Initialize for later gradient calculations
        self.sess.run(tf.initialize_all_variables())

        self.actor_model.load_weights("models/ready position/rate:10,loop:100/actor_model")
        self.target_actor_model.load_weights("models/ready position/rate:10,loop:100/target_actor_model")
        self.critic_model.load_weights("models/ready position/rate:10,loop:100/critic_model")
        self.target_critic_model.load_weights("models/ready position/rate:10,loop:100/target_critic_model")


    def create_actor_model(self,type):
        state_input = Input(shape=(self.states,))
        h1 = Dense(128, activation='tanh')(state_input)
        h2 = Dense(64, activation='tanh')(h1)
        h3 = Dense(32, activation='tanh')(h2)
        output = Dense(self.actions, activation='tanh')(h3)
        
        model = Model(input=state_input, output=output)
        adam  = Adam(lr=0.001)
        model.compile(loss="mse", optimizer=adam)
        dot_img_file = 'model '+type+'.png'
        tf.keras.utils.plot_model(model, to_file=dot_img_file, show_shapes=True)
        return state_input, model


    def create_critic_model(self,type):
        state_input = Input(shape=(self.states,))
        state_h1 = Dense(24, activation='tanh')(state_input)
        state_h2 = Dense(48)(state_h1)
        
        action_input = Input(shape=(self.actions,))
        action_h1    = Dense(48)(action_input)
        
        merged    = Add()([state_h2, action_h1])
        merged_h1 = Dense(24, activation='tanh')(merged)
        output = Dense(1, activation='linear')(merged_h1)
        model  = Model(input=[state_input,action_input], output=output)
        
        adam  = Adam(lr=0.001)
        model.compile(loss="mse", optimizer=adam)
        dot_img_file = 'model '+type+'.png'
        tf.keras.utils.plot_model(model, to_file=dot_img_file, show_shapes=True)
    
        return state_input, action_input, model

    def _train_actor(self, samples):
        for sample in samples:
            cur_state, action, reward, new_state = sample

            predicted_action = self.actor_model.predict(cur_state)
            grads = self.sess.run(self.critic_grads, feed_dict={ self.critic_state_input:  cur_state,self.critic_action_input: predicted_action})[0]

            self.sess.run(self.optimize, feed_dict={
                self.actor_state_input: cur_state,
                self.actor_critic_grad: grads
            })

    def _train_critic(self, samples):
        for sample in samples:
            cur_state, action, reward, new_state = sample

            target_action = self.target_actor_model.predict(new_state)
            future_reward = self.target_critic_model.predict([new_state, target_action])[0][0]
            # reward += self.gamma * future_reward
            

            reward = np.reshape(reward,[1,1])
            # print("check:",cur_state,action,reward)

            self.critic_model.fit([cur_state, action], reward,verbose=0, epochs = 5000)

    def train(self):
        batch_size = 10
        if len(self.memory) < batch_size:
            return

        rewards = []
        samples = random.sample(self.memory, batch_size)
        print("samples:",samples)
        self._train_critic(samples)
        self._train_actor(samples)

    # ========================================================================= #
    #                         Target Model Updating                             #
    # ========================================================================= #

    def _update_actor_target(self):
        actor_model_weights  = self.actor_model.get_weights()
        actor_target_weights = self.target_actor_model.get_weights()
        
        for i in range(len(actor_target_weights)):
            actor_target_weights[i] = actor_model_weights[i]
        self.target_actor_model.set_weights(actor_target_weights)

    def _update_critic_target(self):
        critic_model_weights  = self.critic_model.get_weights()
        critic_target_weights = self.target_critic_model.get_weights()
        
        for i in range(len(critic_target_weights)):
            critic_target_weights[i] = critic_model_weights[i]
        self.target_critic_model.set_weights(critic_target_weights)     

    def update_target(self):
        self._update_actor_target()
        self._update_critic_target()

        self.actor_model.save_weights("models/ready position/rate:10,loop:100/actor_model")
        self.target_actor_model.save_weights("models/ready position/rate:10,loop:100/target_actor_model")
        self.critic_model.save_weights("models/ready position/rate:10,loop:100/critic_model")
        self.target_critic_model.save_weights("models/ready position/rate:10,loop:100/target_critic_model")


    # ========================================================================= #
    #                              Model Predictions                            #
    # ========================================================================= #


    def act(self, cur_state):
        self.epsilon *= self.epsilon_decay
        if np.random.random() < self.epsilon:
            return [ self.output_range*2*( random.random() - 0.5 )  for i in range(self.actions) ] 
        return self.actor_model.predict(cur_state) * self.output_range 



def reward_func( state ):
    reward = 1 - cart_dist(0.45,0,0.4,state[0][0],state[0][1],state[0][2])       # ready position
    return reward

def cart_dist( x1,y1,z1,x2,y2,z2 ):

    return ( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 )**0.5


def get_state(listener,model_coordinates,actor_critic):
    (trans,rot) = listener.lookupTransform( '/world','/tool0', rospy.Time(0))
    euler = transform.transformations.euler_from_quaternion(rot)

    ball = model_coordinates('table_tennis_ball', 'ground_plane')

    # print(trans)

    inp = []
    inp.extend((trans + 
        # list(euler)))
    [0]*3))
    inp.extend([0]*6) 
    print(inp)
    # inp.append(ball.pose.position.x)
    # inp.append(ball.pose.position.y)
    # inp.append(ball.pose.position.z)
    # inp.append(ball.twist.linear.x)
    # inp.append(ball.twist.linear.y)
    # inp.append(ball.twist.linear.z)

    inp = np.reshape(inp,[1,actor_critic.states])

    return inp

def send_directions(op,pub,no):
    # print(op)
    msg = TwistStamped()

    msg.twist.linear.x = op[0][0]
    msg.twist.linear.y = op[0][1]
    msg.twist.linear.z = op[0][2]

    # msg.twist.angular.x = op[0][3]
    # msg.twist.angular.y = op[0][4]
    # msg.twist.angular.z = op[0][5]

    msg.twist.angular.x = 0
    msg.twist.angular.y = 0
    msg.twist.angular.z = 0

    for i in range(no):
        pub.publish( msg )


def main():

    sess = tf.Session()
    K.set_session(sess)
    actor_critic = ActorCritic( sess )


    rospy.init_node('listener')
    listener = transform.TransformListener()
    listener.waitForTransform( '/tool0','/world', rospy.Time(0), rospy.Duration(3)  )
    try:
        model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
    except rospy.ServiceException as e:
            rospy.loginfo("Get Model State service call failed:  {0}".format(e))
    pub = rospy.Publisher('/servo_server/delta_twist_cmds', TwistStamped, queue_size=3)

    rate = rospy.Rate( 10 )

    
    count = 0
    
    prev_state = get_state(listener,model_coordinates,actor_critic)
    action = actor_critic.act(prev_state)
    action = np.reshape(action,[1,actor_critic.actions])

    start = rospy.get_time()
    
    while ( rospy.get_time()-start < int(sys.argv[1]) ):
        # print(rospy.get_time(),start)
        # print(sys.argv[1])
        # if( rospy.get_time()-start > int(sys.argv[1])): 
        #     print("over")
        global action,prev_state

        state = get_state(listener,model_coordinates,actor_critic)
        reward = reward_func(state)

        
        actor_critic.memory.append( (prev_state,action,reward,state) )
        print((prev_state[0],action[0],reward,state[0]))

        action = actor_critic.act(state)
        action = np.reshape(action,[1,actor_critic.actions])

        send_directions(action,pub,1000)

        actor_critic.scores.append(reward)
        pd.Series(actor_critic.scores[-1]).to_csv("results/ready position/rate:10,loop:100/train",mode='a')

        # if( count % 10 == 0 ):
        #     actor_critic.train()
        #     if( count % 100 == 0 ):
        #         actor_critic.update_target()
                

        prev_state = state    
        
        print(count,actor_critic.epsilon,reward)

        count+=1
        rate.sleep()

if __name__ == '__main__':
    print("hello")
    main()
    print("bye")