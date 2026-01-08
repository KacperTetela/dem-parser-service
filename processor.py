import os
import json
import pandas as pd
from awpy import Demo
from awpy.stats import adr, kast, rating


def process_demo_file(demo_path: str, output_dir: str):
    """
    Parses a CS:GO demo file and saves the analysis results.
    """

    # Initialize the Demo parser
    dem = Demo(demo_path, verbose=False)
    dem.parse()

    data_categories = {
        "header": dem.header,
        "rounds": dem.rounds,
        "kills": dem.kills,
        "damages": dem.damages,
        "shots": dem.shots,
        "bomb": dem.bomb,
        "smokes": dem.smokes,
        "infernos": dem.infernos,
        "grenades": dem.grenades,
        "footsteps": dem.footsteps,
        "ticks": dem.ticks,
        "adr": adr(dem),
        "kast": kast(dem, trade_length_in_seconds=5),
        "rating": rating(dem)
    }

    generated_files = []

    # Ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    for category, data in data_categories.items():
        try:
            file_path = ""

            # Handle Header
            if category == "header":
                file_path = os.path.join(output_dir, f"{category}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                generated_files.append(file_path)

            # Handle DataFrames
            else:
                if data is not None:
                    file_path = os.path.join(output_dir, f"{category}.csv")

                    if hasattr(data, 'to_csv'):
                        data.to_csv(file_path, index=False)
                    elif hasattr(data, 'to_pandas'):
                        data.to_pandas().to_csv(file_path, index=False)
                    else:
                        pd.DataFrame(data).to_csv(file_path, index=False)

                    generated_files.append(file_path)

            if file_path:
                print(f"Category data '{category}' saved to: {file_path}")

        except Exception as e:
            print(f"Error while saving category '{category}': {e}")

    return generated_files
