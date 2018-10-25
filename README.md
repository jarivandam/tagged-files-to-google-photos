# tagged-files-to-google-photos
Upload files to different google photo albums based on part of filename between first - and second -. For example Test-T1-23.jpg will be uploaded to the album T1. 
The results will be stored in csv with the tag and shareable url.


#Usage
1. Install required packages from requirments.txt
`pip install -t requirements.txt`
2. Create a OAuth token at [https://console.cloud.google.com/apis/credentials ][https://console.cloud.google.com/apis/credentials]
3. Add Client ID and Client secret to client_secret.json
4. Run python main.py /home/jari/Inputfolder filedescription output.csv



