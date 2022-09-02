import arrow as arrow
from weight_budget.client_gen import client_gen
import pandas as pd

def delete_seq_rel(prefix, client):
    seq = client.sequences.list(external_id_prefix=prefix, limit=None).to_pandas()
    rel = client.relationships.list(limit=None).to_pandas()
    for i, row in seq.iterrows():
        id = row["id"]
        client.sequences.delete(id=id)

    for a, low in rel.iterrows():
        if prefix in low["targetExternalId"]:
            client.relationships.delete(external_id=low["externalId"])

    #client.assets.delete(external_id="noa-fulla-staad-OS-AP500APG038")

def seq_for_amit():
    ids = [
        1287149333386410,
        7823005911720794,
        7460367384177970,
        4128452059777526,
        260961076492924,
        7973159500793864,
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

def delete_old_input_seq(cliente):
    element_types = [
                        "EQUI",
                        "STRU",
                        "PSUP",
                        "CTRAY",
                        "PWEICRIT",
                        "PWEINCRIT",
                    ]
    seq_df =cliente.sequences.list(limit=None).to_pandas()
    vip_seq = []
    for elm in element_types:
        seq_elm = seq_df.loc[seq_df["name"]==f"noafulla-{elm}-sequence"]
        aux2 = seq_elm.copy()  # to avoid warnings
        aux2.loc[:, "createdTime"] = pd.to_datetime(
            aux2.loc[:, "createdTime"], unit="ms"
        )
        aux = aux2.copy()  # to avoid warnings
        aux.sort_values(by="createdTime", inplace=True)
        aux.reset_index(inplace=True)
        for i in range(aux.shape[0]-1):
            delete_seq_rel(aux.loc[i, "externalId"], cliente)
        vip_seq.append(aux.iloc[-1, aux.columns.get_loc("externalId")])

    print(vip_seq)
    rel = cliente.relationships.list(limit=None).to_pandas()
    for i, row in rel.iterrows():
        if "e3d-weightbudget" in row["sourceExternalId"] and row["sourceExternalId"] not in vip_seq:
            cliente.relationships.delete(external_id=row["externalId"])


if __name__ == "__main__":
    delete_old_input_seq(client_gen("test"))
