import datetime


class Logger:

    @staticmethod
    def log(message: str):

        dt = datetime.datetime.now()
        print(dt)
        with open('./log.txt', 'a') as log_file:
            log_file.write(str(dt) + '\n')
            log_file.write(message + '\n')
            log_file.write('\n')
