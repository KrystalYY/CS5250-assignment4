'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    last_switch_time = 0  # switch process
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

# Input: process_list, time_quantum (Positive Integer)
# Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
# Output_2 : Average Waiting Time
# Assumption: the curernt running process always to the the end of queue if others come at the same time
def RR_scheduling(process_list, time_quantum):
    def _next_important_time():
        if queue:
            # current one completes
            current_remaing_time = queue[0]["remaining_time"]
            # quantum expires
            quantum_expiring_time = Process.last_switch_time + time_quantum - current_time
            if current_remaing_time <= quantum_expiring_time:
                return current_time + current_remaing_time
            else:
                return current_time + quantum_expiring_time
        else:
            return process_list[next_process_idx].arrive_time if next_process_idx < len(process_list) else -1


    schedules = []
    queue = []
    completed = []
    current_time = 0

    # assumes there will always be a process at t=0
    p1 = process_list[0]
    queue.append({"process": p1, "remaining_time": p1.burst_time, "waiting_time": 0})

    schedules.append((0, p1.id))
    current_time = _next_important_time()
    next_process_idx = 1
    while queue or next_process_idx < len(process_list):
        used_time = current_time - Process.last_switch_time
        running_process = {}
        if queue:  # queue may be empty when the early processes have been completed
            # update remaining time for first
            running_process = queue[0]
            running_process["remaining_time"] -= used_time
            # update wait time for rest
            if len(queue) > 1:
                for p in queue[1:]:
                    p["waiting_time"] += used_time
        # check if incoming process during the past period, maybe multiple
        checking = True
        while checking:
            if next_process_idx >= len(process_list):
                checking = False
            else:
                next_process = process_list[next_process_idx]
                if Process.last_switch_time < next_process.arrive_time <= current_time:
                    queue.append({"process": next_process, "remaining_time": next_process.burst_time, "waiting_time": current_time-next_process.arrive_time})
                    next_process_idx += 1
                else:
                    checking = False
        # reorder queue
        if running_process:
            if running_process["remaining_time"] > 0:  # the running one has not completed yet
                if len(queue) > 1:
                    queue = queue[1:]
                    queue.append(running_process)
                else:
                    pass  # only one process remaining
            else:  # completed
                queue = queue[1:] if len(queue) > 1 else []
                completed.append(running_process)
        # update schedules
        if queue:
            schedules.append((current_time, queue[0]["process"].id))
        # update last_scheduled_time
        Process.last_switch_time = current_time

        # import pdb;pdb.set_trace()
        # print(current_time)
        # for p in queue:
        #     print(p)
        # print(f'schedules: {schedules}')
        # print(f'completed: {completed}')

        # update current_time
        current_time = _next_important_time()
        if current_time < 0:
            break

    total_waiting_time = sum([p["waiting_time"] for p in completed])
    return (schedules, total_waiting_time / float(len(completed)))


def SRTF_scheduling(process_list):
    return (["to be completed, scheduling process_list on SRTF, using process.burst_time to calculate the remaining time of the current process "], 0.0)

def SJF_scheduling(process_list, alpha):
    return (["to be completed, scheduling SJF without using information from process.burst_time"],0.0)


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

