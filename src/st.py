import argparse
import sys
from dataclasses import dataclass,field
from collections import deque

argparser = argparse.ArgumentParser(
    description="Exact matching using suffix tree construction")
argparser.add_argument("genome", type=argparse.FileType('r'))
argparser.add_argument("reads", type=argparse.FileType('r'))
args = argparser.parse_args()

@dataclass
class node:
    # A node in a suffix tree
    index: list = field(default_factory=lambda: [0, None])
    suffix_link: int = None
    parent: int = None # Batman
    children: dict = field(default_factory = dict)
    self_pointer: int = 0
    leaf_start: int = None

def fasta_translator(file):
    output_dict = {}
    start = True
    for i in file:
        if i[0] == ">":
            if  not start:
                output_dict[name] = seq
            name = i[1:].strip()
            seq = ""
            if start:
                start = False
        else:
            seq += i.strip()
    output_dict[name] = seq
    return output_dict

def fastq_translator(file):
    output_dict = {}
    for i in file:
        if i[0] == "@":
            name = i[1:].strip()
        else:
            seq = i.strip()
            output_dict[name] = seq
    return(output_dict)

def suffix_tree(string):
    remaining = 0
    active_edge = None
    edge_length = 0
    tree_list = [node(index = None)] #create root node
    active_node = tree_list[0]
    string = string + "0"
    for i in range(len(string)):
        remaining += 1
        suffix_link_update = None
        current_char = string[i]
        while remaining > 0:
            if edge_length:
                edge_char = string[active_edge]
                matched_node = tree_list[active_node.children[edge_char]]
                if matched_node.index[1] is not None and matched_node.index[1] < (matched_node.index[0] + edge_length): # We have to jump an internal node
                    internal_node_length = matched_node.index[1] - matched_node.index[0] + 1
                    if internal_node_length < edge_length: # We have to jump past the internal node to begin matching
                        active_node = matched_node
                        active_edge += internal_node_length
                        edge_length -= internal_node_length
                        continue # we have the code to care of the rest elsewhere, no need to write it twice in a while loop

                    else: # We can begin matching with the start of the internal nodes edges
                        if current_char in matched_node.children.keys(): # we can extend from the internal node
                            active_node = matched_node
                            matched_node = tree_list[active_node.children[current_char]]
                            active_edge = matched_node.index[0]
                            edge_length = 1
                            break

                        else: # we can't extend from the internal node

                            newnode = node(index = [i, None], parent = matched_node.self_pointer, self_pointer = len(tree_list), leaf_start = i - remaining + 1)
                            tree_list.append(newnode)
                            tree_list[matched_node.self_pointer].children[current_char] = len(tree_list) - 1
                            if suffix_link_update:
                                tree_list[suffix_link_update].suffix_link = matched_node.self_pointer
                            suffix_link_update = matched_node.self_pointer
                            remaining -= 1
                            if active_node.suffix_link is not None:
                                active_node = tree_list[active_node.suffix_link]
                            else:
                                active_edge += 1
                                edge_length -= 1
                                active_node == tree_list[0]

                else: # We don't have to jump an internal node
                    match = string[matched_node.index[0] + edge_length] # the character we are matching against
                    if current_char == match: # there is a match
                        edge_length += 1
                        break

                    else: # there is no match

                        internal_node_index = matched_node.self_pointer

                        newnode = node(index = [matched_node.index[0] + edge_length, matched_node.index[1]], parent = internal_node_index,
                            self_pointer = len(tree_list), children = matched_node.children, leaf_start = tree_list[internal_node_index].leaf_start) # Creates the node that was previously found in the old node
                        tree_list[internal_node_index].leaf_start = None

                        tree_list.append(newnode)
                        tree_list[internal_node_index].children = dict()
                        for j in tree_list[newnode.self_pointer].children:
                            tree_list[newnode.children[j]].parent = newnode.self_pointer

                        tree_list[internal_node_index].children[string[newnode.index[0]]] = newnode.self_pointer
                        
                        if tree_list[internal_node_index].suffix_link is None:
                            tree_list[internal_node_index].suffix_link = 0

                        tree_list[internal_node_index].index[1] = matched_node.index[0] + edge_length - 1

                        newnode = node(index = [i, None], parent = internal_node_index, self_pointer = len(tree_list), leaf_start = i - remaining + 1) # and creates the new child
                        tree_list.append(newnode)
                        tree_list[internal_node_index].children[current_char] = newnode.self_pointer
                        if suffix_link_update:
                            tree_list[suffix_link_update].suffix_link = active_node.self_pointer
                        suffix_link_update = internal_node_index
                        if active_node.suffix_link is not None:
                            active_node = tree_list[active_node.suffix_link]
                        else:
                            active_edge += 1
                            edge_length -= 1
                            active_node == tree_list[0]
                        remaining -= 1
            else: #There is no active edge
                
                assert active_node.self_pointer == 0
                assert remaining == 1
                if current_char in active_node.children.keys(): # We can extend from root
                    active_edge = tree_list[active_node.children[current_char]].index[0]
                    edge_length = 1
                    break
                else: # we cant extend from root
                    newnode = node(index = [i, None], parent = 0, self_pointer = len(tree_list), leaf_start = i - remaining + 1)
                    tree_list.append(newnode)
                    tree_list[0].children[current_char] = len(tree_list) - 1
                    remaining -= 1
    return tree_list

