import sys
import yaml
from cognite.client import CogniteClient
from cdf_util import CDFUtil
from cdf_fun_wb import CDF_Function_WB
from client_gen import client_gen

sys.path.insert(
    0, "/Users/pedrolindeza/repos/Sepals/functions/cognite_weight_budget/weight_budget"
)


def handle(client: CogniteClient, data):
    with open("env-config.yml", "r") as stream:
        projects = yaml.load(stream, yaml.SafeLoader)

    print("Weight budget calculation started")
    output = {}
    if "projects" not in data:
        print(
            'Input project not specified. Use: \ndata={\n\t"project" = ["project_n1", ...]\n}'
        )
        return SystemExit

    for project in projects["projects"]:
        project = project["project-name"]
        if project not in data["projects"]:
            continue
        cdf_instance = CDFUtil(project, client)
        if "input" in data:
            a = CDF_Function_WB(
                cdf_instance,
                element_types=data["input"]["element_types"],
                internal_ids=data["input"]["internal_ids"],
            )
        else:
            a = CDF_Function_WB(cdf_instance)

        summary, list_seq = a.process_weight_budget()
        for elm in list_seq:
            output[f"{project}_{elm.name.split('_')[1]}_OutID"] = elm.id
        output[f"{project}_SUM_OutID"] = summary.id
        print(f"\tSuccess: Weight budget calculated for {project} \n")
    return output


if __name__ == "__main__":
    data = {
        "projects": ["noafulla"],
        "input": {
            "element_types": [
                "PWEITCRIT",
            ],
            "internal_ids": [],
        },
    }
    handle(client_gen("test"), data)
