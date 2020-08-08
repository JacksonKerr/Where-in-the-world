
import sys
import re
import pprint
import traceback

verbose = False
accept_unspecific_input = False

def main():
    global verbose, accept_unspecific_input
    # Print out help message if -h flag is used
    if "-h" in sys.argv:
        print(help_info())
        sys.exit()
    # Give more detailed error messsages if -v flag is used
    if "-v" in sys.argv:
        verbose = True
    # Wrap latitudes when < -90 or > 90, and allow negitive values with explicit diretions if -w flag is given
    if "-u" in sys.argv:
        accept_unspecific_input = True

    san_coords = read_coords()

    # Regex for checking if a string is close to standard form
    std_form_regex = re.compile(r"^-?[0-9]+(\.[0-9]+)?[, ]+?-?[0-9]+(\.[0-9]+)?$")

    # Regex for checking if string is in DMS form (With or without Decimals)
    dms_regex = re.compile( r"^(-?[0-9]+(.[0-9]+)? ?[dms]?)"
                            r"( -?[0-9]+(.[0-9]+)? ?[dms]?)?"
                            r"( -?[0-9]+(.[0-9]+)? ?[dms]?)?"
                            r"( [nsew])?"
                            r"[ ,]+?"
                            r"(-?[0-9]+(.[0-9]+)? ?[dms]?)"
                            r"( -?[0-9]+(.[0-9]+)? ?[dms]?)?"
                            r"( -?[0-9]+(.[0-9]+)? ?[dms]?)?"
                            r"( [nsew])?$")

    for str_coord in san_coords:
        given_str = str_coord

        # Replace symbols with their corresponding letters for easier processing
        str_coord = str_coord.lower()
        str_coord = str_coord.replace("°", "d")
        str_coord = str_coord.replace("′", "m")
        str_coord = str_coord.replace("″", "s")
        str_coord = str_coord.replace("north", "n")
        str_coord = str_coord.replace("east", "e")
        str_coord = str_coord.replace("south", "s")
        str_coord = str_coord.replace("west", "w")
        str_coord = str_coord.strip()

        # Check if string is in something resembling standard form:
        if re.match(std_form_regex, str_coord):
            try:
                print_6dp(close_to_stand_form(str_coord))
            except Exception as e:
                if verbose:
                    print("Unable to process:", given_str, "\t|", e)
                else:
                    print("Unable to process:", given_str)
            continue



            continue

        # Check if string is in something resembling DMS form:
        if re.match(dms_regex, str_coord):
            try:
                print_6dp(alt_form(str_coord))
            except Exception as e:
                if verbose:
                    print("Unable to process:", given_str, "\t|", e)
                else:
                    print("Unable to process:", given_str)
            continue

        if verbose:
            print("Unable to process:", given_str,"\t| Bad format, use -h for accepted formats")
        else:
            print("Unable to process:", given_str)

def read_coords():
    """
    Reads in coordinates from stdin, and stores them as strings in an array.
    @return Array of String containing sanitised lines read from stdin.
    """
    # buffers for each ant object
    refined_lines = []

    # reads stdin
    lines = sys.stdin.readlines()

    for line in lines:
        # Removing lead/tailing whitespace, double spaces, and newlines from line
        line = line.strip()
        comment_index = line.find("#")
        re.sub(' +', ' ', line)
        line = line if comment_index == -1 else line[:comment_index]

        # if the comment was the only thing on the line it will now be empty, so skip it
        if len(line) < 1:
            continue

        refined_lines.append(line)
    return refined_lines


def close_to_stand_form(in_string):
    """
        Takes a string that is in the form "lat, lon" or similar, and returns
        a list of format [lat, lon].
    """
    num_commas = in_string.count(",")
    num_spaces = in_string.count(" ")
    split_string = []

    if (num_commas == 1) and (num_spaces == 1): # If string has a single space and comma
        if in_string.find(", ") > 0:
            split_string = in_string.split(", ")
        else:
            split_string = in_string.split(" ,")

    if (num_commas == 1) ^ (num_spaces == 1): # If string has a single space xor comma
        if (num_commas == 1):
            split_string = in_string.split(",")
        else:
            split_string = in_string.split(" ")

    lat = float(split_string[0])
    lon = float(split_string[1])

    latlon = remove_wrapping(lat, lon)

    return latlon


