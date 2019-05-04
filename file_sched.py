import time
from dbmngr import DBManager
import os


def file_scheduler_mainloop(path: str, upload_path, delay=300):
    """

    :param path: str database path
    :param delay: int polling delay
    :return:
    """
    print("Scheduling initialized")
    db = DBManager(path)
    while True:
        print('Scheduler awake...')
        db.connect()
        cur_time = time.time()
        data = db.get_all()
        for filename, exp_date in data:
            if cur_time > exp_date:
                db.remove_file(filename)
                os.remove(os.path.join(upload_path, filename))
                print(f"Scheduler removed file {filename}")
        db.disconnect()
        print(f"Scheduler asleep for {delay} secs")
        time.sleep(delay)


if __name__ == '__main__':
    file_scheduler_mainloop('file_data.db', './upload_folder', 10)