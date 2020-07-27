
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
        
        str_coord = str_coord.replace("°", "d")
        str_coord = str_coord.replace("′", "m")
        str_coord = str_coord.replace("″", "s")

        # Check if string is in alt (With or without Decimals)
        regex = re.compile(r"^(-?[0-9]+(.[0-9]+)? ?d? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?m? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?s? )?"
                            r"[NSEW]?"
                            r"[ ,]+?"
                            r"(-?[0-9]+(.[0-9]+)? ?d? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?m? )?"
                            r"(-?[0-9]+(.[0-9]+)? ?s? )?"
                            r"[NSEW]?$") # TODO Fix regex being big and ugly
        if re.match(regex, str_coord):
            #print(str_coord +"\t\t\t\t CAUGHT (Alt Form)")
            alt_form(str_coord)
        else:
            print(str_coord+" FAILED")
        

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
    commaRegex = re.compile(r"^(-?[0-9]+(.[0-9]+)? ?d? )?"
                        r"(-?[0-9]+(.[0-9]+)? ?m? )?"
                        r"(-?[0-9]+(.[0-9]+)? ?s? )?"
                        r"[NSEW]?")
    search = re.search(commaRegex, new_string)
    if search is not None:
        index = search.span()[1]
        move1 = new_string[:index]
        move2 = new_string[index+1:].strip() 
        split_string = [move1, move2]

    # If string has no comma, or direction letters. Split on 3rd space.
    if new_string.count(" ") == 5: # Will have 5 spaces if in the form "d m s d m s"
        index = None
        search = re.finditer(r" ", new_string)
        for x in range(3):
            found = search.__next__()
        index = found.span()[0]
        move1 = new_string[:index]
        move2 = new_string[index+1:].strip()
        split_string = [move1, move2]

    # Split direction values into their base parts.
    split_string = [split_string[0].split(), split_string[1].split()]
    
    # Retrieve direction values.
    dir1 = split_string[0].pop()
    dir2 = split_string[1].pop()

    # Otherwise something is wrong.
    print(split_string)

def print_6dp(latlon):
    """
        Prints in format "lat, lon" (to 6dp).
    """
    print("{0:.6f}".format(latlon[0])+", "+"{0:.6f}".format(latlon[1]))

if __name__ == "__main__":
    main()