def traverse_tree(tree_list): # test function
    path_list = []
    visited_leafs = []
    while tree_list:
        for i in range(len(tree_list)):
            if not tree_list[i].children and i not in visited_leafs:
                visited_leafs.append(i)
                leaf = tree_list[i]
                break
        else:
            break
        path = []
        while True:
            if leaf.index is not None:
                path.append(leaf.index)
            if leaf.parent:
                leaf = tree_list[leaf.parent]
            else:
                path_list.append(path)
                break
    return path_list

def extract_patterns(path_list, string): # test function
    suffixes = []
    string = string + "0"
    for i in path_list:
        suffix = ""
        for j in range(len(i) -1, -1, -1):
            if i[j][1] is None:
                i[j][1] = len(string)
            suffix += string[i[j][0] : i[j][1] + 1]
        suffixes.append(suffix)
    suffixes.sort(key = len)
    return suffixes

def search_tree(tree_list, pattern, string):
    edge_length = None
    active_node = tree_list[0]
    str_len = len(string)

    for i in pattern:
        if edge_length is None and i in active_node.children:
            active_node = tree_list[active_node.children[i]]
            edge_length = 1
            if active_node.index[1] is None:
                active_node.index[1] = str_len
        elif edge_length is None:
            return None
        elif edge_length > (active_node.index[0] - active_node.index[1]):
            if i in active_node.children: # Should be a "repeat current iteration" keyword in python
                active_node = tree_list[active_node.children[i]] # then i would just set edge length to none and repeat
                edge_length = 1
                if active_node.index[1] is None:
                    active_node.index[1] = str_len
            else:
                return None
        elif i == string[active_node.index[0] + edge_length]:
            edge_length += 1
        else:
            return None
    return active_node.self_pointer

def traverse_tree(tree_list, subtree_start):
    if subtree_start == None:
        return []
    matches = []
    queue = deque([subtree_start])
    while queue: # While queue should work, but it doesnt?
        current = queue.popleft()
        if tree_list[current].children:
            for i in tree_list[current].children:
                queue.append(tree_list[current].children[i])
        else:
            matches.append(tree_list[current].leaf_start + 1)
    return matches

def suffix_tree_match(string, pattern, tree_list):
    if pattern == "" or string == "" or len(pattern) > len(string):
        return []

    subtree_start = search_tree(tree_list, pattern, string)
    matches = traverse_tree(tree_list, subtree_start)
    return matches

def matches_to_SAM(read_file, reference_file):
    read_name = []
    reference_name = []
    match_index = []
    CIGARS = []
    match_string = []

    fasta_dict, fastq_dict = fasta_translator(reference_file), fastq_translator(read_file)

    for i in fasta_dict:
        st = suffix_tree(fasta_dict[i])
        for j in fastq_dict:
            matches_temp = suffix_tree_match(fasta_dict[i], fastq_dict[j], st)
            if matches_temp:
                for match in matches_temp: # Each iteration makes a SAM row
                    read_name.append(j)
                    reference_name.append(i)
                    match_index.append(match + 1)
                    CIGARS.append(str(len(fastq_dict[j])) + "M")
                    match_string.append(fastq_dict[j])
    output = (read_name, reference_name, match_index, CIGARS, match_string)
    return output

def print_SAM(SAM):
    for i in range(len(SAM[0])):
        sys.stdout.write(SAM[0][i] + "\t" + SAM[1][i] + "\t" + str(SAM[2][i]) + "\t" + SAM[3][i] + "\t" + SAM[4][i] + "\n")

SAM = matches_to_SAM(args.reads, args.genome)

print_SAM(SAM)
