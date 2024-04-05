import json
import boto3
import botocore

# Get Volume ID
def get_volume_id(volume_arn):
    volume_arn_split = volume_arn.split(':')
    volume_id = volume_arn_split[-1].split('/')[-1]
    return volume_id

# Main handler function
def lambda_handler(event, context):
    # Get Volume ARN from the event
    volume_arn = event['resources'][0]
    if not volume_arn:
        print("No volume ARN found in event.")
        return False
        
    # Get Volume ID from the ARN
    volume_id = get_volume_id(volume_arn)
    if not volume_id:
        print("Failed to get volume ID from ARN {}.".format(volume_arn))
        return False
    
    while True:
        client = boto3.client('ec2')    # Instantiating boto3 client
        try:
            describe_response = client.describe_volumes(VolumeIds=[volume_id])
            volume_state = describe_response['Volumes'][0]['State']
            volume_type = describe_response['Volumes'][0]['VolumeType']
            print("Volume {} is currently in {} state with type {}.".format(volume_id, volume_state, volume_type))
            # Check to verify the volume state and type
            if volume_type == 'gp2':
                if volume_state == 'available':
                    try:
                        client.modify_volume(
                            VolumeId=volume_id,
                            VolumeType='gp3',
                        )
                        print("Volume conversion to type gp3 initiated.")
                        break
                    except botocore.exceptions.ClientError as ex:
                        print("Failed to modify volume {} to type gp3: {}.".format(volume_id, ex))
                        continue
                else:
                    print("Volume {} is not in available state.".format(volume_id))
            else:
                print("Volume {} type is NOT gp2. Exiting.".format(volume_id))
                break
        except botocore.exceptions.ClientError as ex:
            print("Failed to describe volume {}: {}".format(volume_id, ex))
            continue
