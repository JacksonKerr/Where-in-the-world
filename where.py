
import sys
import re
import pprint

def main():
    san_coords = read_coords()

    # Regex for checking if a string is close to standard form
    std_form_regex = re.compile(r"^-?[0-9]+(\.[0-9]+)?[, ]+?-?[0-9]+(\.[0-9]+)?$")

    # Regex for checking if string is in DMS form (With or without Decimals)
    dms_regex = re.compile( r"^(-?[0-9]+(.[0-9]+)? ?d?)"
                            r"( -?[0-9]+(.[0-9]+)? ?m?)?"
                            r"( -?[0-9]+(.[0-9]+)? ?s?)?"
                            r"( [NSEW])?"
                            r"[ ,]+?"
                            r"(-?[0-9]+(.[0-9]+)? ?d?)"
                            r"( -?[0-9]+(.[0-9]+)? ?m?)?"
                            r"( -?[0-9]+(.[0-9]+)? ?s?)?"
                            r"( [NSEW])?$")


    lazy_dms_regex = re.compile( r"^([0-9]+ [0-9]+ ?){1,3}$")

    for str_coord in san_coords:
        # Replace symbols with their corresponding letters for easier processing
        str_coord = str_coord.replace("°", "d")
        str_coord = str_coord.replace("′", "m")
        str_coord = str_coord.replace("″", "s")

        # Check if string is in something resembling standard form:
        if re.match(std_form_regex, str_coord):
            print("Std form Below:")
            print(str_coord)
            print_6dp(close_to_stand_form(str_coord))
            print("======================")
            continue

        # Check if string is in something resembling DMS form:
        if re.match(dms_regex, str_coord):
            print("DMS Below:")
            print(str_coord)
            try:
                print_6dp(alt_form(str_coord))
            except Exception as e:
                print("Unable to process: ",e)
            print("======================")
            continue

        print(str_coord)
        print("Unable to process: Bad Format")
        print("======================")

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
                            r" ([NSEW] )")
    search = re.search(commaRegex, new_string)
    if len(split_string) == 0 and search is not None:
        index = search.span()[1]
        split_string = [new_string[:index], new_string[index:].strip()]

    # If string has no comma, or first letter. Split on the middle space
    num_spaces = new_string.count(" ")
    if len(split_string) < 1: # Will have 5 spaces if in the form "d m s d m s"
        index = None
        search = re.finditer(r" ", new_string)
        for x in range(int(num_spaces/2 + num_spaces%2)):
            found = search.__next__()
        index = found.span()[0]
        split_string = [new_string[:index], new_string[index+1:].strip()]

    # Split direction values into their base parts.
    move1 = split_string[0].split()
    move2 = split_string[1].split()

    # Retrieve direction values, or assume them to be N, W if they were not given
    dir1 = "N"
    last_item = move1[len(move1)-1]
    if last_item.isalpha():
        dir1 = move1.pop()

    dir2 = "E"
    last_item = move2[len(move2) - 1]
    if last_item.isalpha():
        dir2 = move2.pop()

    # Convert DMS arrays to decimal format
    dir1_magnitude = DMS_to_decimal(move1)
    dir2_magnitude = DMS_to_decimal(move2)  

    # Rearrange values to lat, lon
    lat = None
    lon = None

    if (dir1 in "EW" and dir2 in "EW") or (dir1 in "NS" and dir2 in "NS"):
        raise Exception("Both directions cannot be on the same axis.")

    if dir1 == "N":
        lat = dir1_magnitude
    elif dir1 == "S":
        lat = -dir1_magnitude
    elif dir1 == "E":
        lon = dir1_magnitude
    elif dir1 == "W":
        lon = -dir1_magnitude

    if dir2 == "N":
        lat = dir2_magnitude
    elif dir2 == "S":
        lat = -dir2_magnitude
    elif dir2 == "E":
        lon = dir2_magnitude
    elif dir2 == "W":
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

    missing_labels_exception = Exception("A DMS Representation may only contain one of each value d, m, s "
                                       + "for degrees, miniutes, and seconds respectively")

    significant_decimal_exception = Exception("Decimal values can only be used for the least significant value given.")
    
    # If every value in DMS is labeled with a magnitude TODO Does not work
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
        
    if len(values_seen) != len(set(values_seen)): # If the same magnitude for a value is used twice, this is likely a mistake.
        raise missing_labels_exception

    # If input does not contain labels, assume the order d, m, s until we run out of values # TODO Might not work
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
    if (lat < -90 or 90 < lat): # If lat outside the valid range
        lat %= 90
    if (lon < -180 or 180 < lon): # If lon outside the valid range
        lon %= 180
    return [lat, lon]


def print_6dp(latlon):
    """
        Prints in format "lat, lon" (to 6dp).
    """
    print("{0:.6f}".format(latlon[0])+", "+"{0:.6f}".format(latlon[1]))

if __name__ == "__main__":
    main()