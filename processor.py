import os
import json
import pandas as pd
from awpy import Demo

def process_demo_file(demo_path: str, output_dir: str):
    """
    Parses a CS:GO demo file and saves the analysis results (headers, kills, rounds, etc.)
    to the specified output directory.
    """
    
    # Initialize the Demo parser
    # verbose=False because we don't want to spam the server logs too much
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
    }

    generated_files = []

    # Ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    for category, data in data_categories.items():
        try:
            # Handle Header (which is a dict usually)
            if category == "header":
                file_path = os.path.join(output_dir, f"{category}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                generated_files.append(file_path)
            
            # Handle DataFrames
            else:
                # awpy properties usually return DataFrames, but sometimes None if empty
                if data is not None:
                    file_path = os.path.join(output_dir, f"{category}.csv")
                    # If it's already a dataframe, save it
                    if hasattr(data, 'to_csv'):
                         data.to_csv(file_path, index=False)
                    # Use awpy to_pandas() helper if it's a specific object type that requires it
                    # (In recent awpy versions, properties like dem.kills ARE DataFrames, but the user code used .to_pandas() on data)
                    # We will try both or stick to user's pattern if applicable. 
                    # User's code: data.to_pandas().to_csv(...)
                    # However, modern awpy usually returns DFs directly. I'll implement a safe check.
                    elif hasattr(data, 'to_pandas'):
                        data.to_pandas().to_csv(file_path, index=False)
                    else:
                        # Fallback for dicts or other types
                        pd.DataFrame(data).to_csv(file_path, index=False)
                        
                    generated_files.append(file_path)

            print(f"Category data '{category}' saved to: {file_path}")
            
        except Exception as e:
            print(f"Error while saving category '{category}': {e}")
            
    return generated_files
