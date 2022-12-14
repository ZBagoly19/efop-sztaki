"""
@author: Bagoly Zoltán
         zoltan.bagoly@gmail.com
"""
#import random
import scipy.io
#import math
import numpy as np
#import time
import matplotlib.pyplot as plt
#from sklearn.preprocessing import MinMaxScaler


# adat elokeszites
my_training_data = []
my_testing_data = []
LEN_OF_SEGMENTS = 1
NUM_OF_INPUT_DATA_TYPES = 11 + 2 # 11 angles, deviation dist, velocity
NUM_OF_OUTPUT_DATA_TYPES = 1
LEN_OF_INPUT = NUM_OF_INPUT_DATA_TYPES * LEN_OF_SEGMENTS
LEN_OF_OUTPUT = NUM_OF_OUTPUT_DATA_TYPES * LEN_OF_SEGMENTS
DATA_STRIDE = 2  # ez matlab-os TS 0.01-hez, 0.001-re legyen 20
NUM_OF_OUT_MOM = 1
# az adat tizedmásodpercenként van rögzítve, ezzel lehet ugrani benne. 
# Ha 10, másodpercenként olvasunk belőle
TEST_DATA_PART_RECIP = 5
TESTED_BIT = 0             # kisebb kell legyen a TEST_DATA_PART_RECIP-nel
# time_ = int(time.time())
# print("time:", time_)
glob_train_segs = []
glob_test_segs = []
x_glob_train_tmp = []
y_glob_train_tmp = []
x_glob_test_tmp = []
y_glob_test_tmp = []
test_ids = []
train_ids = []
#mat = scipy.io.loadmat("meas_cornercut0_speed50_gas_brake_long_sens.mat")

class Data_read():
        
    def read_from_raw_data(self, source, start_of_last):
        print("Data preparation")
        mat = scipy.io.loadmat(source)
        
        # Kimenetek
        WheAng = mat["WheAng_avg"]
        # Gas = mat["Gas"]
        # Brake = mat["Brake"]
        # A_X = mat["AccX"]
        
        # Bemenetek
        Vel = mat["Vel"]

        DevDist000 = mat["DevDist000"]
        
        angles = [None] * (NUM_OF_INPUT_DATA_TYPES - 2)
        # -2: az input sok angle-bol es 2 adatbol all, a sebessegbol es a lateral errorbol
        idx = 0
        for i in range(000, 201, 50):
            angles[idx] = mat["DevAng{:03d}".format(i)]
            idx += 1
        for j in range(250, 501, 50):
            angles[idx] = mat["DevAng{:03d}".format(j)]
            idx += 1
        
        segment = 20   # ez matlab-os TS 0.01-hez, 0.001-re legyen 200
        seg_cnt = 0
        while segment <= start_of_last:
            seg_cnt += 1
            
            target = my_training_data
            trg = "train"
            # if we will stay in bounds if we get a test data
            if segment <= start_of_last:
                # if seg_cnt % TEST_DATA_PART_RECIP == TESTED_BIT:
                # print(seg_cnt, segment, int(start_of_last * 0.9))
                if segment < int(start_of_last * 0.2):
                    target = my_testing_data
                    trg = "test"
                    # segment += 500
                # elif int(start_of_last * 0.8) < segment:
                #     target = my_training_data
                #     trg = "train"
                else:
                    target = my_training_data
                    trg = "train"
            else:
                target = my_training_data
                trg = "train"
                
            # if seg_cnt % 1 == 0:
            #     #print(seg_cnt)
            #     print(segment)
            #     print(trg)
            
            my_input = [None] * NUM_OF_INPUT_DATA_TYPES
            my_output = [None] * NUM_OF_OUTPUT_DATA_TYPES * NUM_OF_OUT_MOM
            
            # angle = -1 * Orientation [segment]
            
            # rand_x = random.randint(-100, 100)
            # rand_y = random.randint(-100, 100)
            # rand_x = 0
            # rand_y = 0
            
            x_glob_test_tmp = [None] * LEN_OF_SEGMENTS
            y_glob_test_tmp = [None] * LEN_OF_SEGMENTS
            x_glob_train_tmp = [None] * LEN_OF_SEGMENTS
            y_glob_train_tmp = [None] * LEN_OF_SEGMENTS
            
            for i in range(len(angles)):
                my_input[i] = angles[i][segment] * 3
            my_input[len(angles)] = DevDist000 [segment] * 5
            my_input[len(angles) + 1] = Vel [segment] * 0.4
            
            # if segment == 0:
            #     print(my_input[0], my_input[1])
            # for i in range(NUM_OF_OUT_MOM):
               # print("i", i)
                # print("segment + i", segment + i)
                
                # if trg == "test":
                #     x_glob_test_tmp[i] = Pos_X [segment + i]
                #     y_glob_test_tmp[i] = Pos_Y [segment + i]
                # else:
                #     x_glob_train_tmp[i] = Pos_X [segment + i]
                #     y_glob_train_tmp[i] = Pos_Y [segment + i]
                
            my_output[0] = WheAng [segment] * 10
            # my_output[1] = Gas [segment] * 4
            # my_output[2] = Brake [segment] * 4
            # my_output[3] = A_X [segment] # * valami súly a hossz gyorsulásnak
            
            # if segment == 0:
            #     print(my_output)
            # if len(my_input) != 400:
            #     print(len(my_input))
            # A [:] nelkul csak referencia atadas tortenik, .clear()-kor torli innen is
            if trg == "test":
                glob_test_segs.append([x_glob_test_tmp[:], y_glob_test_tmp[:]])
                test_ids.append(segment)
                #segment += 500
            else:
                glob_train_segs.append([x_glob_train_tmp[:], y_glob_train_tmp[:]])
                train_ids.append(segment)
            
            target.append([np.array(my_input), np.array(my_output)])
            #print(segment, "my_out", np.array(my_output), np.array(my_output).shape)
            #print("my_in", np.array(my_output).shape, np.array(my_input))
            
            segment += DATA_STRIDE
        
        if any(x in set(test_ids) for x in train_ids):
            print("Átfedés a test és train adatok között!!!")
        else:
            print("done, saving")
            #print("test data", np.array(my_testing_data).shape)
            #print("train data", np.array(my_training_data).shape)
            np.save("testing_data_first20pct_test_unshuffled_LongLong_cc0_acc333__ritka_70kmph" + str(TESTED_BIT) + ".npy", my_testing_data)
            np.save("training_data_first20pct_test_unshuffled_LongLong_cc0_acc333__ritka_70kmph" + str(TESTED_BIT) + ".npy", my_training_data)
            
            np.random.shuffle(my_testing_data)
            np.save("testing_data_first20pct_test_LongLong_cc0_acc333__ritka_70kmph" + str(TESTED_BIT) + ".npy", my_testing_data)
            np.random.shuffle(my_training_data)
            np.save("training_data_first20pct_test_LongLong_cc0_acc333__ritka_70kmph" + str(TESTED_BIT) + ".npy", my_training_data)

        
