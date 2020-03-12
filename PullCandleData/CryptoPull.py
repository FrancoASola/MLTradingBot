import gdax
import datetime, time, csv
from numpy import diff
import numpy as np
import pandas as pd
from itertools import zip_longest
client = gdax.PublicClient()


##Inputs
symbol='ETH-USD'
binsize=15
dt=1200
##MA Paremeters

MA1Period=20
MA2Period=30
VMAPeriod=10
##EMA Parameters
EMA1Period=26      #Slow MACD EMA
EMA2Period=12       #Fast MACD EMA
EMA3Period=9
alpha1=2/(EMA1Period+1)     ##Needed for Calculation
alpha2=2/(EMA2Period+1)
alpha3=2/(EMA3Period+1)
EMA1Cntr=0
EMA2Cntr=0
EMA3Cntr=0

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

granularity=binsize*60

for j in range (dt):
   
    startTime = datetime.datetime.now()-datetime.timedelta(minutes=(200*binsize*dt))+datetime.timedelta(hours=7)   #Start time !!WARNING!! change binsizeT to correct size
    endTime = datetime.datetime.now()-datetime.timedelta(minutes=200*binsize*(dt-1))+datetime.timedelta(hours=7)
    dt+=-1
    candles=client.get_product_historic_rates(product_id=symbol, start=startTime, end=endTime,  granularity=granularity)
    candles.reverse()
    Candles.extend(candles)
    time.sleep(0.5)
    


for Candle in Candles:
    CandleTime.append(Candle[0])
    CandleOpen.append(Candle[3])
    CandleClose.append(Candle[4])
    CandleHigh.append(Candle[2])
    CandleLow.append(Candle[1])
    CandleVolume.append(Candle[5])

for i in range(len(CandleClose)):
    
    #MA Calculation
    if i>=MA1Period:
        MA1=sum(CandleClose[i-MA1Period:i])/MA1Period
        #print("MA1=" + str(MA1))
    if i>=MA2Period:
        MA2=sum(CandleClose[i-MA2Period:i])/MA2Period
    if i>=VMAPeriod:
        VMA.append(sum(CandleVolume[i-VMAPeriod:i])/VMAPeriod)
    ##EMAs Calculation
    if i>=EMA1Period:
        if i==EMA1Period:
            EMA1.append(sum(CandleClose[-EMA1Period:])/EMA1Period)    ##First one is a SMA
        else:
            EMA1.append(((CandleClose[i]-EMA1[EMA1Cntr-1])*alpha1)+EMA1[EMA1Cntr-1])
        EMA1Cntr=EMA1Cntr+1
    if i>=EMA2Period:
        if i==EMA2Period:
            EMA2.append(sum(CandleClose[-EMA2Period:])/EMA2Period)    ##First one is a SMA
        else:
            EMA2.append(((CandleClose[i]-EMA2[EMA2Cntr-1])*alpha2)+EMA2[EMA2Cntr-1])
        EMA2Cntr=EMA2Cntr+1
    if i>=EMA3Period:
        if i==EMA3Period:
            EMA3.append(sum(CandleClose[-EMA3Period:])/EMA3Period)    ##First one is a SMA
        else:
            EMA3.append(((CandleClose[i]-EMA3[EMA3Cntr-1])*alpha3)+EMA3[EMA3Cntr-1])
        EMA3Cntr=EMA3Cntr+1            
    #MACD Calculation
    if i>=EMA1Period:
        MACDLine.append(EMA2[EMA2Cntr-1]-EMA1[EMA1Cntr-1])
        MACDCur=EMA2[EMA2Cntr-1]-EMA1[EMA1Cntr-1] 
        if i==(EMA1Period+MACDEMAPeriod-1):
            MACDSignalCur=sum(MACDLine[-MACDEMAPeriod:])/MACDEMAPeriod
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
        AvgGain=sum(j for j in GainLoss[-RSIPeriod:] if j>0)/RSIPeriod
        AvgLoss=(sum(j for j in GainLoss[-RSIPeriod:] if j<0)/RSIPeriod)*-1
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
        AvgGain=((LastAvgGain*(RSIPeriod-1)+Gain)/RSIPeriod)
        AvgLoss=((LastAvgLoss*(RSIPeriod-1)+Loss)/RSIPeriod)
        AvgGainlst.append(AvgGain)
        AvgLosslst.append(AvgLoss)
        RS=AvgGain/AvgLoss
        RSIcur=100-(100/(1+RS))
        RSI.append(RSIcur)
    #BB Calculation 
    if i>=BBLength:
        BBStd=np.std(CandleClose[-BBLength:])
        BBMiddle.append(MA1)
        BBTopCur=MA1+(2*BBStd)
        BBBotCur=MA1-(2*BBStd)
        BBTop.append(BBTopCur)
        BBBot.append(BBBotCur)
        BBRatios.append(1-(BBBotCur/BBTopCur))
        

