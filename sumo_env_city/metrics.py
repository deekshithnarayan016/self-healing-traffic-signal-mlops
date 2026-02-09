import traci
import sumolib

# Get SUMO binary
SUMO_BINARY = sumolib.checkBinary("sumo")

# Start SUMO
traci.start([
    SUMO_BINARY,
    "-c", "city.sumocfg",
    "--start",
    "--quit-on-end"
])

MAX_STEPS = 3600
step = 0

# System-level metrics
step_waiting_times = []
step_queue_lengths = []

# Vehicle-level tracking (final cumulative waiting time)
vehicle_waiting_times = {}

throughput = 0

while step < MAX_STEPS:
    traci.simulationStep()

    # ----- System waiting time (per step) -----
    waiting_time_this_step = 0
    vehicle_ids = traci.vehicle.getIDList()

    for vid in vehicle_ids:
        wt = traci.vehicle.getWaitingTime(vid)
        waiting_time_this_step += wt

        # Track maximum (final) waiting time per vehicle
        if vid not in vehicle_waiting_times:
            vehicle_waiting_times[vid] = wt
        else:
            vehicle_waiting_times[vid] = max(vehicle_waiting_times[vid], wt)

    step_waiting_times.append(waiting_time_this_step)

    # ----- Queue length (per step) -----
    queue_length_this_step = 0
    for lane_id in traci.lane.getIDList():
        queue_length_this_step += traci.lane.getLastStepHaltingNumber(lane_id)

    step_queue_lengths.append(queue_length_this_step)

    # ----- Throughput -----
    throughput += traci.simulation.getArrivedNumber()

    step += 1

traci.close()

# ----- Final metrics -----
avg_system_waiting_time = sum(step_waiting_times) / len(step_waiting_times)
avg_queue_length = sum(step_queue_lengths) / len(step_queue_lengths)

avg_waiting_time_per_vehicle = (
    sum(vehicle_waiting_times.values()) / len(vehicle_waiting_times)
    if vehicle_waiting_times else 0
)

print("Simulation Finished")
print("System Waiting Time per step:", avg_system_waiting_time)
print("Average Queue Length per step:", avg_queue_length)
print("Total Throughput:", throughput)
print("Average Waiting Time per vehicle:", avg_waiting_time_per_vehicle)

with open("baseline_metrics.txt", "w") as f:
    f.write("Baseline Metrics (City Network)\n")
    f.write(f"System Waiting Time per step: {avg_system_waiting_time}\n")
    f.write(f"Average Queue Length per step: {avg_queue_length}\n")
    f.write(f"Total Throughput: {throughput}\n")
    f.write(f"Average Waiting Time per vehicle: {avg_waiting_time_per_vehicle}\n")
