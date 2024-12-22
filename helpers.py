class SumsTable():
    def __init__(self):
        self.sums_dict = {1: [[1]]}

    def get_all_sums(self, x: int):
        if (x in self.sums_dict):
            return self.sums_dict[x]

        sums = [[x]]
        for y in range(x - 1, (x//2), -1):
            # lesser number (x - y), greater number (y)
            # all the possible sums of x are the sums of y and all the combinations
            # of sums of (x - y)
            for lesser_sum in self.get_all_sums(x - y):
                sum = [y]
                sum.extend(lesser_sum)
                sums.append(sum)

        self.sums_dict[x] = sums
        return sums
    
def box_ascii(boxes_closed) -> str:
    ascii = "```\n"
    box_len = len(boxes_closed)
    num_digits = len(str(box_len))

    ascii += '_' * ((box_len + 1) + (num_digits * box_len))
    ascii += "\n"
    for i in range(box_len):
        if (boxes_closed[i]):
            ascii += "|"
            ascii += ' ' * num_digits
        else :
            digits_of_i = len(str(i + 1))
            ascii += f"|{i + 1}"
            ascii += ' ' * (num_digits - digits_of_i)
    ascii += "|\n"
    ascii += '-' * ((box_len + 1) + (num_digits * box_len))
    ascii += "```"
    return ascii