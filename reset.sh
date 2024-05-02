suffix=$(ls -lt | grep "TEMP_" | head -n 1 | cut -f2 -d"_")
rm -r /home/ubuntu/TEMP_$suffix
rm BigBuckBunny.mp4
rm BigBuckBunny_4s.mpd
rm -r ASTREAM_LOGS