##EMA
gEMA1=np.gradient(EMA1,1)
dEMA1=diff(EMA1)
gEMA2=np.gradient(EMA2,1)
dEMA2=diff(EMA2)
gEMA3=np.gradient(EMA3,1)
dEMA3=diff(EMA3)
##MACD
gMACDLine=np.gradient(MACDLine,1)
dMACDLine=diff(MACDLine)
gMACDSignal=np.gradient(MACDSignal,1)
dMACDSignal=diff(MACDSignal)

##RSI
gRSI=np.gradient(RSI,1)
dRSI=diff(RSI)

##BB
gBBMiddle=np.gradient(BBMiddle,1)
dBBMiddle=diff(BBMiddle)
gBBTop=np.gradient(BBTop,1)
dBBTop=diff(BBTop)
gBBBot=np.gradient(BBBot,1)
dBBBot=diff(BBBot)

DataLength=len(CandleClose)-50
headersRNN=["Time",'Close', 'Volume', 'VMA',  'RSI', 'dRSI', 'gRSI', 'MACD', 'dMACD', 'gMACD', 'Signal', 'dSignal', 'gSignal', 'TBB', 'dTBB', 'gTBB', 'BBB', 'dBBB', 'gBBB']
d=np.column_stack((CandleTime[-DataLength:-75] ,CandleClose[-DataLength:-75], CandleVolume[-DataLength:-75], VMA[-DataLength:-75], RSI[-DataLength:-75],dRSI[-DataLength:-75],gRSI[-DataLength:-75],MACDLine[-DataLength:-75],dMACDLine[-DataLength:-75],gMACDLine[-DataLength:-75],MACDSignal[-DataLength:-75],dMACDSignal[-DataLength:-75],gMACDSignal[-DataLength:-75],BBTop[-DataLength:-75],dBBTop[-DataLength:-75],gBBTop[-DataLength:-75],BBBot[-DataLength:-75],dBBBot[-DataLength:-75],gBBBot[-DataLength:-75]))
dm=np.column_stack((CandleTime[-75:] ,CandleClose[-75:], CandleVolume[-75:], VMA[-75:], RSI[-75:],dRSI[-75:],gRSI[-75:],MACDLine[-75:],dMACDLine[-75:],gMACDLine[-75:],MACDSignal[-75:],dMACDSignal[-75:],gMACDSignal[-75:],BBTop[-75:],dBBTop[-75:],gBBTop[-75:],BBBot[-75:],dBBBot[-75:],gBBBot[-75:]))

print(DataLength)
with open(f"ResultsRNN{binsize}m.csv","w",  encoding="ISO-8859-1", newline="") as csvfile:
    for i in range(len(d)):
        writer= csv.writer(csvfile)
        if i==0:
            writer.writerow(headersRNN)
            writer.writerow(d[i])
        else:
            writer.writerow(d[i])
csvfile.close()
with open(f"ResultsRNN{binsize}mModel.csv","w",  encoding="ISO-8859-1", newline="") as csvfile:
    for i in range(len(dm)):
        writer= csv.writer(csvfile)
        if i==0:
            writer.writerow(headersRNN)
            writer.writerow(dm[i])
        else:
            writer.writerow(dm[i])
csvfile.close()