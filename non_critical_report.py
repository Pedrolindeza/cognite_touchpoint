import logging
import os
import time

import pandas as pd

from client_gen import client_gen
from cognite.client import CogniteClient
import sys
sys.path.insert(
    0, "/Users/pedrolindeza/repos/Sepals/functions/cognite_caesar_report_noncritical/caesar_non_critical"
)
from report_util import get_report
from cdf_util import CDFUtil
from report_logic import create_new_base_case


def main(client: CogniteClient):
    logging.info("Starting CFAC parser")
    start_time = time.time()
    # Get credentials from app env vars

    dataset_id = 106826391582427
    project = "noafulla"
    nc_metadata_table_name = "pipe_metadata_non_critical"

    node_name = "caesar_non_critical_loads"
    seq_name = "non_critical_loads"

    try:
        cdfutil = CDFUtil(node_name, project, dataset_id, client)
        e3d_data = cdfutil.get_raw_table(nc_metadata_table_name)
        new_report = get_report(e3d_data)

        if cdfutil.base_case_exists(seq_name):
            base_case, prev_seq = cdfutil.retrieve_latest_sequence(seq_name)
            new_base_case = create_new_base_case(new_report, base_case)
            if new_base_case:
                meta_data = {"prev_seq": prev_seq.id}
                seq = cdfutil.upload_df_as_sequence(new_base_case, seq_name, meta_data)
                logging.info(f"Uploaded sequence: {seq.name}")
            else:
                logging.info("No changes found")
        else:
            meta_data = {"prev_seq": "None"}
            seq = cdfutil.upload_df_as_sequence(new_report, seq_name, meta_data)
            logging.info(f"Uploaded sequence: {seq.name}")
        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"The script execution time in seconds is: {total_time}")
    except Exception:
        logging.exception("Error occured while creating non critical report")

if __name__ == "__main__":
    df = client_gen("develop").raw.rows.retrieve_dataframe(limit=-1, db_name="noafulla_sepals", table_name="pipe_metadata_non_critical")
    df["index"] = df["NAME"]
    df.set_index("index", inplace=True)
    client_gen("develop").raw.rows.insert_dataframe("noafulla_sepals", "pipe_metadata_non_critical", df)

