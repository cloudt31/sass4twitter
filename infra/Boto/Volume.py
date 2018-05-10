import boto
import time

from boto.ec2.regioninfo import RegionInfo

import CloudProperties as clo

region = RegionInfo(name=clo.NectarRegion, endpoint='nova.rc.nectar.org.au')
print(region)
ec2_conn = boto.connect_ec2(aws_access_key_id=clo.aws_access,
                            aws_secret_access_key=clo.aws_secret,
                            is_secure=True, region=region, port=8773, path='/services/Cloud', validate_certs=False)
print(ec2_conn)

# Creating Volume of 75GB for Primary DB Server
dbvol1 = ec2_conn.create_volume(75, clo.NectarRegion)
print('Volume Id: ', dbvol1.id)
ec2_conn.create_tags([dbvol1.id], {"Name": "T31_DB_75_Primary"})

curr_vol = ec2_conn.get_all_volumes([dbvol1.id])[0]
while curr_vol.status == 'creating':
    curr_vol = ec2_conn.get_all_volumes([dbvol1.id])[0]
    print('Primary DB Volume Status: ', curr_vol.status)
    time.sleep(2)
print('Primary DB Volume Zone: ', curr_vol.zone)

result = ec2_conn.attach_volume(dbvol1.id, clo.db_server_instance1, "/dev/vdc")
print('Attach Volume Result: ', result)

# Creating Volume of 75GB for Secondary DB Server
dbvol2 = ec2_conn.create_volume(75, clo.NectarRegion)
print('Volume Id: ', dbvol2.id)
ec2_conn.create_tags([dbvol2.id], {"Name": "T31_DB_75_Secondary"})

curr_vol = ec2_conn.get_all_volumes([dbvol2.id])[0]
while curr_vol.status == 'creating':
    curr_vol = ec2_conn.get_all_volumes([dbvol2.id])[0]
    print('Secondary DB Volume Status: ', curr_vol.status)
    time.sleep(2)
print('Secondary DB Volume Zone: ', curr_vol.zone)

result = ec2_conn.attach_volume(dbvol2.id, clo.db_server_instance2, "/dev/vdc")
print('Attach Volume Result: ', result)

# Creating Volume of 30 GB for DB Server 3
dbvol3 = ec2_conn.create_volume(30, clo.NectarRegion)
print('Volume Id: ', dbvol3.id)
ec2_conn.create_tags([dbvol3.id], {"Name": "T31_DB_30_Spare"})

curr_vol = ec2_conn.get_all_volumes([dbvol3.id])[0]
while curr_vol.status == 'creating':
    curr_vol = ec2_conn.get_all_volumes([dbvol3.id])[0]
    print('Tertiary DB Volume Status: ', curr_vol.status)
    time.sleep(2)
print('Tertiary DB Volume Zone: ', curr_vol.zone)

result = ec2_conn.attach_volume(dbvol3.id, clo.db_server_instance3, "/dev/vdc")
print('Attach Volume Result: ', result)

# Creating Volume of 60 GB for App Server
appvol = ec2_conn.create_volume(60, clo.NectarRegion)
print('Volume Id: ', appvol.id)
ec2_conn.create_tags([appvol.id], {"Name": "T31_APP_90"})

curr_vol = ec2_conn.get_all_volumes([appvol.id])[0]
while curr_vol.status == 'creating':
    curr_vol = ec2_conn.get_all_volumes([appvol.id])[0]
    print('App Server Volume Status: ', curr_vol.status)
    time.sleep(2)
print('App Server Volume Zone: ', curr_vol.zone)

result = ec2_conn.attach_volume(appvol.id, clo.app_server_instance, "/dev/vdc")
print('Attach Volume Result: ', result)

'''
Attach volume on server.
1. Logon to the server
2. Check where the volume has been attached using:
sudo fdisk -l
3. It should be something like /dev/vdc/ Confirm once again with:
sudo lsblk
4. Format the partition using:
sudo mkfs.ext4 /dev/vdc
5. Create mountpoint in base root directory:
cd /
sudo mkdir /data
6. Mount the newly formatted filesystem:
sudo mount /dev/vdc /data

'''
