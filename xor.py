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


runs_per_net = 2

def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    fitnesses = []
    for runs in range(runs_per_net):
        balance = 1000
        pnl = 0
        fitness = 0
        highest = balance
        done = False
        while done == False:
            position = 0 #0 for nothing, 1 for long, -1 for short
            pnl = 0
            openprice = 0
            amount = 0
            tickcount = 0

            for data in forex:
                if position != 0:
                    tickcount += 1
                ohlcv = data.split(',')
                #print(f'Date: {ohlcv[0]}, Open: {ohlcv[1]}, High: {ohlcv[2]}, Low: {ohlcv[3]}, Close: {ohlcv[4]}, VBTC: {ohlcv[5]}, VUSDT: {ohlcv[6]}')
                #convert date to timestamp
                #ohlcv[0] = time.mktime(datetime.datetime.strptime(ohlcv[0], "%Y-%m-%d %H:%M:%S").timetuple())
                #convert to string
                ohlcv = [float(i) for i in ohlcv]
                #append open trade
                ohlcv.append(position)
                #append pnl
                if position == 1 :
                    pnl = (ohlcv[4] - openprice) * (amount / ohlcv[4]) * 100
                if position == -1:
                    pnl = (openprice - ohlcv[4]) * (amount / ohlcv[4]) * 100
                if position == 0:
                    pnl = 0
                ohlcv.append(pnl)
                #break if pnl < balance
                if pnl > balance:
                    balance = 0
                    done = True
                    break
                #append openprice
                ohlcv.append(openprice)
                #append balance
                ohlcv.append(balance)
                opentrade, closetrade, openlong, openshort = net.activate(ohlcv)
                #check if both 0 or 1
                #print(round(opentrade) != round(closetrade))
                if position == 0 and round(opentrade) == 1:
                    #check if both 0 or 1
                    if round(openlong) != round(openshort):
                        #open long
                        balance += 0.1
                        if round(openlong) == 1:
                            position = 1
                            openprice = ohlcv[4]
                            amount = balance * 0.01
                            balance -= amount * 0.003
                        #open short
                        if round(openshort) == 1:
                            position = -1
                            openprice = ohlcv[4]
                            amount = balance * 0.01
                            balance -= amount * 0.003
                        #print(f'New position -- Open Price: {ohlcv[4]} Position: {position} Amount: {amount}')
                #close position
                if round(position) != 0 and round(closetrade) == 1 and pnl != 0 and tickcount > 4:
                    #add reward for every closing trade
                    openprice = 0
                    balance = balance + pnl
                    #print(balance)
                    position = 0
                    amount = 0
                    tickcount = 0
                    if balance > highest:
                        highest = balance
                    #print(f'Close position -- Close Price: {ohlcv[4]} PnL: {pnl} Balance: {balance}')
                        
            #print(balance)
            done = True
        fitnesses.append(balance)

    return np.mean(fitnesses)


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
    #pop = neat.Checkpointer.restore_checkpoint('winner')
    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    winner = pop.run(pe.evaluate)

    # Save the winner.
    with open('winner', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)




if __name__ == '__main__':
    run()