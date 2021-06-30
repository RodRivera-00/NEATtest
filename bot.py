from binance.client import Client
import json
import threading
import os
import time
client = Client('BynirAL6vuOkjLicv51ZfW7iD37wBMzLx2eRX4ismvwIm0l6K65M6dejGeYIuvK1', 'rBYmd3bFptXr5XbU5mGCDC4Lp1AlBBeeu3EiANmfHzc9EU7rY5Re9X7xVza4dwBu')
#Globals
Positions = None
Messages = []
PositionMsg = []
Total = 1
PNL = 1
prev = [0,0]
#Functions
def getBalance():
    accounts = client.futures_account_balance()
    result = 0
    for account in accounts:
        if account["asset"] == "USDT":
            result = account["balance"]
    return result

def TakeProfit(position):
    if float(position["positionAmt"]) > 0:
        return float(position["entryPrice"]) * (1/float(position["leverage"]) + 2)
    else:
        return float(position["entryPrice"]) * (1-2/float(position["leverage"]))
def getTrades(prevpositions):
    positions = client.futures_position_information()
    result = []
    for position in positions:
        added = False
        if prevpositions is not None:
            for prevpos in prevpositions:
                if prevpos["symbol"] == position["symbol"]:
                    added = True
        if float(position["positionAmt"]) != 0 and added == False:
            result.append(position)
    return result

def positionValue(position):
    if float(position["positionAmt"]) > 0:
        positionvalue = float(position["positionAmt"]) * float(position["entryPrice"]) / float(position["leverage"])
        position["side"] = "BUY"
        position["take"] = "SELL"
    else:
        positionvalue = -1 * float(position["positionAmt"]) * float(position["entryPrice"]) / float(position["leverage"])
        position["side"] = "SELL"
        position["take"] = "BUY"
    return positionvalue

def calculateTrades(positions):
    global Positions
    global Messages
    global PositionMsg
    for position in positions:
        positionvalue = positionValue(position)
        positionpercent = (float(position["unRealizedProfit"]) / positionvalue) * 100
        #print(positionpercent)
        #Check for TP
        if float(position["positionAmt"]) < 0:
            quantity = -1 * round(float(position["positionAmt"]),2)
        else:
            quantity = round(float(position["positionAmt"]),2)
        if positionpercent > 200:
            client.futures_create_order(symbol=position['symbol'],side=position["take"],type="MARKET",quantity=quantity)
            Messages.append(f'TAKE PROFIT | PAIR: {str(position["symbol"])} | Amount: {positionvalue}')
            for msg in PositionMsg:
                if position["symbol"] in msg:
                    PositionMsg.remove(msg)
        #Check for -100 Loss
        if positionpercent < -100:
            if float(position["positionAmt"]) < 0:
                quantity = -1 * round(float(position["positionAmt"]),2)
            else:
                quantity = round(float(position["positionAmt"]),2)
            if positionvalue < 200:
                try:
                    client.futures_create_order(symbol=position['symbol'],side=position["side"],type="MARKET",quantity=quantity)
                    Messages.append(f"Position | Amount: {positionvalue} | Symbol: {position['symbol']}" )
                except Exception:
                    pass
            
def printer(positions):
    global PositionMsg
    global Total
    global PNL
    global prev
    for position in positions:
        for msg in PositionMsg:
            if position['symbol'] in msg:
                PositionMsg.remove(msg)
        PositionMsg.append(f"{position['symbol']}   | Amount: {round(positionValue(position),2)}    | PNL: {round(float(position['unRealizedProfit']),2)} USD   | ROE: {round(float(position['unRealizedProfit']) / positionValue(position) * 100,2)} % | Take Profit: {round(TakeProfit(position),8)}")
        Total += round(positionValue(position),2)
        PNL += round(float(position['unRealizedProfit']),2)
    if prev[0] != Total:
        Total -= prev[0]
        PNL -= prev[1]
        prev[0] = Total
        prev[1] = PNL
def Main():
    global Positions
    global Messages
    global PositionMsg
    global Total
    global PNL
    while True:

        #Get Available Positions
        #print("Getting open positions...")
        Positions = getTrades(Positions)
        os.system("clear")
        printer(Positions)
        PositionMsg.sort()
        for posmsg in PositionMsg:
            print(posmsg)
        print(f'TOTAL | Amount: {round(Total,2)} | PNL: {round(PNL,2)}    | ROE: {round((PNL/Total) * 100,2)}%')
        print('-------------------------LOG-------------------------')
        for message in Messages:
            print(message)
        #print(Positions)
        #Re-Calculate
        #print("Re-calculating orders...")
        calculateTrades(Positions)
        time.sleep(0.1)

    
thread = threading.Thread(target=Main)
thread.start()