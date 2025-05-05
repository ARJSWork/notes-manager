###
# File:   src\__main__.py
# Date:   2025-01-21 / 06:52
# Author: alexrjs
###


# imports
#from pathlib import Path
from argparse import ArgumentParser, Namespace
from db import register
from ui import app


# constants


# variables


# functions/classes
def parse_arguments():
    """Add this function to handle command-line arguments"""

    parser = ArgumentParser(description="Convert PDF files to Markdown.")
    # parser.add_argument("data_folder", type=str, default="data", help="Path to the input data folder containing PDF files.")
    # parser.add_argument("out_folder", type=str, default="out", help="Path to the output folder for Markdown files.")
    args = parser.parse_args()

    # # Validate the data folder
    # data_path = Path(args.data_folder)
    # if data_path and not data_path.is_dir():
    #     parser.error(f"The specified data folder '{args.data_folder}' does not exist or is not a directory.")

    # # Validate the output folder
    # out_path = Path(args.out_folder)
    # if not out_path.is_dir() and out_path.exists():
    #     parser.error(f"The specified output folder '{args.out_folder}' exists but is not a directory.")
    
    return args


def main(args_:Namespace) -> None:
    """ Main function """

    print("Hello world! This is a simple Flet Demo!")
    register("args", args_)
    register("dirty", False)
    app.run()


# Import Guard
if __name__ == "__main__":
    main(parse_arguments())
