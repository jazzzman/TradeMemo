import argparse



TICK_SIZE = 0.01
STOP_LOSS = 50


ap = argparse.ArgumentParser(
        prog = "pose_calculator", 
        description="Program processes position volume according to"
                    "input tick_count, tick_size, and risk managment stop loss.")

ap.add_argument("tick_count",help="Tick count to calculate",type=float)
ap.add_argument("-l","--limit",help=f"Limit size to lose in USD. (Default: ${STOP_LOSS})", default=STOP_LOSS, type=float)
ap.add_argument("-ts","--tick_size",help=f"Tick size in USD. (Default: ${TICK_SIZE})", default=TICK_SIZE,type=float)


args = ap.parse_args()

tc,sl,ts = args.tick_count,args.limit,args.tick_size

print(f'Position volume: {sl/ts/tc:.0f}')
