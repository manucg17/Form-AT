import os
import shutil
from flask import Flask, render_template, request, jsonify
import json
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)

# Define the upload folder path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Uploads')

# Delete the existing upload directory if it exists
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)

# Create a new upload directory and set permissions
os.makedirs(UPLOAD_FOLDER)
os.chmod(UPLOAD_FOLDER, 0o777)

# JSON data associated with different endpoints
json_schemas = {
    '/user-register/activate': {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "example": "FilePath"
                    },
                    "id": {
                        "type": "integer",
                        "format": "int64"
                    },
                    "emailId": {
                        "type": "string"
                    },
                    "password": {
                        "type": "string"
                    },
                    "firstName": {
                        "type": "string"
                    },
                    "lastName": {
                        "type": "string"
                    },
                    "gender": {
                        "type": "string",
                        "enum": [
                            "FEMALE",
                            "MALE",
                            "DONT_WANT_TO_DISCLOSE"
                        ]
                    },
                    "dob": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "nationality": {
                        "type": "string"
                    },
                    "languagePreference": {
                        "type": "string"
                    },
                    "timeZone": {
                        "type": "string"
                    },
                    "phoneNumber": {
                        "type": "string"
                    },
                    "address": {
                        "type": "string"
                    },
                    "roles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "format": "int64"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "subEntityId": {
                                    "type": "integer",
                                    "format": "int64"
                                },
                                "subEntity": {
                                    "type": "integer",
                                    "format": "int64"
                                },
                                "archive": {
                                    "type": "boolean"
                                }
                            }
                        }
                    },
                    "state": {
                        "type": "string",
                        "enum": [
                            "PENDING",
                            "ACTIVE",
                            "INACTIVE"
                        ]
                    },
                    "registerToken": {
                        "type": "string"
                    },
                    "registerTokenExpiryDate": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "createdAt": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "lastUpdatedAt": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "secretKey": {
                        "type": "string"
                    },
                    "mfaType": {
                        "type": "string",
                        "enum": [
                            "GOOGLE",
                            "DUO",
                            "NONE"
                        ]
                    },
                    "googleAuthEnabled": {
                        "type": "boolean"
                    },
                    "mfaEnabled": {
                        "type": "boolean"
                    },
                    "ssoEnabled": {
                        "type": "boolean"
                    },
                    "notifyUserDTO": {
                        "type": "object",
                        "properties": {
                            "sendEmail": {
                                "type": "boolean"
                            },
                            "sendSms": {
                                "type": "boolean"
                            },
                            "emailMessage": {
                                "type": "object",
                                "properties": {
                                    "subject": {
                                        "type": "string"
                                    },
                                    "message": {
                                        "type": "string"
                                    },
                                    "to": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "fromAddress": {
                                        "type": "string"
                                    },
                                    "cc": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "bcc": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "html": {
                                        "type": "boolean"
                                    }
                                }
                            },
                            "smsMessage": {
                                "type": "object",
                                "properties": {
                                    "recipients": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "message": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    },
                    "groupList": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "format": "int64"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "additionalDetails": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            },
            "token": {
                "type": "string"
            },
            "verificationCode1": {
                "type": "string"
            },
            "verificationCode2": {
                "type": "string"
            },
            "mfaType": {
                "type": "string"
            },
            "duoSelected": {
                "type": "boolean"
            }
        },
        "description": "User details"
    }
}

def generate_example(schema):
    """Generate example JSON data based on the schema."""
    if schema['type'] == 'object':
        example = {}
        for key, prop in schema['properties'].items():
            example[key] = generate_example(prop)
        return example
    elif schema['type'] == 'array':
        return [generate_example(schema['items'])]
    elif schema['type'] == 'integer':
        return 0
    elif schema['type'] == 'string':
        if 'enum' in schema:
            return schema['enum'][0]  # Use the first enum value as an example
        return 'string'
    elif schema['type'] == 'boolean':
        return True
    elif schema['type'] == 'number':
        return 0.0
    elif schema['type'] == 'date-time':
        from datetime import datetime
        return datetime.now().isoformat()
    return None

@app.route('/')
def index():
    return render_template('index.html', endpoints=json_schemas.keys())

@app.route('/edit-json', methods=['POST'])
def edit_json():
    endpoint = request.form.get('endpoint')
    schema = json_schemas.get(endpoint)
    logging.info(f'Schema for {endpoint}: {schema}')
    if schema:
        example_json = generate_example(schema)
        return render_template('form.html', schema=schema, example_json=json.dumps(example_json, indent=2), endpoint=endpoint)
    return 'Endpoint not found', 404

@app.route('/submit_edits', methods=['POST'])
def submit_edits():
    json_data = request.form.get('jsonEditor')
    edited_data = {}

    if json_data:
        # Handling JSON Fields Tab Submission
        try:
            edited_data = json.loads(json_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"}), 400
    else:
        # Handling Values Tab Submission
        edited_data = request.form.to_dict()
    
        # Handle file uploads
        if 'fileUploadInput' in request.files:
            file = request.files['fileUploadInput']
            if file:
                file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(file_path)
                edited_data['user.filePath'] = file_path  # Ensure this matches the nested structure

        # Convert string values "true"/"false" to Python booleans True/False
        for key in edited_data:
            value = edited_data[key]
            if isinstance(value, str):
                if value.lower() == 'true':
                    edited_data[key] = True
                elif value.lower() == 'false':
                    edited_data[key] = False

    return jsonify(edited_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
