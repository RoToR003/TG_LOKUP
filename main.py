import os
import platform
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import time
from tqdm import tqdm
from tabulate import tabulate
import requests
import logging
import shutil
import subprocess

logging.getLogger('patool').setLevel(logging.CRITICAL)

logo = r"""
 ________   ______         __        ______   __    __  __    __  _______  
|        \ /      \       |  \      /      \ |  \  /  \|  \  |  \|       \ 
 \$$$$$$$$|  $$$$$$\      | $$     |  $$$$$$\| $$ /  $$| $$  | $$| $$$$$$$\
   | $$   | $$ __\$$      | $$     | $$  | $$| $$/  $$ | $$  | $$| $$__/ $$
   | $$   | $$|    \      | $$     | $$  | $$| $$  $$  | $$  | $$| $$    $$
   | $$   | $$ \$$$$      | $$     | $$  | $$| $$$$$\  | $$  | $$| $$$$$$$ 
   | $$   | $$__| $$      | $$_____| $$__/ $$| $$ \$$\ | $$__/ $$| $$      
   | $$    \$$    $$______| $$     \\$$    $$| $$  \$$\ \$$    $$| $$      
    \$$     \$$$$$$|      \\$$$$$$$$ \$$$$$$  \$$   \$$  \$$$$$$  \$$      
                    \$$$$$$                                                                                                 
                                                                    MADE: @cmxjq       
                                                                    lines in database: 182~ kk
                                                                    Version: 2.3
"""

def download_file(url, dest_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise exception for HTTP errors
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc="Downloading")
        
        with open(dest_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        if total_size != 0 and progress_bar.n != total_size:
            print("ERROR: Something went wrong with the download")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
        return False

def get_table_info(conn):
    try:
        cursor = conn.cursor()
        table_info = {}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        for table_name in tables:
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                table_info[table_name] = {'columns': [col[1] for col in columns]}
            except sqlite3.OperationalError as e:
                print(f"Failed to get columns for table {table_name}: {e}")
                continue

        return table_info
    except sqlite3.DatabaseError as e:
        print(f"Database error while retrieving table info: {e}")
        return {}

def format_value(value):
    if value is None:
        return None
    if value == 0:
        return 'False'
    if value == 1:
        return 'True'
    return value

def search_ids_in_table(cursor, table_name, id_columns, id_list):
    found_results = []
    for id_col in id_columns:
        try:
            placeholders = ", ".join("?" for _ in id_list)
            cursor.execute(f"SELECT * FROM {table_name} WHERE {id_col} IN ({placeholders})", id_list)
            results = cursor.fetchall()
            for result in results:
                found_results.append((id_col, result))
        except sqlite3.OperationalError as e:
            print(f"Error searching in table {table_name}: {e}")
            continue
    return found_results

def search_ids_in_db(db_path, id_list, progress_bar, result_list):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        table_info = get_table_info(conn)

        for table_name, info in table_info.items():
            id_columns = [col for col in info['columns'] if 'id' in col.lower()]
            if id_columns:
                found_results = search_ids_in_table(cursor, table_name, id_columns, id_list)
                for id_col, result in found_results:
                    db_path = db_path.replace("\\", "/")
                    formatted_result = [
                        [f"Database: {db_path}\nTable: {table_name}"],
                        ["\n".join(
                            f"{col_name}: {format_value(value)}" for col_name, value in zip(info['columns'], result) if format_value(value) is not None
                        )]
                    ]
                    result_list.append(tabulate(formatted_result, tablefmt="grid"))

        progress_bar.update(1)
        conn.close()
    except sqlite3.DatabaseError as e:
        print(f"Database error while processing {db_path}: {e}")

def process_database(file_name, folder_path, id_list, progress_bar, result_list):
    db_path = os.path.join(folder_path, file_name)
    if os.path.exists(db_path):
        search_ids_in_db(db_path, id_list, progress_bar, result_list)
    else:
        print(f"Database file {db_path} not found.")

def search_ids_in_all_dbs(folder_path, id_list):
    try:
        start_time = time.time()
        db_files = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('.db')]

        if not db_files:
            print("No database files found in the folder.")
            return

        result_list = []

        with tqdm(total=len(db_files), desc="Processing Databases", position=0, leave=True, ncols=100, unit="db") as progress_bar:
            with ThreadPoolExecutor() as executor:
                futures = []
                for db_file in db_files:
                    futures.append(executor.submit(process_database, db_file, folder_path, id_list, progress_bar, result_list))

                for future in futures:
                    future.result()

        if result_list:
            print("\n\n".join(result_list))
        else:
            print(f'\nNone of the ID(s) {id_list} were found in any file.')

        print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"Error processing databases: {e}")

def extract_rar_with_validation(file_path, extract_to):
    try:
        if platform.system() == "Windows":
            import patoolib
            patoolib.extract_archive(file_path, verbosity=-1, outdir=extract_to)
        else:
            if shutil.which("unrar"):
                subprocess.run(["unrar", "x", "-y", file_path, extract_to], check=True)
            elif shutil.which("bsdtar"):
                subprocess.run(["bsdtar", "-xvf", file_path, "-C", extract_to], check=True)
            else:
                raise EnvironmentError("Neither `unrar` nor `bsdtar` is installed on your system.")

        print(f"Extraction completed to folder '{extract_to}'.")

        if os.path.exists(extract_to):
            confirm = input(f"Do you want to delete the archive '{file_path}'? (y/n): ").strip().lower()
            if confirm == 'y':
                os.remove(file_path)  # Видалення архіву
                print(f"Archive '{file_path}' successfully deleted.")
            else:
                print(f"Archive '{file_path}' was not deleted.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Extraction failed with system command: {e}")
        return False
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return False
    except EnvironmentError as e:
        print(f"Environment error: {e}")
        return False
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

if __name__ == "__main__":
    folder_path = 'db/db'
    rar_url = "https://example.com/your-rar-file.rar"  # Змініть на ваш URL
    rar_path = "db.rar"

    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(logo)
        
        if os.path.exists(rar_path) and not os.path.exists(folder_path):
            print("Extracting...\nPlease wait")
            if extract_rar_with_validation(rar_path, os.getcwd()):
                print(f"Extraction completed to folder '{folder_path}'.")
            else:
                print("Extraction failed.")
        elif not os.path.exists(folder_path):
            response = requests.head(rar_url, allow_redirects=True)
            file_size = int(response.headers.get('content-length', 0)) / (1024 * 1024)

            print(f"The file size is approximately {file_size:.2f} MB.\nWarning, the unzipped file weighs 9.3 GB")
            confirm = input("Do you want to download and extract this file? (y/n): ").strip().lower()

            if confirm == "y":
                if download_file(rar_url, rar_path):
                    print("Download completed. Extracting files...")
                    if extract_rar_with_validation(rar_path, os.getcwd()):
                        print(f"Extraction completed to folder '{folder_path}'.")
                    else:
                        print("Extraction failed.")
                else:
                    print("Failed to download the file.")
            else:
                print("Download canceled.")
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(logo)
        
        id_input = input("Enter ID(s): ")
        id_list = [id.strip() for id in id_input.split(',')]

        search_ids_in_all_dbs(folder_path, id_list)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
