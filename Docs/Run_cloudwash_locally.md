# How to run the cloudwash setup locally


You will need a pod spec file, config map file (optional) and a secrets file. Create files locally named:

* cloudwash.testpod.yaml:
```
apiVersion: v1
kind: Pod
metadata:
  name: cloudwash-test-pod
spec:
  containers:
    - name: cloudwash
      image: quay.io/redhatqe/cloudwash
      command: ["/bin/sh"]
      args: ["-c", "sleep 5000"]
      volumeMounts:
      - name: config-volume
        mountPath: /opt/app-root/src/cloudwash/settings.yaml
        subPath: settings.yaml
      env:
        - name: CLEANUP_AZURE__AUTH__CLIENT_ID
          valueFrom:
            secretKeyRef:
              key: azure_client_id
              name: cloudwash-secret
        - name: CLEANUP_AZURE__AUTH__SECRET_ID
          valueFrom:
            secretKeyRef:
              key: azure_client_secret
              name: cloudwash-secret
        - name: CLEANUP_AZURE__AUTH__TENANT_ID
          valueFrom:
            secretKeyRef:
              key: azure_tenant_id
              name: cloudwash-secret
        - name: CLEANUP_AZURE__AUTH__SUBSCRIPTION_ID
          valueFrom:
            secretKeyRef:
              key: subscription_id
              name: cloudwash-secret
  volumes:
    - name: config-volume
      configMap:
        name: cloudwash-config
  restartPolicy: Never
```
* cloudwash.configmap.yaml
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudwash-config
data:
  settings.yaml: |
    AZURE:
        AUTH:
            CLIENT_ID: ""
            SECRET_ID: ""
            TENANT_ID: ""
            SUBSCRIPTION_ID: ""
            RESOURCE_GROUPS: []
            REGIONS: []
        CRITERIA:
            VM:
                DELETE_VM: ''
                SLA_MINUTES: 120
            DISC:
                UNASSIGNED: True
            NIC:
                UNASSIGNED: True
            IMAGE:
                DELETE_IMAGE: ''
                UNASSIGNED: True
            PUBLIC_IP:
                UNASSIGNED: True
            RESOURCE_GROUP:
                LOGIC: AND
                DELETE_GROUP:
                RESOURCES_SLA_MINUTES: 120
        EXCEPTIONS:
            VM:
                VM_LIST: []
                STOP_LIST: []
            GROUP:
                RG_LIST: []
            IMAGES: []
```
* cloudwash.secrets.yaml
```
apiVersion: v1
kind: Secret
metadata:
  name: cloudwash-secret
  namespace: default
type: Opaque
stringData:
  azure_client_id: "XXXXXXXX"
  azure_client_secret: "XXXXXXX"
  azure_tenant_id: "XXXXXXXXX"
  subscription_id: "XXXXXXXXX"
```

After creating the files run these commands


Note: Ensure you have minikube installed:
https://minikube.sigs.k8s.io/docs/start/

* Check minikube status
```
minikube status
```
* If the status is stopped then start it
```
minikube start
```

* Now create all yaml files in minikube cluster:
```
minikube kubectl -- create -f cloudwash.testpod.yaml
minikube kubectl -- create -f cloudwash.configmap.yaml
minikube kubectl -- create -f Cloudwash.secrets.yaml
```

* You can check already created yaml files:
```
 minikube kubectl -- get configmap
 minikube kubectl -- get pods
 minikube kubectl -- get secrets
 ```

* If required, to delete any of the yaml files:
```
 minikube kubectl -- delete pod <podname>
 minikube kubectl -- delete configmap <configmap name>
 minikube kubectl -- delete secrets <secret name>
 ```
* Verify the container is running; check the below line from the pod yaml file
```
containers:
- name: cloudwash
   image: quay.io/redhatqe/cloudwash
command: ["/bin/sh"]
args: ["-c", "sleep 5000"]
```
* Here the lines say to stop the cloud wash container for 5000 seconds so we can run the “swach” commands in the shell
After getting the container in a running state, run this command to enter the bash shell
```
minikube kubectl -- exec -it cloudwash-test-pod -- /bin/bash
```

* Where “cloudwash-test-pod” is the name of the pod we defined in the pod spec file.
Now it will prompt you with the shell command line. Run the cloudwash commands here:
```
pip install cloudwash
swach -d azure  -- all
```
