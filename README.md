# AutoTeSG
Automated test suite generation tool for a subset of python. It generates test cases which ensure high coverage of a Python function.
The target are Python functions which
- take only integer arguments (however, there may be an unspecified number of arguments).
- have only integer type local variables; these can be assigned, and be used in predicates too.
- can contain loops
- contain predicates that only involve relational operators (==, !=, <. >. <=, >=), integer
variables, and calls to functions with integer return type
- can call external functions, including external libraries (but it only tries to achieve
coverage for the target function itself)
## General description
The general approach of the automated test data generation tool is to instrument the source code using _print()_ statements, which print out line numbers and their corresponding branch distance.
An Alternating Variable Method (AVM) search is used to determine a valid input for a given branch.

The tool follows the following steps.


- For every file:
- Read in the file
- Parse file to AST
- Replace all print statements by their argument
- Instrument code by adding print statements at control flow statement
- Walk AST to find function definitions
- For every function:
- Collect the possible branches of the function
- For every branch:
- Do an AVM search to cover the current branch
- Return the result of the optimisation

## Usage
The tool can be used from the command line using the following form.

	AutoTESG.py [-v] [-h] FILE...

Calling it with the _-v_ option will print out the version number while the _-h_ option wild print out usage instructions.
If neither of the options is specified, the tool will analyse one file after another and print out the results.

## Description of the individual files
In the following the individual files of the program will be described in detail.
### AutoTESG.py
This is the main file and handles the command line arguments.
If files were specified and no other command line parameters are given it will read in the fill and initiate the test data generation.
### AVM.py
This file contains the implementation of the AVM search method.
Inside of the function _AVMsearch()_, the search is started.
First it is checked, if there is already a set of input values, that covers as many branches of the goal branch set as possible.
This set is then used to initialise the input parameters to speed up the search.

Next the function iterates over the functions input parameters.
For each parameter it first executes an exploratory move and second a pattern move.
In case, no improvement of the fitness for any of the input parameters was found, the search will be restarted using random values, ranging from one to ten.
This range seems to be a reasonable prior for the value of the input parameters, if nothing more is known about the function at hand.
If the function failed to find a solution over three restarts, the branch is given up and declared as not reachable.

During the exploratory move, the respective variable is increased and decreased by one to see, which direction yields the biggest potential of improvement.

During the pattern move, the variable well be increased or decreased according to the direction determinde during the exploratory move.
Hereby the step size is doubled at each try.
If the fitness decreases, the last step in the variable value will be reverted and the exploratory move for the next variable is done.

If all goal branches are covered by an input set, an exception is thrown and the search ends.

### BranchCollector.py
The purpose of this file is to generate a list of all possible branches of a function, identified by the line number of the branching statements.
The function _add\_childs()_ recursively walks over the child nodes of a given node.
If it is a branching statement, namely _If, For_ or _While_, the respective branch and it's else branch, if existent, are added to the list of branches.

### CodeInstrumentator.py
This file contains a class to instrument the source with _print()_ statements.
Additionally it contains a class to replace all _print()_ statements by their arguments so they don't interfere with our instrumentation.

For the instrumentation the algorithm walks over the whole AST and whenever it encounters a branching statement, it inserts the respective _print()_ statements.

The _print()_ statements are added inside of the body, as well as the _else_ block of the statement.
Each _print()_ statement prints out the line number, which is negative, if the statement is located inside an else block.
Additionally each _print()_ statement prints out the branch distance to it's counterpart.
This means that the _print()_ statement inside an _if_ block will print the branch distance for the _else_ branch and vice versa.

The distance calculation is done as proposed by Korel 1990. 

### DistanceCalculator.py
In this file the distance which serves as an inverse fitness function is calculated.
The distance of an execution trace is calculated using two different metrics.

The first metric is the approach level.
This is simply the number of unpenetrated levels, separating the execution branches and the goal branches.

The second metric is the branch distance.
It is calculated as stated above and determines the distance between the actual parameter values and the values that are required to enter a branch.
As the code may have run through a certain branch several times, the minimal branch distance is returned.

Eventually these two metrics are combined according to the following formula.

![equation](http://www.sciweavers.org/tex2img.php?eq=d%20%3D%20d_%7Bapproach%5C_lvl%7D%20%2B%201%20-%201.001%5E%7Bd_%7Bbranch%7D%7D&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0)

### CodeRunner.py
This file is used to run the instrumented AST.
As we used _print()_ statements to instrument the code, first _stdout_ has to be redirected to our own input/output stream so we can process the output of the code.

Afterwards the AST will be compiled to a code object which is then executed.
Hereby it is important to set the global variables dictionary to be the same as the local variables dictionary.
This is because at the Module level, variables added to the locals dictionary should automatically be added to the globals dictionary but Python doesn't always do this within a code object's scope.
As a result, functions defined within the code object are only accessible locally but not within the scope of other functions.

## References
Korel, B. (1990). “Automated Software Test Data Generation”. In: IEEE Trans. Softw. Eng. 16.8, pp. 870–879. issn: 0098-5589. doi: 10.1109/32.57624. url: http://dx.doi.org/10.1109/32.57624.
