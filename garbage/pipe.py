
from multiprocessing import Process, Pipe
import time

def reader_proc(p_input):
    ## Read from the pipe; this will be spawned as a separate Process
    print('Reader')
    while True:
        if p_input.poll():
            msg = p_input.recv()
        # Read from the output pipe and do nothing
            print('received',msg)
            if msg=='DONE':
                p_input.send('OK')
             #   time.sleep(4)
                p_input.close()
                break

def writer_proc(p_input):
    count = 20
    for ii in range(0, count):
        print(ii)
        p_input.send(ii)             # Write 'count' numbers into the input pipe
    p_input.send('DONE')
    while True:
        if p_input.poll():
            msg = p_input.recv()
            print(msg)
            if msg=='OK':
                p_input.close()
                break


if __name__=='__main__':

        # Pipes are unidirectional with two endpoints:  p_input ------> p_output
        p_output, p_input = Pipe()  # writer() writes to p_input from _this_ process
        reader_p = Process(target=reader_proc, args=(p_input,))
        reader_p.daemon = True
        reader_p.start()     # Launch the reader process

        writer_p = Process(target=writer_proc, args=(p_output,))
        writer_p.start()

       # p_input.close()
        reader_p.join()
        writer_p.join()
