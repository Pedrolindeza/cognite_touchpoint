import logging
import os, sys
import time
import azure.functions as func
from cognite.client import CogniteClient
from client_gen import client_gen

sys.path.insert(
    0,
    "/Users/pedrolindeza/Repos/Sepals/functions/cognite_caesar_report_critical/caesar_cfac",
)

from contingency_factor_logic import compare_base_case_and_report
from cdf_util import (
    CDFUtil,
)
from contingency_factor_util import (
    unique_seq_names,
    create_joint_report_from_e3d_matches,
    get_report_w_cfac,
    get_metadata,
)


def main(client: CogniteClient, nodes=[]):
    logging.info("Starting CFAC parser")
    start_time = time.time()
    dataset_id = 5601372144288760
    project = "noafulla"
    cfac_table_name = "pipe_cfac"
    metadata_table_name = "pipe_metadata_critical"
    node_name = "caesar_critical_loads"

    try:
        cdfutil = CDFUtil(node_name, project, dataset_id, client)
        cfac_df = cdfutil.get_raw_table(cfac_table_name)
        e3d_data = cdfutil.get_raw_table(metadata_table_name)
        e3d_data = cdfutil.modify_psp_names(e3d_data)
        node_seqs = cdfutil.list_sequences_for_node()
        for seq_name in unique_seq_names(node_seqs):
            print(seq_name)
            if len(nodes) > 0:
                if seq_name not in nodes:
                    continue
            try:
                logging.info(f"Retrieveing latest {seq_name} from CDF")
                calc_df, calc_seq = cdfutil.retrieve_latest_sequence(
                    seq_name, is_base_case=False
                )

                report_extended = create_joint_report_from_e3d_matches(
                    calc_df, e3d_data, seq_name
                )
                final_report = get_report_w_cfac(report_extended, cfac_df)
                if not cdfutil.base_case_exists(seq_name):
                    logging.info("Creating base case based on input file")
                    metadata = get_metadata(calc_seq.id, None)
                    cdfutil.upload_df_as_sequence(final_report, seq_name, metadata)
                else:
                    base_case, seq_bc_info = cdfutil.retrieve_latest_sequence(
                        seq_name, is_base_case=True
                    )
                    logging.info("Starting comparison with existing base case")
                    base_case, flag = compare_base_case_and_report(
                        final_report, base_case, cfac_df
                    )
                    if flag:
                        logging.info("Upload report to CDF")
                        metadata = get_metadata(calc_seq.id, seq_bc_info.id)
                        cdfutil.upload_df_as_sequence(base_case, seq_name, metadata)
                    else:
                        logging.info(f"No changes to file: {seq_name}")
            except Exception as exc:
                logging.exception(f"Failed to process: {seq_name}  due to {exc}")
        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"The script execution time in seconds is: {total_time}")
    except Exception:
        logging.exception("Exception while parsing file")


if __name__ == "__main__":
    main(client_gen("test"))
