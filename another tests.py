from time import sleep, perf_counter
from threading import Thread


def task(id):
    print(f'Начинаем выполнение задачи {id}...')
    sleep(1)
    print(f'Задача {id} выполнена')


start_time = perf_counter()
# создаем и запускаем 10 потоков
threads = []
for n in range(1, 11):
    t = Thread(target=task, args=(n,))
    threads.append(t)
    t.start()

# ждем, когда потоки выполнятся
for t in threads:
    t.join()

end_time = perf_counter()

print(f'Выполнение заняло {end_time- start_time: 0.2f} секунд.')