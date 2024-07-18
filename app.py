from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from models import LCApplicationModel
import random
import traceback
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
lc_model = LCApplicationModel()
otp_store = {}  # Temporary store for OTPs for simplicity

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    logger.info(f"Serving file: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/apply_lc', methods=['POST'])
def apply_lc():
    data = request.get_json()
    otp = data.get('otp')
    mobile_number = data.get('applicant_mobile')
    
    if otp_store.get(mobile_number) != int(otp):
        logger.warning(f"Invalid OTP for mobile number: {mobile_number}")
        return jsonify({'message': 'Invalid OTP'}), 400

    applicant_country = data.get('applicant_country')
    applicant_name = data.get('applicant_name')
    applicant_bank_account = data.get('applicant_bank_account')
    applicant_pan = data.get('applicant_pan')
    amount = data.get('amount')
    currency = data.get('currency')
    applicant_bank_name = data.get('applicant_bank_name')
    purpose = data.get('purpose')
    beneficiary_country = data.get('beneficiary_country')
    beneficiary_name = data.get('beneficiary_name')
    beneficiary_bank_account = data.get('beneficiary_bank_account')
    beneficiary_bank_name = data.get('beneficiary_bank_name')

    if not all([applicant_country, applicant_name, applicant_bank_account, applicant_pan, amount, currency, applicant_bank_name, purpose, beneficiary_country, beneficiary_name, beneficiary_bank_account, beneficiary_bank_name]):
        logger.warning("All fields are required")
        return jsonify({'message': 'All fields are required'}), 400

    application_id = random.randint(100000, 999999) 

    try:
        lc_model.create_application(application_id, applicant_country, applicant_name, applicant_bank_account, applicant_pan, amount, currency, applicant_bank_name, purpose, beneficiary_country, beneficiary_name, beneficiary_bank_account, beneficiary_bank_name)
        logger.info(f"LC Application created successfully with ID: {application_id}")
        return jsonify({'message': 'LC Application created successfully', 'application_id': application_id}), 201
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to create LC Application: {error_message}")
        traceback.print_exc()  
        return jsonify({'message': 'Failed to create LC Application', 'error': error_message}), 500

@app.route('/get_lc_applications', methods=['GET'])
def get_lc_applications():
    try:
        applications = lc_model.get_all_applications()
        logger.info("Retrieved LC applications")
        return jsonify(applications), 200
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to retrieve LC applications: {error_message}")
        traceback.print_exc() 
        return jsonify({'message': 'Failed to retrieve LC applications', 'error': error_message}), 500

@app.route('/view_lc_applications_page', methods=['GET'])
def view_lc_applications_page():
    logger.info("Serving LC applications page")
    return send_from_directory(os.getcwd(), 'view_lc_applications.html')

@app.route('/check_account_balance_page', methods=['GET'])
def check_account_balance_page():
    logger.info("Serving check account balance page")
    return send_from_directory(os.getcwd(), 'check_account_balance.html')

@app.route('/')
def index():
    logger.info("Serving index page")
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    mobile_number = data.get('mobile_number')
    otp = random.randint(100000, 999999)
    otp_store[mobile_number] = otp
    logger.info(f"OTP for {mobile_number}: {otp}") 
    return jsonify({'message': 'OTP sent successfully'}), 200

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    mobile_number = data.get('mobile_number')
    otp = data.get('otp')
    if otp_store.get(mobile_number) == int(otp):
        logger.info(f"Successfully verified OTP for mobile number: {mobile_number}")
        return jsonify({'message': 'Successfully verified'}), 200
    logger.warning(f"Invalid OTP for mobile number: {mobile_number}")
    return jsonify({'message': 'Not a valid customer'}), 400

@app.route('/check_balance', methods=['POST'])
def check_balance():
    data = request.get_json()
    mobile_number = data.get('mobile_number')
    logger.info(f"Checking balance for mobile number: {mobile_number}")
    # Mock account details for demonstration
    account_details = {
        'account_holder': 'John Doe',
        'bank_name': 'SBI',
        'balance': '1000 USD'
    }
    return jsonify({'message': 'Account details fetched successfully', 'account_holder': account_details['account_holder'], 'bank_name': account_details['bank_name'], 'balance': account_details['balance']}), 200

@app.route('/delete_lc_application', methods=['DELETE'])
def delete_lc_application():
    application_id = request.args.get('id')
    if not application_id:
        logger.warning("Application ID is required")
        return jsonify({'message': 'Application ID is required'}), 400

    try:
        lc_model.delete_application(application_id)
        logger.info(f"LC Application deleted successfully with ID: {application_id}")
        return jsonify({'message': 'LC Application deleted successfully'}), 200
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to delete LC Application: {error_message}")
        traceback.print_exc()
        return jsonify({'message': 'Failed to delete LC Application', 'error': error_message}), 500

@app.route('/approve_lc', methods=['POST'])
def approve_lc():
    data = request.get_json()
    application_id = data.get('application_id')
    try:
        lc_model.update_approval_status(application_id, 'approved')
        logger.info(f"LC approved successfully with ID: {application_id}")
        return jsonify({'message': 'LC approved successfully'}), 200
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to approve LC: {error_message}")
        traceback.print_exc()
        return jsonify({'message': 'Failed to approve LC', 'error': error_message}), 500

@app.route('/dispatch_goods', methods=['POST'])
def dispatch_goods():
    data = request.get_json()
    application_id = data.get('application_id')
    try:
        lc_model.update_dispatch_status(application_id, 'dispatched')
        logger.info(f"Goods dispatched successfully for application ID: {application_id}")
        return jsonify({'message': 'Goods dispatched successfully'}), 200
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to dispatch goods: {error_message}")
        traceback.print_exc()
        return jsonify({'message': 'Failed to dispatch goods', 'error': error_message}), 500

@app.route('/seller_dashboard', methods=['GET'])
def seller_dashboard():
    logger.info("Serving seller dashboard")
    return send_from_directory(os.getcwd(), 'seller_dashboard.html')

@app.route('/get_lc_application_by_id', methods=['GET'])
def get_lc_application_by_id():
    application_id = request.args.get('application_id')
    if not application_id:
        logger.warning("Application ID is required")
        return jsonify({'message': 'Application ID is required'}), 400
    try:
        query = "SELECT * FROM lc_applications WHERE application_id = %s"
        result = lc_model.db.fetchone(query, (application_id,))
        if result:
            logger.info(f"LC Application found with ID: {application_id}")
            return jsonify(result), 200
        else:
            logger.warning(f"LC Application not found with ID: {application_id}")
            return jsonify({'message': 'LC Application not found'}), 404
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to retrieve LC Application: {error_message}")
        traceback.print_exc()
        return jsonify({'message': 'Failed to retrieve LC Application', 'error': error_message}), 500

@app.route('/upload_document', methods=['POST'])
def upload_document():
    try:
        application_id = request.form['application_id']
        if 'document' not in request.files:
            logger.warning("No file part in the request")
            return jsonify({'message': 'No file part'}), 400
        file = request.files['document']
        if file.filename == '':
            logger.warning("No selected file")
            return jsonify({'message': 'No selected file'}), 400
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        lc_model.update_document_url(application_id, filename)
        logger.info(f"Document uploaded successfully for application ID: {application_id}")
        return jsonify({'message': 'Document uploaded successfully', 'file_url': file_path}), 200
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to upload document: {error_message}")
        traceback.print_exc()
        return jsonify({'message': 'Failed to upload document', 'error': error_message}), 500

@app.route('/get_document/<application_id>', methods=['GET'])
def get_document(application_id):
    try:
        document_url = lc_model.get_document_url(application_id)
        if document_url:
            logger.info(f"Document found for application ID: {application_id}")
            return jsonify({'message': 'Document found', 'document_url': document_url}), 200
        else:
            logger.warning(f"Document not found for application ID: {application_id}")
            return jsonify({'message': 'Document not found'}), 404
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to retrieve document: {error_message}")
        traceback.print_exc()
        return jsonify({'message': 'Failed to retrieve document', 'error': error_message}), 500

@app.route('/buyer_dashboard', methods=['GET'])
def buyer_dashboard():
    logger.info("Serving buyer dashboard")
    return send_from_directory(os.getcwd(), 'buyer_dashboard.html')

@app.route('/release_funds', methods=['POST'])
def release_funds():
    data = request.get_json()
    application_id = data.get('application_id')
    
    try:
        lc_model.update_fund_release_status(application_id, 'released')
        logger.info(f"Funds released successfully for application ID: {application_id}")
        return jsonify({'message': 'Funds released successfully'}), 200
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to release funds: {error_message}")
        traceback.print_exc()
        return jsonify({'message': 'Failed to release funds', 'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
