from tensorboardX import SummaryWriter
from concurrent.futures import ThreadPoolExecutor

class Logger(object):
    def __init__(self, run_dir, **kwargs):
        self.writer = SummaryWriter(run_dir, **kwargs)
        self.async_executor = ThreadPoolExecutor(max_workers=4)
        self.futures = dict()

    def add_scalar(self, name, scalar, global_step):
        self.writer.add_scalar(name, scalar, global_step)

    def add_audio(self, name, audio, global_step, sr=22050):
        self.writer.add_audio(name, audio, global_step, sample_rate=sr)

    def add_image(self, name, image, global_step):
        self.writer.add_image(name, image, global_step)

    def add_async(self, fn, cb, *args, **kwargs):
        future = self.async_executor.submit(fn, *args, **kwargs)
        self.futures[future] = cb

    def process_async(self):
        done = list(filter(lambda future: future.done(), self.futures))

        for future in done:
            cb = self.futures[future]
            try:
                res = future.result()
            except TimeoutError:
                print('TimeoutError, no need to be too upset')
            else:
                del self.futures[future]
                cb(res)

    def close(self):
        self.async_executor.shutdown(wait=True)
        self.process_async()
        self.writer.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

