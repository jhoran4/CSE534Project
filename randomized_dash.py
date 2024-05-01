__author__ = 'horan'

import config_dash
import random
import math

GAMMA = "GAMMA"
ALPHA = "ALPHA"

def get_expected_download_time(bitrate, download_rate, next_segments, prev_download_time):
    cur_download_time = 0
    
    for segment in next_segments:
        cur_download_time += float(segment[bitrate])/download_rate
    
    # Return the average of the download times
    if len(next_segments) == 0:
        return prev_download_time
    return cur_download_time/len(next_segments)

def randomized_dash(bitrates, dash_player, avg_down_rate, current_bitrate, prev_dwn_rate, next_segments, state, segment_download_time, gamma, alpha):
    '''
    The idea behind this algorithm is to utilize the same concepts as the previous three policies, but
    to have a random element in which there is a chance the "unsuitable" bitrate will be chosen. This
    is to offset variability in the network download rate so that there are cases where a more optimal
    bitrate is chosen for an upswing in the network download rate and a more optimal bitrate is chosen
    for a downswing in the network.
    
    To provide further security, there will be another defined constant LOOKAHEAD that will be used
    to determine how many future segments to take into account for choosing the next bitrate 
    '''
    # Initialize similar to SARA policy
    bitrates.sort()
    delay = 0
    next_bitrate = None
    next_bitrate_index = 0
    available_video_segments = dash_player.buffer.qsize() - dash_player.initial_buffer
    available_video_duration = available_video_segments * dash_player.segment_duration
    
    # Instead of starting at the minimum bitrate, start at a random bitrate
    # Adjust from that bitrate. This is to avoid slow starts in the event of
    # the download rate/buffer occupancy being high OR to avoid quick starts
    # in the event the download rate/buffer occupancy is low (Average case)
    print("VIDEO SEGMENTS: {0} AVAILABLE DURATION: {1}".format(available_video_segments, available_video_duration))
    if available_video_segments <= (1-gamma)*config_dash.RANDOMIZED_BUFFER_SIZE and state == "INITIAL":
        next_bitrate = random.choice(bitrates[0:(int((len(bitrates)-1)/4))])
        return next_bitrate, delay, "INITIAL", None, None, None, gamma, alpha
    elif state != "RUNNING":
        next_bitrate = bitrates[0]
        next_bitrate = random.choice(bitrates)
        next_bitrate_index = bitrates.index(next_bitrate)
        delay = dash_player.buffer.qsize()/4
        return next_bitrate, 0, "RUNNING", None, None, None, gamma, alpha
    else:
        state = "RUNNING"
    
    # Establish the average download rate in bits/sec
    download_rate = avg_down_rate * 8
    previous_download_rate = prev_dwn_rate * 8
    
    print("Previous Download Rate: {0}".format(previous_download_rate))
    print("Download Rate: {0}".format(download_rate))
    print("Current Bitrate: {0}".format(current_bitrate))
    
    param = (previous_download_rate - download_rate)/current_bitrate
    ret_gamma = 1/(1 + (math.exp(-1*param)))
    
    print("Gamma: {0}".format(ret_gamma))
    
    # If the previous download rate is greater than or equal to the average, lean toward a higher bitrate with a small chance to choose lower
    # else do the opposite
    use_gamma = gamma
    use_alpha = alpha
    if download_rate > previous_download_rate:
        use_gamma = alpha
        use_alpha = gamma
        
    # Obtain the expected download time for the next few segments
    expected_download_time = get_expected_download_time(current_bitrate, avg_down_rate, next_segments, segment_download_time)
    print("Expected Download Time: {0}".format(expected_download_time))
    
    # Obtain two distinct bitrates, a higher bitrate and a lower bitrate
    higher_bitrate = None
    lower_bitrate = None
    
    # Unlike the netflix policy, only about 30 percent of the buffer is required to be full
    # just to make sure the DASH client can always perform work
    
    if available_video_segments <= (1-use_gamma)*config_dash.RANDOMIZED_BUFFER_SIZE:
        # Select a lower bitrate
        if current_bitrate == bitrates[0]:
            lower_bitrate = current_bitrate
            higher_bitrate = bitrates[1]
        else:
            for i in range(bitrates.index(current_bitrate), -1, -1):
                # Use the previous download rate in this case because network may be decreasing in performance
                # So an average could lead to an inaccurate assessment of the network
                new_download_time = get_expected_download_time(bitrates[i], prev_dwn_rate, next_segments, segment_download_time)
                if new_download_time <= available_video_duration:
                    if i < (len(bitrates) - 1):
                        lower_bitrate = bitrates[i]
                        higher_bitrate = bitrates[i+1]
                    else:
                        lower_bitrate = bitrates[i - 1]
                        higher_bitrate = bitrates[i]
                    break
            if higher_bitrate is None or lower_bitrate is None:
                lower_bitrate = bitrates[0]
                higher_bitrate = bitrates[1]
                
    elif expected_download_time > available_video_duration:
        # Select a lower bitrate
        if current_bitrate == bitrates[0]:
            lower_bitrate = current_bitrate
            higher_bitrate = bitrates[1]
        else:
            reversed_bitrates = list(reversed(bitrates))
            for i in range(len(reversed_bitrates)):
                new_download_time = get_expected_download_time(reversed_bitrates[i], avg_down_rate, next_segments, segment_download_time)
                if new_download_time <= available_video_duration:
                    if i > (len(reversed_bitrates) - 2):
                        lower_bitrate = reversed_bitrates[i]
                        higher_bitrate = reversed_bitrates[i-1]
                    else:
                        lower_bitrate = reversed_bitrates[i+1]
                        higher_bitrate = reversed_bitrates[i]
                    break
            if higher_bitrate is None or lower_bitrate is None:
                lower_bitrate = reversed_bitrates[len(reversed_bitrates) - 1]
                higher_bitrate = reversed_bitrates[len(reversed_bitrates) - 2]
    else:
        # Select a higher bitrate
        if current_bitrate == bitrates[-1]:
            lower_bitrate = bitrates[-2]
            higher_bitrate = current_bitrate
        else:
            for i in range(bitrates.index(current_bitrate)+1, len(bitrates)):
                new_download_time = get_expected_download_time(bitrates[i], avg_down_rate, next_segments, segment_download_time)
                if new_download_time > available_video_duration:
                    break
                else:
                    if i < (len(bitrates) - 1):
                        lower_bitrate = bitrates[i]
                        higher_bitrate = bitrates[i+1]
                    else:
                        lower_bitrate = bitrates[i-1]
                        higher_bitrate = bitrates[i]
            if higher_bitrate is None or lower_bitrate is None:
                if bitrates.index(current_bitrate) == 0:
                    lower_bitrate = current_bitrate
                    higher_bitrate = bitrates[1]
                else:
                    lower_bitrate = bitrates[bitrates.index(current_bitrate) - 1]
                    higher_bitrate = current_bitrate
        delay = dash_player.buffer.qsize() - (1-gamma)*config_dash.RANDOMIZED_BUFFER_SIZE
    
    print("Buffer Queue Size: {0} Buffer Percentage Size: {1}".format(dash_player.buffer.qsize(), (1-gamma)*config_dash.RANDOMIZED_BUFFER_SIZE))
    
    if random.random() <= use_gamma:
        # Select the higher bitrate
        flag = False
        if use_gamma >= 0.5:
            flag = True
        next_bitrate = higher_bitrate
        return next_bitrate, 0, state, GAMMA, flag, get_expected_download_time(next_bitrate, avg_down_rate, next_segments, segment_download_time), ret_gamma, 1-ret_gamma
    else:
        # Select the lower bitrate
        flag = False
        if use_alpha >= 0.5:
            flag = True
        next_bitrate = lower_bitrate
        return next_bitrate, 0, state, ALPHA, flag, get_expected_download_time(next_bitrate, avg_down_rate, next_segments, segment_download_time), ret_gamma, 1-ret_gamma