from flask import Flask, render_template, request
import boto3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/migrate', methods=['POST'])
def migrate():
    # Get the source and destination table names from the form
    source_table_name = request.form['source_table']
    destination_table_name = request.form['destination_table']

    # Initialize DynamoDB client
    dynamodb = boto3.client('dynamodb')

    try:
        # Scan the source table to get all items
        response = dynamodb.scan(TableName=source_table_name)
        items = response['Items']

        # Batch write items to the destination table
        with dynamodb.batch_writer(TableName=destination_table_name) as batch:
            for item in items:
                batch.put_item(Item=item)

        return render_template('success.html', source_table=source_table_name, destination_table=destination_table_name)
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
