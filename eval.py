import os
import sys
from enum import Enum
import csv
import pprint

##################################
''' Enums for CSV files '''
class CSVFields(Enum):
    EpochTime = 0
    CurrentPlaybackTime = 1
    CurrentBufferSize = 2
    CurrentPlaybackState = 3
    Action = 4
    Bitrate = 5
    
##################################

class Metrics:
    def __init__(self, interruptions=0, avg_bitrate=0, throughput=0):
        self.interruptions = interruptions
        self.avg_bitrate = avg_bitrate
        self.throughput = throughput

# The video is needed to determine the Throughput of a given run
VIDEO_NAME = "BigBuckBunny.mp4"
LOG_NAME = "DASH_BUFFER_LOG.csv"
NUM_RUNS = 16

run_dirs = os.listdir()

run_dirs = [n for n in run_dirs if os.path.isdir(n) and 'run' in n]
run_dirs.sort()

# Metrics dictionary contains all Metrics objects
# That will contain the metrics obtained for each run

metrics = {}

def display():
    with open('evaluation.txt', 'w') as f:
        for i in range(NUM_RUNS):
            metrics_to_print = metrics['run'+str(i+1)]
            interruptions = metrics_to_print.interruptions
            avg_bitrate = metrics_to_print.avg_bitrate
            throughput = metrics_to_print.throughput
            print('=========================')
            print(f'Evaluation for run{i+1}')
            pprint.pprint(f'Interruptions: {interruptions}')
            pprint.pprint(f'Average Bitrate: {avg_bitrate}')
            pprint.pprint(f'Throughput: {throughput}')
            print('=========================')
            f.write('=========================\n')
            f.write(f'Evaluation for run{i+1}\n')
            f.write(f'Interruptions: {interruptions}\n')
            f.write(f'Average Bitrate: {avg_bitrate}\n')
            f.write(f'Throughput: {throughput}\n')
            f.write('=========================\n\n')

def get_metrics(size_produced, run):
# This function will return a tuple of metrics (interruptions, avg_bitrate, throughput) for each run
    total_bitrate = 0
    end_time = 0
    num_rows = 0
    interruptions = 0
    
    buffering_flag = False
    
    i = 0 # Row iterator to ensure that maximum 3 rows are skipped over (First 3 rows are header/initial rows)
    
    with open(run + '/' + LOG_NAME, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            playbackState = row[CSVFields.CurrentPlaybackState.value]
            if (playbackState == 'CurrentPlaybackState' or playbackState == 'INITIAL_BUFFERING') and i <= 2:
                # This skips the iterations where the row consists of the
                # headers of the data or the initial buffering to remove
                # skews in the analysis
                i = i + 1
                continue
            if playbackState == 'BUFFERING' and not buffering_flag:
                # This indicates the detection of a new interval of buffering
                interruptions = interruptions + 1
                buffering_flag = True
            if playbackState != 'BUFFERING' and buffering_flag:
                buffering_flag = False
            num_rows += 1
            bitrate = float(row[CSVFields.Bitrate.value])
            total_bitrate = total_bitrate + bitrate
            # Ensure that the end time will be stored at the end of the loop
            end_time = float(row[CSVFields.EpochTime.value])
        csv_file.close
    avg_bitrate = (total_bitrate / num_rows) / 1000 # Average bitrate in Kbps
    throughput = size_produced / end_time # Throughput in Kbps
    return (interruptions, avg_bitrate, throughput)

# Go through each run and analyze metrics
for run in run_dirs:
    # This is the size of the "BigBuckBunny" video produced
    # This will be used to measure throughput for the entire run
    # The size is retrieved in bytes and divided by 1000 to get Kilobytes
    size_produced = os.path.getsize(run + '/' + VIDEO_NAME) / 1000
    '''
    get_metrics() returns a tuple in the following format:
    (interruptions, average bitrate, throughput)
    '''
    metrics_collected = get_metrics(size_produced, run)
    metrics[run] = Metrics(metrics_collected[0], metrics_collected[1], metrics_collected[2])

display()