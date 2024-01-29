# SpeedSpy
Discord bot that follows server users speedrun.com stats. To run, create .env based on env_Base file

# Commands
```shell
git clone https://github.com/your-username/SpeedSpy.git

pip install -r requirements.txt

python spyBot.py
```

## azure

Login to Azure
```shell
az login
```

Install oauth secret. Needs to be run only once
```shell
az aks get-credentials --name vauhtijuoksu --resource-group Vauhtijuoksu-Azure-Sponsorship
kubectl create secret generic meta-credentials --from-file credentials.json
```

### Commands
```shell
docker build -t vauhtijuoksu.azurecr.io/vauhtijuoksu/speedspy:dev .
az acr login --name vauhtijuoksu
docker push vauhtijuoksu.azurecr.io/vauhtijuoksu/speedspy:dev
az aks get-credentials --name vauhtijuoksu --resource-group Vauhtijuoksu-Azure-Sponsorship
kubectl apply -f deploy.yaml
# Because the image is not versioned
kubectl rollout restart deployment speedspy
```

connect to pod
```shell
kubectl get pods
kubectl exec -it <pod-name> -- /bin/sh
```

Copy database to local
```shell
kubectl cp <pod-name>:/app/speedrunners.db ./database.db
```