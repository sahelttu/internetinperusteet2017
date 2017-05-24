def reverse_words_in_string(s):

    # split string into words, reverse & print result
    a = s.split()
    a.reverse()
    result = " ".join(a)
    print(a)


s = input("Enter string: ")

reverse_words_in_string(s)