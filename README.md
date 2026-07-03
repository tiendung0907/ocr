# Hades
Dự án này để rút trích các thông tin CMND của myanmar

# Deploy
Build docker
```
docker build -t hades:v0 .
```
## Run 
Run docker with all gpus
```
docker run  --gpus all -it -p 30004:8000 hades:v0
```

Run with specific gpus
```
docker run  --gpus '"device=0"' -it -p 30004:8000 hades:v0
```

## Run in background
Run docker with detach
```
docker run  --gpus all -itd -p 30004:8000 hades:v0
```

Run with specific gpu
```
docker run  --gpus '"device=0"' -itd -p 30004:8000 hades:v0
```

Parallel
```
docker run  --gpus '"device=0"' -itd -p 30004:8000 hades:v0 -w {num_worker}
```

# Test 
```
curl -F 'file=@011030002-11.jpg' 183.91.11.38:30004/nic_img
```

## Problems
Nếu có bất kì vấn đề gì vui lòng liên hệ pbcquoc@gmail.com

# hades
# hades
