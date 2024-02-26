import logging
from logging import handlers
from datetime import datetime
import os

LogFormatter = logging.Formatter('%(message)s')
today_ymd=datetime.today().strftime("%Y%m%d")

logFile="scalper"
#logPath="/home/hmpark/upbit_data/log"
logPath="/home/hmpark/upbit_sim/log"
LOGPATH=os.path.join(logPath, logFile)

LogHandler = handlers.TimedRotatingFileHandler(filename=LOGPATH, when='midnight', interval=1, encoding='utf-8')
LogHandler.setFormatter(LogFormatter)
LogHandler.suffix = "%Y%m%d"

Logger = logging.getLogger()
Logger.setLevel(logging.INFO)
Logger.addHandler(LogHandler)

def log(level, *args):
    now = datetime.now()
    real_time = now.strftime('%Y-%m-%d %H:%M:%S')

    if level not in ("TR", "DG", "INFO"):
        logs = f"TR|{real_time}|Log Level Error|"
        Logger.info(logs)
        return 0

    logs = f"{level}|{real_time}"

    try:
        for i in args:
            i = str(i)
            logs += f"| {i}"
    except Exception as e:
        logs += f"ER({e})"

    if level != "TR":
        Logger.info(logs)
    return 1
    
def log_function_call(func):
    def wrapper(*args, **kwargs):
        params = ", ".join([f"{arg}" for arg in args])
        log("TR",f"{func.__name__}({params})")
        return func(*args, **kwargs)
    return wrapper

if __name__ == '__main__':
    print("logger.py")
