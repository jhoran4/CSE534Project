The code in this repository are modifications/additions to code in this repository [https://github.com/teaching-on-testbeds/AStream](https://github.com/teaching-on-testbeds/AStream) (config_dash.py and dash_client.py) 
for adaptive video streaming and it also contains the code for a new adaptive video streaming policy (randomized_dash.py).

Files that are NOT mine that I have made modifications to (see [https://github.com/teaching-on-testbeds/AStream/dist/client](https://github.com/teaching-on-testbeds/AStream/tree/master/dist/client)):
- config_dash.py
- dash_client.py

For these files mentiuoned above, credit goes to Parikshit Juluri and the other contributors in the above mentioned repository.

My adaptive video streaming policy:
- randomized_dash.py

The adaptive video streaming policy above uses inspirations from the three main policies in the github repository mentioned above (basic -> basic_dash2.py, netflix -> netflix_dash.py, and SARA -> weighted_dash.py) for the factors in selecting the bitrate for the stream (doiwnload rate, buffer occupancy, download times of the next segments). After a pair of bitrates are selected (one higher and one lower), one of the two bitrates are selected via a defined probability (gamma or alpha). The probabiltieis are then updated.
