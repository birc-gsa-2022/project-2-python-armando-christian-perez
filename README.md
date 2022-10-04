[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-c66648af7eb3fe8bc4f294546bfd86ef473780cde1dea487d3c4ff354943c9ae.svg)](https://classroom.github.com/online_ide?assignment_repo_id=8670321&assignment_repo_type=AssignmentRepo)
# Project 2: Suffix tree construction

You should implement a suffix tree construction algorithm. You can choose to implement the naive O(n²)-time construction algorithm as discussed in class or McCreight’s O(n) construction algorithm. After that, implement a search algorithm (similar to slow-scan) for finding all occurrences of a pattern. This algorithm should run in O(m+z) where m is the length of the pattern and z the number of occurrences.

Write a program, `st` using the suffix tree exact pattern search algorithm (similar to slow-scan) to report all indices in a string where a given pattern occurs. 

The program should take the same options as in project 1: `st genome.fa reads.fq`. The program should output (almost) the same SAM file. Because a search in a suffix tree is not done from the start to the end of the string the output might be in a different order, but if you sort the output from the previous project and for this program, they should be identical.

## Evaluation

Implement the tool `st` that does exact pattern matching using a suffix tree. Test it to the best of your abilities, and then fill out the report below.

# Report

## Specify if you have used a linear time or quadratic time algorithm.
Linear

## Insights you may have had while implementing and comparing the algorithms.
That suffix trees allow us to find all patterns in a string by isolating the subtree for which all leafs are suffixes of the string suffixes, so that pattern + subtree suffix equals all suffixes of the string that includes the pattern as a prefix.

## Problems encountered if any.
Many.

## Correctness
I've run suffix tree construction on many types of strings, including the two analyzed in https://www.youtube.com/watch?v=aPRqocoBsFQ. These trees ive confirmed looked exactly like the ones in the video. I've also made two function for extracting and printing all the suffixes from shortest to longest from the leaf nodes (by first getting the suffixes and then sorting them, nothing fancy).
*Describe experiments that verifies the correctness of your implementations.*

## Running time

*Describe experiments that verifies that your implementation of `st` uses no more time than O(n) or O(n²) (depending on the algorithm) for constructing the suffix tree and no more than O(m) for searching for a given read in it. Remember to explain your choice of test data. What are “best” and “worst” case inputs?*

*If you have graphs that show the running time--you probably should have--you can embed them here like we did in the previous project.*

