"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat
import visualize
import multiprocessing
import os
import pickle
import numpy as np
import time
import random
import datetime
import math
#import file
file1 = open('processed.csv', 'r')
forex = file1.readlines()
forex = [i.strip() for i in forex]
forex = forex[::-1]



def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    balance = 1000
    pnl = 0
    fitness = 0
    highest = balance
    done = False
    nontrade = 0
    while done == False:
        position = 0 #0 for nothing, 1 for long, -1 for short
        pnl = 0
        openprice = 0
        amount = 0
        lowestpnl = 0
        highestpnl = 0
        for index, data in enumerate(forex):
            ohlcv = data.split(',')
            #print(f'Date: {ohlcv[0]}, Open: {ohlcv[1]}, High: {ohlcv[2]}, Low: {ohlcv[3]}, Close: {ohlcv[4]}, VBTC: {ohlcv[5]}, VUSDT: {ohlcv[6]}')
            #convert date to timestamp
            #ohlcv[0] = time.mktime(datetime.datetime.strptime(ohlcv[0], "%Y-%m-%d %H:%M:%S").timetuple())
            #convert to string
            ohlcv = [float(i) for i in ohlcv]
            #previousdata
            prev1 = forex[index -1].split(',')
            prev1 = [float(i) for i in ohlcv]
            prev1.pop(0)
            ohlcv = ohlcv + prev1
            prev2 = forex[index -2].split(',').pop(0)
            prev2= [float(i) for i in ohlcv]
            prev2.pop(0)
            ohlcv = ohlcv + prev2
            #print(ohlcv)
            #append open trade
            ohlcv.append(position)
            #append pnl
            if position == 1 :
                nontrade = 0
                pnl = (ohlcv[4] - openprice) * (amount / ohlcv[4]) * 100
            if position == -1:
                nontrade = 0
                pnl = (openprice - ohlcv[4]) * (amount / ohlcv[4]) * 100
            if position == 0:
                nontrade += 1
                pnl = 0
            if lowestpnl > pnl:
                lowestpnl = pnl
            if pnl > highestpnl:
                highestpnl = pnl
            ohlcv.append(pnl)
            #break if pnl < balance
            if pnl > balance:
                balance = 0
                done = True
                return balance
            if nontrade > 30:
                return -5000
            #append openprice
            ohlcv.append(openprice)
            #append balance
            ohlcv.append(balance)
            closetrade, openlong, openshort = net.activate(ohlcv)
            #print(f'Data - {round(closetrade)} {round(openlong)} {round(openshort)}')
            #print(round(opentrade) != round(closetrade))
            if position == 0:
                #check if both 0 or 1
                if round(openlong) != round(openshort):
                    #open long
                    if round(openlong) > 0:
                        position = 1
                        openprice = ohlcv[4]
                        amount = balance * 0.05
                        balance -= amount * 0.003
                    #open short
                    if round(openshort) > 0:
                        position = -1
                        openprice = ohlcv[4]
                        amount = balance * 0.05
                        balance -= amount * 0.003
                    #print(f'New position -- Open Price: {ohlcv[4]} Position: {position} Amount: {amount}')
            #close position
            if round(position) != 0 and round(closetrade) == 1 and pnl != 0:
                #add reward for every closing trade
                openprice = 0
                balance = balance + pnl
                #print(balance)
                position = 0
                amount = 0
                if balance > highest:
                    highest = balance
                #print(f'Close position -- Close Price: {ohlcv[4]} PnL: {pnl} Balance: {balance}')
            if balance < 1:
                balance = 0   
        #print(balance)
        done = True
    if balance < 1000:
        balance = -1000
    return balance


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)
def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.Checkpointer(100))
    #pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint-855.gz')
    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    winner = pop.run(pe.evaluate)

    # Save the winner.
    with open('winner', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)




if __name__ == '__main__':
    run()