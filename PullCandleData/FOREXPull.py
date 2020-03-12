import datetime, time, csv
from numpy import diff
import numpy as np
import pandas as pd
import oandapyV20
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20 import API

access_token = ""

client = API(access_token=access_token)
dt=20
instrument="USD_CAD"
binsize=60
granularity="H1"

MA1Period=20
MA2Period=30
MA5Period=5
VMAPeriod=10
##EMA Parameters
EMA1Period=26      #Slow MACD EMA
EMA2Period=12       #Fast MACD EMA
EMA3Period=9
EMA100Period=100
alpha1=2/(EMA1Period+1)     ##Needed for Calculation
alpha2=2/(EMA2Period+1)
alpha3=2/(EMA3Period+1)
alpha100=2/(EMA100Period+1)
EMA1Cntr=0
EMA2Cntr=0
EMA3Cntr=0
EMA100Cntr=0

#MACD Parameters
MACDEMAPeriod=9
MACDCntr=0
alphaMACD=2/(MACDEMAPeriod+1)

#RSI Paremeters
RSIPeriod=14

#BB Paremeters
BBLength=20
BBMultiplier=2
Candles=[]
CandleTime=[]
CandleOpen=[]
CandleClose=[]
CandleHigh=[]
CandleLow=[]
CandleTrades=[]
CandleVolume=[]
Candlevwap=[]
EMA1=[]
EMA2=[]
EMA3=[]
EMA100=[]
MACDLine=[]
MACDSignal=[]
GainLoss=[]
AvgGainlst=[]
AvgLosslst=[]
RSI=[]
BBMiddle=[]
BBTop=[]
BBBot=[]
BBRatios=[]
VMA=[]
CandleTurnover=[]
CandleHomeNotional=[]
CandleForeingNotional=[]
Candles=[]
MA5=[]

for j in range(dt):
    startTime = (datetime.datetime.now()-datetime.timedelta(minutes=(4000*binsize*dt))).timestamp()   #Start time !!WARNING!! change binsize to correct size
    endTime = (datetime.datetime.now()-datetime.timedelta(minutes=(4000*binsize*(dt-1)))).timestamp()
    params={
    "granularity": granularity,
    "from" :f"{startTime}",
    "to":f"{endTime}"}

    dt+=-1
    r=oandapyV20.endpoints.instruments.InstrumentsCandles(instrument=instrument, params=params)
    client.request(r)
    candles=r.response['candles']
    Candles.extend(candles)
    time.sleep(0.05)
    
   
for Candle in Candles:
    Time=datetime.datetime.strptime(Candle['time'], "%Y-%m-%dT%H:%M:%S.%f000Z").timestamp()
    CandleTime.append(Time)
    CandleOpen.append(float(Candle['mid']['o']))
    CandleClose.append(float(Candle['mid']['c']))
    CandleHigh.append(float(Candle['mid']['h']))
    CandleLow.append(float(Candle['mid']['l']))
    CandleVolume.append(float(Candle['volume']))



