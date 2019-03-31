from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))
sys.path.insert(0, os.path.join(BASE_DIR))


from common import flask_app

# 声明定时任务执行时使用的执行器
executors = {
    'default': ProcessPoolExecutor(5)
}

# 创建定时任务调度器对象
scheduler = BlockingScheduler(executors=executors)

# 添加任务
from statistic import fix_statistics
# 定时修正统计数据的任务，想要按照每天凌晨3点执行，选用cron方式触发
scheduler.add_job(fix_statistics, 'cron', hour=3)
# scheduler.add_job(fix_statistics)


# 启动定时任务调度器
# blocking的特点，start方法会阻塞程度，不让程序退出，同时去调度添加的定时任务并执行
scheduler.start()
