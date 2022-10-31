import sys
import logging
import os
import time
import azure.functions as func
from client_gen import client_gen
from cognite.client.exceptions import CogniteException

sys.path.insert(
    0, "/Users/pedrolindeza/repos/Sepals/functions/cognite_caesar_parser/caesar_parser"
)
from cdf_util import CDFUtil
from file_parsing import parse_file, upload_df_as_sequence
from sequence_calc import create_calc_sequence
from sequence_cfac import upload_cfac_seq, create_cfac_sequence


def main(stressFileStream):
    dataset_id = 5601372144288760
    metadata_table_name = "pipe_metadata_critical"
    project = "noafulla"
    cfac_table_name = "pipe_cfac"
    node_name = "caesar_critical_loads"

    try:
        client = client_gen("test")
        stress_file_name = stressFileStream
        start_time = time.time()
        with open(stress_file_name, "r") as input_file:
            file_df, file_metadata, load_case_dct = parse_file(
                input_file, stress_file_name
            )
            try:
                if file_df.empty:
                    raise Exception(f"No data in file {stress_file_name}")
                else:
                    cdfutil = CDFUtil(node_name, project, dataset_id, client)
                    raw_seq = upload_df_as_sequence(
                        cdfutil,
                        file_df,
                        stress_file_name,
                        file_metadata,
                    )
                    calc_df = create_calc_sequence(
                        cdfutil,
                        raw_seq,
                        stress_file_name,
                        load_case_dct,
                    )
                    if not calc_df.empty:
                        seq_w_cfac_df = create_cfac_sequence(
                            cdfutil,
                            stress_file_name,
                            calc_df,
                            metadata_table_name,
                            cfac_table_name,
                        )
                        if not seq_w_cfac_df.empty:
                            upload_cfac_seq(
                                cdfutil,
                                stress_file_name,
                                seq_w_cfac_df,
                            )
                        else:
                            logging.info("Failed crating cfac sequence empty dataframe")
                    else:
                        logging.info(f"No calculations found for {stress_file_name}")
            except Exception:
                logging.exception("Exception while parsing file")
        logging.info(f"Finished Sequence creation for {stress_file_name}")
        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"The script execution time in seconds is: {total_time}")
    except CogniteException as exc:
        logging.error(f"Failed to upload {stressFileStream.name}. Error message: {exc}")


if __name__ == "__main__":
    main("/Users/pedrolindeza/Downloads/29001.OUT")
