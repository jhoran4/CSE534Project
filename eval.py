import os
import sys
from enum import Enum
import csv
import pprint

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

c = {'INITIAL_BUFFERING': 'violet', 'PLAY': 'lightcyan', 'BUFFERING': 'lightpink'}

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
    def __init__(self, interruptions=0, avg_bitrate=0):
        self.interruptions = interruptions
        self.avg_bitrate = avg_bitrate

# The video is needed to determine the Throughput of a given run
VIDEO_NAME = "BigBuckBunny.mp4"
LOG_NAME = "DASH_BUFFER_LOG.csv"
NUM_RUNS = 16

RESULTS = "results/"
POLICIES = ["rb/", "bb/", "sara/", "ra/"]
EXPERIMENTS = ["cbr/", "interruptions/", "trace/bus_m15/", "trace/bus_b62_2/", "trace/NYU_Campus_Bus/"]

run_dirs = []
for experiment in EXPERIMENTS:
    for policy in POLICIES:
        run_dirs.append(RESULTS + policy + experiment)

# Metrics dictionary contains all Metrics objects
# That will contain the metrics obtained for each run

metrics = {}

def display():
    with open('evaluation.txt', 'w') as f:
        for run in run_dirs:
            metrics_to_print = metrics[run]
            interruptions = metrics_to_print.interruptions
            avg_bitrate = metrics_to_print.avg_bitrate
            print('=========================')
            print(f'Evaluation for {run}')
            pprint.pprint(f'Interruptions: {interruptions}')
            pprint.pprint(f'Average Bitrate: {avg_bitrate}')
            print('=========================')
            f.write('=========================\n')
            f.write(f'Evaluation for {run}\n')
            f.write(f'Interruptions: {interruptions}\n')
            f.write(f'Average Bitrate: {avg_bitrate}\n')
            f.write('=========================\n\n')

def get_metrics(run):
# This function will return a tuple of metrics (interruptions, avg_bitrate, throughput) for each run
    total_bitrate = 0
    end_time = 0
    num_rows = 0
    interruptions = 0
    
    buffering_flag = False
    
    i = 0 # Row iterator to ensure that maximum 3 rows are skipped over (First 3 rows are header/initial rows)
    
    with open(run + LOG_NAME, 'r') as csv_file:
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
    return (interruptions, avg_bitrate)

# Go through each run and analyze metrics
i = 0
for run in run_dirs:
    print(run)
    # This is the size of the "BigBuckBunny" video produced
    # This will be used to measure throughput for the entire run
    # The size is retrieved in bytes and divided by 1000 to get Kilobytes
    # size_produced = os.path.getsize(run + '/' + VIDEO_NAME) / 1000
    '''
    get_metrics() returns a tuple in the following format:
    (interruptions, average bitrate, throughput)
    '''
    metrics_collected = get_metrics(run)
    metrics[run] = Metrics(metrics_collected[0], metrics_collected[1])
    
    dash = pd.read_csv(run + LOG_NAME)
    dash = dash.loc[dash.CurrentPlaybackState.isin(c.keys() )]
    states = pd.DataFrame({'startState': dash.CurrentPlaybackState[0:-2].values, 'startTime': dash.EpochTime[0:-2].values,
    'endState':  dash.CurrentPlaybackState[1:-1].values, 'endTime':   dash.EpochTime[1:-1].values})
    
    color = 'kx:'
    label = ''
    if i % 4 == 0:
        color = 'bx:'
        label = 'rb'
    elif i % 4 == 1:
        color = 'go:'
        label = 'bb'
    elif i % 4 == 2:
        color = 'y+:'
        label = 'sara'
    elif i % 4 == 3:
        color = 'rd:'
        label = 'ra'
        
    i += 1
    
    plt.subplot(211)

    for index, s in states.iterrows():
        plt.axhspan(0, 2000000, color=c[s['startState']], alpha=1)
        plt.axvspan(s['startTime'], s['endTime'], color=c[s['startState']], alpha=1) 

    plt.plot(dash[dash.Action!="Writing"].EpochTime, dash[dash.Action!="Writing"].Bitrate, color, label=label)
    plt.title("Video rate (bps)")
    plt.xlabel("Time (s)")
    plt.ylabel("Bitrate")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.subplot(212)

    for index, s in states.iterrows():
        plt.axhspan(0, 40, color=c[s['startState']], alpha=1)
        plt.axvspan(s['startTime'], s['endTime'],  color=c[s['startState']], alpha=1) 

    plt.plot(dash[dash.Action!="Writing"].EpochTime, dash[dash.Action!="Writing"].CurrentBufferSize, color, label=label)
    plt.title("Buffer(segments)")
    plt.xlabel("Time (s)")
    plt.ylabel("Segments")

    plt.tight_layout()
    if i % 4 == 0:
        save_str = run.replace('results/', '')
        save_str = save_str.split('/')
        print(save_str[len(save_str) - 2])
        plt.savefig('result_graphs/' + save_str[len(save_str) - 2])
        plt.clf()
    

display()