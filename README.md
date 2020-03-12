# MLTradingBot

Cryptocurrency and FOREX trading bots.

# About
This was a hobby that I got into after I finished grad school. I have been working on it on and off for some time. <br>
<br>
Although I have found some success with this endeavor, I mostly do it for fun. I gave up working with ML about a year ago as I feel it is not very well equiped for financial markets (or I am not experienced enough to make it work in such conditions). <br>
<br>
Currently I still play around with bot trading, but in a much simplified way using MT4
<br>
<br>
Data can be pulled either for the FOREX or Crypto markets via their respective Python Files. Different indicators are computed and added to the training file. This file can then be used to train the models. I seperated the models into Buys and Sells and each model will predict a percent probability of the candle moving a certain percentage in their specific direction. The bot can then be coded to act  depending on the percent predicted by the models.
