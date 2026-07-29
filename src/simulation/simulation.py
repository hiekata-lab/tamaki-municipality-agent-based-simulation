import os
import random
import signal
from datetime import datetime, timedelta
from typing import Callable, Any
from lsps import stochastic_process, save_simulation_results, State
import pandas as pd
from immutabledict import ImmutableOrderedDict
import time
from itertools import product
import asyncio
import os
import json
import boto3
from dotenv import load_dotenv
import botocore.exceptions
from src.constants import ACTIVITIES, TRAVEL_MODES

if os.path.exists("secrets.env"):
    load_dotenv("secrets.env")
else:
    raise RuntimeError(
        "Could not find environment variable file secrets.env in the CWD"
    )
if not "AWS_BEARER_TOKEN_BEDROCK" in os.environ.keys():
    raise RuntimeError(
        "Could not find AWS_BEARER_TOKEN_BEDROCK in the environment variables"
    )

# Disable EC2 metadata checks to prevent connection timeout errors when boto3 searches for credentials locally
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

bedrock_client = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

# Set SEED!
random.seed(20011108)

import argparse

parser = argparse.ArgumentParser(
    description="Run the Tamaki Town Agent-Based Simulation"
)
parser.add_argument(
    "--output-dir", type=str, default="simulation_results/raw", help="Output directory"
)
parser.add_argument(
    "--locations",
    type=str,
    default="./locations_graph.json",
    help="Path to locations graph JSON",
)
parser.add_argument(
    "--agents", type=str, default="./agents.csv", help="Path to agents CSV"
)
parser.add_argument(
    "--temperature", type=float, default=0.0, help="Temperature for inference"
)
parser.add_argument(
    "--model-id", type=str, default="minimax.minimax-m2.5", help="Model ID"
)
parser.add_argument(
    "--transitions", type=int, default=100, help="Number of transitions to simulate"
)

args, _ = parser.parse_known_args()

print("Loading simulation data...")

# Agents visitable locations
locations_path = args.locations
with open(locations_path, "r", encoding="utf-8") as f:
    LOCATIONS = json.load(f)

# Agents dataframe
agents_path = args.agents
AGENTS_DF = pd.read_csv(agents_path)

print("Done!")

# MARK: LSPS Helper Functions
# Functions that provide utility to the LSPS prompt arguments and state attributes

ARRIVING = ["Arriving"]

DATE_FORMAT: str = "%Y-%m-%d %H.%M"


def add_minutes_to_time(t: str, minutes: int) -> str:
    current_time = datetime.strptime(t, DATE_FORMAT)
    return (current_time + timedelta(minutes=minutes)).strftime(DATE_FORMAT)


def starting_time(history: list[State]) -> JsonValue:
    last_state = history[-1]
    tm1_act = last_state["activity"]
    timestamp = last_state["starting_time"]

    match tm1_act:
        case "Arriving":
            tm2_act = history[-2]["activity"]
            tm2_loc = history[-2]["location"]
            tm1_loc = last_state["location"]
            # The closest locations from the starting point of the travel activity
            closest_list = LOCATIONS[tm2_loc]["closest_locations"]
            # Find the first closest location that matches the arrival location
            dist = next(
                loc["distance"] for loc in closest_list if loc["name"] == tm1_loc
            )
            # Calculate the travel time by dist (km) / speed (km/h) * 60 = minutes
            travel_time = (dist / TRAVEL_MODES[tm2_act]["speed"]) * 60
            return add_minutes_to_time(timestamp, travel_time)

        case _:
            duration = ACTIVITIES[tm1_act]["duration"]
            return add_minutes_to_time(timestamp, duration)


def location(history: list[State]) -> list[JsonValue]:
    tm1_state = history[-1]
    match tm1_state["activity"]:
        case a if a in TRAVEL_MODES:
            closest = LOCATIONS[tm1_state["location"]]["closest_locations"]
            return [loc["name"] for loc in closest]
        case _:
            return [tm1_state["location"]]


def activity(history: list[State]) -> list[JsonValue]:
    tm1_state = history[-1]
    match tm1_state["activity"]:
        case a if a in TRAVEL_MODES:
            return ARRIVING
        case _:
            tm1_loc = tm1_state["location"]
            tm1_loc_types = LOCATIONS[tm1_loc]["type"]
            loc_activities = list(
                {
                    act
                    for t in tm1_loc_types
                    for act, act_data in ACTIVITIES.items()
                    if act_data["available_in"] and t in act_data["available_in"]
                }
            )
            return loc_activities + list(TRAVEL_MODES.keys())


def location_distances(history: list[State]) -> JsonValue:
    tm1_loc = history[-1]["location"]
    closest = LOCATIONS[tm1_loc]["closest_locations"]
    return "\n".join(f"to {loc['name']} its {loc['distance']:.2f}km" for loc in closest)


