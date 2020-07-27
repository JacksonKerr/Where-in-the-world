
import sys
import re
import pprint

def main():
    san_coords = read_coords()

    for str_coord in san_coords:
        
        # Check if string is in something resembling standard form:
        if re.match(r"^-?[0-9]+(.[0-9]+)?[, ]+?-?[0-9]+(.[0-9]+)?$", str_coord):
            #print(str_coord +"\t\t\t\t CAUGHT (Close to Standard Form)")
            print_6dp(close_to_stand_form(str_coord))
            continue
        
        
        # Check if string is in alt (With or without Decimals)
        regex = re.compile(r"^(-?[0-9]+(.[0-9]+)? ?[°d]? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?[′m]? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?[″s]? )?"
                            r"[NSEW]?"
                            r"[ ,]+?"
                            r"(-?[0-9]+(.[0-9]+)? ?[°d]? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?[′m]? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?[″s]? )?"
                            r"[NSEW]?$") # TODO Fix regex being big and ugly
        if re.match(regex, str_coord):
            print(str_coord +"\t\t\t\t CAUGHT (Alt Form)")
            alt_form(str_coord)
        else:
            print(str_coord)
        

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
    split_string = split_std_to_latlon(in_string)

    lat = float(split_string[0])
    lon = float(split_string[1])

    if (lat < -90 or 90 < lat): # If lat outside the valid range
        lat %= 90
    if (lon < -180 or 180 < lon): # If lon outside the valid range
        lon %= 180
    
    return [lat, lon]

def alt_form(in_string):
    """
        53.21 N, 21.12 W
        21.12 E, 532.1 N
        21.12 E, 532 N
        40° 26′ 46″ N 79° 58′ 56″ W
        40 d 26 m 46 s N, 79 d 58 m 56 s W
        40 26 46 N, 79 58 56 W
    """
    found = re.search(r"\d \D", in_string) # TODO Found now holds some weird thing showing
                                           # Where the natch is
    print(found)
    return split_std_to_latlon(in_string)

def split_std_to_latlon(in_string):
    num_commas = in_string.count(",")
    num_spaces = in_string.count(" ")
    split_string = []

    if (num_commas == 1) and (num_spaces == 1): # If string has a single space and comma
        if in_string.find(", ") > 0:
            return in_string.split(", ")
        else:
            return in_string.split(" ,")

    if (num_commas == 1) ^ (num_spaces == 1): # If string has a single space xor comma
        if (num_commas == 1):
            return in_string.split(",")
        else:
            return in_string.split(" ")
    print("ERROR ERROR")


def print_6dp(latlon):
    """
        Prints in format "lat, lon" (to 6dp).
    """
    print("{0:.6f}".format(latlon[0])+", "+"{0:.6f}".format(latlon[1]))

if __name__ == "__main__":
    main()