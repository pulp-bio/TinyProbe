import argparse

#!/usr/bin/env python3

def parse_env_file(env_path):
    env_vars = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                # Remove surrounding quotes if present
                val = val.strip().strip('"').strip("'")
                env_vars[key.strip()] = val
    return env_vars

def write_header_file(header_path, env_vars):
    # Create a unique include guard based on the header filename
    guard = header_path.upper().replace(".", "_").replace("/", "_").replace("\\", "_")
    with open(header_path, "w") as f:
        f.write("/* Auto-generated C header file from .env file */\n")
        f.write("#ifndef {}\n".format(guard))
        f.write("#define {}\n\n".format(guard))
        for key, val in env_vars.items():
            # Emit the value as a string literal
            f.write('#define {} "{}"\n'.format(key, val))
        f.write("\n#endif /* {} */\n".format(guard))
    
    print("Wrote {} environment variables to {}".format(len(env_vars), header_path))
    for key, val in env_vars.items():
        print("  - {}: {}".format(key, val))

def main():
    parser = argparse.ArgumentParser(description="Generate a C header file from a .env file")
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument("header_file", help="Path to the output C header file")
    args = parser.parse_args()

    env_vars = parse_env_file(args.env_file)
    write_header_file(args.header_file, env_vars)

if __name__ == "__main__":
    main()