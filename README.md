# BreadBrawl

*Get ready for the battle of your loaf*

## Intro

Welcome to BreadBrawl, a showdown of the finest focaccias, the strongest sourdoughs, and the cleverest
croissants. This simple RPG will put each player's wheats to the test in a tournament where the last loaf
standing wins. The catch? You won't be the one piloting your loaf. Contestants will instead train a 
reinforcement learning agent to battle for them while learning the basics of how it works.

## How does reinforcement learning work?

### Basic Components

![Reinforcement Learning](https://www.altexsoft.com/static/blog-post/2023/11/345fadfa-549a-462a-b757-9ab258e747f3.jpg)

At its core, reinforcement learning is learning by trial and error. An agent interacts with its environment
by taking actions. Then, the agent is rewarded or punished for taking that action. In order to receive higher
rewards, the agent must change its strategy based on the actions it sampled from training. By iteratively
improving its strategy enough times, an agent can even perform as well as or better than humans!

> **Key Terms**:
> - **Environment** - the thing the agent is interacting with that defines what actions can be taken and what effect
>   those actions will have
> - **Action** - something the agent can do in the environment
> - **State** - any information about the environment (for example, the location of objects if the agent is trying
>   to navigate)
> - **Agent** - a program that chooses actions to take and can improve is policy as it trains
> - **Policy** - the strategy the agent uses to select actions (think of it like a function where the state of the
>   environment is he input and the output is the action the agent should take)

### Reinforcement learning with BreadBrawl

For this project, our environment is BreadBrawl. The actions available to the agent are three attacks chosen for
your character. The state includes information such as how much HP each player has left and the duration of the
effects of some attacks. The agent is rewarded for inflicting damage and winning, and it is punished for taking
damage and losing.

## Deep Q-Learning

In this project, the reinforcement learning method used is deep Q-learning. The methods used determine how the
policy selects actions and how it improves itself.

### Q-Learning

the idea behind Q-learning is to estimate the expected value of taking a given action in a given state for every
possible state-action pair. These expected values of state-action pairs are called **Q-values**, and the function
that maps these state-action pairs to their Q-values is called the **Q-function**. Once you have a well estimated
Q-function, then a good policy naturally emerges. Just pick the action with the highest Q-value in your current
state.

To get good estimates of the Q-value, the output of the Q-function must represent an average of the sampled 
rewards as a result of selecting the action in the state the Q-value corresponds to. This means using the reward
from taking that action but also accounting for future rewards. Q-learning does this by adding the rewards
received immediately after taking that action with the highest Q-value of the next state (the Q-value of the
action your policy would select). As your estimate of the Q-function improves, each Q-value depending on the
Q-value for the next state effectively represents future rewards caused by that action.

### Deep

The "deep" part of deep Q-learning comes from using a neural network as a Q-function. Consider two options: a
37,000,000 x 3 table of every possible state-action pair or a mathematical function defined by 35,000 parameters.
Functions tend to be far more efficient, and neural networks are perfect for the job. Think of neural networks
as infinitely flexible functions that can accurately represent the Q-function of any environment. Neural networks
can also be optimized easily by using chain rule.

## Training your agent

Use the following steps to create, train, and submit your loaf.

### Mac

#### Step 1: Check if Python is already installed

1. Press `Cmd + Spacebar`, type "Terminal", press Enter.
2. In the window that opens, type `python3 --version` and press Enter.
3. If you see something like `Python 3.13.5`, you're all set — skip to Step 3.
4. If you see an error instead, go to Step 2.

#### Step 2: Install Python
 
1. Go to **python.org/downloads** in your browser.
2. Click the big "Download Python" button (it automatically detects Mac vs. Windows).
3. Run the installer you downloaded.
4. When installation finishes, **close your terminal completely and reopen it**, then repeat the version check from Step 1 to confirm it worked.

#### Step 3: Download the BreadBrawl code

1. Go to `github.com/ShinyHydropi/BreadBrawl` in your browser.
2. Click the green **Code** button, then click **Download ZIP**.
3. Find the downloaded file in your Downloads folder and unzip it (double-click the ZIP file):
4. You should now have a folder named `BreadBrawl-main`. Move it somewhere easy to find, like your Desktop.
You're ready to set everything up.

#### Step 4: Setup BreadBrawl

1. Open Terminal.
2. Move into the folder you unzipped:
```
cd Desktop/BreadBrawl-main
```
   *(Tip: type `cd ` — with a trailing space — then drag the folder itself into the Terminal window. It will fill in the path for you.)*  
3. Create a virtual environment. This is just a private, self-contained space for this project's software so it doesn't interfere with anything else on your computer:
```
python3 -m venv .venv
```
4. Turn on the virtual environment:
```
source .venv/bin/activate
```
   You'll know it worked when you see `(.venv)` appear at the start of your terminal line.
5. Install the required software. This can take a few minutes — that's expected:
```
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

#### Step 5: Time to bake!

Every time you come back to this later (a new day, after closing your terminal, etc.), redo step 4 above first — activate the virtual environment — before running anything below.
 
1. **Create your loaf.** This asks you a few questions to set up your character:
```
python3 setup_loaf.py
```
2. **Train your agent.** Replace `NAME` with the name you gave your loaf in step 1:
```
python3 dql_agent_NAME.py
```
   This is where your agent actually learns to fight. It may take a while and print out a lot of numbers while it trains — that's normal, just let it run.
3. **Watch your agent fight.** Replace `NAME` again:
```
streamlit run agent_arena.py NAME/main.py
```
   This should open a new tab in your web browser showing your agent in action.

#### Step 6: Entering the brawl

1. Open your file browser (Finder on Mac) and find the BreadBrawl folder.
2. Inside it, find the folder named after your loaf.
3. Right-click that folder and click **Compress** (creates a .zip file).
4. Send the resulting ZIP file to the activity leader.

### Windows

#### Step 1: Check if Python is already installed

1. Press the Windows key, type "PowerShell", press Enter.
2. Type `python --version` and press Enter.
3. If you see something like `Python 3.13.5`, you're all set — skip to Step 3.
4. If it says Python isn't recognized, or the Microsoft Store opens up, go to Step 2.

#### Step 2: Install Python

1. Go to **python.org/downloads** in your browser.
2. Click the big "Download Python" button (it automatically detects Mac vs. Windows).
3. Run the installer you downloaded. On the very first screen of the installer, check the box at the bottom that says **"Add python.exe to PATH"** before clicking Install. This step is easy to miss, and nothing will work correctly without it.
4. When installation finishes, **close your PowerShell window completely and reopen it**, then repeat the version check from Step 1 to confirm it worked.

#### Step 3: Download the BreadBrawl code

1. Go to `github.com/ShinyHydropi/BreadBrawl` in your browser.
2. Click the green **Code** button, then click **Download ZIP**.
3. Find the downloaded file in your Downloads folder and unzip it (right-click it → **Extract All** → Extract)
4. You should now have a folder named `BreadBrawl-main`. Move it somewhere easy to find, like your Desktop.

#### Step 4: Setup BreadBrawl

1. Open PowerShell.
2. Move into the folder you unzipped:
```
cd Desktop\BreadBrawl-main
```
   *(Tip: type `cd ` — with a trailing space — then drag the folder itself into the PowerShell window. It will fill in the path for you.)*  
3. Create a virtual environment:
```
python -m venv .venv
```
4. Turn on the virtual environment:
```
.\.venv\Scripts\Activate.ps1
```
   - If you get a red error message mentioning "execution policy," run this once (type `Y` and press Enter when it asks), then try the activate command again:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
   You'll know it worked when you see `(.venv)` appear at the start of your line.
5. Install the required software. This can take a few minutes — that's expected:
```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### Step 5: Time to bake!

Every time you come back to this later (a new day, after closing your terminal, etc.), redo step 4 above first — activate the virtual environment — before running anything below.
 
1. **Create your loaf.** This asks you a few questions to set up your character:
```
python setup_loaf.py
```
2. **Train your agent.** Replace `NAME` with the name you gave your loaf in step 1:
```
python dql_agent_NAME.py
```
   This is where your agent actually learns to fight. It may take a while and print out a lot of numbers while it trains — that's normal, just let it run.
3. **Watch your agent fight.** Replace `NAME` again:
```
streamlit run agent_arena.py NAME/main.py
```
   This should open a new tab in your web browser showing your agent in action.

#### Step 6: Entering the brawl

1. Open your file browser (File Explorer on Windows) and find the BreadBrawl folder.
2. Inside it, find the folder named after your loaf.
3. Right-click that folder and click **Send to** → **Compressed (zipped) folder**.
4. Send the resulting ZIP file to the activity leader.

## References

brthor. (2021, January 18). *Coding deep Q-learning in PyTorch – Reinforcement learning DQN code tutorial series p.1* [Video]. YouTube. https://www.youtube.com/watch?v=NP8pXZdU-5U

Sutton, R. S., & Barto, A. G. (2015). *Reinforcement learning: An introduction* (2nd ed., in progress). https://web.stanford.edu/class/psych209/Readings/SuttonBartoIPRLBook2ndEd.pdf