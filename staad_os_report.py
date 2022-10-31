import logging
import time
import sys

sys.path.insert(
    0, "/Users/pedrolindeza/repos/Sepals/functions/cognite_staad_report_os/report/"
)

from report_util import (
    create_report_from_df,
    create_and_upload_support_reactions,
)
from base_case_logic import compare_base_case_and_report  # unique_stress_runs
import cdf_util as CDFUtil
import base_case_logic as base_case_logic
from client_gen import client_gen
from report_util import create_report_from_df


dataset_id = 5601372144288760  # test
# dataset_id = 106826391582427 # develop
project = "noafulla"
parent_asset = "staad_OS"


def main(env):
    client = client_gen(env)
    start_time = time.time()
    cdf_util = CDFUtil.CDFUtil(parent_asset, project, dataset_id, client)
    e3d_data = cdf_util.get_raw_table("pipe_metadata_staad")
    uniq_seq = base_case_logic.unique_seq_names(cdf_util)

    for stress_file_name in uniq_seq:
        logging.info(f"Retrieveing latest {stress_file_name} from CDF")
        calc_list, calc_info = cdf_util.retrieve_latest_sequence(
            stress_file_name, is_base_case=False
        )

        report = create_report_from_df(calc_list, e3d_data, stress_file_name)
        support_reactions = report["Analysis Condition"].unique()

        if not cdf_util.base_case_exists(stress_file_name):
            metadata = cdf_util.create_meta_data(calc_info.id, None)
            cdf_util.upload_df_as_sequence(report, stress_file_name, metadata)
            logging.info("Creating base case based on input file")
            create_and_upload_support_reactions(
                report, stress_file_name, support_reactions, cdf_util, metadata
            )
        else:
            base_case, seq_bc_info = cdf_util.retrieve_latest_sequence(
                stress_file_name, is_base_case=True
            )

            logging.info("Starting comparison with existing base case")
            new_base_case, flag = compare_base_case_and_report(report, base_case)
            if flag:
                logging.info(f"Upload report to CDF of len {len(new_base_case)}")
                metadata = cdf_util.create_meta_data(calc_info.id, seq_bc_info.id)
                cdf_util.upload_df_as_sequence(
                    new_base_case, stress_file_name, metadata
                )
                create_and_upload_support_reactions(
                    new_base_case,
                    stress_file_name,
                    support_reactions,
                    cdf_util,
                    metadata,
                )

            else:
                logging.info(f"No changes to file: {stress_file_name}")

    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"The script execution time in seconds is: {total_time}")


if __name__ == "__main__":
    main("test")
