# Co-ordinate converter by Jackson Kerr

## Takes input from stdin, and attempts to interpret each line as a coordinate.

### Flags:
- -h Prints out this help message
- -v Gives more verbose error messages
- -u Enables longitude wrapping, and allows negative values when an explicit
   direction is also given

### Examples of accepted format:
#### Lat, Lon formats:
- 4, 2
- 4 ,2
- 1.234567 -23.987654
- 1.2, -23.9
- 0 0.004
- 1.234567, -23.987654
- 1234.567, -23987.654

#### Degrees, Miniutes, Seconds formats:
- 20° 20′ 20″ S, 20° 20′ 20″ W
- 20 ° 20 ′ 20 ″ S, 20 ° 20 ′ 20 ″ W
- 20° 20′ 20″ S 20° 20′ 20″ W

- 20d 20m 20s N, 20d 20m 20s E
- 20 d 20 m 20 s S, 20 d 20 m 20 s W
- 20d 20m 20s W 20d 20m 20s S

- 20 20 20 N, 20 20 20 E
- 20 20 W, 20 20 S
- 20 20 West, 20 20 South
- 20 E, 20 S
- 20 20 S , 20 20 20 W
- 20.33 E, 190 S
- 40° 26.767′ N 79° 58.933′ W

- 20 20 20 20 20 20
- 20 20 20 20
