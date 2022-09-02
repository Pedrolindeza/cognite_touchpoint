import yaml
from cognite.experimental import CogniteClient


def client_gen(env):
    config = read_config(env)
    client = CogniteClient(
        token_url=config["token_url"],
        token_client_id=config["client_id"],
        token_client_secret=config["client_secret"],
        token_scopes=config["token_scopes"],
        project=config["cognite_project"],
        base_url=f"https://{config['cdf_cluster']}.cognitedata.com",
        client_name=config["client_name"],
        debug=False,
    )

    return client


def read_config(env):
    with open(f"/Users/pedrolindeza/.secret/Integral-{env}-client.yaml", "r") as stream:
        config = yaml.load(stream, yaml.SafeLoader)
    return config