def alt_form(in_string):
    """
        Takes a string that is in DMS form, or similar, and returns
        a list of format [lat, lon].
    """
    explicit_dir = [False, False]
    new_string = in_string

    # Remove spaces between values and dms.
    search = re.search(r"\d [a-z]", in_string)
    while search is not None:
        index = search.span()[0]
        new_string = new_string[:index+1] + new_string[index+2:]
        search = re.search(r"\d [a-z]", new_string)
    
    num_commas = in_string.count(",")
    split_string = []

    # If string has a single comma, split on it.
    if in_string.count(",") == 1:
        if new_string.find(", ") > 0:
            split_string = new_string.split(", ")
        elif new_string.find(" ,") > 0:
            split_string = new_string.split(" ,")

    # If string has no comma, split on the space after the first direction letter.
    commaRegex = re.compile(r"^(-?[0-9]+(\.[0-9]+)? ?d?)?"
                            r"( -?[0-9]+(\.[0-9]+)? ?m?)?"
                            r"( -?[0-9]+(\.[0-9]+)? ?s?)?"
                            r" ([nsew] )")
    search = re.search(commaRegex, new_string)
    if len(split_string) == 0 and search is not None:
        index = search.span()[1]
        split_string = [new_string[:index], new_string[index:].strip()]

    # Otherwise If string has no comma, or first letter. Split on the middle space
    num_spaces = new_string.count(" ")
    if len(split_string) < 1:
        index = None
        search = re.finditer(r" ", new_string)
        for x in range(int(num_spaces/2 + num_spaces%2)):
            found = search.__next__()
        index = found.span()[0]
        split_string = [new_string[:index], new_string[index+1:].strip()]

    # If string has not been split, an error occurecd
    if len(split_string) < 1:
        raise Exception("Bad string format: ", in_string)

    # Split direction values into their base parts.
    move1 = split_string[0].split()
    move2 = split_string[1].split()

    # Retrieve direction values, or assume them to be N, W if they were not given
    dir1 = "n"
    lastIndex = len(move1) - 1
    last_item = move1[lastIndex]
    if last_item.isupper() or last_item.islower(): # If string contains a letter.
        explicit_dir[0] = True
        if len(last_item) == 1: # If last item only contains a letter, remove it and take it as the direction.
            dir1 = move1.pop()
        else:
            dir1 = last_item[len(last_item)-1]
            move1[lastIndex] = move1[lastIndex].replace(dir1, "")

    dir2 = "e"
    lastIndex = len(move2) - 1
    last_item = move2[len(move2) - 1]
    if last_item.isupper() or last_item.islower(): # If string contains a letter.
        explicit_dir[1] = True
        if len(last_item) == 1: # If last item only contains a letter, remove it and take it as the direction.
            dir2 = move2.pop()
        else:
            dir2 = last_item[len(last_item)-1]
            move2[lastIndex] = move2[lastIndex].replace(dir2, "")

    # If a negative value and a direction are given, this could be a typo
    if not accept_unspecific_input:
        explicit_value_exception = Exception("Direction values cannot be negative if an explicit direction is given")
        if "-" in move1[0] and explicit_dir[0]:
            raise explicit_value_exception
        if "-" in move2[0] and explicit_dir[1]:
            raise explicit_value_exception

    # Convert DMS arrays to decimal format
    dir1_magnitude = DMS_to_decimal(move1)
    dir2_magnitude = DMS_to_decimal(move2)  

    # Rearrange values to lat, lon
    lat = None
    lon = None

    if (dir1 in "ew" and dir2 in "ew") or (dir1 in "ns" and dir2 in "ns"):
        raise Exception("Both directions cannot be on the same axis.")

    if dir1 == "n":
        lat = dir1_magnitude
    elif dir1 == "s":
        lat = -dir1_magnitude
    elif dir1 == "e":
        lon = dir1_magnitude
    elif dir1 == "w":
        lon = -dir1_magnitude

    if dir2 == "n":
        lat = dir2_magnitude
    elif dir2 == "s":
        lat = -dir2_magnitude
    elif dir2 == "e":
        lon = dir2_magnitude
    elif dir2 == "w":
        lon = -dir2_magnitude

    latlon = remove_wrapping(lat, lon)

    return latlon
    

