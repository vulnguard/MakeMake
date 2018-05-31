import sys # For command line args
import os  # For file enumeration


# ========== Self Defined Errors ============
class InvalidFileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)

# ===== Valid Configuration File Flags ======
VALID_CONFIG_FLAGS = {":ENVIRONMENT:" : ":END_ENVIRONMENT:", ":VARS:" : ":END_VARS:" , ":TESTS:" : ":END_TESTS:", ":ALLWAYS:" : ":END_ALLWAYS:"}

# ============= Main Program ================

# Command line arguments: (Will override defaults, and everything in config file)
# --root-dir
# --src-dir
# --config-file
# --output-name
#DEFAULT_CONFIG_FILE_NAME = "smol.cfg"
DEFAULT_CONFIG_FILE_NAME = "MakeMakeConfig.cfg"

def main():
    print("Running MakeMake...")

    config_file_name = DEFAULT_CONFIG_FILE_NAME

    # @TODO be more robust in parsing command line args, and parse the rest too.
    # (Right now we're just checking that the first arg is the config file name)
    if len(sys.argv) == 1 or sys.argv[1].startswith("-"):
        print("Using default config file.")
    else:
        config_file_name = sys.argv[1]

    print("Attempting to parse config file '{}'...".format(config_file_name))

    config, using_default = parse_config_file(config_file_name)

    if using_default:
        # Use all defaults.
        print("Creating default makefile...")
    else:
        # Use the config.
        print("Creating makefile based on config file...")

    discover_makefile_rules(config)

    # create_makefile(config)

    return 0

# ======== Makefile Rule Creation  =========
def discover_makefile_rules(config):
    source_dir = config[":ENVIRONMENT:"]["PROJ_SOURCE_DIR"]

    for file in os.listdir(source_dir):
        print(file)


# ====== Makefile Creation Functions =======
def create_makefile(config):
    makefile_path = config[":ENVIRONMENT:"]["PROJ_ROOT_DIR"] + "/" + config[":ENVIRONMENT:"]["MAKEFILE_NAME"]
    with open(makefile_path, "w") as makefile:
        makefile.write("# This file was auto-generated by MakeMake.py\n")

        write_makefile_vars(makefile, config[":VARS:"])

        write_makefile_rules(makefile, config[":RULES:"])

        write_makefile_tests(makefile, config[":TESTS:"])

        # Write the rest of the makefile.
        makefile.write(config[":ALLWAYS:"] + "\n")


def write_makefile_vars(makefile, make_vars):
    makefile.write("CC=" + make_vars["CC"] + "\n")
    makefile.write("CFLAGS=" + make_vars["CFLAGS"] + "\n" + "\n")

    makefile.write("EXE_DIR=" + make_vars["EXE_DIR"] + "\n")
    makefile.write("TEST_DIR=" + make_vars["TEST_DIR"] + "\n")
    makefile.write("OBJ_DIR=" + make_vars["OBJ_DIR"] + "\n" + "\n")

    makefile.write("EXE_NAME=" + make_vars["EXE_NAME"] + "\n" + "\n")

    makefile.write("INCLUDE_DIRS=" + make_vars["INCLUDE_DIRS"] + "\n" + "\n")

    makefile.write("LIB_DIRS=" + make_vars["LIB_DIRS"] + "\n")
    makefile.write("LINK_COMMANDS=" + make_vars["LINK_COMMANDS"] + "\n" + "\n")

    makefile.write("COMPILE_WITH_CFLAGS=" + make_vars["COMPILE_WITH_CFLAGS"] + "\n")
    makefile.write("COMPILE_WITH_INCLUDES=" + make_vars["COMPILE_WITH_INCLUDES"] + "\n")

    makefile.write("OBJ_FILES=" + make_vars["OBJ_FILES"] + "\n" + "\n")


def write_makefile_rules(makefile, make_rules):
    pass


def write_makefile_tests(makefile, make_tests):
    pass

# ======= Config Parsing Functions =========

# Returns: config, using_defaults
#            dict, bool
def parse_config_file(config_file_name):
    config = get_default_config()
    using_default = False

    try:
        contents = []
        with open(config_file_name, "r") as f:
            for line in f:
                contents.append(line.strip("\n"))

        if len(contents) == 0:
            print("Warning: config file is empty.")
            using_default = True
            return config, using_default

        curr_line_number = 0
        flag_line_number = 0
        exit_flag_line_number = 0

        while(curr_line_number < len(contents)):
            # Ignore blank lines because they are not inside a flag block.
            curr_line_number = eat_empty_lines(contents, curr_line_number)
            curr_line = contents[curr_line_number]

            # Ignore all lines starting with a '#' outside of flag blocks.
            if curr_line.startswith('#'):
                curr_line_number += 1
                continue

            # Check if the flag is valid.
            if curr_line not in VALID_CONFIG_FLAGS.keys():
                msg = "Config file has incorrect format. Flag '{}' is invalid. (Or text outside of flag block).".format(curr_line)
                raise InvalidFileFormatError(msg)
            else:
                flag_line_number = curr_line_number
                exit_flag_line_number = find_exit_flag(contents, curr_line_number, VALID_CONFIG_FLAGS[curr_line])

                if not exit_flag_line_number:
                    msg = "Config file has incorrect format. Flag '{}' has no exit flag ('{}').".format(curr_line, VALID_CONFIG_FLAGS[curr_line])
                    raise InvalidFileFormatError(msg)

                parse_flag_contents(config, contents, flag_line_number, exit_flag_line_number)
                curr_line_number = exit_flag_line_number + 1

    except FileNotFoundError as e:
        print("\tConfig file '{}' not found.".format(config_file_name))
        using_default = True

    except IsADirectoryError as e:
        print("\tGiven config file '{}' is a directory!".format(config_file_name))
        using_default = True

    except InvalidFileFormatError as e:
        print("\t", e, sep="")
        using_default = True

        # Since the file didn't parse correctly, set the config back to defaults.
        config = get_default_config()

    return config, using_default


