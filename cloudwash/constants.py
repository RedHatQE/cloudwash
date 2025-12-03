aws_data = ['VMS', 'NICS', 'DISCS', 'PIPS', 'RESOURCES', 'STACKS', 'OCPS']
azure_data = ['VMS', 'NICS', 'DISCS', 'IMAGES', 'PIPS', 'RESOURCES']
gce_data = ['VMS', 'NICS', 'DISCS']
vmware_data = ['VMS', 'NICS', 'DISCS']
container_data = ['CONTAINERS']

# OCP resources tags for filtering
OCP_TAG_SUBSTR = "kubernetes.io/cluster/"
CLUSTER_NAME_TAGS = [
    "clusterName",
    "api.openshift.com/name",
]
CLUSTER_ID_TAGS = [
    "openshiftClusterID",
    "api.openshift.com/id",
]
CLUSTER_EXP_DATE_TAG = "expirationDate"
