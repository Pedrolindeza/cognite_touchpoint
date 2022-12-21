import datetime
import logging
import sys
from client_gen import client_gen

sys.path.insert(
    0,
    "/Users/pedrolindeza/repos/Sepals/functions/cognite_metadata_noncritical_loads/non_critical_metadata",
)
from cognite.client import CogniteClient
from cognite.client.exceptions import CogniteAPIError
from util import (
    get_pipe_to_node_df,
    get_branch_name_and_text,
    get_load_df,
)


def main(client: CogniteClient) -> None:
    project = "noafulla"
    e3d_table_name = "e3d_pipe_params"
    metadata_table_name = "pipe_metadata_non_critical"

    db = f"{project}_sepals"

    logging.info("Fetching sequences from CDF")
    e3d_df = client.raw.rows.list(db, e3d_table_name, limit=-1).to_pandas()
    e3d_df = e3d_df.loc[e3d_df["deleted"] != "1"]
    e3d_df = e3d_df.drop_duplicates()

    if e3d_df.empty:
        logging.info(f"No rows found for table: {e3d_table_name} in db: {db}")
    else:
        try:
            column_map = {
                "STRESSNODENR_pjoi": "Caesar Node Number",
                "pipeStatusE3D_pipe": "Pipe Status",
                "projectcode_pipe": "Project Code",
                "NAME_pjoi": "Pipe Support Point",
                "NAME_pipe": "Pipe Name",
                "STRESSNO_pipe": "Pipe Stress Analysis Run Identification",
                "X_pjoi": "X (m)",
                "Y_pjoi": "Y (m)",
                "Z_pjoi": "Z (m)",
                "deleted_pjoi": "isDeleted_pjoi",
                "deleted_pipe": "isDeleted_pipe",
            }
            logging.info("Parsing raw rows for relationships")
            pipe_to_node_df = get_pipe_to_node_df(e3d_df, list(column_map.keys()))
            ref_and_text_df = get_branch_name_and_text(e3d_df, pipe_to_node_df)
            non_critical_loads_df = get_load_df(ref_and_text_df)
            if non_critical_loads_df.empty:
                logging.info("Dataframe is empty no sequence will be created")
            else:
                try:
                    non_critical_loads_df = non_critical_loads_df.rename(
                        columns=column_map
                    )
                    try:
                        tmp_metadata = client.raw.rows.retrieve_dataframe(db_name=db, table_name=metadata_table_name,
                                                                          limit=-1)
                        client.raw.rows.delete(db_name=db, table_name=metadata_table_name, key=list(tmp_metadata.index))
                    except Exception as e:
                        logging.warning(f"Exception while deleting previous metadata table: {e}")
                    client.raw.rows.insert_dataframe(
                        db, metadata_table_name, non_critical_loads_df
                    )
                except CogniteAPIError as e:
                    logging.error(f"Exception while creating sequence in CDF: {e}")
        except Exception:
            logging.exception("Exception occured while creating metadata")
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    logging.info("Python timer trigger function ran at %s", utc_timestamp)


if __name__ == "__main__":
    main(client_gen("test"))