def eat_empty_lines(contents, curr_line_number):
    while(curr_line_number < len(contents) and len(contents[curr_line_number]) == 0):
        curr_line_number += 1

    return curr_line_number


def find_exit_flag(contents, curr_line_number, exit_flag):
    while curr_line_number < len(contents) - 1 and not contents[curr_line_number] == exit_flag:
        curr_line_number += 1

    if contents[curr_line_number] == exit_flag:
        return curr_line_number
    else:
        return None


def get_default_config():
    config = {}

    # Set up environment variables.
    env_vars = {}

    env_vars["PROJ_ROOT_DIR"] = "."
    env_vars["PROJ_SOURCE_DIR"]  = env_vars["PROJ_ROOT_DIR"] + "/src"

    env_vars["MAKEFILE_NAME"] = "Makefile"

    config[":ENVIRONMENT:"] = env_vars

    # Set up makefile variables.
    makefile_vars = {}
    makefile_vars["CC"] = "g++"
    makefile_vars["CFLAGS"] = "-std=c++11 -Wall -pedantic -g -ggdb -c"

    makefile_vars["EXE_DIR"] = "bin"
    makefile_vars["TEST_DIR"] = "bin/tests"
    makefile_vars["OBJ_DIR"] = "bin/obj"

    makefile_vars["EXE_NAME"] = "program"

    makefile_vars["INCLUDE_DIRS"] = " # Empty"   # Empty until we look through the files.

    makefile_vars["LIB_DIRS"] = " # Empty"       # Empty until we look through the files.
    makefile_vars["LINK_COMMANDS"] = " # Empty"  # Empty until we look through the files.

    makefile_vars["COMPILE_WITH_CFLAGS"] = "$(CC) $(CFLAGS)"
    makefile_vars["COMPILE_WITH_INCLUDES"] = "$(CC) $(CFLAGS) $(INCLUDE_DIRS)"

    makefile_vars["OBJ_FILES"] = " # Empty"      # Empty until we look through the files.

    config[":VARS:"] = makefile_vars

    # Set up test cases. (Empty unless user specifies).
    tests = {}

    config[":TESTS:"] = tests

    # Set up rules. (Empty until we look through the files).
    rules = {}

    config[":RULES:"] = rules

    # Set up 'allways' makefile code.
    allways = """
# Run stuff
.PHONY: run
run:
	./$(EXE_DIR)/$(EXE_NAME)

.PHONY: runVal
runVal:
	valgrind ./$(EXE_DIR)/$(EXE_NAME)


# Clean
.PHONY: clean
clean:
	rm -rf $(OBJ_DIR)/*.o $(EXE_DIR)/$(EXE_NAME) $(EXE_DIR)/*.dll $(TEST_DIR)/* *~*


# Memes
.PHONY: urn
urn:
	@echo "You don't know how to make an urn."


.PHONY: rum
rum:
	@echo "Why is the rum gone?!"


.PHONY: ruin
ruin:
	@echo "You ruined it! :("


.PHONY: riun
riun:
	@echo "Dam dude... can't even ruin it right. :\\"
    """

    config[":ALLWAYS:"] = allways

    return config


def parse_flag_contents(config, contents, start_line, end_line):
    # At this point the tag should be valid, so we don't worry about keyerror here.
    tag = contents[start_line]

    curr_line_number = start_line + 1

    if tag == ":ENVIRONMENT:" or tag == ":VARS:":
        while curr_line_number != end_line:
            curr_line = contents[curr_line_number]

            # Skip comments and empty lines.
            if len(curr_line) == 0 or curr_line.startswith("#"):
                curr_line_number += 1
                continue

            split_line = curr_line.split("=", 1)

            var = split_line[0]
            value = split_line[1]

            if var not in config[tag].keys():
                raise InvalidFileFormatError("Unknown variable '{}' in '{}'.".format(var, tag))

            config[tag][var] = value
            curr_line_number += 1

        return

    if tag == ":ALLWAYS:":
        allways_str = ""
        for ii in range(start_line + 1, end_line):
            allways_str += contents[ii] + "\n"

        config[tag] = allways_str
        return

    print("\tUnprocessed tag:", tag)


# ======= Entry Point ========
if __name__ == "__main__":
    main()
