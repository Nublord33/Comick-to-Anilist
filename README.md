
# install python and deps


windows) https://www.youtube.com/watch?v=-kqfNvedYp0
mac OS) https://www.youtube.com/watch?v=nhv82tvFfkM

0.5) after you installed python run this command in yout shell/command prompt

```shell
pip install pandas
```
then run
```shell
pip install requests
```

# step 0.75

download anilist.py

# step 1

export your list to csv by going to comick.io click on "My List" click export click on Request to export your list and rename the file "out.csv"

# step 2

go to https://anilist.co/api/v2/oauth/authorize?client_id=25365&response_type=token wait a bit and go to the search bar and copy the text starting from access_token='

# setp 3

go into anilist.py look for the line of code access_token = 'your-access-token-here' and past your acess token that you copied into the qoutes

# step 4

run the anilist.py file by doing

```python
python anilist.py
```







