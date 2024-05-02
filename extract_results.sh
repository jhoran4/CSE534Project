cp $(ls -t1  /home/ubuntu/ASTREAM_LOGS/DASH_BUFFER_LOG_*  | head -n 1 ) /home/ubuntu/ASTREAM_LOGS/DASH_BUFFER_LOG-last.csv
suffix=$(ls -lt | grep "TEMP_" | head -n 1 | cut -f2 -d"_")
cd /home/ubuntu/TEMP_$suffix
rm -f /home/ubuntu/BigBuckBunny.mp4 # if it exists
cat BigBuckBunny_4s_init.mp4 $(ls -vx BigBuckBunny_*.m4s) > BigBuckBunny_tmp.mp4
ffmpeg -i  BigBuckBunny_tmp.mp4 -c copy /home/ubuntu/BigBuckBunny.mp4
cd ~
