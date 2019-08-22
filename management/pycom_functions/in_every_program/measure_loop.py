def measure_loop(i2c):
    exp_count = 0
    exp_count_max = 3 #maximum subsequent errors
    zero_exp_counter = 60 #10 mintues
    while True:
        try:
            m = Measure(i2c)
            count = 0
            while True:
                count += 1
                if count == zero_exp_counter:
                    exp_count = 0 #prevent rebooting without subsequent exceptions
                    count = 0
                utime.sleep(10) #wait until exception
        except Exception as e:
            exp_count += 1
            if exp_count == exp_count_max:
                machine.reset() #if exp_count_max exceptions reset board
            print(e)
            gc.collect()
            utime.sleep(10)