# MARK: LSPS LLMServerPost
INFERENCE_PARAMETERS = {"temperature": args.temperature}

ADDITIONAL_MODEL_REQUEST_FIELDS = {}

MODEL_ID = args.model_id


def amz_bedrock_runtime_post(prompt: str, response_format: dict[str, Any]) -> str:
    # Extract system and user prompt from the single prompt string,
    # the LSPS module is built around the raw-prompt since it does
    # not use any chat-bot prompt formatting (since its not a chat-bot)
    parts = prompt.split("<|user|>")
    system_prompt = (
        parts[0]
        .replace("<|system|>", "")
        .replace("[gMASK]", "")
        .replace("<sop>", "")
        .strip()
    )
    clean_prompt = (
        parts[1]
        .replace("<|assistant|>", "")
        .replace("[gMASK]", "")
        .replace("<think>", "")
        .replace("<|user|>", "")
        .replace("<sop>", "")
        .replace("<eop>", "")
        .strip()
    )

    system_prompt_parameter = [{"text": system_prompt}]
    messages_parameter = [{"role": "user", "content": [{"text": clean_prompt}]}]

    # Inference configuration
    inference_configuration_parameter = INFERENCE_PARAMETERS

    # Additional model request fields
    additional_model_request_fields = {
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "dynamic_response_format",
                "schema": response_format,
            },
        },
    } | ADDITIONAL_MODEL_REQUEST_FIELDS

    # Get response with exponential backoff
    wait_time = 1.0
    max_wait = 600.0

    while True:
        try:
            constrained_response = bedrock_client.converse(
                modelId=MODEL_ID,
                messages=messages_parameter,
                system=system_prompt_parameter,
                inferenceConfig=inference_configuration_parameter,
                additionalModelRequestFields=additional_model_request_fields,
            )
            return constrained_response["output"]["message"]["content"][-1]["text"]
        except (
            botocore.exceptions.ConnectionError,
            botocore.exceptions.EndpointConnectionError,
            botocore.exceptions.ReadTimeoutError,
            botocore.exceptions.ConnectTimeoutError,
            botocore.exceptions.ConnectionClosedError,
            botocore.exceptions.ProxyConnectionError,
            botocore.exceptions.SSLError,
            botocore.exceptions.ClientError,
            ConnectionError,
            TimeoutError,
        ) as e:
            # Add some jitter to not cluster retries
            sleep_time = wait_time * random.uniform(0.8, 1.2)
            print(
                f"API request failed with error {e}, retrying in {sleep_time:.2f}s..."
            )
            time.sleep(sleep_time)
            wait_time = min(wait_time * 2, max_wait)


# MARK: LSPS Simulation

ACTIVITY_TIMES_STR = "\n".join(
    [
        f"- {k}: {v['duration']} minutes"
        for k, v in ACTIVITIES.items()
        if isinstance(v, dict)
    ]
)

PROMPT_TEMPLATE = f"""[gMASK]<sop><|system|>
<INSTRUCTIONS>
You are an agent simulating the life of a human persona. You simulate the persona's life through generating new states that extend a sequence of states. The sequence of states represents the persona's activities, location, memories and reasoning at some point in time. The current sequence of states is defined under the <STATE_SEQUENCE> label. Your response, referred to as "the next state" from now on, will be appended to this sequence. The next state should be realistic for a human and reflect real world behavior, be consistent with your memory from the preceding states, and your persona defined under the <PERSONA> label.

<RESPONSE_FORMAT>
The next state should be a valid JSON object that follows the JSON schema defined under the <SCHEMA> label. More information about what to write under each JSON object property can be found under the <MEMORY_ATTRIBUTE>, <REASONING_ATTRIBUTE>, <LOCATION_ATTRIBUTE>, <ACTIVITY_ATTRIBUTE> labels.

<MEMORY_ATTRIBUTE>
The memory attribute, `memory`, serves as a way for you to maintain a long term memory of opinions, plans, ideas, schedules or anything else you deem to be important to remember in the next states. The memory attribute should be actively managed. This means you should not keep every action and location visited in your memory. You should actively select and summarize the important factors of the persona's simulated life and place these in the memory attribute. The memory attribute has a (soft) max number of sentences allowed at 20 sentences. You should include timestamps when writing to the memory attribute. 

<REASONING_ATTRIBUTE>
The reasoning attribute, `reasoning`, serves as a way for you to plan and reason on what to write in the other attributes of the next state.

<LOCATION_ATTRIBUTE>
The location attribute, `location`, stores your location during the timespan of the state. The only way to change this attribute value in the next state is if you selected one of the transportation mode activities, that are defined under <TRANSPORTATION_MODES>, as the `activity` attribute in the preceding state.

<ACTIVITY_ATTRIBUTE>
The activity attribute, `activity`, stores your activity during the timespan of a state. As stated under <INSTRUCTIONS> you need to select activities that are consistent with your persona, memories and preceding states.

<TIME_ATTRIBUTE>
The starting time attribute, `starting_time`, stores the starting time of a state and is dependent on the, fixed, duration of the activity of the preceding state. These fixed durations can be found under the label <ACTIVITY_TIMES>. The duration of a state is the difference in time between the starting time attribute of the preceding state and the starting time attribute of the next state. 
<|user|>

<ACTIVITY_TIMES>
{ACTIVITY_TIMES_STR}

<TRANSPORTATION_MODES>
- Driving car or Riding car: costs 30 JPY per km.
- Riding bus: costs 20 JPY per km.
- Riding bike: costs nothing.
- Walking: costs nothing.
- {{mod_policy}}.

<PERSONA>
- Nationality: {{nationality}},
- Regionality: {{regionality}},
- Town: {{town}},
- Home: {{home}},
- Age: {{age}},
- Health: {{health}},
- Working: {{working}},

<SCHEMA>
{{response_schema}}

<KNOWN_LOCATIONS>
{{location_distances}}

<STATE_SEQUENCE>
{{state_history}}
<|assistant|>
"""

