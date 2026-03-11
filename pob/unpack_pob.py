import sys
import base64
import zlib

def unpack_pob_from_file(file_path):
    try:
        # 1. Read the file content
        with open(file_path, 'r') as f:
            pob_code = f.read().strip()

        if not pob_code:
            print("Error: The file is empty.")
            return

        # 2. Sanitize the string
        # PoB uses URL-safe Base64. Replace '-' with '+' and '_' with '/'
        pob_code = pob_code.replace('-', '+').replace('_', '/')
        
        # Ensure correct padding for Base64
        padding = len(pob_code) % 4
        if padding:
            pob_code += '=' * (4 - padding)

        # 3. Base64 Decode
        compressed_data = base64.b64decode(pob_code)

        # 4. Zlib Decompress
        xml_bytes = zlib.decompress(compressed_data)

        # 5. Output the result
        print(xml_bytes.decode('utf-8'))

    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
    except Exception as e:
        print(f"Error processing string: {e}")

if __name__ == "__main__":
    # Check if a filename was provided as an argument
    if len(sys.argv) < 2:
        print("Usage: python unpack_pob.py <path_to_text_file>")
    else:
        unpack_pob_from_file(sys.argv[1])
