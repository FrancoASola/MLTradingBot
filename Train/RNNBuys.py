import pandas as pd
from collections import deque
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, CuDNNLSTM, BatchNormalization
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.callbacks import ModelCheckpoint, ModelCheckpoint
import time
from sklearn import preprocessing



SEQ_LEN = 30  # how long of a preceeding sequence to collect for RNN
RATIO_TO_PREDICT = "Close"
EPOCHS = 10  # how many passes through our data
BATCH_SIZE = 100  # how many batches? Try smaller batch if you're getting OOM (out of memory) errors.


BinTime="15m"
pct=0.3
FUTURE_PERIOD_PREDICT = 1  

NAME = f"{SEQ_LEN}-SEQ-{FUTURE_PERIOD_PREDICT}-PRED-{int(time.time())}"

#Classify whether its a buy or sell depending on the change percentage between curr and future.
def classify(current, future):
    change_percent = ((float(future) - float(current)) / float(current)) * 100
    if change_percent > float(pct):
        return 1
    else:
        return 0


# Preprocess data for training and validation

def preprocess_df(df):
    df = df.drop("future", 1)  # don't need this anymore.
    for col in df.columns:  
        if col != "target":  
            df[col] = (df[col].pct_change()) # normalize different currencies
            df.dropna(inplace=True)  
            df[col].dropna(inplace=True)  
            df[col] = preprocessing.scale(df[col].values)        #scale(df[col].values)  # scale between 0 and 1.
                     

    df.dropna(inplace=True) 


    sequential_data = []  
    prev_days = deque(maxlen=SEQ_LEN)  

    for i in df.values: 
        prev_days.append([n for n in i[:-1]]) 
        if len(prev_days) == SEQ_LEN: 
            sequential_data.append([np.array(prev_days), i[-1]])  
    
    random.shuffle(sequential_data) 

    buys = []  # list that will store our buy sequences and targets
    sells = []  # list that will store our sell sequences and targets
   

    #Check if for target
    for seq, target in sequential_data: 
        if target == 0:  
            sells.append([(seq), (target)])  
        elif target == 1:  
            buys.append([(seq), (target)]) 

    random.shuffle(buys)  
    random.shuffle(sells)  


    #Ensure there is equal number of buys and sells
    lower = min(len(buys), len(sells))  
    buys = buys[:lower] 
    sells = sells[:lower]  
  
    #Data is both buys & sells
    sequential_data = buys+sells  
    random.shuffle(sequential_data)  
    
    X = []
    y = []

    for seq, target in sequential_data: 
        X.append(seq)  
        y.append(target) 

    return np.array(X), y  


main_df = pd.DataFrame() 

#Select data used. Change file name or path if necessary
dataset = f'ResultsRNN{BinTime}.csv' 
df = pd.read_csv(dataset) 
df.set_index("Time", inplace=True)
main_df=df

main_df.fillna(method="ffill", inplace=True)  
main_df.dropna(inplace=True)

main_df['future'] = main_df[f'Close'].shift(-FUTURE_PERIOD_PREDICT)
main_df['target'] = list(map(classify, main_df[f'Close'], main_df['future']))
main_df.dropna(inplace=True)

times = sorted(main_df.index.values) 

#Seperate training and validation data
last_5pct = sorted(main_df.index.values)[-int(0.05*len(times))]  
validation_main_df = main_df[(main_df.index >= last_5pct)]  
main_df = main_df[(main_df.index < last_5pct)]  

train_x, train_y = preprocess_df(main_df)
validation_x, validation_y = preprocess_df(validation_main_df)

print(f"train data: {len(train_x)} validation: {len(validation_x)}")
print(f"Dont buys: {train_y.count(0)}, buys: {train_y.count(1)}, sells: {train_y.count(-1)}")
print(f"VALIDATION Dont buys: {validation_y.count(0)}, buys: {validation_y.count(1)}")

##Assemble model. CuDNNLSTM. Trial and error were used for current parameters. Feels free to experiment with other things
model = Sequential()
model.add(CuDNNLSTM(128, input_shape=(train_x.shape[1:]), return_sequences=True))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(CuDNNLSTM(128, return_sequences=True))
model.add(Dropout(0.1))
model.add(BatchNormalization())

model.add(CuDNNLSTM(128))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(Dense(32, activation='sigmoid'))
model.add(Dropout(0.2))

model.add(Dense(2, activation='softmax'))

# Add optimizer
opt = tf.keras.optimizers.Adam(lr=1e-4, decay=1e-6)

# Compile model
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=opt,
    metrics=['accuracy']
)

tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))

filepath = "RNN_Final-{epoch:02d}-{val_acc:.3f}" 
checkpoint = ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max'))

# Train model
history = model.fit(
    train_x, train_y,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=(validation_x, validation_y),
    callbacks=[tensorboard, checkpoint],
)

# Score model
score = model.evaluate(validation_x, validation_y, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
# Save model
model.save("models/{}".format(NAME))