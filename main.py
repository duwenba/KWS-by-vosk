from pathlib import Path
from kws.service import KeywordService


def example_action():
    print('检测到关键词，执行动作！')


def main():
    # 创建关键词检测服务，会自动下载和管理模型
    service = KeywordService()
    
    # 注册关键词动作
    service.register_action('你好', example_action)
    service.register_action('结束识别', service.stop)

    
    print('关键词检测服务已启动，说"你好小艺"试试看！')
    print('按Ctrl+C退出程序')
    
    # 运行服务
    service.run_forever()

if __name__ == '__main__':
    main()