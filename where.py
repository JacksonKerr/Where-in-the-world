
import sys
import re
import pprint

def main():
    san_coords = read_coords()

    pprint.pprint(read_coords())

    for str_coord in san_coords:

        # Check if string is in something resembling standard form:
        if re.match(r"^-?[0-9]+(.[1-9]+)?,? ?-?[0-9]+(.[1-9]+)?$", str_coord):
            print(str_coord +"\t\t\t\t CAUGHT (Close to standard form)")

        # Check if string is in alt form TODO: Complete this
        elif re.match(r"^-?([0-9]+°)?$", str_coord):
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

if __name__ == "__main__":
    main()