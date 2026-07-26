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
> - Environment - the thing the agent is interacting with that defines what actions can be taken and what effect
>   those actions will have
> - Action - something the agent can do in the environment
> - State - any information about the environment (for example, the location of objects if the agent is trying
>   to navigate)
> - Agent - a program that chooses actions to take and can improve is policy as it trains
> - Policy - the strategy the agent uses to select actions (think of it like a function where the state of the
>   environment is he input and the output is the action the agent should take)

### Reinforcement learning with BreadBrawl

For this project, our environment is BreadBrawl. The actions available to the agent are seven attacks. The state
includes information such as how much HP each player has left and the duration of the effects of some attacks.

## Deep Q-Learning

### Q-Learning

### Deep

## Training your agent

### Recipe for success

### Time to bake!

### Entering the brawl

## References