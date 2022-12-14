import uuid
import arrow as arrow
from client_gen import client_gen
from cognite.client import CogniteClient
from cognite.client.data_classes import (
    Asset,
    Relationship,
    Sequence,
    SequenceUpdate,
)
import pandas as pd


def delete_seq_rel(prefix, client: CogniteClient):
    seq = client.sequences.list(external_id_prefix=prefix, limit=None).to_pandas()
    rel = client.relationships.list(limit=None).to_pandas()
    for i, row in seq.iterrows():
        id = row["id"]
        client.sequences.delete(id=id)

    for a, low in rel.iterrows():
        if prefix in low["targetExternalId"]:
            client.relationships.delete(external_id=low["externalId"])


def seq_for_amit():
    ids = [
        7658022579365504
    ]

    list_seq = client_gen("test").sequences.list(limit=None).to_pandas()

    for i, seq in list_seq.iterrows():
        if seq["id"] in ids:
            client_gen("test").sequences.data.retrieve_dataframe(
                id=seq["id"], start=0, end=None
            ).to_excel(
                "./amit_excel/"
                + seq["name"]
                + "_"
                + str(arrow.get(seq["createdTime"]))
                + ".xlsx"
            )


def delete_old_input_wtb(client: CogniteClient):
    element_types = [
        "EQUI",
        "STRU",
        "PSUP",
        "CTRAY",
        "PWEICRIT",
        "PWEINCRIT",
    ]
    seq_df = client.sequences.list(limit=None).to_pandas()
    vip_seq = []
    for elm in element_types:
        seq_elm = seq_df.loc[seq_df["name"] == f"noafulla-{elm}-sequence"]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        for i in range(aux.shape[0] - 1):
            delete_seq_rel(aux.loc[i, "externalId"], client)
        vip_seq.append(aux.iloc[-1, aux.columns.get_loc("externalId")])

    print(vip_seq)
    rel = client.relationships.list(limit=None).to_pandas()
    for i, row in rel.iterrows():
        if (
            "e3d-weightbudget" in row["sourceExternalId"]
            and row["sourceExternalId"] not in vip_seq
        ):
            client.relationships.delete(external_id=row["externalId"])


def delete_old_output_wtb(client: CogniteClient):
    element_types = [
        "EQUI",
        "STRU",
        "PSUP",
        "CTRAY",
        "PWEICRIT",
        "PWEINCRIT",
    ]
    seq_df = client.sequences.list(limit=None).to_pandas()
    vip_seq = []
    for elm in element_types:
        seq_elm = seq_df.loc[seq_df["name"] == f"noafulla_{elm}_output"]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        for i in range(aux.shape[0] - 1):
            delete_seq_rel(aux.loc[i, "externalId"], client)
        vip_seq.append(aux.iloc[-1, aux.columns.get_loc("externalId")])

    print(vip_seq)


def delete_old_input_OS(client: CogniteClient):
    element_types = client.assets.list(
        parent_external_ids=["noafulla_staad_OS"], limit=None
    ).to_pandas()
    seq_df = client.sequences.list(
        limit=None, external_id_prefix="noafulla_staad_OS_"
    ).to_pandas()
    rel_df = client.relationships.list(limit=None).to_pandas()
    vip_seq = []
    for elm in element_types["name"]:
        seq_elm = seq_df.loc[seq_df["name"] == elm]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        for i in range(aux.shape[0] - 1):
            client.sequences.delete(external_id=aux.loc[i, "externalId"])
            for a, low in rel_df.iterrows():
                if aux.loc[i, "externalId"] in low["targetExternalId"]:
                    client.relationships.delete(external_id=low["externalId"])
        vip_seq.append(aux.iloc[-1, aux.columns.get_loc("externalId")])

        seq_elm = seq_df.loc[seq_df["name"] == f"calc_{elm}"]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        for i in range(aux.shape[0] - 1):
            client.sequences.delete(external_id=aux.loc[i, "externalId"])
            for a, low in rel_df.iterrows():
                if aux.loc[i, "externalId"] in low["targetExternalId"]:
                    client.relationships.delete(external_id=low["externalId"])
        vip_seq.append(aux.iloc[-1, aux.columns.get_loc("externalId")])

    print(vip_seq)


