# Main Project Code
The code in this repository are modifications/additions to code in this repository [https://github.com/teaching-on-testbeds/AStream](https://github.com/teaching-on-testbeds/AStream) (config_dash.py and dash_client.py) 
for adaptive video streaming and it also contains the code for a new adaptive video streaming policy (randomized_dash.py).

Files that are NOT mine that I have made modifications to (see [https://github.com/teaching-on-testbeds/AStream/dist/client](https://github.com/teaching-on-testbeds/AStream/tree/master/dist/client)):
- config_dash.py
- dash_client.py

For these files mentioned above, credit goes to Parikshit Juluri and the other contributors in the above mentioned repository.

My adaptive video streaming policy:
- randomized_dash.py

The adaptive video streaming policy above uses inspirations from the three main policies in the github repository mentioned above (basic -> basic_dash2.py, netflix -> netflix_dash.py, and SARA -> weighted_dash.py) for the factors in selecting the bitrate for the stream (doiwnload rate, buffer occupancy, download times of the next segments). After a pair of bitrates are selected (one higher and one lower), one of the two bitrates are selected via a defined probability (gamma or alpha). The probabiltieis are then updated.

# Notebook
The notebook used in this project is from the reserve_resources_fabric.ipynb notebook in https://github.com/teaching-on-testbeds/AStream with slight modifications to the code in the notebook. This includes utility code such as uploading and downloading files to/from the nodes in the network topology

## Experiment Set-Up
Once the slice is created from the notebook and the SSH commands for each node are obtained, you must run the same set-up as in the AStream repository to set up each node for experimentation.

### Client ("justin")
SSH into the client node and run the following commands on the client node:
```
git clone https://github.com/teaching-on-testbeds/AStream
sudo apt update
sudo apt install -y python3 ffmpeg
```

You must upload the config_dash.py, dash_client.py, and randomized_dash.py files to the client using the notebook in this repository in order to test the Randomized Adaptation policy.

Additionally, use the notebook from this repository to upload the reset.sh and extract_results.sh scripts to the client node. The reset.sh script is for clearing all of the video files and logs from a previously run experiment to set up for a new experiment and the extract_results.sh script is used for extracting the BigBuckBunny.mp4 file after running an experiment.

### Router
SSH into the router and run the following commands on the router node:
```
git clone https://github.com/NYU-METS/Main nyc-traces
sudo apt update
sudo apt install -y unrar-free
unrar nyc-traces/Dataset/Dataset_1.rar
wget https://raw.githubusercontent.com/teaching-on-testbeds/adaptive-video/main/rate-vary.sh -O ~/rate-vary.sh
wget https://raw.githubusercontent.com/teaching-on-testbeds/adaptive-video/main/rate-set.sh -O ~/rate-set.sh
```

### Server ("vid_db")
SSH into the server and run the following commands on the server node:
```
sudo apt update  
sudo apt install -y apache2
wget https://nyu.box.com/shared/static/d6btpwf5lqmkqh53b52ynhmfthh2qtby.tgz -O media.tgz
sudo tar -v -xzf media.tgz -C /var/www/html/
```

Once the setup is completed, only the router and client terminals are needed for experimentation.

On the router you can run either:
`bash rate-set.sh 1000Kbit`
or
`bash rate-vary.sh <path_to_trace_file> <scale_factor>` where path_to_trace_file is the path to one of the CSV trace files and scaling factor is greater than 0 and less than 1.

On the client you can run:
`python3 ~/AStream/dist/client/dash_client.py -m http://vid_db/media/BigBuckBunny/4sec/BigBuckBunny_4s.mpd -p '<policy_name>' -d`
where policy_name can be the following:
basic      --> rate-based
netflix    --> buffer-based policy
sara       --> Segment-Aware Rate Adaptation
randomized --> Randomized Adaptation

You can run the client for as long as you'd like or until completion and then you can use the extract_results.sh script to get the resulting BigBuckBunny.mp4

## Evaluation
After an experiment, download the resulting log file from the client node using the notebook into the appropriate folder. The folders are in results/ and there is a folder to each specific policy with a few outlined experiments and their collected log files.

Run the eval.py script to obtain the metric for each log file for each experiment (average bitrate and the number of interruptions) and the output of the graphs for experiment. (Each graph should be one experiment with the four policies)
