# from flask import Flask, render_template, request
# import boto3

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/migrate', methods=['POST'])
# def migrate():
#     # Get the source and destination table names from the form
#     source_table_name = request.form['source_table']
#     destination_table_name = request.form['destination_table']

#     # Get AWS credentials and region from the form
#     aws_access_key_id = request.form['access_key']
#     aws_secret_access_key = request.form['secret_key']
#     aws_region = request.form['region']

#     # Initialize DynamoDB resource
#     dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,
#                             aws_secret_access_key=aws_secret_access_key,
#                             region_name=aws_region)

#     try:
#         # Get source and destination tables
#         source_table = dynamodb.Table(source_table_name)
#         destination_table = dynamodb.Table(destination_table_name)

#         # Scan the source table to get all items
#         response = source_table.scan()
#         items = response['Items']

#         # Transform items to match the schema of the destination table
#         transformed_items = transform_items(items)

#         # Batch write transformed items to the destination table
#         with destination_table.batch_writer() as batch:
#             for item in transformed_items:
#                 batch.put_item(Item=item)

#         return render_template('success.html', source_table=source_table_name, destination_table=destination_table_name)
    
#     except Exception as e:
#         error_message = f"An error occurred: {str(e)}"
#         return render_template('error.html', error_message=error_message)

# def transform_items(items):
#     # Implement your data transformation logic here
#     transformed_items = []
#     for item in items:
#         # Example: Transform attributes to match destination table schema
#         transformed_item = {
#             'FirmwareVersion': item['FirmwareVersion'],  # Map 'FirmwareVersion' from source table to 'FirmwareVersion' in destination table
#             'HubType': 'DefaultHubType',  # Provide a default HubType value for the destination table
#             # Add additional transformations as needed
#         }
#         transformed_items.append(transformed_item)
#     return transformed_items

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request
import boto3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/migrate', methods=['POST'])
def migrate():
    # Get form data including AWS credentials
    access_key = request.form['access_key']
    secret_key = request.form['secret_key']
    region = request.form['region']
    source_table_name = request.form['source_table']
    destination_table_name = request.form['destination_table']
    
    try:
        # Initialize DynamoDB client with provided AWS credentials and region
        dynamodb = boto3.client('dynamodb',
                                aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key,
                                region_name=region)
        
        # Scan the source table to get all items
        response = dynamodb.scan(TableName=source_table_name)
        items = response['Items']
        
        # Transform and migrate items to the destination table
        for item in items:
            transformed_item = transform_item(item)
            write_item_to_destination_table(dynamodb, destination_table_name, transformed_item)
        
        return render_template('success.html', source_table=source_table_name, destination_table=destination_table_name)
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render_template('error.html', error_message=error_message)

def transform_item(item):
    # Transformation logic for each item
    firmware_version = item.get('FirmwareVersion', '')
    if isinstance(firmware_version, str):
        if firmware_version.startswith('box'):
            hub_type = 'box'
        elif firmware_version.startswith('eg500'):
            hub_type = 'eg500'
        else:
            hub_type = 'DefaultHubType'
    else:
        hub_type = 'DefaultHubType'
    
    transformed_item = {
        'FirmwareVersion': item.get('FirmwareVersion'),
        'HubType': {'S': hub_type},  # Convert to DynamoDB attribute format
        'BaseVersion': item.get('BaseVersion'),
        'PackageArchiveName': item.get('PackageArchiveName'),
        'UpdateType': item.get('UpdateType'),
        # Add additional attributes and transformations as needed
    }
    
    return transformed_item



def write_item_to_destination_table(dynamodb, destination_table_name, item):
    # Write item to destination table
    dynamodb.put_item(TableName=destination_table_name, Item=item)

if __name__ == '__main__':
    app.run(debug=True)
