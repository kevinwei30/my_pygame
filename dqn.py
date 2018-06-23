#!/usr/bin/env python
from __future__ import print_function

import argparse
import skimage as skimage
from skimage import transform, color, exposure
from skimage.transform import rotate
from skimage.viewer import ImageViewer
import sys
sys.path.append("game/")
import wrapped_game as game
import random
import numpy as np
from collections import deque

import json
from keras.initializers import normal, identity
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD , Adam
import tensorflow as tf
import json

# GAME = 'dinasour' # the name of the game being played for log files
# CONFIG = 'nothreshold'
ACTIONS = 3 # number of valid actions
GAMMA = 0.99 # decay rate of past observations
OBSERVATION = 4000 # timesteps to observe before training
EXPLORE = 100000. # frames over which to anneal epsilon
FINAL_EPSILON = 0.0001 # final value of epsilon
INITIAL_EPSILON = 0.1 # starting value of epsilon
REPLAY_MEMORY = 20000 # number of previous transitions to remember
BATCH = 32 # size of minibatch
FRAME_PER_ACTION = 1
LEARNING_RATE = 1e-5
TRAIN_ITER = 8000
TOTAL_ROUND = 5

img_rows , img_cols = 100, 50
img_channels = 4 #We stack 4 frames

def make_json(name): # store the model hyper parameters
    data = {}
    data['ACTIONS'] = ACTIONS
    data['GAMMA'] = GAMMA
    data['OBSERVATION'] =OBSERVATION
    data['EXPLORE'] = EXPLORE
    data['FINAL_EPSILON'] = FINAL_EPSILON
    data['INITIAL_EPSILON'] = INITIAL_EPSILON
    data['REPLAY_MEMORY'] = REPLAY_MEMORY
    data['BATCH'] = BATCH
    data['FRAME_PER_ACTION'] = FRAME_PER_ACTION
    data['LEARNING_RATE'] = LEARNING_RATE
    data['TRAIN_ITER'] = TRAIN_ITER
    data['TOTAL_ROUND'] = TOTAL_ROUND
    data['img_rows'] = img_rows
    data['img_cols'] = img_cols
    data['img_channels'] = img_channels

    with open(name + '_hyperparams.json', 'w') as f:
        json.dump(data, f)

def buildmodel():
    print("Now we build the model")
    model = Sequential()
    model.add(Convolution2D(32, 8, 8, subsample=(4, 4), border_mode='same',input_shape=(img_rows,img_cols,img_channels)))  #80*80*4
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 4, 4, subsample=(2, 2), border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3, subsample=(1, 1), border_mode='same'))
    model.add(Activation('relu'))
    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dense(ACTIONS))
   
    adam = Adam(lr=LEARNING_RATE)
    model.compile(loss='mse',optimizer=adam)
    print("We finish building the model")
    return model

