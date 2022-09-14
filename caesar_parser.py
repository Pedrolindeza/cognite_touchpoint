import logging
import time
import sys
sys.path.insert(
    0, "/Users/pedrolindeza/repos/Sepals/functions/cognite_caesar_parser/caesar_parser"
)
from file_parsing import parse_file
from __init__ import main as lol

if __name__ == "__main__":

    lol("/Users/pedrolindeza/repos/Sepals/functions/cognite_caesar_parser/tests/29001.OUT")
    # with open("/Users/pedrolindeza/repos/Sepals/functions/cognite_caesar_parser/tests/29001.OUT", "r") as input_file:
    #     file_df, file_metadata, load_case_dct = parse_file(
    #         input_file, "29001.OUT"
    #     )
    #
