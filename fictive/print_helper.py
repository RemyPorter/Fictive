def print_line(line:str, w:int=80):
    """
    Print a line, automatically breaking at the space nearest to
    `w` characters wide. This is to fit neatly into terminals.
    """
    length = len(line)
    if length <= w: # string is shorter than our window
        print(line)
        return
    n = 0
    while n < length:
        if n+w > length: # the last block of the string
            print(line[n:])
            return
        window = line[n:n+w]
        split_at = window.rfind(" ")
        if split_at >= 0:
            print(window[0:split_at])
            n += split_at + 1
        else:
            print(window[0:w])
            n += w
        
def margined_print(text:str, w:int=80):
    """
    Print a multiline block of text across multiple wrapped lines,
    wrapping at `w` characters wide
    """
    lines = text.split("\n")
    for l in lines:
        print_line(l, w)