def trainNetwork(model, target_model, args, round_n):
    # open up a game state to communicate with emulator
    game_state = game.GameState()

    # store the previous observations in replay memory
    D = deque()

    # get the first state by doing nothing and preprocess the image to 100x50x4
    do_nothing = np.zeros(ACTIONS)
    do_nothing[0] = 1
    x_t, r_0, terminal = game_state.frame_step(do_nothing)

    x_t = skimage.color.rgb2gray(x_t)
    x_t = skimage.transform.resize(x_t,(img_rows,img_cols))
    x_t = skimage.exposure.rescale_intensity(x_t,out_range=(0,255))

    x_t = x_t / 255.0

    s_t = np.stack((x_t, x_t, x_t, x_t), axis=2)

    #In Keras, need to reshape
    s_t = s_t.reshape(1, s_t.shape[0], s_t.shape[1], s_t.shape[2])

    if args['mode'] == 'Run':
        OBSERVE = 999999999
        epsilon = FINAL_EPSILON
        print ("Now we load weight")
        model.load_weights(args['name'] + "_model.h5")
        adam = Adam(lr=LEARNING_RATE)
        model.compile(loss='mse',optimizer=adam)
        print ("Weight load successfully")  
        print('New game start!')  
    else:
        # try:
        #     model.load_weights(args['name'] + "_model.h5")
        #     print('model loaded!')
        # except:
        #     make_json(args['name'])
        #     print('new model!')
        # target_model.set_weights(model.get_weights())
        OBSERVE = OBSERVATION
        epsilon = INITIAL_EPSILON

    t = 0
    score = 0
    for i in range(TRAIN_ITER + OBSERVE):
        loss = 0
        Q_sa = 0
        action_index = 0
        r_t = 0
        a_t = np.zeros([ACTIONS])
        #choose an action epsilon greedy
        if t % FRAME_PER_ACTION == 0:
            if random.random() <= epsilon:
                print("----------Random Action----------")
                action_index = random.randrange(ACTIONS)
                a_t[action_index] = 1
            else:
                q = model.predict(s_t)
                max_Q = np.argmax(q)
                action_index = max_Q
                a_t[max_Q] = 1

        #We reduced the epsilon gradually
        if epsilon > FINAL_EPSILON and t > OBSERVE:
            epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE

        #run the selected action and observed next state and reward
        x_t1_colored, r_t, terminal = game_state.frame_step(a_t)
        if args['mode'] == 'Run':
            if r_t == 1:
                score += 1
                print('Now score: %d' % score)
            elif r_t == -1:
                print('Final score: %d' % score)
                score = 0
                print('New game start!')

        x_t1 = skimage.color.rgb2gray(x_t1_colored)
        x_t1 = skimage.transform.resize(x_t1,(img_rows,img_cols))
        x_t1 = skimage.exposure.rescale_intensity(x_t1, out_range=(0, 255))

        x_t1 = x_t1 / 255.0

        x_t1 = x_t1.reshape(1, x_t1.shape[0], x_t1.shape[1], 1) #1x80x80x1
        s_t1 = np.append(x_t1, s_t[:, :, :, :3], axis=3)

        # store the transition in D
        if args['mode'] == 'Train':
            D.append((s_t, action_index, r_t, s_t1, terminal))
            if len(D) > REPLAY_MEMORY:
                D.popleft()

        #only train if done observing
        if t > OBSERVE:
            #sample a minibatch to train on
            minibatch = random.sample(D, BATCH)

            #Now we do the experience replay
            state_t, action_t, reward_t, state_t1, terminal = zip(*minibatch)
            state_t = np.concatenate(state_t)
            state_t1 = np.concatenate(state_t1)
            targets = model.predict(state_t)
            # Q_sa = model.predict(state_t1)
            if t % 500 == 0:
                target_model.set_weights(model.get_weights())
                print('Target network update!')
            Q_sa = target_model.predict(state_t1)
            targets[range(BATCH), action_t] = reward_t + GAMMA*np.max(Q_sa, axis=1)*np.invert(terminal)

            loss += model.train_on_batch(state_t, targets)

        s_t = s_t1
        t = t + 1

        # save progress every 10000 iterations
        if t % 1000 == 0 and args['mode'] == 'Train':
            print("Now we save model.")
            model.save_weights(args['name'] + "_model.h5", overwrite=True)
            with open(args['name'] + "_model.json", "w") as outfile:
                json.dump(model.to_json(), outfile)

        # print info
        state = ""
        if t <= OBSERVE:
            state = "observe"
        elif t > OBSERVE and t <= OBSERVE + EXPLORE:
            state = "explore"
        else:
            state = "train"

        if args['mode'] == 'Train':
            print("ROUND", round_n,  "/ TIMESTEP", t, "/ STATE", state, \
                "/ EPSILON", epsilon, "/ ACTION", action_index, "/ REWARD", r_t, \
                "/ Q_MAX " , np.max(Q_sa), "/ Loss ", loss)

    print("Round finished!")
    print("************************")

def playGame(args):
    model = buildmodel()
    target_model = buildmodel()

    try:
        model.load_weights(args['name'] + "_model.h5")
        print('model loaded!')
    except:
        make_json(args['name'])
        print('new model!')

    for i in range(TOTAL_ROUND):
        target_model.set_weights(model.get_weights())
        trainNetwork(model, target_model, args, i+1)

def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-m','--mode', help='Train / Run', required=True)
    parser.add_argument('-n','--name', help='Model name', default='default', required=False)
    args = vars(parser.parse_args())
    playGame(args)

if __name__ == "__main__":
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    from keras import backend as K
    K.set_session(sess)
    main()
