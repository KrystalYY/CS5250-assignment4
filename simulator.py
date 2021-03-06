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

def _update_remaining_waiting_time(queue, time_elapsed):
    """
    update remaining time and waiting time for all processes in the queue
    """
    current_process = {}
    if queue:
        # update remaining time for first process
        current_process = queue[0]
        current_process["remaining_time"] -= time_elapsed
        # update wait time for rest
        if len(queue) > 1:
            for p in queue[1:]:
                p["waiting_time"] += time_elapsed
    return current_process, queue

def _add_process_to_queue(process_list, next_process_idx, queue, current_time):
    """
    find processes that arrive in the passed time period and add to queue
    """
    checking = True
    while checking:
        if next_process_idx >= len(process_list):
            checking = False
        else:
            next_process = process_list[next_process_idx]
            if Process.last_switch_time < next_process.arrive_time <= current_time:
                queue.append({
                    "process": next_process, 
                    "remaining_time": next_process.burst_time, 
                    "waiting_time": current_time-next_process.arrive_time
                })
                next_process_idx += 1
            else:
                checking = False
    return next_process_idx, queue

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
            return current_time + min(current_remaing_time, quantum_expiring_time)
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
    next_process_idx = 1
    
    while queue or next_process_idx < len(process_list):
        current_time = _next_important_time()
        if current_time < 0:
            break
        current_process, queue = _update_remaining_waiting_time(queue, current_time - Process.last_switch_time)
        next_process_idx, queue = _add_process_to_queue(process_list, next_process_idx, queue, current_time)
        # reorder queue
        if current_process:
            queue = queue[1:]
            if current_process["remaining_time"] > 0:  # the running one has not completed yet
                queue.append(current_process)
            else:  # completed
                completed.append(current_process)
        # update schedules
        if queue:
            schedules.append((current_time, queue[0]["process"].id))
        # update last_scheduled_time
        Process.last_switch_time = current_time
        
    Process.last_switch_time = 0
    total_waiting_time = sum([p["waiting_time"] for p in completed])
    return (schedules, total_waiting_time / float(len(completed)))


def SRTF_scheduling(process_list):
    def _next_important_time():
        if queue:
            current_remaing_time = queue[0]["remaining_time"]  # current one completes
            if next_process_idx < len(process_list):
                return min(current_time + current_remaing_time, process_list[next_process_idx].arrive_time)
            else:
                return current_time + current_remaing_time
        else:
            return process_list[next_process_idx].arrive_time if next_process_idx < len(process_list) else -1

    schedules = []
    queue = []  # always sort by remaining_time, shortest comes first
    completed = []
    current_time = 0

    # assumes there will always be a process at t=0
    p1 = process_list[0]
    queue.append({"process": p1, "remaining_time": p1.burst_time, "waiting_time": 0})

    schedules.append((0, p1.id))
    next_process_idx = 1

    while queue or next_process_idx < len(process_list):
        current_time = _next_important_time()
        if current_time < 0:
            break
        current_process, queue = _update_remaining_waiting_time(queue, current_time - Process.last_switch_time)
        next_process_idx, queue = _add_process_to_queue(process_list, next_process_idx, queue, current_time)
        # reorder queue
        if current_process and current_process["remaining_time"] <= 0:  # completed
            queue = queue[1:]
            completed.append(current_process)
        queue = sorted(queue, key=lambda p: p["remaining_time"])
        # update schedules if process switches
        if (not current_process) or (queue and current_process["process"].id != queue[0]["process"].id):
            schedules.append((current_time, queue[0]["process"].id))
        # update last_scheduled_time
        Process.last_switch_time = current_time

    Process.last_switch_time = 0
    total_waiting_time = sum([p["waiting_time"] for p in completed])
    return (schedules, total_waiting_time / float(len(completed)))

def SJF_scheduling(process_list, alpha):
    INITIAL_GUESS = 5
    def _next_important_time():
        if queue:
            return current_time + queue[0]["process"].burst_time
        else:
            return process_list[next_process_idx].arrive_time if next_process_idx < len(process_list) else -1
    
    schedules = []
    queue = []  # always sort by priority_num, shortest comes first
    completed = []
    current_time = 0
    predicted_next_burst = {}

    # assumes there will always be a process at t=0
    p1 = process_list[0]
    queue.append({
        "process": p1, 
        "remaining_time": p1.burst_time,
        "waiting_time": 0,
        "priority_num": INITIAL_GUESS
    })

    schedules.append((0, p1.id))
    next_process_idx = 1

    while queue or next_process_idx < len(process_list):
        current_time = _next_important_time()
        if current_time < 0:
            break
        current_process, queue = _update_remaining_waiting_time(queue, current_time - Process.last_switch_time)
        # insert processes that have arrived during the past time period
        checking = True
        while checking:
            if next_process_idx >= len(process_list):
                checking = False
            else:
                next_process = process_list[next_process_idx]
                if Process.last_switch_time < next_process.arrive_time <= current_time:
                    queue.append({
                        "process": next_process,
                        "remaining_time": next_process.burst_time,
                        "waiting_time": current_time - next_process.arrive_time,
                        "priority_num": predicted_next_burst.get(next_process.id, INITIAL_GUESS)
                    })
                    next_process_idx += 1
                else:
                    checking = False
        # reorder queue
        if current_process and current_process["remaining_time"] <= 0:  # completed
            queue = queue[1:]
            completed.append(current_process)
            # update priority num
            new_priority_num = alpha * current_process["process"].burst_time + (1 - alpha) * predicted_next_burst.get(current_process["process"].id, INITIAL_GUESS)
            predicted_next_burst[current_process["process"].id] = new_priority_num
        queue = sorted(queue, key=lambda p: p["priority_num"])
        # update schedules
        if queue:
            schedules.append((current_time, queue[0]["process"].id))
        # update last_scheduled_time
        Process.last_switch_time = current_time

    Process.last_switch_time = 0
    total_waiting_time = sum([p["waiting_time"] for p in completed])
    return (schedules, total_waiting_time / float(len(completed)))


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
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list, time_quantum=2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha=0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )
    for quantum in range(1, 51):
        _, RR_avg_waiting_time =  RR_scheduling(process_list, quantum)
        print(f'quantum: {quantum}, waiting_time: {RR_avg_waiting_time}')
    for alpha in range(0, 100, 1):
        alpha = alpha / 100.0
        _, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha)
        print(f'alpha: {alpha}, waiting_time: {SJF_avg_waiting_time}')

if __name__ == '__main__':
    main(sys.argv[1:])