MOD_POLICIES = [
    "Mobility-on-demand shuttle: not available",
    "Mobility-on-demand shuttle: is Free when traveling within Tamaki-town",
    "Mobility-on-demand shuttle: costs 400 yen fixed when traveling within Tamaki-town",
    "Mobility-on-demand shuttle: costs 800 yen fixed when traveling within Tamaki-town",
]

TRANSITIONS = args.transitions

AGENTS = [ImmutableOrderedDict(row.to_dict()) for _, row in AGENTS_DF.iterrows()]

AGENT_SCENARIO_PAIRS = list(product(AGENTS, MOD_POLICIES))


def run_single_simulation(
    sim_id: int,
    agent: State,
    mod_policy: str,
    llm_server_post: Callable[[str, dict[str, Any]], str],
) -> None:
    START_TIME = datetime.now()
    agent = dict(agent)
    agent["mod_policy"] = mod_policy

    prompt_arguments = [
        ("location_distances", location_distances),
        ("state_history", lambda s: ",\n".join(str(dict(x)) for x in s[-5:])),
        ("mod_policy", lambda _: agent["mod_policy"]),
        ("nationality", lambda _: agent["nationality"]),
        ("regionality", lambda _: agent["regionality"]),
        ("town", lambda _: agent["town"]),
        ("age", lambda _: agent["age"]),
        ("working", lambda _: agent["working"]),
        ("health", lambda _: agent["health"]),
        ("home", lambda _: agent["home"]),
    ]

    state_attributes = [
        ("reasoning", lambda s: {"type": "string"}),
        ("memory", lambda _: {"type": "string"}),
        ("starting_time", lambda s: {"type": "string", "const": starting_time(s)}),
        ("location", lambda s: {"type": "string", "enum": location(s)}),
        ("activity", lambda s: {"type": "string", "enum": activity(s)}),
    ]

    genesis_state = [
        ImmutableOrderedDict(
            {
                "reasoning": "Since i just woke up and im feeling kind of hungry i should get up from bed and eat breakfast.",
                "memory": "I remember waking up from a good nights sleep at 2026-06-10 08.00 feeling kind of hungry.",
                "starting_time": "2026-06-10 08.00",
                "location": agent["home"],
                "activity": "Rest and relaxation",
            }
        )
    ]

    results = stochastic_process(
        sim_id,
        TRANSITIONS,
        state_attributes,
        genesis_state,
        PROMPT_TEMPLATE,
        prompt_arguments,
        llm_server_post,
    )

    save_simulation_results(
        results,
        START_TIME,
        sim_id,
        TRANSITIONS,
        PROMPT_TEMPLATE,
        state_attributes,
        prompt_arguments,
        llm_server_post,
        dir=args.output_dir,
        extra_config={
            "agent_params": agent,
            "inference_parameters": INFERENCE_PARAMETERS,
            "additional_model_request_fields": ADDITIONAL_MODEL_REQUEST_FIELDS
            | {"model": MODEL_ID},
        },
    )


async def process_all():
    print(f"Sending all {len(AGENT_SCENARIO_PAIRS)} requests...")
    tasks = [
        asyncio.to_thread(
            run_single_simulation,
            i,
            agent,
            mod_policy,
            amz_bedrock_runtime_post,
        )
        for i, (agent, mod_policy) in enumerate(AGENT_SCENARIO_PAIRS)
    ]
    await asyncio.gather(*tasks)
    print("Finished batch!")


if __name__ == "__main__":
    # Ignore keyboard interrupt
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    asyncio.run(process_all())
