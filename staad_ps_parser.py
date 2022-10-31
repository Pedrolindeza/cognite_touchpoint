import logging
import os
import time

import azure.functions as func
from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteException
from client_gen import client_gen
import sys

sys.path.insert(
    0, "/Users/pedrolindeza/Repos/Sepals/functions/cognite_staad_parser_ps/anl_parse_ps"
)

from calculations import create_calc_df
from file_parsing import parse_file
from cdf_util import CDFUtil


def main(client, file):

    logging.info(f"--- Python blob trigger function processed blob \n")

    dataset_id = 5601372144288760
    project = "noafulla"
    node_name = "staad_PS"

    try:
        start_time = time.time()
        anlFile_name = file
        with open(anlFile_name, "r") as local_file:
            try:
                cdfutil = CDFUtil(node_name, project, dataset_id, client)
                data, meta_data = parse_file(anlFile_name)
                anlFile_name = anlFile_name.replace(".ANL", "")
                logging.info(f"Finished parsing file: {anlFile_name}")
                if not data.empty:
                    cdfutil.create_asset(anlFile_name)
                    seq = cdfutil.upload_df_as_sequence(
                        data, anlFile_name, meta_data, ""
                    )
                    seq = client.sequences.data.retrieve_dataframe(
                        id=seq.id, start=0, end=None
                    )
                    calc_df = create_calc_df(seq)
                    if not calc_df.empty:
                        cdfutil.upload_df_as_sequence(
                            calc_df, anlFile_name, meta_data, "calc_"
                        )
                end_time = time.time()
                total_time = end_time - start_time
                logging.info(f"The script execution time in seconds is: {total_time}")
                logging.info("Function finished successfully")
            except Exception:
                logging.exception("Exception caught while parsing")
    except CogniteException as exc:
        logging.error(f"Failed to upload. Error message: {exc}")


if __name__ == "__main__":
    main(client_gen("test"), "DP130PS0001.ANL")