def DMS_to_decimal(dms):
    """
        Converts a list representing a DMS magnitude of the format [[Xd], [Xm], [Xs]] 
        where X represents magnitude into a decimal value.

        Values can be given in any order. Use a regex to check input if this is undesirable

        Decimal values can only be used for the least significant value.
    """
    magnitude = 0
    values_seen = []
    vals = {}

    missing_labels_exception = Exception("A DMS Representation must have either all, or none of it's magnitudes labeled. The same goes for direction.")

    duplicate_labels_exception = Exception("A DMS Representation may only contain one of each value d, m, s "
                                         + "for degrees, miniutes, and seconds respectively")

    significant_decimal_exception = Exception("Decimal values can only be used for the least significant value given.")

    too_many_values_exception = Exception("A DMS representation may contain up to 3 magnitude values, got: " + str(len(dms)))
    
    # A DMS representation may contains a max of 3 values
    if 3 < len(dms):
        raise too_many_values_exception
    
    # If every value in DMS is labeled with a magnitude
    for value in dms:
        if "d" in value:
            value = value.replace("d","")
            values_seen.append("d")
            magnitude += float(value)
        elif "m" in value:
            value = value.replace("m","")
            values_seen.append("m")
            magnitude += float(value)/60 # Min is 1/60th of a degree
        elif "s" in value:
            value = value.replace("s","")
            values_seen.append("s")
            magnitude += float(value)/3600 # Sec is 1/3600th of a degree
        else:
            if 0 < len(values_seen):
                raise missing_labels_exception
            break
        
    if len(values_seen) != len(set(values_seen)): # If same magnitude is used twice, this is likely a mistake.
        raise duplicate_labels_exception

    # If input does not contain labels, assume the order d, m, s until we run out of values



    if len(values_seen) == 0:
        magnitude = 0
        last_item_index = len(dms)-1
        for i in range(len(dms)):
            curr = dms[i]
            if i == 0:
                magnitude += float(dms[i])
            elif i == 1:
                magnitude += float(dms[i])/60 # Min is 1/60th of a degree
            elif i == 2:
                magnitude += float(dms[i])/3600 # Sec is 1/3600th of a degree
            if i != last_item_index and "." in dms[i]:
                raise significant_decimal_exception

    return magnitude


def remove_wrapping(lat, lon):
    """
        Returns a set of co-ordinate's simplest equivilent.

        This longitude calculation in this method may be a little difficult to understand. 
        It's easiest to assume the logitude will be positive when reading throught it.
    """

    # Latitude
    if -90 <= lat and lat <= 90:
        # Lat is already valid
        pass
    else:
        if accept_unspecific_input:
            # Unwrap lat
            magnitude = lat % 360 # The distance from the equtor
            breaks = magnitude // 90 # The number of times the equator or a pole if crossed

            direction = 1
            if not magnitude in range(0, 180):  # ie. If we are in the sothern hemisphere
                direction = -1

            magnitude  %= 90 # magnitude now represents the distance from the previous equator/pole intersection

            if breaks % 2 == 1: # If magnitude is getting closer to the equator in it's last moment of travel
                magnitude = 90 - magnitude

            lat = magnitude * direction
        else:
            raise Exception("Latitude cannot be > 90 or < -90 unless -w flag is given")

    # Longitude
    if lon in range(-180, 180):
        # Lon is already valid
        pass
    else:
        magnitude = lon % 360 # The distance east from 0

        if magnitude > 180: # If the distance east is > 180, 
            magnitude -= 360

        lon = magnitude

    return [lat, lon]


def print_6dp(latlon):
    """
        Prints in format "lat, lon" (to 6dp).
    """
    print("{0:.6f}".format(latlon[0])+", "+"{0:.6f}".format(latlon[1]))

def help_info():
    """
        Returns a string of help information.
    """
    return  "\n"\
            "Co-ordinate converter by Jackson Kerr\n"\
            "\n"\
            "Takes input from stdin, and attempts to interpret each line as a coordinate.\n"\
            "\n"\
            "Flags:\n"\
            "\t-h Prints out this help message\n"\
            "\t-v Gives more verbose error messages\n"\
            "\t-u Enables longitude wrapping, and allows negative values when an explicit\n"\
            "\t   direction is also given\n"\
            "\n"\
            "Examples of accepted format:\n"\
            "\tLat, Lon formats:\n"\
            "\t\t4, 2\n"\
            "\t\t4 ,2\n"\
            "\t\t1.234567 -23.987654\n"\
            "\t\t1.2, -23.9\n"\
            "\t\t0 0.004\n"\
            "\t\t1.234567, -23.987654\n"\
            "\t\t1234.567, -23987.654\n"\
            "\n"\
            "\tDegrees, Miniutes, Seconds formats:\n"\
            "\t\t20° 20′ 20″ S, 20° 20′ 20″ W\n"\
            "\t\t20 ° 20 ′ 20 ″ S, 20 ° 20 ′ 20 ″ W\n"\
            "\t\t20° 20′ 20″ S 20° 20′ 20″ W\n"\
            "\n"\
            "\t\t20d 20m 20s N, 20d 20m 20s E\n"\
            "\t\t20 d 20 m 20 s S, 20 d 20 m 20 s W\n"\
            "\t\t20d 20m 20s W 20d 20m 20s S\n"\
            "\n"\
            "\t\t20 20 20 N, 20 20 20 E\n"\
            "\t\t20 20 W, 20 20 S\n"\
            "\t\t20 20 West, 20 20 South\n"\
            "\t\t20 E, 20 S\n"\
            "\t\t20 20 S , 20 20 20 W\n"\
            "\t\t20.33 E, 190 S\n"\
            "\t\t40° 26.767′ N 79° 58.933′ W\n"\
            "\n"\
            "\t\t20 20 20 20 20 20\n"\
            "\t\t20 20 20 20\n"\


if __name__ == "__main__":
    main()