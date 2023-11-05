from multiprocessing import Pool
import time, os


def main():
    with Pool(processes=4) as pool:
        #items = range(10)
        # launching multiple evaluations asynchronously *may* use more processes
        try:
            for i in range(50):
                pool.apply_async(f, (i,))
                print("got it")
            print("got all")
        #multiple_results = [pool.apply_async(f, (item)) for item in items]
        #print([res.get(timeout=1) for res in multiple_results])

        except Exception as e:
            print(e)
    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")

async def f(num):
    print("my num is",num)
    time.sleep(1)

if __name__ == '__main__':
    main()
    