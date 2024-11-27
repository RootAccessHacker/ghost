import sys
from PyPDF2 import PdfReader, PdfWriter
import os

def sanitize_pdf(input_file, verbose=False):
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return
    
    # Extract the file name and extension
    base_name, ext = os.path.splitext(input_file)
    if ext.lower() != '.pdf':
        print(f"Error: The file '{input_file}' is not a PDF.")
        return
    
    output_file = f"{base_name}_SANITIZED.pdf"
    
    # Open and process the PDF
    with open(input_file, "rb") as pd:
        print("[+]\tReading the PDF file...")
        reader = PdfReader(pd)
        writer = PdfWriter()

        # Add all pages to the new PDF
        for page in reader.pages:
            writer.add_page(page)

        # Check and sanitize metadata
        if reader.metadata:
            sanitized_metadata = {
                    "/Author"   :   "",
                    "/Producer" :   "",
                    "/Title"    :   "",
                    "/Subject"  :   "",
                    "/Creator"  :   "",
                    "/Keywords" :   "",
                    "/CreationDate":"",
                    "/ModDate"  :   "",
                    "/Trapped"  :   "",
                    "/PTEX.Fullbanner": ""
                }
            
            for key, value in reader.metadata.items():
                if verbose:
                    print(f"[i]\t{key}: {value}")
                sanitized_metadata[key] = ""
            writer.add_metadata(sanitized_metadata)
            
        else:
            print("No metadata found to sanitize.")

        # Write the new PDF
        with open(output_file, "wb") as td:
            print(f"[+]\tWriting sanitized PDF to '{output_file}'")
            writer.write(td)

    print("[+]\tSanitization complete.\n")

# Main function to handle command-line arguments
if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python ghost.py <path_to_pdf> [-v | --verbose]")
    else:
        input_pdf = sys.argv[1]
        verbose_mode = "-v" in sys.argv or "--verbose" in sys.argv
        sanitize_pdf(input_pdf, verbose_mode)