dr = Data_read()
#dr.read_from_raw_data("meas01.mat", 10118 - LEN_OF_SEGMENTS)
#dr.read_from_raw_data("meas02.mat", 10305 - LEN_OF_SEGMENTS)
#dr.read_from_raw_data("data_zoli_carmaker_leaf_02.mat", 137238 - LEN_OF_SEGMENTS)
#dr.read_from_raw_data("meas_X_Y_Ori_Vel_AngVel_mom1sec.mat", 1373 - LEN_OF_SEGMENTS)
dr.read_from_raw_data("meas_cornercut0_speed70_acc333_longlong_sens.mat", 163637 - LEN_OF_SEGMENTS)


# Vizualizacio
def visualization():
    # plt.figure(1)
    # for segm in glob_test_segs:
    #     plt.plot(segm[0], segm[1])
    # plt.show()
    
    # plt.figure(2)
    # for segm in glob_test_segs:
    #     plt.plot(segm[0], segm[1])
    # for segm in glob_train_segs:
    #     plt.plot(segm[0], segm[1])
    # plt.show()
    
    d_dist = []
    d_ang = []
    sw = []
    which_one = 0
    for i in range(my_testing_data[0][0].size):
        if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 0:
            d_dist.append(my_testing_data[which_one][0][i])
        if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 1:
            d_ang.append(my_testing_data[which_one][0][i])
    for i in range(my_testing_data[0][1].size):
        sw.append(my_testing_data[which_one][1][i])
    plt.figure(101)
    plt.title("test " + str(which_one))
    print("test")
    plt.plot(d_dist, 'blue', marker='o', label='distance')
    print("dist:", d_dist[0], "/ 6=", d_dist[0]/6)
    plt.plot(d_ang, 'green', marker='o', label='angle')
    print("ang:", d_ang[0])
    plt.plot(sw, 'black', marker='o', label='sw')
    print("sw:", sw[0], "x2=", sw[0]*2)
    plt.legend(loc=1)
    plt.show()
    
    d_dist = []
    d_ang = []
    sw = []
    which_one = 0
    for i in range(my_training_data[0][0].size):
        if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 0:
            d_dist.append(my_training_data[which_one][0][i])
        if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 1:
            d_ang.append(my_training_data[which_one][0][i])
    for i in range(my_training_data[0][1].size):
        sw.append(my_training_data[which_one][1][i])
    plt.figure(102)
    plt.title("train " + str(which_one))
    print("train")
    plt.plot(d_dist, 'blue', marker='o', label='distance')
    print("dist:", d_dist[0], "/ 6=", d_dist[0]/6)
    plt.plot(d_ang, 'green', marker='o', label='angle')
    print("ang:", d_ang[0])
    plt.plot(sw, 'black', marker='o', label='sw')
    print("sw:", sw[0], "x2=", sw[0]*2)
    plt.legend(loc=1)
    plt.show()
    
    # fig_idx = 0
    # for seg in my_testing_data:
    #     d_dist = []
    #     d_ang = []
    #     sw = []
    #     for i in range(my_testing_data[1][0].size):
    #         if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 0:
    #             d_dist.append(seg[0][i])
    #         if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 1:
    #             d_ang.append(seg[0][i])
    #     for i in range(my_testing_data[1][0].size):
    #         sw.append(my_testing_data[which_one][1][i])
    #     plt.figure(fig_idx)
    #     plt.plot(d_dist, 'blue')
    #     plt.plot(d_ang, 'green')
    #     plt.plot(sw, 'black')
    #     plt.show()
    #     fig_idx += 1
    # plt.figure(fig_idx)
    # for seg in my_testing_data:
    #     d_dist = []
    #     d_ang = []
    #     sw = []
    #     for i in range(my_testing_data[1][0].size):
    #         if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 0:
    #             d_dist.append(seg[0][i])
    #         if i % int(LEN_OF_INPUT / LEN_OF_SEGMENTS) == 1:
    #             d_ang.append(seg[0][i])
    #     for i in range(my_testing_data[1][0].size):
    #         sw.append(my_testing_data[which_one][1][i])
    #     plt.figure(fig_idx)
    #     plt.plot(d_dist, 'blue')
    #     plt.plot(d_ang, 'green')
    #     plt.plot(sw, 'black')
    # plt.show()

# print("done, visualizing")
# visualization()
