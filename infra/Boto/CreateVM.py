import CloudProperties as clo
import boto
from boto.ec2.regioninfo import RegionInfo

region = RegionInfo(name=clo.NectarRegion, endpoint='nova.rc.nectar.org.au')
print(region)

# Getting Images
ec2_conn = boto.connect_ec2(aws_access_key_id=clo.aws_access,
                            aws_secret_access_key=clo.aws_secret,
                            is_secure=True, region=region, port=8773, path='/services/Cloud', validate_certs=False)
print(ec2_conn)
# images = ec2_conn.get_all_images()

# Launching App Server Instance 1

reservation_app_server1 = ec2_conn.run_instances(clo.vm_image_id, key_name=clo.key_name,
                                                 instance_type=clo.app_server,
                                                 security_groups=[clo.security_group], placement=clo.NectarRegion)
instance = reservation_app_server1.instances[0]
print('New instance {} has been created. APP SERVER'.format(instance.id))
clo.app_server_instance1 = str(instance.id)

# Launching DB Server Instance 1
reservation_dbserver1 = ec2_conn.run_instances(clo.vm_image_id, key_name=clo.key_name,
                                               instance_type=clo.db_server,
                                               security_groups=[clo.security_group], placement=clo.NectarRegion)
instance = reservation_dbserver1.instances[0]
print('New instance {} has been created. DB SERVER 1'.format(instance.id))
clo.db_server_instance1 = str(instance.id)

# Launching DB Server Instance 2
reservation_dbserver2 = ec2_conn.run_instances(clo.vm_image_id, key_name=clo.key_name,
                                               instance_type=clo.db_server,
                                               security_groups=[clo.security_group], placement=clo.NectarRegion)
instance = reservation_dbserver2.instances[0]
print('New instance {} has been created. DB SERVER 2'.format(instance.id))
clo.db_server_instance2 = str(instance.id)

# Launching DB Server Instance 3
reservation_dbserver3 = ec2_conn.run_instances(clo.vm_image_id, key_name=clo.key_name,
                                               instance_type=clo.db_server,
                                               security_groups=[clo.security_group], placement=clo.NectarRegion)
instance = reservation_dbserver3.instances[0]
print('New instance {} has been created. DB SERVER 2'.format(instance.id))
clo.db_server_instance3 = str(instance.id)

'''
After output update instance id's in the property files so that the volumes can be attached properly

'''
