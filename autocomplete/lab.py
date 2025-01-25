"""
Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    def __init__(self):
        """
        Initializes instance of PrefixTree.
        """
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        >>> t = PrefixTree()
        >>> t['bark'] = ':)'
        >>> t['bark']
        ':)'
        """
        # key isnt a string
        if not isinstance(key, str):
            raise TypeError
        # key doesn't exist so set value
        if not key:
            self.value = value
        else:
            # check if first letter in children and add if not
            current = key[0]
            if current not in self.children:
                self.children[current] = PrefixTree()
            # recursively set/add value from rest of letters in key
            self.children[current].__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        # key isn't a string
        if not isinstance(key, str):
            raise TypeError

        if len(key) == 1:
            # return value that letter node maps to
            if key in self.children and self.children[key].value is not None:
                return self.children[key].value
            # key not found or value is None
            raise KeyError
        current = key[0]
        return self.children[current].__getitem__(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        >>> 
        """
        # get key and set key to None
        self.__getitem__(key)
        self.__setitem__(key, None)

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        # key not string
        if not isinstance(key, str):
            raise TypeError
        # if reached end of key, return True if current node has a value
        if len(key) == 0:
            return self.value is not None
        current = key[0]
        # first letter not in tree so False
        if current not in self.children:
            return False
        return self.children[current].__contains__(key[1:])

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        # value not None, then yield pair
        if self.value is not None:
            yield "", self.value
        # iterate through all children and concatenate letters to yield key
        for letter, child in self.children.items():
            for key, value in child:
                yield letter + key, value


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    token = tokenize_sentences(text)
    # split sentence into list of words
    sentences = [sentence.split() for sentence in token]
    freq_tree = PrefixTree()
    # iterate through each word per sentence
    for sentence in sentences:
        for word in sentence:
            # increment count if word in tree, o.w. add
            if word in freq_tree:
                freq_tree[word] += 1
            else:
                freq_tree[word] = 1
    return freq_tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    # prefix not a string
    if not isinstance(prefix, str):
        raise TypeError
    # traverse tree based on prefix
    child_tree = sub_tree(tree, prefix)
    # prefix doesn't have tree
    if child_tree is None:
        return []
    # generate key-values for prefix tree
    words_with_pref = list(child_tree)
    # sort words by frequencies
    words_with_pref.sort(key=lambda tree: tree[1], reverse=True)
    # concatatenate initial prefix to subtree keys
    actual_words = [prefix + word[0] for word in words_with_pref]
    # return list of words to max count amount or whole list if max count isn't int
    if isinstance(max_count, int):
        return actual_words[:max_count]
    else:
        return actual_words


def sub_tree(tree, prefix):
    """
    Finds subtree of prefix (all nodes that extend from prefix
    point)
    """
    node = tree
    for char in prefix:
        if char not in node.children:
            return None
        node = node.children[char]
    return node


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    # get autocompletion words from prefix
    freq_words = autocomplete(tree, prefix, max_count)
    # set difference for how many edits you need to extend by
    if max_count is None:
        additional_words = float("inf")
    else:
        additional_words = max_count - len(freq_words)

    # Generate valid edits for prefix
    valid_edits = edit_pref(tree, prefix)

    # Sort valid edits by frequency
    valid_edits.sort(key=lambda edit: tree[edit], reverse=True)

    # Combine autocompletion words with edits, ensuring uniqueness
    if additional_words == float("inf"):
        all_words = freq_words + valid_edits
    else:
        all_words = freq_words + valid_edits[:additional_words]
    # Return max_count suggestions and ensure no duplicates
    return list(set(all_words[:max_count]))


def edit_pref(tree, prefix):
    """
    Generates edits for a prefix through single character insertion,
    single character deletion, singe char replacement, and 
    two-character transpose.
    """
    edits = []
    edits.extend(ins_char(tree, prefix))
    edits.extend(del_char(tree, prefix))
    edits.extend(replace(tree, prefix))
    edits.extend(transpose(tree, prefix))
    return list(set(edits))


def ins_char(tree, prefix):
    """
    insert edit for a prefix.
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    edits = []
    # add any char to any place in word
    for i in range(len(prefix) + 1):
        for char in alphabet:
            edit = prefix[:i] + char + prefix[i:]
            if edit != prefix and edit in tree:
                edits.append(edit)
    return edits


def del_char(tree, prefix):
    """
    delete char from a prefix.
    """
    edits = []
    # delete any char from word
    for i in range(len(prefix)):
        if i < len(prefix):
            edit = prefix[:i] + prefix[i + 1:]
            if edit != prefix and edit in tree:
                edits.append(edit)
    return edits


def replace(tree, prefix):
    """
    replace char in a prefix.
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    edits = []
    for i in range(len(prefix)):
        # replace any char from word
        for char in alphabet:
            edit = prefix[:i] + char + prefix[i + 1:]
            if edit != prefix and edit in tree:
                edits.append(edit)
    return edits


def transpose(tree, prefix):
    """
    transposes 2 adjacent chars in prefix.
    """
    edits = []
    for i in range(len(prefix) - 1):
        edit = prefix[:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
        if edit != prefix and edit in tree:
            edits.append(edit)
    return edits


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    def recurse(tree, pattern, so_far):
        """
        Helper function to recurse through tree and match pattern 
        to words in tree.
        """
        # if done with pattern, word has been found so add to list
        if not pattern:
            if tree.value is not None:
                matches.append((so_far, tree.value))
        # if first char in pattern in tree, recurse on that char
        elif pattern[0] in tree.children:
            new_t = tree.children[pattern[0]]
            recurse(new_t, pattern[1:], so_far + pattern[0])
        # if first char is question mark, add any letter for word in tree
        elif pattern[0] == "?":
            for letter, child in tree.children.items():
                recurse(child, pattern[1:], so_far + letter)
        elif pattern[0] == "*":
            # if * is 0 so no letter
            recurse(tree, pattern[1:], so_far)
            # if * is any length from 1 - infinity extra letters
            for letter, child in tree.children.items():
                recurse(child, pattern, so_far + letter)

    matches = []
    recurse(tree, pattern, "")
    return list(set(matches))


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    # t = PrefixTree()
    # t['bat'] = 7
    # t['bar'] = 3
    # t['bark'] = ':)'
    # print(t.__delitem__('bark'))
    with open("testing_data/dracula.txt", encoding="utf-8") as f:
        text = f.read()
    words = word_frequencies(text)
    # print(autocomplete(words, "gre", 6))

    # print(word_filter(words, "c*h"))

    # print(word_filter(words, "r?c*t"))

    # print(autocomplete(words, "hear", max_count = None))
    # print(autocorrect(words, "hear", max_count = None))

    # print(len(list(words)))

    # token = tokenize_sentences(text)
    # sentences = [sentence.split() for sentence in token]
    # count = 0
    # for sentence in sentences:
    #     for word in sentence:
    #         count += 1
    # print(count)













