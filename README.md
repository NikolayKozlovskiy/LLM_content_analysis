# dkv_auto_search
A repo to perform news' social risk analysis

## Deployment

1. `git clone <you know what>`
2. `cd <you know where>`
3. `docker compose up --build`
4. in new terminal run: `docker exec -it py_app_cont  /bin/bash`
5. within the container execute `python auto_internet_search/main.py configs/config.ini` , if you need jupyter lab - simply `jl`
6. don't forget to stop running the containers once you don't need them e.g. `docker compose down`