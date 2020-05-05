# from django.shortcuts import render
# from apscheduler.schedulers.background import BackgroundScheduler
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# from . exec_sign_task import start_run
#
#
# # 实例化调度器
# scheduler = BackgroundScheduler()
# # 调度器使用默认的DjangoJobStore()
# scheduler.add_jobstore(DjangoJobStore(), 'default')
# # 每天8点半执行这个任务
# @register_job(scheduler, 'interval', id='test', seconds=10, args=['test'])
# def test():
#     # 具体要执行的代码
#     print("执行打卡")
#     start_run()
#
# # 注册定时任务并开始
# register_events(scheduler)
# scheduler.start()
#

