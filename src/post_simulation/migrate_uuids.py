import json
import os
import uuid
import pandas as pd


def migrate_uuids():
    # 1. Update agents.csv
    agents_path = "data/processed/agents.csv"
    if os.path.exists(agents_path):
        df_agents = pd.read_csv(agents_path)
        if "agent_uuid" not in df_agents.columns:
            print("Adding agent_uuid column to data/processed/agents.csv...")
            agent_uuids = [
                str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tamaki-agent-{i}"))
                for i in range(len(df_agents))
            ]
            df_agents.insert(0, "agent_uuid", agent_uuids)
            df_agents.to_csv(agents_path, index=False)
            print("Saved updated agents.csv")
        agent_uuids_list = df_agents["agent_uuid"].tolist()
    else:
        print(f"Warning: {agents_path} not found.")
        agent_uuids_list = [
            str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tamaki-agent-{i}")) for i in range(100)
        ]

    # 2. Update existing conf.json files in simulation_results
    sim_res_dir = "simulation_results"
    if not os.path.exists(sim_res_dir):
        print(f"No {sim_res_dir} directory found.")
        return

    migrated_count = 0
    for model_name in os.listdir(sim_res_dir):
        raw_dir = os.path.join(sim_res_dir, model_name, "raw")
        if not os.path.exists(raw_dir) or not os.path.isdir(raw_dir):
            continue

        for folder_name in os.listdir(raw_dir):
            folder_path = os.path.join(raw_dir, folder_name)
            conf_path = os.path.join(folder_path, "conf.json")
            if os.path.isfile(conf_path):
                with open(conf_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except Exception as e:
                        print(f"Error reading {conf_path}: {e}")
                        continue

                updated = False
                if "simulation_uuid" not in data:
                    data["simulation_uuid"] = str(
                        uuid.uuid5(uuid.NAMESPACE_DNS, f"{model_name}-{folder_name}")
                    )
                    updated = True

                sim_id = data.get("simulation_id", 0)
                if isinstance(sim_id, int):
                    agent_idx = sim_id % len(agent_uuids_list)
                    expected_agent_uuid = agent_uuids_list[agent_idx]
                else:
                    expected_agent_uuid = str(
                        uuid.uuid5(uuid.NAMESPACE_DNS, f"tamaki-agent-{sim_id}")
                    )

                if data.get("agent_uuid") != expected_agent_uuid:
                    data["agent_uuid"] = expected_agent_uuid
                    updated = True

                if updated:
                    with open(conf_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                    migrated_count += 1

    print(f"Migration completed. Updated {migrated_count} conf.json files.")


if __name__ == "__main__":
    migrate_uuids()
