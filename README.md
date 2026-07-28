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
15,000,000 x 3 table of every possible state-action pair or a mathematical function defined by 35,000 parameters.
Functions tend to be far more efficient, and neural networks are perfect for the job. Think of neural networks
as infinitely flexible functions that can accurately represent the Q-function of any environment. Neural networks
can also be optimized easily by using chain rule.

## Training your agent

Use the following steps to create, train, and submit your loaf

### Recipe for success

1. Create a name for your loaf and rename the "Default" folder to the name you created
2. Replace "Default" in both dql_agent.py and main.py with your loaf's name
3. Delete the `# ` on line 71 of dql_agent.py fill in the extra values you want in each stat and what three
attacks your loaf will use
4. Delete line 68 in dql_agent.py

### Time to bake!

1. Open a terminal
   - Linux: press Ctrl + Alt + T
   - Mac: press Cmd + Spacebar and type "Terminal"
   - Windows: press the Windows key, type "Terminal"
2. Copy and paste the following command into your terminal, fill in your username, and hit enter  
> ```git clone https://github.com/YOUR_GITHUB_USERNAME_HERE/BreadBrawl```
3. Copy, paste, and enter this command as well
> ```cd BreadBrawl```
4. To train your agent, enter this command
> ```python dql_agent.py```
5. To see your agent in action, add your loaf's name and enter this command
> ```streamlit run agent_arena.py THE_NAME_YOU_CHOSE_FOR_YOUR_LOAF\main.py```

### Entering the brawl

1. Open files and find where you saved BreadBrawl
2. Open BreadBrawl and right-click on the folder with your loaf's name and click "Compress to zip"
3. Send the zipped file to me

## References

brthor. (2021, January 18). *Coding deep Q-learning in PyTorch – Reinforcement learning DQN code tutorial series p.1* [Video]. YouTube. https://www.youtube.com/watch?v=NP8pXZdU-5U

Sutton, R. S., & Barto, A. G. (2015). *Reinforcement learning: An introduction* (2nd ed., in progress). https://web.stanford.edu/class/psych209/Readings/SuttonBartoIPRLBook2ndEd.pdf