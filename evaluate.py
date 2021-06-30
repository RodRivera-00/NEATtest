import time
import random
import datetime
import numpy as np
file1 = open('processed.csv', 'r')
forex = file1.readlines()
forex = [i.strip() for i in forex]
forex = forex[::-1]

balance = 1000
pnl = 0
fitness = 0
done = False
while done == False:
    position = 0 #0 for nothing, 1 for long, -1 for short
    pnl = 0
    openprice = 0
    amount = 0
    for data in forex:
        ohlcv = data.split(',')
        #print(f'Date: {ohlcv[0]}, Open: {ohlcv[1]}, High: {ohlcv[2]}, Low: {ohlcv[3]}, Close: {ohlcv[4]}, VBTC: {ohlcv[5]}, VUSDT: {ohlcv[6]}')
        #convert to string
        ohlcv = [float(i) for i in ohlcv]
        #append open trade
        ohlcv.append(position)
        #append pnl
        if position == 1 :
            pnl = ((ohlcv[4] - openprice) * 100) * (amount / ohlcv[4])
        if position == -1:
            pnl = ((openprice - ohlcv[4]) * 100) * (amount / ohlcv[4])
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
        #output = net.activate(ohlcv)
        #random position
        print(ohlcv)
        newposition = random.randrange(-1,1)
        if position == 0 and amount < balance:
            position = newposition
            openprice = ohlcv[4]
            amount = 500
            print(f'New position -- Open Price: {ohlcv[4]} Position: {newposition} Amount: {amount}')
        else:
            if newposition == 0:
                openprice = 0
                balance = balance + pnl
                position = 0
                amount = 0
                print(f'Close position -- Close Price: {ohlcv[4]} PnL: {pnl} Balance: {balance}')
    done = True
fitness = balance