for i in range(len(CandleClose)):
    
    #MA Calculation
    if i>=MA1Period:
        MA1=sum(CandleClose[i-MA1Period:i])/MA1Period
        #print("MA1=" + str(MA1))
    if i>=MA2Period:
        MA2=sum(CandleClose[i-MA2Period:i])/MA2Period
    if i>=VMAPeriod:
        VMA.append(sum(CandleVolume[i-VMAPeriod:i])/VMAPeriod)
    if i>=MA5Period:
        MA5.append(sum(CandleClose[i-MA5Period:i])/MA5Period)
    ##EMAs Calculation
    if i>=EMA1Period:
        if i==EMA1Period:
            EMA1.append(sum(CandleClose[i-EMA1Period:i])/EMA1Period)    ##First one is a SMA
        else:
            EMA1.append(((CandleClose[i]-EMA1[EMA1Cntr-1])*alpha1)+EMA1[EMA1Cntr-1])
        EMA1Cntr=EMA1Cntr+1
    if i>=EMA2Period:
        if i==EMA2Period:
            EMA2.append(sum(CandleClose[i-EMA2Period:i])/EMA2Period)    ##First one is a SMA
        else:
            EMA2.append(((CandleClose[i]-EMA2[EMA2Cntr-1])*alpha2)+EMA2[EMA2Cntr-1])
        EMA2Cntr=EMA2Cntr+1
    if i>=EMA3Period:
        if i==EMA3Period:
            EMA3.append(sum(CandleClose[i-EMA3Period:i])/EMA3Period)    ##First one is a SMA
        else:
            EMA3.append(((CandleClose[i]-EMA3[EMA3Cntr-1])*alpha3)+EMA3[EMA3Cntr-1])
        EMA3Cntr=EMA3Cntr+1  
    if i>=EMA100Period:
        if i==EMA100Period:
            EMA100.append(sum(CandleClose[i-EMA100Period:i])/EMA100Period)    ##First one is a SMA
        else:
            EMA100.append(((CandleClose[i]-EMA100[EMA100Cntr-1])*alpha100)+EMA100[EMA100Cntr-1])
        EMA100Cntr=EMA100Cntr+1                    
    #MACD Calculation
    if i>=EMA1Period:
        MACDLine.append(EMA2[EMA2Cntr-1]-EMA1[EMA1Cntr-1])
        MACDCur=EMA2[EMA2Cntr-1]-EMA1[EMA1Cntr-1] 
        if i==(EMA1Period+MACDEMAPeriod-1):
            MACDSignalCur=sum(MACDLine[i-MACDEMAPeriod:i])/MACDEMAPeriod
            MACDSignal.append(MACDSignalCur)
            MACDCntr=MACDCntr+1
        elif i>(EMA1Period+MACDEMAPeriod-1):
            MACDSignalCur=((MACDCur-MACDSignal[MACDCntr-1])*alphaMACD)+MACDSignal[MACDCntr-1]
            MACDSignal.append(MACDSignalCur)
            MACDCntr=MACDCntr+1        
    #RSI Calculation
    GainOrLoss=CandleClose[i]-CandleOpen[i]
    GainLoss.append(GainOrLoss)
    if i==RSIPeriod-1:
        AvgGain=sum(j for j in GainLoss[i-RSIPeriod:i] if j>0)/RSIPeriod
        AvgLoss=(sum(j for j in GainLoss[i-RSIPeriod:i] if j<0)/RSIPeriod)*-1
        AvgGainlst.append(AvgGain)
        AvgLosslst.append(AvgLoss)
        if AvgLoss != 0:
            RS=AvgGain/AvgLoss
        else:
            RS=0
        RSIcur=100-(100/(1+RS))
        RSI.append(RSIcur)
    elif i>RSIPeriod-1:
        LastAvgGain=AvgGainlst[i-RSIPeriod]
        LastAvgLoss=AvgLosslst[i-RSIPeriod]
        Gain=0
        Loss=0
        if GainOrLoss>0:
            Gain=GainOrLoss
        elif GainOrLoss<0:
            Loss=GainOrLoss*-1
        AvgGain=float((LastAvgGain*(RSIPeriod-1)+Gain)/RSIPeriod)
        AvgLoss=float((LastAvgLoss*(RSIPeriod-1)+Loss)/RSIPeriod)
        AvgGainlst.append(AvgGain)
        AvgLosslst.append(AvgLoss)
        RS=AvgGain/AvgLoss
        RSIcur=100-(100/(1+RS))
        RSI.append(RSIcur)
    #BB Calculation 
    if i>=BBLength:
        BBStd=np.std(CandleClose[i-BBLength:i])
        BBMiddle.append(MA1)
        BBTopCur=MA1+(2*BBStd)
        BBBotCur=MA1-(2*BBStd)
        BBTop.append(BBTopCur)
        BBBot.append(BBBotCur)
        BBRatios.append(1-(BBBotCur/BBTopCur))
        

##EMA
dEMA1=diff(EMA1)
dEMA2=diff(EMA2)
dEMA3=diff(EMA3)
dEMA100=diff(EMA100)
##MACD
dMACDLine=diff(MACDLine)
dMACDSignal=diff(MACDSignal)

##RSI
dRSI=diff(RSI)

##BB

dBBMiddle=diff(BBMiddle)
dBBTop=diff(BBTop)
dBBBot=diff(BBBot)

DataLength=len(CandleClose)-125
headersRNN=["Time",'Close','CloseReal', 'Open', 'Low', 'High', 'Volume', 'VMA',  
            'RSI', 'dRSI', 
            'MACD', 'dMACD', 
            'Signal', 'dSignal', 
            'TBB', 'BBB', 
            'EMA1', 'dEMA1', 
            'EMA2', 'dEMA2',
            'EMA3', 'dEMA3',
            'EMA100','dEMA100' ]
d=np.column_stack((CandleTime[-DataLength:-3000] ,MA5[-DataLength:-3000], CandleClose[-DataLength:-3000], CandleOpen[-DataLength:-3000], CandleLow[-DataLength:-3000], CandleHigh[-DataLength:-3000],
                    CandleVolume[-DataLength:-3000], VMA[-DataLength:-3000], 
                    RSI[-DataLength:-3000],dRSI[-DataLength:-3000],
                    MACDLine[-DataLength:-3000],dMACDLine[-DataLength:-3000],
                    MACDSignal[-DataLength:-3000],dMACDSignal[-DataLength:-3000],
                    BBTop[-DataLength:-3000], BBBot[-DataLength:-3000],
                    EMA1[-DataLength:-3000], dEMA1[-DataLength:-3000] ,
                    EMA2[-DataLength:-3000], dEMA2[-DataLength:-3000] ,
                    EMA3[-DataLength:-3000], dEMA3[-DataLength:-3000],
                    EMA100[-DataLength:-3000], dEMA100[-DataLength:-3000]
                    ))
print(DataLength)
with open(f"ResultsRNN{binsize}mForex.csv","w",  encoding="ISO-8859-1", newline="") as csvfile:
    for i in range(len(d)):
        writer= csv.writer(csvfile)
        if i==0:
            writer.writerow(headersRNN)
            writer.writerow(d[i])
        else:
            writer.writerow(d[i])
csvfile.close()