def delete_old_input_PS(client: CogniteClient):
    element_types = client.assets.list(
        parent_external_ids=["noafulla_staad_PS"], limit=None
    ).to_pandas()
    seq_df = client.sequences.list(
        limit=None, external_id_prefix="noafulla_staad_PS_"
    ).to_pandas()
    rel_df = client.relationships.list(limit=None).to_pandas()
    vip_seq = []
    for elm in element_types["name"]:
        print(elm)
        seq_elm = seq_df.loc[seq_df["name"] == elm]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        for i in range(aux.shape[0] - 1):
            client.sequences.delete(external_id=aux.loc[i, "externalId"])
            for a, low in rel_df.iterrows():
                if aux.loc[i, "externalId"] in low["targetExternalId"]:
                    client.relationships.delete(external_id=low["externalId"])

        seq_elm = seq_df.loc[seq_df["name"] == f"calc_{elm}"]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        for i in range(aux.shape[0] - 1):
            client.sequences.delete(external_id=aux.loc[i, "externalId"])
            for a, low in rel_df.iterrows():
                if aux.loc[i, "externalId"] in low["targetExternalId"]:
                    client.relationships.delete(external_id=low["externalId"])


def delete_old_input_critical(client: CogniteClient):
    element_types = client.assets.list(
        parent_external_ids=["noafulla_caesar_critical_loads"], limit=None
    ).to_pandas()
    seq_df = client.sequences.list(
        limit=None, external_id_prefix="noafulla_caesar_critical_loads_"
    ).to_pandas()
    vip_seq = []
    for elm in element_types["name"]:
        print(elm)
        seq_elm = seq_df.loc[seq_df["name"] == elm]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        if aux.shape[0] > 0:
            for i in range(aux.shape[0] - 1):
                delete_seq_rel(aux.loc[i, "externalId"], client)

        seq_elm = seq_df.loc[seq_df["name"] == f"calc_{elm}"]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        if aux.shape[0] > 0:
            for i in range(aux.shape[0] - 1):
                delete_seq_rel(aux.loc[i, "externalId"], client)

        seq_elm = seq_df.loc[seq_df["name"] == f"cfac_{elm}"]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        if aux.shape[0] > 0:
            for i in range(aux.shape[0] - 1):
                delete_seq_rel(aux.loc[i, "externalId"], client)

    print(vip_seq)


def delete_recent_input(client, prefix):
    seq_df = client.sequences.list(limit=None, external_id_prefix=prefix).to_pandas()
    aux2 = seq_df.copy()  # to avoid warnings
    aux2.loc[:, "createdTime"] = pd.to_datetime(aux2.loc[:, "createdTime"], unit="ms")
    aux = aux2.copy()  # to avoid warnings
    aux.sort_values(by="createdTime", inplace=True, ascending=False)
    aux.reset_index(inplace=True)
    for i in range(aux.shape[0] - 1):
        delete_seq_rel(aux.loc[i, "externalId"], client)

def delete_old_wtb_sum(client):
    seq_df = client.sequences.list(limit=None, external_id_prefix="noafulla_SUMMARY").to_pandas()
    aux2 = seq_df.copy()  # to avoid warnings
    aux2.loc[:, "createdTime"] = pd.to_datetime(aux2.loc[:, "createdTime"], unit="ms")
    aux = aux2.copy()  # to avoid warnings
    aux.sort_values(by="createdTime", inplace=True, ascending=True)
    aux.reset_index(inplace=True)
    for i in range(aux.shape[0] - 1):
        delete_seq_rel(aux.loc[i, "externalId"], client)


if __name__ == "__main__":
    client = client_gen("test")
    delete_seq_rel("noafulla_caesar_critical_loads_base_case_29001_d7796bf9-cf11-48ae-928e-c6e9daf0bf1d", client)

