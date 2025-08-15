import os
import json
import argparse
import os, json, math

IMG_W, IMG_H = 1280, 720    

#renames json file data  to quaternion xyzw 
#deletes any file that is not completely visible at frame 

def clean_dataset(folder):
    for fname in os.listdir(folder):
        if not fname.endswith(".json"):
            continue
        jpath = os.path.join(folder, fname)
        ipath = jpath.replace(".json", ".png")

        with open(jpath) as f:
            data = json.load(f)

        bad, changed = False, False
        for obj in data.get("objects", []):
            # renombrar quaternion si existe
            if "quaternion_wxyz" in obj:
                obj["quaternion_xyzw"] = obj.pop("quaternion_wxyz")
                changed = True

            cuboid = obj.get("projected_cuboid", [])
            if len(cuboid) < 8:
                bad = True; break
            for x, y in cuboid:
                print("Checking:", x, y)
                if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                    bad = True
                    print("Invalid type")
                    break
                if (
                    x < 0 or x > IMG_W or
                    y < 0 or y > IMG_H or
                    math.isnan(x) or math.isnan(y)
                ):
                    bad = True
                    print("Out of bounds or NaN")
                    break


        if bad:
            os.remove(jpath)
            if os.path.exists(ipath):
                os.remove(ipath)
            print("Deleted:", fname)
        elif changed:
            with open(jpath, "w") as f:
                json.dump(data, f, indent=2)
            print("Fixed quat:", fname)
        else:
            print("OK:", fname)






# Argumento solo para el folder de entrada
parser = argparse.ArgumentParser("Rename Quaternion Field in JSONs")
parser.add_argument("--data_dir", type=str, default=os.getcwd() + "/_palletjack_data", help="Input folder with JSON files")
args, _ = parser.parse_known_args()

clean_dataset(args.data_dir)



'''
def rename_quaternion_field_in_jsons(input_folder):
    # Crear un nuevo directorio de salida automáticamente
    output_folder = input_folder.rstrip("/") + "_modified"
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with open(input_path, 'r') as f:
                data = json.load(f)

            changed = False
            for obj in data.get("objects", []):
                if "quaternion_wxyz" in obj:
                    obj["quaternion_xyzw"] = obj.pop("quaternion_wxyz")
                    changed = True

            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)

            if changed:
                print(f"Modified: {filename}")
            else:
                print(f"Not Modified: {filename}")

    print(f"\n Modified files saved in : {output_folder}")


# Argumento solo para el folder de entrada
parser = argparse.ArgumentParser("Rename Quaternion Field in JSONs")
parser.add_argument("--data_dir", type=str, default=os.getcwd() + "/_palletjack_data", help="Input folder with JSON files")
args, _ = parser.parse_known_args()

rename_quaternion_field_in_jsons(args.data_dir)
'''