import logging
import time
from client_gen import client_gen
from cognite.client.exceptions import CogniteException
import sys

sys.path.insert(
    0,
    "/Users/pedrolindeza/repos/Sepals/functions/cognite_staad_report_ps/staad_report",
)

from base_case_logic import compare_base_case_and_report, unique_seq_names
from cdf_util import CDFUtil
from report_util import create_report_from_df


def main(client, input_stress=list):
    logging.info("Starting CFAC parser")
    start_time = time.time()
    dataset_id = 5601372144288760
    project = "noafulla"
    metadata_table_name = "pipe_metadata_staad"
    node_name = "staad_PS"

    try:
        cdfutil = CDFUtil(node_name, project, dataset_id, client)
        try:
            e3d_data = cdfutil.get_raw_table(metadata_table_name)
            e3d_data.drop_duplicates(inplace=True)
            e3d_data = e3d_data.loc[e3d_data["IsDeleted"] != "1"]
            for stress_file_name in unique_seq_names(cdfutil):
                print(stress_file_name)
                #if input_stress and stress_file_name not in input_stress:
                #    continue
                ##
                isDeleted = False
                if stress_file_name.startswith("deleted_"):
                    isDeleted = True
                logging.info(f"Retrieveing latest {stress_file_name} from CDF")
                calc_seq, calc_info = cdfutil.retrieve_latest_sequence(
                    stress_file_name, is_base_case=False
                )

                report = create_report_from_df(
                    calc_seq, calc_info, e3d_data, stress_file_name.replace("deleted_", "")
                )

                if not cdfutil.base_case_exists(stress_file_name):
                    logging.info("Creating base case based on input file")
                    if isDeleted:
                        try:
                            report, seq_bc_info = cdfutil.retrieve_latest_sequence(
                                stress_file_name.replace("deleted_", ""), is_base_case=True
                            )
                            cdfutil.delete_seq_rel(
                                f"noafulla_staad_PS_base_case_{stress_file_name.replace('deleted_', '')}")
                        except Exception:
                            logging.warning(f"Could not find {stress_file_name.replace('deleted_', '')} to delete "
                                            f"from CDF")
                            pass
                    try:
                        cdfutil.delete_seq_rel(
                            f"noafulla_staad_PS_base_case_deleted_{stress_file_name}")
                    except Exception as e:
                        logging.warning(f"Could not find {stress_file_name.replace('deleted_', '')} to delete "
                                        f"from CDF")
                    meta_data = cdfutil.create_meta_data(calc_info.id, None)
                    _ = cdfutil.upload_df_as_sequence(
                        report, stress_file_name, meta_data
                    )

                else:
                    if isDeleted:
                        continue
                    base_case, seq_bc_info = cdfutil.retrieve_latest_sequence(
                        stress_file_name, is_base_case=True
                    )

                    logging.info("Starting comparison with existing base case")
                    new_base_case, flag = compare_base_case_and_report(
                        report, base_case
                    )

                    if flag:
                        logging.info(
                            f"Upload report to CDF of len {len(new_base_case)}"
                        )
                        meta_data = cdfutil.create_meta_data(
                            calc_info.id, seq_bc_info.id
                        )
                        _ = cdfutil.upload_df_as_sequence(
                            new_base_case, stress_file_name, meta_data
                        )
                    else:
                        logging.info(f"No changes to file: {stress_file_name}")
            end_time = time.time()
            total_time = end_time - start_time
            logging.info(f"The script execution time in seconds is: {total_time}")
        except Exception:
            logging.exception("Failed to generate Staad PS report")
    except CogniteException as exc:
        logging.error(
            f"Failed to generate new report from: {stress_file_name}. Error message: {exc}"
        )


if __name__ == "__main__":
    client = client_gen("test")
    main(client)
