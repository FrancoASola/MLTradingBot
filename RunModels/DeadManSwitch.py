import bitmex
import pandas as pd
import time

##Initiation 
client = bitmex.bitmex(test=False, config=None, api_key="_XMpt4HNveijYNO0xPpEKYd_", api_secret="Hnk4sXdCDTSVX5tPW7zJKXC3l1WZi0hgkV-ES00oLoHgLkwI")
symbol_bx="ETHUSD"
contracts=500
orders=[]
cur_candle_time=0
cur_time=datetime.datetime.utcnow()
orders_completed=0
Time="15m"

for i in range(100000000):
    
    df = pd.read_csv("/Users/Franco/Desktop/API/Bitmex/Action15m.csv")  # read in specific file

    trade_df=df

    action_t=trade_df['Time'][0]

    action_time=datetime.datetime.strptime(action_t, "%Y-%m-%d %H:%M:%S")
    action=trade_df['Action'][0]

    past_action=trade_df['PastAction'][0]

    
    if abs(cur_time.timestamp()-action_time.timestamp())>3600:

        ##CHECK POSITIONS
        cur_pos=client.Position.Position_get().result()
        cur_contracts=abs(cur_pos[0][0]['currentQty'])

        if action=="Buy":
            orders.append(client.Order.Order_new(symbol=symbol_bx, orderQty=-cur_contracts).result())
            print("Position Exited")
            break
            
        if action=="Sell":
            orders.append(client.Order.Order_new(symbol=symbol_bx, orderQty=cur_contracts).result())
            print("Position Exited")
            break
    
    print("cycle complete")
    time.sleep(1800)