import json
import argparse


CONTRACT_INFO ='okx_contract_info.txt' 
STOP_LOSS = 100

def fee_per_trade(ticker, contract_info, price, change, sl):
    """Return contract count, approximate fee for position, tigertrade order volume, zero result price change"""
    FEE_TIER = 0.0005
    contract_weight = float(contract_info['Multiplier'])*float(contract_info['FaceValue'])
    vol = sl/change/float(contract_info['FaceValue'])
    fee = vol*price*FEE_TIER*contract_weight
    return vol, fee*2, vol*float(contract_info['FaceValue']), fee*2/vol/float(contract_info['FaceValue'])

ap = argparse.ArgumentParser(
        prog = "pose_calculator", 
        description="Program processes position volume according to"
                    "input tick_count, tick_size, and risk managment stop loss.")

ap.add_argument('ticker', help='Ticker. BTC, ADA, LTC', type=str)
ap.add_argument('price', help='Current price', type=float)
ap.add_argument("tick_count",help="Tick count to calculate",type=float)
ap.add_argument("-l","--limit",help=f"Stop loss size in USD. (Default: ${STOP_LOSS})", default=STOP_LOSS, type=float)


args = ap.parse_args()

ticker,price,ticks,sl = args.ticker,args.price,args.tick_count,args.limit


with open(CONTRACT_INFO,'r') as f:
    contract_info = json.loads(f.read())

vol, fee, ttvol, zero_ticks = fee_per_trade(ticker, contract_info[ticker],price,ticks,sl)

print(f'Order Volume: {vol:.2f}\n'
      f'TigerTrade vol: {ttvol:.2f}\n'
      f'Approximate fee: {fee:.2f}\n'
      f'Zero profit ticks: {zero_ticks}\n')
