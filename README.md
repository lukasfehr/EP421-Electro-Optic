# EP421-Electro-Optic
Electro-optic effect experiment simulation for EP 421.

There are two ways to run this code:
1. Go to the [repl.it project](https://repl.it/@LukasFehr/EP421-Electro-Optic?outputonly=1) and click run (easiest option).
2. Clone or download this repository and run the code offline (requires python 3).

## Install Python via Anaconda

If you want to run the simulation offline but you don't have python 3 on your computer, I would recommend installing [Anaconda or Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

Then open the Anaconda Prompt and enter the following commands:
 - Create an 'environment' called ep421 to hold all the packages you need to run the program:
     - `> conda create -n ep421 python=3.8`
 - Enter the new environment:
     - Windows: `> activate ep421`
     - Mac/Linux: `> source activate ep421`
 - Install the required packages (these are very good packages to have anyways!):
     - `> conda install numpy`
     - `> conda install matplotlib`

## Download the Repository

If you are familiar with git, clone the repository using your preferred method.

If you are not, click the green "Code" button, download the zip file, and extract the contents.

## Run the program

1. Open the Anaconda Prompt again and navigate to the directory where you cloned/extracted the repository.

2. If you are not familiar with navigating in a command prompt:
    - Windows: `> dir` will list the files and directories in your current directory
    - Mac/Linux: `> ls` will list the files and directories in your current directory
    - `> cd EP421-Electro-Optic` will move you into the directory called EP421-Electro-Optic, if it exists in the current directory
    - `> cd ..` will move you up into the directory containing the current directory

3. If you have closed and re-opened the prompt, be sure to re-enter the environment you created before.

4. Run the command `> python main.py --offline`.

 
