import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def ob_range(ob, bound, metric, amount=None, value=None):
    data = requests.get(base_url + products + pair + '/ticker').json()
    price = float(data['price'])
    upper = price + bound
    lower = price - bound
    ob = ob[ob.price < upper]
    ob = ob[ob.price > lower]
    ob = ob.sort_values(by='price')
    colors = []
    for index in range(len(ob.price.tolist())):
        if ob['bid'].tolist()[index] == 1:
            colors.append('green')
        if ob['ask'].tolist()[index] == 1:
            colors.append('red')
    if not(amount is None):
        ob = ob[ob.amount > amount]
    if not(value is None):
        ob = ob[ob.value > value]
    ax1.clear()
    x = ob['price'].apply(lambda price: str(price)).tolist()
    y = ob[metric].tolist()
    ax1.barh(x,y,color=colors)
    plt.title('Bids and Asks', loc='center')
    plt.xticks(rotation=45)
    plt.grid(True)

def gen_ob(pair, level):
    data = requests.get(base_url + products + pair + book + level)
    data = json.loads(data.content.decode('utf-8').replace("'", '"'))
    bids = pd.DataFrame(data['bids'], columns=['price', 'amount', 'id'])
    asks = pd.DataFrame(data['asks'], columns=['price', 'amount', 'id'])
    bids['bid'] = 1
    asks['ask'] = 1
    ob = pd.concat([bids, asks])
    ob = ob.fillna(0)
    ob = ob.sort_values(by='price', ascending=False)
    ob['price'] = ob['price'].apply(lambda price: float(price))
    ob['amount'] = ob['amount'].apply(lambda amnt: float(amnt))
    ob['price'] = np.round(ob['price'], 0)
    ob['price'] = ob['price'].apply(lambda price: round_num(price, 10))
    ob_price = ob.groupby('price')
    result ={
        'price': [],
        'amount': [],
        'bid': [],
        'ask': []
    }
    for price in ob_price:
        result['price'].append(price[0])
        result['amount'].append(np.sum(price[1]['amount']))
        result['bid'].append(price[1]['bid'].tolist()[0])
        result['ask'].append(price[1]['ask'].tolist()[0])
    ob = pd.DataFrame(result)
    ob = ob.sort_values(by='price', ascending=False)
    ob['amount'] = ob['amount'].apply(lambda amnt: float(amnt))
    ob['amount'] = np.round(ob['amount'], 5)
    ob['price'] = ob['price'].apply(lambda price: int(price))
    ob['value'] = ob['price'] * ob['amount']
    curr1 = pair.split('-')[0].strip('/')
    curr2 = pair.split('-')[1]
    ob.to_excel(curr1+'_'+curr2+'_ob.xlsx')
    return ob

def animate(i):
    ob = gen_ob(pair, level=level_3)
    ob_range(ob=ob, bound=200, metric='amount')

def round_num(num, round_to_val):
    while num % round_to_val != 0:
        num -= 1
    return num

base_url = 'https://api.pro.coinbase.com'

products = '/products'

book = '/book?level='

# Only shows best bid and ask
level_1 = '1'
# Only shows top 50 bids and asks
level_2 = '2'
# Shows all bids and asks
level_3 = '3'

curr1 = 'ETH'
curr2 = 'USD'

pair = '/' + curr1 + '-' + curr2

if __name__ == '__main__':
    fig = plt.figure(figsize=(10,300))
    ax1 = fig.add_subplot(1,1,1)
    ani = animation.FuncAnimation(fig, animate, blit=False, interval=10000)
    plt.show()