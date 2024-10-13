import pyzipper
import argparse
import itertools
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored  # For colorful output

def try_password(zip_file, password, output_folder='output_folder'):
    try:
        with pyzipper.AESZipFile(zip_file) as zf:
            zf.pwd = bytes(password, 'utf-8')
            print(colored(f"Trying password: {password}", 'cyan'))
            zf.extractall(path=output_folder)
            print(colored(f"🎉 Password found: {password} 🎉", 'green'))
            return True
    except (RuntimeError, pyzipper.BadZipFile):
        return False
    except Exception as e:
        print(colored(f"😱 An error occurred: {e}", 'red'))
        return False

def dictionary_attack(zip_file, password_file, max_workers=20, output_folder='output_folder'):
    def password_workers(password):
        if password:
            return try_password(zip_file, password, output_folder)

    print(colored("🚀 Starting dictionary attack with multithreading...\n", 'yellow'))
    with open(password_file, 'r') as pf:
        for line in pf:
            password = line.strip()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(password_workers, password)]
                for future in futures:
                    if future.result():
                        print(colored("🔒 Password found! Stopping attack.", 'green'))
                        return True

    print(colored("❌ Dictionary attack failed. No valid password found.", 'red'))
    return False

def brute_force_attack(zip_file, charset, max_len, max_workers=10, output_folder='output_folder'):
    def password_workers(password_tuple):
        password = ''.join(password_tuple)
        print(colored(f"Trying password: {password}", 'cyan'))
        return try_password(zip_file, password, output_folder)

    print(colored("🚀 Starting brute-force attack...\n", 'yellow'))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for length in range(1, max_len + 1):
            futures = []
            for password_tuple in itertools.product(charset, repeat=length):
                futures.append(executor.submit(password_workers, password_tuple))
                for future in futures:
                    if future.result():
                        print(colored("🔒 Password found! Stopping attack.", 'green'))
                        return True

    print(colored("❌ Brute-force attack failed. No valid password found.", 'red'))
    return False

def open_zip_file(zip_file_path, output_folder, password_file=None, brute_force=False, charset=None, max_len=None, max_workers=10):
    print(colored(f"🔍 Attempting to crack: {zip_file_path}", 'blue'))

    if password_file and output_folder:
        if dictionary_attack(zip_file_path, password_file, max_workers=max_workers, output_folder=output_folder):
            return True

    if brute_force and charset and max_len and output_folder:
        if brute_force_attack(zip_file_path, charset, max_len, max_workers=max_workers, output_folder=output_folder):
            return True

    print(colored("❌ Failed to extract the ZIP file. Could not find the correct password.", 'red'))
    return False

def main():
    parser = argparse.ArgumentParser(description="A ZIP file cracker with dictionary and brute-force options.")
    parser.add_argument("zipfile", help="The path to the ZIP file to check and extract.")
    parser.add_argument('-o', '--output', default="output_folder", help="The directory to extract the files to.")
    parser.add_argument('-d', "--dictionary", help="Path to the dictionary file for password cracking.")
    parser.add_argument("-b", "--bruteforce", action="store_true", help="Enable brute-force attack.")
    parser.add_argument("-c", "--charset", default="abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+?><", help="Character set for brute-force.")
    parser.add_argument("-m", "--maxlen", type=int, help="Maximum password length for brute-force.")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Number of threads to use for multithreading.")

    args = parser.parse_args()

    open_zip_file(
        args.zipfile,
        args.output,
        password_file=args.dictionary,
        brute_force=args.bruteforce,
        charset=args.charset,
        max_len=args.maxlen,
        max_workers=args.workers
    )

if __name__ == '__main__':
    main()