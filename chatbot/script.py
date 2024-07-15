import re
import pytesseract
import cv2

# Function to extract Aadhar details from text
def extract_aadhar_details(text):
    # Updated name pattern to look for two consecutive words with capital first letters
    name_pattern = re.compile(r'([A-Z][a-z]+)\s+([A-Z][a-z]+)')
    dob_pattern = re.compile(r'([0-9]{2}/[0-9]{2}/[0-9]{4})')
    aadhar_pattern = re.compile(r'\d{4}\s\d{4}\s\d{4}')

    # Search for the name
    name_matches = name_pattern.findall(text)
    name = ' '.join(name_matches[0]) if name_matches else 'Not Found'

    dob = dob_pattern.search(text)
    aadhar_number = aadhar_pattern.search(text)
    print(aadhar_number.group(0) )

    return {
        'Name': name,
        'DOB': dob.group(0) if dob else 'Not Found',
        'Aadhar_Number': aadhar_number.group(0) if aadhar_number else 'Not Found'
    }

# Function to perform OCR on an image and extract Aadhar details
def extract_details_from_image(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(gray_image)
    
    # Extract Aadhar details from the extracted text
    details = extract_aadhar_details(text)
    
    return details

# Example usage
if __name__ == "__main__":
    image_path = '/home/rishabh/Downloads/fd/image_copy.png'
    details = extract_details_from_image(image_path)
    print(details)
